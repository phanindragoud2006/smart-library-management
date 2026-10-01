CREATE DATABASE IF NOT EXISTS smart_library;

USE smart_library;


-- STUDENTS TABLE

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(30) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    email VARCHAR(100)
);


-- BOOKS TABLE

CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(150) NOT NULL,
    category VARCHAR(100),
    total_copies INT DEFAULT 1,
    available_copies INT DEFAULT 1
);


-- TRANSACTIONS TABLE

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    book_id INT NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE NULL,
    status VARCHAR(30) DEFAULT 'Issued',

    FOREIGN KEY (student_id)
        REFERENCES students(id),

    FOREIGN KEY (book_id)
        REFERENCES books(id)
);


-- STUDENT DATA

INSERT INTO students
(student_id, name, department, email)
VALUES
('24761A42B0', 'Phanindra Goud', 'AI & ML', 'phanindra@example.com'),
('24761A42A2', 'Miriyala Susmitha', 'AI & ML', 'susmitha@example.com'),
('25765A4209', 'Kandula Praveen', 'AI & ML', 'praveen@example.com'),
('24761A42C7', 'Thondepu Charithardha Sai', 'AI & ML', 'charith@example.com');


-- BOOK DATA

INSERT INTO books
(title, author, category, total_copies, available_copies)
VALUES

('Python Programming',
 'Reema Thareja',
 'Programming',
 5,
 3),

('Machine Learning',
 'Tom Mitchell',
 'Artificial Intelligence',
 4,
 2),

('Artificial Intelligence',
 'Stuart Russell',
 'Artificial Intelligence',
 3,
 1),

('Data Structures',
 'Mark Allen Weiss',
 'Computer Science',
 5,
 5),

('Database Management Systems',
 'Raghu Ramakrishnan',
 'Database',
 4,
 4),

('Computer Networks',
 'Andrew S. Tanenbaum',
 'Networking',
 3,
 2),

('Operating System Concepts',
 'Abraham Silberschatz',
 'Operating Systems',
 5,
 5),

('Deep Learning',
 'Ian Goodfellow',
 'Artificial Intelligence',
 3,
 2),

('Java Programming',
 'Herbert Schildt',
 'Programming',
 4,
 4),

('Cloud Computing',
 'Rajkumar Buyya',
 'Cloud',
 3,
 3);


-- TRANSACTION DATA

INSERT INTO transactions
(student_id, book_id, issue_date, due_date, status)
VALUES
(
    1,
    1,
    '2026-09-20',
    '2026-10-05',
    'Issued'
),

(
    2,
    2,
    '2026-09-22',
    '2026-10-07',
    'Issued'
),

(
    3,
    3,
    '2026-09-25',
    '2026-10-10',
    'Issued'
);
