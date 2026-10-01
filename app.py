from flask import Flask, render_template, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "libraryuser")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "library123")
DB_NAME = os.environ.get("DB_NAME", "smart_library")


def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


@app.route("/")
def home():
    return render_template("index.html")


# Search books
@app.route("/api/books", methods=["GET"])
def books():
    search = request.args.get("search", "").strip()

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if search:
            query = """
                SELECT *
                FROM books
                WHERE title LIKE %s
                   OR author LIKE %s
                   OR category LIKE %s
                ORDER BY title
            """

            value = "%" + search + "%"

            cursor.execute(
                query,
                (value, value, value)
            )
        else:
            cursor.execute("""
                SELECT *
                FROM books
                ORDER BY title
            """)

        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Check availability of a particular book
@app.route("/api/availability", methods=["GET"])
def availability():
    title = request.args.get("title", "").strip()

    if not title:
        return jsonify({
            "error": "Please provide book title"
        }), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT title, author, available_copies, total_copies
            FROM books
            WHERE title LIKE %s
            LIMIT 1
        """, ("%" + title + "%",))

        book = cursor.fetchone()

        cursor.close()
        conn.close()

        if not book:
            return jsonify({
                "found": False,
                "message": "Book not found"
            })

        if book["available_copies"] > 0:
            status = "Available"
        else:
            status = "Not Available"

        return jsonify({
            "found": True,
            "title": book["title"],
            "author": book["author"],
            "available_copies": book["available_copies"],
            "total_copies": book["total_copies"],
            "status": status
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get issued books
@app.route("/api/issued", methods=["GET"])
def issued_books():
    student_id = request.args.get("student_id", "").strip()

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if student_id:
            cursor.execute("""
                SELECT
                    transactions.id,
                    students.student_id,
                    students.name,
                    books.title,
                    transactions.issue_date,
                    transactions.due_date,
                    transactions.status
                FROM transactions
                JOIN students
                    ON transactions.student_id = students.id
                JOIN books
                    ON transactions.book_id = books.id
                WHERE students.student_id = %s
                AND transactions.status = 'Issued'
                ORDER BY transactions.due_date
            """, (student_id,))
        else:
            cursor.execute("""
                SELECT
                    transactions.id,
                    students.student_id,
                    students.name,
                    books.title,
                    transactions.issue_date,
                    transactions.due_date,
                    transactions.status
                FROM transactions
                JOIN students
                    ON transactions.student_id = students.id
                JOIN books
                    ON transactions.book_id = books.id
                WHERE transactions.status = 'Issued'
                ORDER BY transactions.due_date
            """)

        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get student information
@app.route("/api/student", methods=["GET"])
def student():
    student_id = request.args.get("student_id", "").strip()

    if not student_id:
        return jsonify({
            "error": "Student ID is required"
        }), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT student_id, name, department, email
            FROM students
            WHERE student_id = %s
        """, (student_id,))

        data = cursor.fetchone()

        cursor.close()
        conn.close()

        if not data:
            return jsonify({
                "found": False,
                "message": "Student not found"
            })

        return jsonify({
            "found": True,
            "student": data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Main voice/text command processor
@app.route("/api/command", methods=["POST"])
def command():
    data = request.get_json()

    command_text = data.get("command", "").strip().lower()

    if not command_text:
        return jsonify({
            "response": "Please enter a library command."
        })

    # Availability command
    availability_words = [
        "available",
        "availability",
        "is there",
        "do you have"
    ]

    if any(word in command_text for word in availability_words):

        remove_words = [
            "is",
            "the",
            "book",
            "available",
            "availability",
            "do",
            "you",
            "have",
            "there",
            "of"
        ]

        title = command_text

        for word in remove_words:
            title = title.replace(word, " ")

        title = " ".join(title.split())

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT title, author, available_copies, total_copies
                FROM books
                WHERE title LIKE %s
                LIMIT 1
            """, ("%" + title + "%",))

            book = cursor.fetchone()

            cursor.close()
            conn.close()

            if not book:
                return jsonify({
                    "response": "Sorry, I could not find that book."
                })

            if book["available_copies"] > 0:
                response = (
                    f"{book['title']} by {book['author']} "
                    f"is available. "
                    f"{book['available_copies']} copies are available."
                )
            else:
                response = (
                    f"{book['title']} is currently not available."
                )

            return jsonify({
                "response": response
            })

        except Exception as e:
            return jsonify({
                "response": "Database error: " + str(e)
            }), 500

    # Search command
    if "search" in command_text or "find" in command_text:

        title = command_text

        for word in ["search", "find", "book", "for"]:
            title = title.replace(word, " ")

        title = " ".join(title.split())

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            value = "%" + title + "%"

            cursor.execute("""
                SELECT title, author, category, available_copies
                FROM books
                WHERE title LIKE %s
                   OR author LIKE %s
                   OR category LIKE %s
                ORDER BY title
            """, (value, value, value))

            books_data = cursor.fetchall()

            cursor.close()
            conn.close()

            if not books_data:
                return jsonify({
                    "response": "No matching books were found."
                })

            names = []

            for book in books_data[:5]:
                names.append(
                    f"{book['title']} by {book['author']}"
                )

            response = "I found: " + ", ".join(names)

            return jsonify({
                "response": response,
                "books": books_data
            })

        except Exception as e:
            return jsonify({
                "response": "Database error: " + str(e)
            }), 500

    # Help
    if "help" in command_text:
        return jsonify({
            "response": (
                "You can say: "
                "Is Python Programming available? "
                "Search Python books. "
                "Or show issued books."
            )
        })

    return jsonify({
        "response": (
            "I did not understand the command. "
            "Try asking about book availability or searching for a book."
        )
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
