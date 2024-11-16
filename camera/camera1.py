import cv2
import gspread

from oauth2client.service_account import ServiceAccountCredentials
import threading
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import time

image_filename = 'bread.jpg'
row2=13
row1=13
cam=False
start=False
up=False
cum=False
fine=False
yes=9
full=12

def run1():
    global start
    global frame
    if not start:
        cv2.imwrite("C:\\Users\\korn\\Downloads\\CPram\\hole\\"+'bread.jpg',frame)
        print("cap")
        image_url=drive("C:\\Users\\korn\\Downloads\\CPram\\hole\\bread.jpg")
        send(image_url)
        massage("pass")
def run():
    global start
    global frame
    if not start:
        cv2.imwrite("C:\\Users\\korn\\Downloads\\CPram\\hole\\"+'bread.jpg',frame)
        print("cap")
        image_url=drive("C:\\Users\\korn\\Downloads\\CPram\\hole\\bread.jpg")
        send(image_url)
        massage("fail")
    
def drive(image_filename):
    global scope
    global up
    if not up:
        up=True
        scope = ["https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/spreadsheets"]
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "subtle-well-439603-q6-9d8155a8688e.json", scope
        )
        drive_service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': 'bread.jpg','parents': ['1FUn4DdygkXEFmDzVynHb1zlL9a9b6VBL']}
        media = MediaFileUpload(image_filename, mimetype='image/jpeg')
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        image_url = f"https://drive.google.com/uc?id={file_id}"
        print(f"รูปภาพอัปโหลดสำเร็จ: {image_url}")
        return image_url

def send(image_url):
    global row2
    global cam
    if not cam:
        cam=True
        creds = ServiceAccountCredentials.from_json_keyfile_name(
        "subtle-well-439603-q6-9d8155a8688e.json", scope
        )
        client = gspread.authorize(creds)

        sheet = client.open("bread").sheet1

        cell = f'A{row2}'
        sheet.update_acell(cell, image_url)
        print(f"อัปเดตรูปภาพใน Google Sheet ที่ {cell} สำเร็จ")
        row2 += 1

        print("อัปเดตรูปภาพลงใน Google Sheet สำเร็จ")
        
        
def massage(world):
    global row1
    global up
    global start
    global cam
    global cum
    global fine
    global yes
    global full
    if not cum:
        cum=True
        creds = ServiceAccountCredentials.from_json_keyfile_name(
        "subtle-well-439603-q6-9d8155a8688e.json", scope
        )
        client = gspread.authorize(creds)

        sheet = client.open("bread").sheet1
        cell1 = f'B{row1}'
        sheet.update_acell(cell1,world)
        if world=='pass':
            yes+=1
            sheet.update_acell(f'D{1}',yes)
            print('pass')
        full+=1
        sheet.update_acell(f'D{2}',full)
            
        print("ส่งข้อความ")
        row1 += 1
        cum=False
        start=False
        cam=False
        up=False
        fine=False
    
def detect_holes(frame):
    global cam, fine
    global frame_with_holes
    point_x, point_y = 498, 5
    # แปลงภาพเป็นโทนเทา (Grayscale)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow("gray",gray)
    # ใช้ GaussianBlur เพื่อลด Noise
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    cv2.imshow("blurred",blurred)
    # ใช้ Threshold เพื่อแปลงเป็นภาพ Binary
    _, binary = cv2.threshold(blurred,127, 255, cv2.THRESH_BINARY_INV)
    cv2.imshow('binary',binary)
    # ค้นหา Contours ในภาพ
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # วนลูปเพื่อวาด Contours และตรวจสอบว่าเป็นรูหรือไม่
    if len(contours) >= 1:
        for contour in contours:
            area = cv2.contourArea(contour)  # คำนวณพื้นที่ของ contour
            if 10< area <1800 :  # กรองเฉพาะ contour ที่มีขนาดใหญ่กว่า 50 px
                    cv2.drawContours(frame, [contour], -1, (0, 255, 0), 0)
            (x, y, w, h) = cv2.boundingRect(contour)
            if x <= point_x <= x + w and y <= point_y <= y + h and not fine:
                    fine=True
                    cv2.rectangle(frame, (x, y), (x + w, y + h), 0, 0, 255, 0)  # วาดกรอบรู
                    ku=threading.Thread(target=run)
                    ku.start()        
    else:
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            if x <= point_x <= x + w and y <= point_y <= y + h and not fine:
                fine=True
                cv2.rectangle(frame, (x, y), (x + w, y + h), 0, 0, 255, 2)  # วาดกรอบรู
                ol=threading.Thread(target=run1)
                ol.start()
    return frame
        

def main():
    global frame
    # เปิดกล้อง (ค่า 0 คือกล้องหลัก)
    cap = cv2.VideoCapture(0+cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("ไม่สามารถเปิดกล้องได้")
        return

    while True:
        ret, frame = cap.read()  # อ่านภาพจากกล้อง
        if not ret:
            break
        
        # ตรวจจับรูในภาพ
                   #[y1:y2, x1:x2]
        roi = frame[42:409,8:636]
        frame_with_holes = detect_holes(roi)
        # แสดงผลลัพธ์
        cv2.imshow("Holes Detection", frame_with_holes)
        # กด 'q' เพื่อออกจากโปรแกรม
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.waitKey(1) & 0xFF == ord("l"):
            cv2.imwrite("C:\\Users\\korn\\Downloads\\CPram\\hole\\"+image_filename,frame_with_holes)
            print("cap")
            ku=threading.Thread(target=run)
            ku.start()
    # ปิดการใช้งานกล้องและหน้าต่างทั้งหมด
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()