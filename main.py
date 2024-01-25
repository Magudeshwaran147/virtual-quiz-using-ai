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
import mysql.connector

# Database Configuration
db_config = {
    "host": "localhost",
    "port": "3306",
    "user": "virtualquiz",
    "password": "Virtual@uiz7",
    "database": "quiz_list"
}
# Initialize the database connection
def initialize_database_connection(db_config):

    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

# Function to fetch quiz questions from the MySQL database
def fetch_quiz_questions(connection):
    questions = []

    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM quiz_list")
            questions = cursor.fetchall()
            for question in questions:
                if 'type' not in question or question['type'] not in ['objective', 'technical', 'mathematical']:
                    # Set a default value or handle the error as needed
                    question['type'] = 'unknown'  # You can set it to a default value like 'unknown'

    except mysql.connector.Error as e:
        print(f"Error fetching questions: {e}")

    return questions
# Initialize the database connection
connection = initialize_database_connection(db_config)

if connection is not None:
    # Fetch quiz questions from the database
    quiz_questions = fetch_quiz_questions(connection)
    if not quiz_questions:
        print("No quiz questions available.")
    else:
        connection.close()
        print(f"Total {len(quiz_questions)} quiz questions fetched successfully.")
    for question in quiz_questions:
        question_text = question.get('question', 'N/A')
        question_type = question.get('type', 'N/A')
        print(f"Question: {question_text}, Type: {question_type}")
