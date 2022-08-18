import cv2
from cv2 import VideoCapture
import numpy as np
import face_recognition as face
import os
import pymongo
from datetime import datetime

path = 'imgpool'
images = []
classNames = []
myList = os.listdir(path)

face_locations = []
face_encodings = []
face_names = []
face_percent = []
#ตัวแปรนี้ใช้สำหรับคิดเฟรมเว้นเฟรมเพื่อเพิ่มfps
process_this_frame = True

print(myList)

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def markAttendance(name):
    with open('attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')



encodeListKnown = findEncodings(images)
print('encoding complete')

cap = cv2.VideoCapture(0)

while True:
    # อ่านค่าแต่ละเฟรมจากวิดีโอ
    ret, frame = cap.read()
    if ret:
        # ลดขนาดสองเท่าเพื่อเพิ่มfps
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        # เปลี่ยน bgrเป็น rgb
        rgb_small_frame = small_frame[:, :, ::-1]

        face_names = []
        face_percent = []

        if process_this_frame:
            # ค้นหาตำแหน่งใบหน้าในเฟรม
            face_locations = face.face_locations(rgb_small_frame, model="cnn")
            # นำใบหน้ามาหาfeaturesต่างๆที่เป็นเอกลักษณ์
            face_encodings = face.face_encodings(rgb_small_frame, face_locations)

            # เทียบแต่ละใบหน้า
            for face_encoding in face_encodings:
                face_distances = face.face_distance(encodeListKnown, face_encoding)
                best = np.argmin(face_distances)
                face_percent_value = 1 - face_distances[best]

                # กรองใบหน้าที่ความมั่นใจ50% ปล.สามารถลองเปลี่ยนได้
                if face_percent_value >= 0.5:
                    name = known_face_names[best]
                    percent = round(face_percent_value * 100, 2)
                    face_percent.append(percent)
                else:
                    name = "UNKNOWN"
                    face_percent.append(0)
                face_names.append(name)

        # วาดกล่องและtextเมื่อแสดงผลออกมาออกมา
        for (top, right, bottom, left), name, percent in zip(face_locations, face_names, face_percent):
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2

            if name == "UNKNOWN":
                color = [46, 2, 209]
            else:
                color = [255, 102, 51]

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left - 1, top - 30), (right + 1, top), color, cv2.FILLED)
            cv2.rectangle(frame, (left - 1, bottom), (right + 1, bottom + 30), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, top - 6), font, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, "MATCH: " + str(percent) + "%", (left + 6, bottom + 23), font, 0.6, (255, 255, 255), 1)

        # สลับค่าเป็นค่าตรงข้ามเพื่อให้คิดเฟรมเว้นเฟรม
        process_this_frame = not process_this_frame

    cv2.imshow('camera feeder', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

VideoCapture.release()
cv2.destroyAllWindows()