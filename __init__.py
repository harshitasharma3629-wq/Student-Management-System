"""
Student Management System - Flask blueprint.
Thin web layer on top of student_mgmt/db_logic.py's existing CRUD functions
(the same functions the CLI version uses).
"""
from flask import Blueprint, render_template, request, redirect, url_for

from . import db_logic as db

bp = Blueprint("student_mgmt", __name__, url_prefix="/student-management")


@bp.route("/", methods=["GET"])
def index():
    db.init_db()
    db.seed_sample_data()
    students = db.list_students()
    return render_template("student_mgmt/index.html", active="student_mgmt", students=students, error=None, success=None)


@bp.route("/add", methods=["POST"])
def add():
    db.init_db()
    error = success = None
    try:
        db.add_student(
            request.form.get("name", ""),
            request.form.get("roll_number", ""),
            request.form.get("branch", ""),
            request.form.get("semester", ""),
            request.form.get("gpa", ""),
        )
        success = "Student added successfully."
    except ValueError as e:
        error = str(e)
    students = db.list_students()
    return render_template("student_mgmt/index.html", active="student_mgmt", students=students, error=error, success=success)


@bp.route("/update-gpa", methods=["POST"])
def update_gpa():
    db.init_db()
    error = success = None
    try:
        db.update_gpa(request.form.get("roll_number", ""), request.form.get("gpa", ""))
        success = "GPA updated."
    except ValueError as e:
        error = str(e)
    students = db.list_students()
    return render_template("student_mgmt/index.html", active="student_mgmt", students=students, error=error, success=success)


@bp.route("/delete", methods=["POST"])
def delete():
    db.init_db()
    error = success = None
    try:
        db.delete_student(request.form.get("roll_number", ""))
        success = "Student deleted."
    except ValueError as e:
        error = str(e)
    students = db.list_students()
    return render_template("student_mgmt/index.html", active="student_mgmt", students=students, error=error, success=success)


@bp.route("/attendance", methods=["POST"])
def attendance():
    db.init_db()
    error = success = None
    try:
        db.mark_attendance(
            request.form.get("roll_number", ""),
            request.form.get("date", ""),
            request.form.get("status", ""),
        )
        success = "Attendance recorded."
    except ValueError as e:
        error = str(e)
    students = db.list_students()
    return render_template("student_mgmt/index.html", active="student_mgmt", students=students, error=error, success=success)


@bp.route("/attendance-report", methods=["GET"])
def attendance_report():
    db.init_db()
    roll_number = request.args.get("roll_number", "")
    error = None
    name = None
    rows = []
    attendance_pct = None
    if roll_number:
        try:
            name, rows = db.attendance_report(roll_number)
            if rows:
                present = sum(1 for _, s in rows if s == "Present")
                attendance_pct = round(present / len(rows) * 100, 1)
        except ValueError as e:
            error = str(e)
    students = db.list_students()
    return render_template(
        "student_mgmt/index.html",
        active="student_mgmt",
        students=students,
        error=error,
        success=None,
        report_name=name,
        report_rows=rows,
        report_roll=roll_number,
        attendance_pct=attendance_pct,
    )
