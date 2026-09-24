# Student Management System

A SQLite-backed web app for managing student records, GPA and attendance.

## What it does
- Add students, delete students, update a student's GPA.
- Mark a student Present/Absent for a date, and view an attendance report with the attendance percentage.
- Validation at two levels: in Python (semester 1-8, GPA 0-10, non-empty name/roll number) and in the database (`CHECK` constraints, `UNIQUE` roll numbers).
- On first run the database is created and filled with 60 **sample** students and 15 days of attendance each, so there is data to browse. Delete `student_mgmt/students.db` to start fresh.

## Database design
Two tables linked by a foreign key with `ON DELETE CASCADE`, so deleting a student also removes their attendance rows.

```
students   (student_id PK, name, roll_number UNIQUE, branch, semester CHECK 1..8, gpa CHECK 0..10)
attendance (attendance_id PK, student_id FK -> students ON DELETE CASCADE, date, status CHECK Present/Absent)
```
All queries are plain parameterised SQL (`sqlite3` from the standard library).

## Run it
Requires Python 3.9 or newer.
```bash
pip install -r requirements.txt
python app.py          # opens http://127.0.0.1:5000
```

## Project structure
```
app.py                     # Flask app
student_mgmt/
  __init__.py              # Flask blueprint (routes)
  db_logic.py              # schema, validation and all SQL
templates/                 # HTML pages
static/style.css
```
The database file `student_mgmt/students.db` is created automatically and is git-ignored.

## Tech
Python, SQLite, SQL, Flask
