CREATE TABLE quiz (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    choice1 TEXT NOT NULL,
    choice2 TEXT NOT NULL,
    choice3 TEXT NOT NULL,
    choice4 TEXT NOT NULL,
    answer TEXT NOT NULL,
    type ENUM('objective', 'technical', 'mathematical') NOT NULL
);

INSERT INTO quiz (question, choice1, choice2, choice3, choice4, answer, type)
VALUES
	('What is the capital of India?', 'Mumbai', 'New Delhi', 'Kolkata', 'Chennai', 'New Delhi', 'objective'),
    ('What is the chemical symbol for water?', 'H2O', 'CO2', 'NaCl', 'O2', 'H2O', 'objective'),
	('What protocol is used to retrieve email from a remote server?', 'HTTP', 'SMTP', 'POP3', 'FTP', 'POP3', 'technical'),
    ('Which programming language is used for developing Android apps?', 'Java', 'Python', 'C++', 'Swift', 'Java', 'technical'),
	('Which protocol is used for secure communication over the internet?', 'HTTPS', 'HTTP', 'FTP', 'SMTP', 'HTTPS', 'technical'),
    ('What is the value of 2 + 2?', '3', '4', '5', '6', '4', 'mathematical'),
    ('Simplify: 3 * (4 + 2) - 8', '14', '16', '18', '20', '14', 'mathematical'),
    ('What is the square root of 144?', '10', '12', '14', '16', '12', 'mathematical'),
    ('Find the value of x: 2x + 5 = 15', '5', '6', '7', '8', '5', 'mathematical'),
    ('What is the area of a rectangle with length 6 and width 4?', '20', '24', '28', '30', '24', 'mathematical');
