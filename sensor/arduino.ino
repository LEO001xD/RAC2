#include <HTTPClient.h>
#include <VL53L0X.h>
#include <WiFi.h>
#include <Wire.h>

#define NUM_SENSORS 4 
VL53L0X sensors[NUM_SENSORS];

const char *ssid = "Dx100";
const char *password = "11111118";
const char *serverName = "APPS SCRIPT";

const int xshutPins[NUM_SENSORS] = {16, 17, 18, 19};
const int sensorToBaseHeight = 439;
const int sensorToConveyorHeight = 442; // 459
const int numReadings = 20;

int readings[NUM_SENSORS][numReadings];
int readIndex[NUM_SENSORS] = {0};
int total[NUM_SENSORS] = {0};
int average[NUM_SENSORS] = {0};

int doughHeightSum[NUM_SENSORS] = {0};
int doughHeightCount[NUM_SENSORS] = {0};

bool dataSent = false;
unsigned int hour = 0;

void connectToWiFi() {
    Serial.print("Connecting to WiFi...");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println(" Connected!");
}

bool checkHeightInRange(int height) {
    return (height >= 53 && height <= 57);
}

void sendDataToGoogleSheet(int time, int sensor0, int sensor1, int sensor2, int sensor3, 
                          int overallAverage, bool check1, bool check2, bool check3, bool check4) 
{
    Serial.println("Preparing to send data to Google Sheets...");

    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(serverName);
        http.addHeader("Content-Type", "application/json");

        String jsonData = String("{\"time\":") + time +
                          ",\"sensor0\":" + sensor0 +
                          ",\"sensor1\":" + sensor1 +
                          ",\"sensor2\":" + sensor2 +
                          ",\"sensor3\":" + sensor3 +
                          ",\"overallAverage\":" + overallAverage +
                          ",\"check1\":" + (check1 ? "true" : "false") +
                          ",\"check2\":" + (check2 ? "true" : "false") +
                          ",\"check3\":" + (check3 ? "true" : "false") +
                          ",\"check4\":" + (check4 ? "true" : "false") +
                          ",\"hour\":" + hour + "}";

        Serial.print("JSON Data: ");
        Serial.println(jsonData);

        int httpResponseCode = http.POST(jsonData);
        if (httpResponseCode > 0) {
            Serial.println("Data sent to Google Sheets!");
        } else {
            Serial.print("Error sending data: ");
            Serial.println(httpResponseCode);
        }
        http.end();
    }
}

void SetupSensors() {
    for (int i = 0; i < NUM_SENSORS; i++) {
        pinMode(xshutPins[i], OUTPUT);
        digitalWrite(xshutPins[i], LOW);
    }
    for (int i = 0; i < NUM_SENSORS; i++) {
        digitalWrite(xshutPins[i], HIGH);
        delay(10);

        if (!sensors[i].init()) {
            Serial.print("Failed to detect sensor ");
            Serial.println(i);
            while (1);
        }
        sensors[i].setAddress(0x30 + i);
        sensors[i].setTimeout(500);
        sensors[i].startContinuous();
    }
}

void readAndAverageSensors() {
    for (int i = 0; i < NUM_SENSORS; i++) {
        total[i] -= readings[i][readIndex[i]];
        int reading = sensors[i].readRangeContinuousMillimeters();
        readings[i][readIndex[i]] = reading;
        total[i] += readings[i][readIndex[i]];
        readIndex[i] = (readIndex[i] + 1) % numReadings;
        average[i] = total[i] / numReadings;

        if (i==0) {
          average[i] +=2;
          }
        if (i==1) {
          average[i] += 4;
          }
        if (i==2) {
          average[i] += 10;
          }
        // if (i==3) {
        //   average[i] -= 10;
        //   }
    }
    
}

bool checkForConveyorEnd() {
    for (int i = 0; i < NUM_SENSORS; i++) {
        if (average[i] < sensorToConveyorHeight) {
            dataSent = false;
            return false;
        }
    }
    return true;
}

void calculateAndSendAverageHeight() {
    int averages[NUM_SENSORS];
    bool checks[NUM_SENSORS];

    for (int i = 0; i < NUM_SENSORS; i++) {
        if (doughHeightCount[i] > 0) {
            averages[i] = doughHeightSum[i] / doughHeightCount[i];
            checks[i] = checkHeightInRange(averages[i]);

            doughHeightSum[i] = 0;
            doughHeightCount[i] = 0;
        } else {
            checks[i] = false;
        }
    }

    int overallAverage = (averages[0] + averages[1] + averages[2] + averages[3]) / 4;
    sendDataToGoogleSheet(millis(), averages[0], averages[1], averages[2], averages[3], overallAverage, 
                          checks[0], checks[1], checks[2], checks[3]);
}

void printSensorData() {
    int overallAverage = (average[0] + average[1] + average[2] + average[3]) / 4;

    Serial.print(millis());
    Serial.print(",");
    Serial.print(average[0]);
    Serial.print(",");
    Serial.print(average[1]);
    Serial.print(",");
    Serial.print(average[2]);
    Serial.print(",");
    Serial.print(average[3]);
    Serial.print(",");
    Serial.print(overallAverage);
    Serial.print(",");
    Serial.println(hour);

    collectData();
}

void collectData() {
    for (int i = 0; i < NUM_SENSORS; i++) {
        int doughHeight = sensorToBaseHeight - average[i];
        if (doughHeight < 0) doughHeight = 0;

        doughHeightSum[i] += doughHeight;
        doughHeightCount[i]++;
    }
}

void setup() {
    Serial.begin(115200);
    Wire.begin();
    connectToWiFi();  
    SetupSensors();
    Serial.println("time,sensor0,sensor1,sensor2,sensor3,overallAverage,hour");
}

void loop() {
    static unsigned long lastHourCheck = millis();

    readAndAverageSensors();
    printSensorData();

    if (checkForConveyorEnd() && !dataSent) {
        calculateAndSendAverageHeight();
        dataSent = true;
    }

    if (millis() - lastHourCheck >= 3600000) {
        hour++;
        lastHourCheck = millis();
    }
} 
