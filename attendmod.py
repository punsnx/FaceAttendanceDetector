import cv2
from cv2 import VideoCapture
import numpy as np
import face_recognition
import os
import pymongo
from datetime import datetime

import googlecloud as gc

#import getface as GeT
#import googlecloud as Gc

myclient = pymongo.MongoClient("mongodb+srv://skdev:skdev123456789@skmongocluster.skdn9.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["FaceAttendance"]
workcol = mydb["Attendance"]
mycol = mydb["users"]

path = 'imgpool'
images = []
classNames = []
myList = os.listdir(path)

gc.remove_file()
gc.download_blob()

print(myList)

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)

def initialcsv():
    print("perform csv startup....")
    f = open('attendance.csv', 'r+')
    f.truncate(0)
    today = datetime.now()
    thisday = today.strftime('%c')
    f.writelines(thisday)
    print("csv startup done!")

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
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
            f.writelines(f'\n{name},{saidname},{dtString}')
            #checkin = {"ID": name, "Stamp": dtString}

            Object = {}

            Object["date"] = now.strftime('%d')
            Object["month"] = now.strftime('%m')
            Object["year"] = now.strftime('%Y')
            Object["hour"] = now.strftime('%I')
            Object["minute"] = now.strftime('%M')
            Object["second"] = now.strftime('%S')
            Object["millisecond"] = str(int(now.microsecond/1000))
            Object["apm"] = now.strftime('%p')
            Object["day"] = now.strftime('%A')

            """
            mydoc = mycol.find({"studentID": name}, {"_id": 0, "name": 1, })
            saidname = ""

            for x in mydoc:
                x["name"] = saidname
                #print(x["name"])

            profID = name
            profname = saidname
            """
            checkin = {"studentID": name,"name": saidname, "timestamp": Object}

            workcol.insert_one(checkin)


initialcsv()

print("encoding images....")
encodeListKnown = findEncodings(images)
print('encoding complete!')

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    #imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.resize(img, (0, 0), None, 0.5, 0.5)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    #facesCurFrame = face_recognition.face_locations(imgS, number_of_times_to_upsample=0, model="cnn")
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        #print(faceDis)
        matchIndex = np.argmin(faceDis)

        if faceDis[matchIndex] < 0.50:
            name = classNames[matchIndex].upper()

            mydoc = mycol.find({"studentID": name}, {"_id": 0, "name": 1, })
            for x in mydoc:
                saidname = x["name"]
                print(saidname)

            markAttendance(name)

        else:
            name = 'Unknown'

        y1, x2, y2, x1 = faceLoc
        #y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
        y1, x2, y2, x1 = y1 * 2, x2 * 2, y2 * 2, x1 * 2
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        #cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)#
        #cv2.putText(img, saidname, (x1+6, y2-6),cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(img, saidname, (x1 + 6, y2 + 25), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('camera feeder', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

VideoCapture.release()
cv2.destroyAllWindows()