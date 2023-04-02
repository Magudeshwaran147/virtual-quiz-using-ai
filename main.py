
import cv2 as cv
import csv
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time
cap = cv.VideoCapture(0)
cap.set(3, 1366)
cap.set(4, 768)
detector = HandDetector(detectionCon=0.8,maxHands=1)

class MCQ():
    def __init__(self, data):
        self.question = data[0]
        self.choice1 = data[1]
        self.choice2 = data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])
        self.userAns = None

    def update(self, cursor, bboxs):

        for x, bbox in enumerate(bboxs):
            x1, y1, x2, y2 = bbox
            if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                self.userAns = x + 1
                cv.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), cv.FILLED)

# import csv file
pathCSV = "Mcqs.csv"
with open(pathCSV, newline='\n') as f:
    reader = csv.reader(f)
    dataAll = list(reader)[1:]

# create object
mcqList = []
for q in dataAll:
    mcqList.append(MCQ(q))
print("TOTAL MCQZ : ", len(mcqList))

filename = "mcqans.csv"
with open(filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['question', 'choice1', 'choice2', 'choice3', 'choice4', 'answer', 'userAns'])

    qNo = 0
    qTotal = len(dataAll)

    while True:
        success, img = cap.read()
        # img = cv2.flip(img, 1)
        hands, img = detector.findHands(img)
        # flipType=False

        if qNo < qTotal:
            mcq = mcqList[qNo]

            img, bbox = cvzone.putTextRect(img, mcq.question, [45, 45], 1, 2, offset=20, border=2, colorT=(255, 255, 255), colorB=(255, 160, 0), colorR=(0, 0, 0))
            img, bbox1 = cvzone.putTextRect(img, mcq.choice1, [45, 170], 1, 1, offset=15, border=3, colorT=(0, 0, 0), colorB=(255, 160, 0), colorR=(255, 255, 100))
            img, bbox2 = cvzone.putTextRect(img, mcq.choice2, [370, 170], 1, 1, offset=15, border=3, colorT=(0, 0, 0), colorB=(255, 160, 0), colorR=(255, 255, 100))
            img, bbox3 = cvzone.putTextRect(img, mcq.choice3, [45, 270], 1, 1, offset=15, border=3, colorT=(0, 0, 0), colorB=(255, 160, 0), colorR=(255, 255, 100))
            img, bbox4 = cvzone.putTextRect(img, mcq.choice4, [370, 270], 1, 1, offset=15, border=3, colorT=(0, 0, 0), colorB=(255, 160, 0), colorR=(255, 255, 100))

            if hands:
                lmList = hands[0]['lmList']
                cursor = lmList[8]
                length, info = detector.findDistance(lmList[8], lmList[12])

                if length < 35:
                    mcq.update(cursor, [bbox1, bbox2, bbox3, bbox4])
                    if mcq.userAns is not None:
                        time.sleep(0.3)
                        qNo += 1



        else:
            correct = 0
            wrong = 0
            for mcq in mcqList:
                if mcq.answer == mcq.userAns:
                    correct += 1
                else:
                    wrong += 1
            img, _ = cvzone.putTextRect(img, "Quiz Completed", [250, 350], 1, 2, offset=20,  border=2, colorT=(0, 0, 0), colorR=(255, 255, 100), colorB=(0, 0, 0))
            img, _ = cvzone.putTextRect(img, f'Correct: {correct}', [125, 250], 1, 2, offset=20,  border=2, colorT=(0, 0, 0), colorR=(255, 255, 100), colorB=(0, 0, 0))
            img, _ = cvzone.putTextRect(img, f'Wrong: {wrong}', [350, 250,], 1, 2, offset=20, border=2, colorT=(0, 0, 0), colorR=(255, 255, 100), colorB=(0, 0, 0))
        # Drow process bar
        barValue = 50 + (475//qTotal)*qNo
        cv.rectangle(img, (50, 450), (barValue, 425), (255, 255, 255), cv.FILLED)
        cv.rectangle(img, (50, 450), (525, 425), (0, 0, 0), 5)
        img, _ = cvzone.putTextRect(img, f'{round((qNo/qTotal)*100)}%', [550, 442], 1, 1, offset=10, border=2, colorT=(0, 0, 0), colorR=(255, 255, 255), colorB=(0, 0, 0))




        cv.imshow("Img", img)
        cv.waitKey(1)