else:
    print("Database connection failed.")


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
    cap.set(3, 1920)
    cap.set(4, 1080)
    detector = HandDetector(detectionCon=0.8, maxHands=1)

    class MCQ():
        def __init__(self, data):
            self.question = data['question']
            self.choices = [data['choice1'], data['choice2'], data['choice3'], data['choice4']]
            self.answer = data['answer']
            self.userAns = None


        def update(self, cursor, bboxs):
            for x, bbox in enumerate(bboxs):
                x1, y1, x2, y2 = bbox
                if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                    cv.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), cv.FILLED)
                    if self.userAns is None:
                        self.userAns = self.choices[x]
                        time.sleep(0.3)

    class ObjectiveQuestion(MCQ):
        def __init__(self, data):
            super().__init__(data)

    class TechnicalQuestion(MCQ):
        def __init__(self, data):
            super().__init__(data)

    class MathematicalQuestion(MCQ):
        def __init__(self, data):
            super().__init__(data)

        # Initialize question lists for each type
    objective_mcq_list = [ObjectiveQuestion(q) for q in quiz_questions if q['type'] == 'objective']
    technical_mcq_list = [TechnicalQuestion(q) for q in quiz_questions if q['type'] == 'technical']
    mathematical_mcq_list = [MathematicalQuestion(q) for q in quiz_questions if q['type'] == 'mathematical']

    # Create a list of question lists
    question_lists = [objective_mcq_list, technical_mcq_list, mathematical_mcq_list]

    # Print the total number of questions in each category
    print("Total Questions: ", len(quiz_questions))
    print("Objective MCQs : ", len(objective_mcq_list))
    print("Technical MCQs : ", len(technical_mcq_list))
    print("Mathematical MCQs : ", len(mathematical_mcq_list))

    qTotal = len(objective_mcq_list) + len(technical_mcq_list) + len(mathematical_mcq_list)


    qNo = 0
    email_sent = False
    font2 = cv.FONT_HERSHEY_COMPLEX_SMALL
    max_chars_per_line = 40  # Define the maximum number of characters per line
    question_index = 0
    current_question_type = None
    current_question_list = None  # Track the current question list being displayed
    current_question = None
    timer_limit = 10 * 60  # 15 minutes in seconds
    timer = timer_limit
    font_timer = cv.FONT_HERSHEY_SIMPLEX
    timer_position = (50, 400)
    completed_types = [False, False, False]
    all_question_types_completed = False




    def wrap_text(text, max_chars_per_line):
        lines = []
        words = textwrap.wrap(text, max_chars_per_line)
        for line in words:
            lines.append(line)
        return lines

    while True:
        success, img = cap.read()
        hands, img = detector.findHands(img)
        if not all_question_types_completed:
            if current_question_list is None:

                img, _ = cvzone.putTextRect(img, "Choose a question type:", [100, 100], 1, 1, offset=20, border=2, colorT=(0, 0, 0),
                                            colorR=(255, 255, 100), colorB=(0, 0, 0), font=font2)
                img, aaox1 = cvzone.putTextRect(img, "1. Objective", [100, 180], 1, 1, offset=20, border=2,
                                                colorT=(0, 0, 0),
                                                colorR=(255, 0, 0) if completed_types[0] else (255, 255, 100),
                                                colorB=(0, 0, 0), font=font2)  # Blue if completed, yellow if not
                img, aaox2 = cvzone.putTextRect(img, "2. Technical", [100, 260], 1, 1, offset=20, border=2,
                                                colorT=(0, 0, 0),
                                                colorR=(255, 0, 0) if completed_types[1] else (255, 255, 100),
                                                colorB=(0, 0, 0), font=font2)  # Blue if completed, yellow if not
                img, aaox3 = cvzone.putTextRect(img, "3. Mathematical", [100, 340], 1, 1, offset=20, border=2,
                                                colorT=(0, 0, 0),
                                                colorR=(255, 0, 0) if completed_types[2] else (255, 255, 100),
                                                colorB=(0, 0, 0), font=font2)  # Blue if completed, yellow if not
                if hands:
                    lmList = hands[0]['lmList']
                    if len(lmList) >= 13:  # Ensure there are at least 13 landmarks
                        cursor = lmList[8]
                        length, info = detector.findDistance(lmList[8], lmList[12])
                    if length < 30:
                        if not completed_types[0] and aaox1[0] < cursor[0] < aaox1[2] and aaox1[1] < cursor[1] < aaox1[3]:
                            current_question_list = question_lists[0]  # Objective questions
                            current_question_type = 0
                            timer = timer_limit
                            completed_types[0] = True
                        elif not completed_types[1] and aaox2[0] < cursor[0] < aaox2[2] and aaox2[1] < cursor[1] < aaox2[3]:
                            current_question_list = question_lists[1]  # Technical questions
                            current_question_type = 1
                            timer = timer_limit
                            completed_types[1] = True
                        elif not completed_types[2] and aaox3[0] < cursor[0] < aaox3[2] and aaox3[1] < cursor[1] < aaox3[3]:
                            current_question_list = question_lists[2]  # Mathematical questions
                            current_question_type = 2
                            timer = timer_limit
                            completed_types[2] = True


                        else:
                            img, _ = cvzone.putTextRect(img, "Already Completed", [200, 60], 1, 1, offset=20,
                                                        border=2, colorT=(0, 0, 0), colorR=(0, 0, 255), colorB=(0, 0, 0),
                                                        font=font2)
                            current_question = None


            else:
                current_question_list = question_lists[current_question_type]
                timer -= 1
                if timer <= 0:
                    timer = timer_limit  # Reset the timer
                    current_question_type = None
                    current_question_list = None  # Reset the current question list
                    question_index = 0  # Reset question index to 0
                    current_question = None  # Reset the current question list

                    # Reset question index and user answers for the type that timed out
                    if current_question_type == 0:
                        objective_mcq_list = [ObjectiveQuestion(q) for q in quiz_questions if q['type'] == 'objective']
                    elif current_question_type == 1:
                        technical_mcq_list = [TechnicalQuestion(q) for q in quiz_questions if q['type'] == 'technical']
                    elif current_question_type == 2:
                        mathematical_mcq_list = [MathematicalQuestion(q) for q in quiz_questions if
                                                 q['type'] == 'mathematical']



                if current_question_list is not None:
                    if question_index < len(current_question_list):
                        current_question = current_question_list[question_index]
                        if current_question.userAns is not None:
                            question_index += 1

                        if question_index >= len(current_question_list):
                            current_question_type = None

                    else:
                        question_index = 0
                        current_question_list = None
                        current_question_type = None
                if current_question_type is not None:
                    minutes = timer // 60
                    seconds = timer % 60
                    timer_text = f'Time Left: {minutes:02d}:{seconds:02d}'
                    img = cv.putText(img, timer_text, timer_position, font_timer, 1, (255, 255, 255), 2, cv.LINE_AA)

                    if qNo < qTotal:
                        mcq = current_question
                        if current_question_list is not None:
                            wrapped_question = wrap_text(mcq.question, max_chars_per_line)
                            y_offset = 45

                            for wrapped_line in wrapped_question:
                                img, _ = cvzone.putTextRect(img, wrapped_line, [45, y_offset], 1, 1, offset=20, border=3,
                                                                colorT=(255, 255, 255), colorB=(255, 255, 255), colorR=(0, 0, 0), font=font2)
                                y_offset += 60

                            img, bbox1 = cvzone.putTextRect(img, mcq.choices[0], [75, 200], 1, 1, offset=20, border=2, colorT=(0, 0, 0),
                                                                colorB=(0, 0, 0), colorR=(255, 255, 100), font=font2)
                            img, bbox2 = cvzone.putTextRect(img, mcq.choices[1], [450, 200], 1, 1, offset=20, border=2, colorT=(0, 0, 0),
                                                                colorB=(0, 0, 0), colorR=(255, 255, 100), font=font2)
                            img, bbox3 = cvzone.putTextRect(img, mcq.choices[2], [75, 300], 1, 1, offset=20, border=2, colorT=(0, 0, 0),
                                                                colorB=(0, 0, 0), colorR=(255, 255, 100), font=font2)
                            img, bbox4 = cvzone.putTextRect(img, mcq.choices[3], [450, 300], 1, 1, offset=20, border=2, colorT=(0, 0, 0),
                                                                colorB=(0, 0, 0), colorR=(255, 255, 100), font=font2)

                            if hands:
                                lmList = hands[0]['lmList']
                                cursor = lmList[8]
                                length, info = detector.findDistance(lmList[8], lmList[12])

                                if length < 35:
                                    current_question.update(cursor, [bbox1, bbox2, bbox3, bbox4])
                                    if current_question.userAns is not None:
                                        if mcq.userAns is not None:
                                            time.sleep(0.3)
                                            question_index += 1
                                            qNo += 1

        if qNo >= qTotal:
            all_question_types_completed = True
            correct = 0
            wrong = 0
            unselect_Ans = 0

            for mcq in objective_mcq_list + technical_mcq_list + mathematical_mcq_list:
                if mcq.userAns is not None:
                    if mcq.answer == mcq.userAns:
                        correct += 1
                    else:
                        wrong += 1
                else:
                    unselect_Ans += 1


            # Display "Quiz Completed" here
            img, _ = cvzone.putTextRect(img, "Quiz Completed", [220, 120], 1, 1, offset=20, border=2,colorT=(0, 0, 0),
                                                        colorR=(255, 255, 100), colorB=(0, 0, 0), font=font2)
            img, _ = cvzone.putTextRect(img, f'Correct: {correct}', [125, 250], 1, 1, offset=20, border=2,
                                                        colorT=(0, 0, 0), colorR=(255, 255, 100), colorB=(0, 0, 0), font=font2)
            img, _ = cvzone.putTextRect(img, f'Wrong: {wrong}', [350, 250], 1, 1, offset=20, border=2,
                                                        colorT=(0, 0, 0), colorR=(255, 255, 100), colorB=(0, 0, 0), font=font2)
            img, _ = cvzone.putTextRect(img, f'Unanswered: {unselect_Ans}', [220, 320], 1, 1, offset=20, border=2,
                                        colorT=(0, 0, 0), colorR=(255, 255, 100), colorB=(0, 0, 0), font=font2)
            if not email_sent:
                send_score_email(username, email, correct)
                email_sent = True
        # Drow process bar
        if qTotal > 0:
            barValue = 50 + (475 // qTotal) * qNo
            progress_percentage = round((qNo / qTotal) * 100)
        else:
            barValue = 50
            progress_percentage = 0

        cv.rectangle(img, (50, 450), (barValue, 425), (255, 255, 255), cv.FILLED)
        cv.rectangle(img, (50, 450), (525, 425), (0, 0, 0), 5)
        img, _ = cvzone.putTextRect(img, f'{progress_percentage}%', [550, 442], 1, 1, offset=5, border=2,
                                    colorT=(0, 0, 0), colorR=(255, 255, 255), colorB=(0, 0, 0), font=font2)

        cv.imshow("Quiz", img)
        cv.waitKey(1)


    # Release the camera and close OpenCV windows
    cap.release()
    cv.destroyAllWindows()

    # Wait for 5 seconds before exiting
    print("Quiz completed. Exiting in 10 seconds...")


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
            if not quiz_questions:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'Error: No quiz questions available.')
                return
            run_my_python_script(username, email)  # Pass the username to the Python script
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Python script executed')
            pass
        else:
            super().do_GET()

# Start a local web server to serve the HTML file and handle button clicks
def start_web_server():
    with TCPServer(("", 8000), MyHandler) as httpd:
        print("Web server started at http://localhost:8000")
        httpd.serve_forever()
webbrowser.open("http://localhost:8000")

web_server_thread = threading.Thread(target=start_web_server)
web_server_thread.start()
