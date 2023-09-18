from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import urlparse, parse_qs
from urllib.parse import unquote
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cvzone.HandTrackingModule import HandDetector
import cv2 as cv
import csv
import cvzone
import threading
import webbrowser
import smtplib
import time
import datetime
import textwrap

# Function to send an email with the quiz score
def send_score_email(username, email, score):
    # Email configuration
    sender_email = 'virtualquizusingai@gmail.com'
    sender_password = 'caikslwcxfdbypta'
    receiver_email = email
    subject = 'Quiz Score'

    # Compose the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Email content
    body = f"Hello {username},\n\nYour quiz score is: {score}\n\nThank you for taking the quiz!"
    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print(f"Email sent to {receiver_email} successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")

# Define the Python script you want to run
def run_my_python_script(username, email):

    cap = cv.VideoCapture(0)
    cap.set(3, 1366)
    cap.set(4, 768)
    detector = HandDetector(detectionCon=0.8, maxHands=1)

    class MCQ():
        def __init__(self, data, time_limit=20):
            self.question = data[0]
            self.choice1 = data[1]
            self.choice2 = data[2]
            self.choice3 = data[3]
            self.choice4 = data[4]
            self.answer = int(data[5])
            self.userAns = None
            self.startTime = None
            self.time_limit = time_limit

        def startTimer(self):
            self.startTime = datetime.datetime.now()

        def isTimeUp(self):
            if self.startTime is None:
                return False
            current_time = datetime.datetime.now()
            elapsed_time = (current_time - self.startTime).total_seconds()
            return elapsed_time >= self.time_limit

        def update(self, cursor, bboxs):

            for x, bbox in enumerate(bboxs):
                x1, y1, x2, y2 = bbox
                if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                    cv.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), cv.FILLED)
                    if self.userAns is None:
                        self.userAns = x + 1
                        self.startTimer()
                        time.sleep(0.3)

    # import csv file
    pathCSV = "Mcqs.csv"
    with open(pathCSV, newline='\n') as f:
        reader = csv.reader(f)
        dataAll = list(reader)[1:]

    # create object
    mcqList = []
    for q in dataAll:
        mcqList.append(MCQ(q, time_limit=20))

    print("TOTAL MCQZ : ", len(mcqList))

    qNo = 0
    qTotal = len(dataAll)
    mcqStartTime = None
    email_sent = False
    csv_written = False
    font2 = cv.FONT_HERSHEY_COMPLEX_SMALL
    max_chars_per_line = 40  # Define the maximum number of characters per line

    def wrap_text(text, max_chars_per_line):
        lines = []
        words = text.split()
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars_per_line:
                if current_line:
                    current_line += " "
                current_line += word
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    while True:
        success, img = cap.read()
        hands, img = detector.findHands(img)


        if qNo < qTotal:
            mcq = mcqList[qNo]
            if mcq.userAns is None:
                if mcqStartTime is None:
                    mcqStartTime = time.time()
                elif time.time() - mcqStartTime >= mcq.time_limit:
                    qNo += 1
                    mcqStartTime = None
            else:
                mcqStartTime = None

            wrapped_question = wrap_text(mcq.question, max_chars_per_line)
            y_offset = 45

            for wrapped_line in wrapped_question:
                img, _ = cvzone.putTextRect(img, wrapped_line, [45, y_offset], 1, 1, offset=10, border=2,
                                            colorT=(255, 255, 255), colorB=(255, 160, 0), colorR=(0, 0, 0), font=font2)
                y_offset += 40
            img, bbox1 = cvzone.putTextRect(img, mcq.choice1, [45, 170], 1, 1, offset=10, border=3, colorT=(0, 0, 0),
                                            colorB=(255, 160, 0), colorR=(255, 255, 100), font=font2)
            img, bbox2 = cvzone.putTextRect(img, mcq.choice2, [350, 170], 1, 1, offset=10, border=3, colorT=(0, 0, 0),
                                            colorB=(255, 160, 0), colorR=(255, 255, 100), font=font2)
            img, bbox3 = cvzone.putTextRect(img, mcq.choice3, [45, 270], 1, 1, offset=10, border=3, colorT=(0, 0, 0),
                                            colorB=(255, 160, 0), colorR=(255, 255, 100), font=font2)
            img, bbox4 = cvzone.putTextRect(img, mcq.choice4, [350, 270], 1, 1, offset=10, border=3, colorT=(0, 0, 0),
                                            colorB=(255, 160, 0), colorR=(255, 255, 100), font=font2)

            if hands:
                lmList = hands[0]['lmList']
                cursor = lmList[8]
                length, info = detector.findDistance(lmList[8], lmList[12])

                if length < 35:
                    mcq.update(cursor, [bbox1, bbox2, bbox3, bbox4])
                    if mcq.userAns is not None:
                        mcq.startTimer()
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

            # Send the email and write to the CSV file only if they haven't been done before
            if not email_sent:
                send_score_email(username, email, correct)
                email_sent = True

            if not csv_written:
                # Write the score to the CSV file
                with open("user_scores.csv", mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["name", "Total Quiz", "score", "Wrong"])
                    writer.writerow([username, qTotal, correct, wrong])
                csv_written = True
            img, _ = cvzone.putTextRect(img, "Quiz Completed", [220, 350], 1, 1, offset=20, border=2, colorT=(0, 0, 0),
                                        colorR=(255, 255, 100), colorB=(0, 0, 0), font=font2)
            img, _ = cvzone.putTextRect(img, f'Correct: {correct}', [125, 250], 1, 1, offset=20, border=2,
                                        colorT=(0, 0, 0), colorR=(255, 255, 100), colorB=(0, 0, 0), font=font2)
            img, _ = cvzone.putTextRect(img, f'Wrong: {wrong}', [350, 250, ], 1, 1, offset=20, border=2,
                                        colorT=(0, 0, 0), colorR=(255, 255, 100), colorB=(0, 0, 0), font=font2)
            # Check if quiz has been completed and wait for 10 seconds before exiting
            if correct + wrong == qTotal:
                if mcqStartTime is None:
                    mcqStartTime = time.time()
                elif time.time() - mcqStartTime >= 10:
                    break
        # Drow process bar
        barValue = 50 + (475//qTotal)*qNo
        cv.rectangle(img, (50, 450), (barValue, 425), (255, 255, 255), cv.FILLED)
        cv.rectangle(img, (50, 450), (525, 425), (0, 0, 0), 5)
        img, _ = cvzone.putTextRect(img, f'{round((qNo / qTotal) * 100)}%', [550, 442], 1, 1, offset=5, border=2,
                                    colorT=(0, 0, 0), colorR=(255, 255, 255), colorB=(0, 0, 0), font=font2)

        cv.imshow("Quiz", img)
        cv.waitKey(1)


    # Release the camera and close OpenCV windows
    cap.release()
    cv.destroyAllWindows()

    # Wait for 5 seconds before exiting
    print("Quiz completed. Exiting in 5 seconds...")


# Create a SimpleHTTPRequestHandler to handle the HTTP request
class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        if self.path == '/':
            # Serve the index.html file when the root URL is accessed
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path.startswith('/run_python_script'):
            # Get the username from the query parameter
            query_params = parse_qs(parsed_url.query)
            username = query_params.get('username', [''])[0]
            email = query_params.get('email', [''])[0]
            run_my_python_script(username, email)  # Pass the username to the Python script
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Python script executed')
            pass
        else:
            super().do_GET()

# Start a local web server to serve the HTML file and handle button clicks
def start_web_server():
    with TCPServer(("", 8080), MyHandler) as httpd:
        print("Web server started at http://localhost:8080")
        httpd.serve_forever()
webbrowser.open("http://localhost:8080")

web_server_thread = threading.Thread(target=start_web_server)
web_server_thread.start()
