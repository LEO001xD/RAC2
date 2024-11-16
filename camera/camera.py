import cv2
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import threading

CREDENTIAL_FILE = "your_credentials.json"  # ชื่อไฟล์ Credential
DRIVE_FOLDER_ID = "your_drive_folder_id"   # ID ของโฟลเดอร์ใน Google Drive
OUTPUT_PATH = "./output/bread.jpg"         # Path สำหรับบันทึกภาพ

start = False
frame = None
up = False
cam = False
cum = False
fine = False
row1 = 1
row2 = 1
yes = 0
full = 0

def run1():
    global start, frame
    if not start:
        cv2.imwrite(OUTPUT_PATH, frame)
        print("cap")
        image_url = drive(OUTPUT_PATH)
        send(image_url)
        message("pass")

def run():
    global start, frame
    if not start:
        cv2.imwrite(OUTPUT_PATH, frame)
        print("cap")
        image_url = drive(OUTPUT_PATH)
        send(image_url)
        message("fail")
    
def drive(image_filename):
    global up
    if not up:
        up = True
        scope = ["https://www.googleapis.com/auth/drive",
                 "https://www.googleapis.com/auth/spreadsheets"]
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_FILE, scope)
        drive_service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': 'bread.jpg', 'parents': [DRIVE_FOLDER_ID]}
        media = MediaFileUpload(image_filename, mimetype='image/jpeg')
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        image_url = f"https://drive.google.com/uc?id={file_id}"
        print(f"รูปภาพอัปโหลดสำเร็จ: {image_url}")
        return image_url

def send(image_url):
    global row2, cam
    if not cam:
        cam = True
        scope = ["https://www.googleapis.com/auth/drive",
                 "https://www.googleapis.com/auth/spreadsheets"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_FILE, scope)
        client = gspread.authorize(creds)

        sheet = client.open("bread").sheet1
        cell = f'A{row2}'
        sheet.update_acell(cell, image_url)
        print(f"อัปเดตรูปภาพใน Google Sheet ที่ {cell} สำเร็จ")
        row2 += 1

def message(world):
    global row1, up, start, cam, cum, fine, yes, full
    if not cum:
        cum = True
        scope = ["https://www.googleapis.com/auth/drive",
                 "https://www.googleapis.com/auth/spreadsheets"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_FILE, scope)
        client = gspread.authorize(creds)

        sheet = client.open("bread").sheet1
        cell1 = f'B{row1}'
        sheet.update_acell(cell1, world)
        if world == 'pass':
            yes += 1
            sheet.update_acell(f'D1', yes)
        full += 1
        sheet.update_acell(f'D2', full)
            
        print("ส่งข้อความ")
        row1 += 1
        cum = False
        start = False
        cam = False
        up = False
        fine = False
    
def detect_holes(frame):
    global cam, fine
    point_x, point_y = 498, 5
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    _, binary = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) >= 1:
        for contour in contours:
            area = cv2.contourArea(contour)
            if 10 < area < 1800:
                cv2.drawContours(frame, [contour], -1, (0, 255, 0), 0)
                (x, y, w, h) = cv2.boundingRect(contour)
                if x <= point_x <= x + w and y <= point_y <= y + h and not fine:
                    fine = True
                    threading.Thread(target=run).start()
    else:
        threading.Thread(target=run1).start()
    return frame
        

def main():
    global frame
    cap = cv2.VideoCapture(0+cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("ไม่สามารถเปิดกล้องได้")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        roi = frame[42:409, 8:636]
        frame_with_holes = detect_holes(roi)
        cv2.imshow("Holes Detection", frame_with_holes)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
