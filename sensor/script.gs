function doPost(e) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1");
    const data = JSON.parse(e.postData.contents);

    sheet.appendRow([
      new Date(),            // Timestamp
      data.time,             // Time
      data.sensor0,          // Sensor 0
      data.check1,           // Check 1
      data.sensor1,          // Sensor 1
      data.check2,           // Check 2
      data.sensor2,          // Sensor 2
      data.check3,           // Check 3
      data.sensor3,          // Sensor 3
      data.check4,           // Check 4
      data.overallAverage,   // Overall Average
      data.hour              // Hour
    ]);

    return ContentService.createTextOutput("Success");
  } catch (error) {
    Logger.log("Error: " + error.toString());
    return ContentService.createTextOutput("Error");
  }
}
