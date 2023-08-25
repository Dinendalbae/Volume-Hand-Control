import cv2
import time
import numpy as np
import Module_HandTrackingModule as htm
import mediapipe
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
##########################
wCam, hCam = 640, 480
##########################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=1, maxHands=1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 0
volPer = 0
area = 0
colorVol = (255, 0, 0)
while True:
    success, img = cap.read()

    # Find Hand
    img = detector.findHands(img)
    lmlist, bbox = detector.findPosition(img, draw=True)
    if len(lmlist) > 8:
        if len(lmlist) > 8:
            #print(lmlist[4], lmlist[8])

            # Filter based on size
            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
            print(area)
            if 250 < area < 1000:

                # Find Distance between index and Thumb
                length, img, lineInfo = detector.findDistance(4,8,img)
                #print(length)

                # Convert Volume
                volBar = np.interp(length, [25, 200], [400, 150])
                volPer = np.interp(length, [25, 200], [0, 100])

                # Reduce Resolution to make it smoother
                smoothness = 5
                volPer = smoothness * round(volPer/smoothness)

                # Check fingers up
                fingers = detector.fingersUp()
                print(fingers)

                # If pinky is down set volume
                if not fingers[4]:
                    volume.SetMasterVolumeLevelScalar(volPer/100, None)
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)
                    colorVol = (0, 255, 0)
                else:
                    colorVol = (255, 0, 0)
                x1, y1 = lmlist[4][1], lmlist[4][2]
                x2, y2 = lmlist[8][1], lmlist[8][2]
                cx,cy = (x1 + x2) // 2, (y1 + y2) // 2

                cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 5, (255, 0, 0), cv2.FILLED)

                length = math.hypot(x2 - x1, y2 - y1)
                #print(length)

                # Hand Range 50 - 300
                # Volume Range (-65) - 0



                #if length < 25:
                #    cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)

            cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 2)
            cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                        1, (255, 0, 0), 2)
    cVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, f'Vol Set: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, colorVol, 2)
    # Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img,f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 2)

    cv2.imshow("Img",img)
    cv2.waitKey(1)