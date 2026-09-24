"""
Student Management System (backend logic - shared by CLI and the web blueprint)
---------------------------
A console-based application to manage student records (personal details,
academic performance, and attendance) in a centralized SQLite database,
using structured programming logic and SQL queries, with basic validation
for accurate data entry and retrieval.

Usage:
    python student_management.py
"""
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "students.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the students and attendance tables if they don't already exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name         TEXT NOT NULL,
                roll_number  TEXT NOT NULL UNIQUE,
                branch       TEXT NOT NULL,
                semester     INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
                gpa          REAL CHECK (gpa >= 0 AND gpa <= 10)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id    INTEGER NOT NULL,
                date          TEXT NOT NULL,
                status        TEXT NOT NULL CHECK (status IN ('Present', 'Absent')),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
            )
        """)
        conn.commit()


# ---------------- Sample dataset (seeded once, only if the DB is empty) ----------------

_FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna", "Ishaan", "Rohan",
    "Ananya", "Diya", "Isha", "Kavya", "Myra", "Priya", "Saanvi", "Anika", "Riya", "Tanvi",
    "Karthik", "Nikhil", "Manav", "Yash", "Aryan", "Sneha", "Pooja", "Neha", "Meera", "Shreya",
]
_LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Rana", "Thakur", "Chauhan", "Mehta", "Kapoor",
    "Joshi", "Reddy", "Nair", "Iyer", "Patel", "Bhat", "Chandel", "Negi", "Rawat", "Malhotra",
]
_BRANCHES = ["Computer Science", "Information Technology", "Electronics", "Mechanical", "Civil", "Data Science"]


def seed_sample_data(num_students: int = 60, attendance_days: int = 15):
    """Populates a large, realistic-looking sample dataset (students +
    attendance) the first time the app runs, so the project has plenty of
    data to browse instead of starting empty. Safe to call repeatedly -
    it's a no-op once any student already exists."""
    with get_connection() as conn:
        existing = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        if existing > 0:
            return

        rng = random.Random(42)
        used_rolls = set()
        today = date.today()

        for i in range(num_students):
            first = rng.choice(_FIRST_NAMES)
            last = rng.choice(_LAST_NAMES)
            name = f"{first} {last}"
            branch = rng.choice(_BRANCHES)
            semester = rng.randint(1, 8)
            gpa = round(rng.uniform(5.5, 9.8), 2)

            branch_code = "".join(w[0] for w in branch.split())[:2].upper()
            roll = f"{branch_code}{2021 + rng.randint(0, 4)}{str(i + 1).zfill(3)}"
            while roll in used_rolls:
                roll = f"{branch_code}{2021 + rng.randint(0, 4)}{str(rng.randint(1, 999)).zfill(3)}"
            used_rolls.add(roll)

            cur = conn.execute(
                "INSERT INTO students (name, roll_number, branch, semester, gpa) VALUES (?, ?, ?, ?, ?)",
                (name, roll, branch, semester, gpa),
            )
            student_id = cur.lastrowid

            attendance_rows = []
            for d in range(attendance_days):
                att_date = (today - timedelta(days=attendance_days - d)).isoformat()
                status = "Present" if rng.random() < 0.85 else "Absent"
                attendance_rows.append((student_id, att_date, status))
            conn.executemany(
                "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                attendance_rows,
            )

        conn.commit()


# ---------------- Validation helpers ----------------

def _validate_semester(value: str):
    if not value.isdigit() or not (1 <= int(value) <= 8):
        raise ValueError("Semester must be a whole number between 1 and 8.")
    return int(value)


def _validate_gpa(value: str):
    try:
        gpa = float(value)
    except ValueError:
        raise ValueError("GPA must be a number.")
    if not (0 <= gpa <= 10):
        raise ValueError("GPA must be between 0 and 10.")
    return gpa


# ---------------- CRUD operations ----------------

def add_student(name, roll_number, branch, semester, gpa):
    semester = _validate_semester(str(semester))
    gpa = _validate_gpa(str(gpa))
    if not name.strip() or not roll_number.strip():
        raise ValueError("Name and roll number cannot be empty.")

    with get_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO students (name, roll_number, branch, semester, gpa) "
                "VALUES (?, ?, ?, ?, ?)",
                (name.strip(), roll_number.strip(), branch.strip(), semester, gpa),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Roll number '{roll_number}' already exists.")


def list_students():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT student_id, name, roll_number, branch, semester, gpa "
            "FROM students ORDER BY name"
        ).fetchall()
    return rows


def update_gpa(roll_number, new_gpa):
    new_gpa = _validate_gpa(str(new_gpa))
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE students SET gpa = ? WHERE roll_number = ?",
            (new_gpa, roll_number.strip()),
        )
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"No student found with roll number '{roll_number}'.")


def delete_student(roll_number):
    with get_connection() as conn:
        cur = conn.execute(
            "DELETE FROM students WHERE roll_number = ?", (roll_number.strip(),)
        )
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"No student found with roll number '{roll_number}'.")


def mark_attendance(roll_number, date, status):
    if status not in ("Present", "Absent"):
        raise ValueError("Status must be 'Present' or 'Absent'.")
    with get_connection() as conn:
        student = conn.execute(
            "SELECT student_id FROM students WHERE roll_number = ?", (roll_number.strip(),)
        ).fetchone()
        if not student:
            raise ValueError(f"No student found with roll number '{roll_number}'.")
        conn.execute(
            "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
            (student[0], date.strip(), status),
        )
        conn.commit()


def attendance_report(roll_number):
    with get_connection() as conn:
        student = conn.execute(
            "SELECT student_id, name FROM students WHERE roll_number = ?",
            (roll_number.strip(),),
        ).fetchone()
        if not student:
            raise ValueError(f"No student found with roll number '{roll_number}'.")
        rows = conn.execute(
            "SELECT date, status FROM attendance WHERE student_id = ? ORDER BY date",
            (student[0],),
        ).fetchall()
    return student[1], rows


# ---------------- Console menu ----------------

def _print_students(rows):
    if not rows:
        print("No students found.")
        return
    print(f"{'ID':<4}{'Name':<20}{'Roll No':<12}{'Branch':<10}{'Sem':<5}{'GPA':<5}")
    print("-" * 56)
    for r in rows:
        print(f"{r[0]:<4}{r[1]:<20}{r[2]:<12}{r[3]:<10}{r[4]:<5}{r[5]:<5}")
