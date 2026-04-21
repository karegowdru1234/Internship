import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime
import mysql.connector

# MySQL Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bhairesh123@",
    database="attendance_db"
)

cursor = conn.cursor()

# Dataset folder
path = 'dataset'
images = []
classNames = []

for cl in os.listdir(path):
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

# Encode faces
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodes = face_recognition.face_encodings(img)

        if len(encodes) > 0:
            encodeList.append(encodes[0])

    return encodeList

print("Encoding images...")
encodeListKnown = findEncodings(images)
print("Encoding Complete")

# Start webcam
cap = cv2.VideoCapture(0)

while True:

    success, img = cap.read()

    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):

        y1, x2, y2, x1 = faceLoc
        y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4

        # Draw rectangle
        cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)

        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        if len(faceDis) == 0:
            continue

        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:

            name = classNames[matchIndex].upper()

            # Name label
            cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),
                        cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)

            # Crop face
            face_img = img[y1:y2, x1:x2]

            now = datetime.now()
            date = now.date()
            time = now.strftime('%H:%M:%S')

            # Check if attendance already exists
            cursor.execute(
                "SELECT * FROM attendance WHERE name=%s AND date=%s",
                (name, date)
            )

            result = cursor.fetchone()

            if result is None:

                image_name = f"{name}_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
                filepath = f"static/captured_faces/{image_name}"

                # Save image
                cv2.imwrite(filepath, face_img)

                # Insert attendance
                cursor.execute(
                    "INSERT INTO attendance (name, date, time, image) VALUES (%s,%s,%s,%s)",
                    (name, date, time, image_name)
                )

                conn.commit()

                print("Attendance marked for", name)

            else:
                print(name, "already marked today")

            cv2.imshow("Captured Face", face_img)

    cv2.imshow("Webcam", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()