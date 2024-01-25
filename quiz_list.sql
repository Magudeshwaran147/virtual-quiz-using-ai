create database quiz_list;
use quiz_list;
CREATE TABLE quiz_list(
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    choice1 TEXT NOT NULL,
    choice2 TEXT NOT NULL,
    choice3 TEXT NOT NULL,
    choice4 TEXT NOT NULL,
    answer TEXT NOT NULL,
    type ENUM('objective', 'technical', 'mathematical') NOT NULL
);

INSERT INTO quiz_list (question, choice1, choice2, choice3, choice4, answer, type)
VALUES
    ('What is the capital of France?', 'Paris', 'Berlin', 'London', 'Rome', 'Paris', 'objective'),
    ('Which planet is known as the Red Planet?', 'Mars', 'Venus', 'Jupiter', 'Saturn', 'Mars', 'objective'),
    ('What is the largest mammal in the world?', 'Elephant', 'Giraffe', 'Blue Whale', 'Lion', 'Blue Whale', 'technical'),
    ('Which gas do plants absorb from the atmosphere?', 'Oxygen', 'Nitrogen', 'Carbon Dioxide', 'Hydrogen', 'Carbon Dioxide', 'technical'),
    ('Who wrote the play ?', 'William Shakespeare', 'Charles Dickens', 'Jane Austen', 'Leo Tolstoy', 'William Shakespeare', 'mathematical');
