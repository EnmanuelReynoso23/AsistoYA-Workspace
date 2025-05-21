import firebase_admin
from firebase_admin import credentials, db

class Database:
    def __init__(self, cred_path="firebase_service_account.json", db_url=""):
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': db_url
            })
        self.root = db.reference()

    def add_student(self, name, grade, photo, tutor_contact=None):
        students_ref = self.root.child("students")
        new_student = {
            "name": name,
            "grade": grade,
            "photo": photo,
            "tutor_contact": tutor_contact
        }
        student_ref = students_ref.push(new_student)
        return student_ref.key

    def get_all_students(self):
        students_ref = self.root.child("students")
        students = students_ref.get()
        result = []
        if students:
            for key, value in students.items():
                result.append({
                    "id": key,
                    "name": value.get("name"),
                    "grade": value.get("grade"),
                    "status": "Sin registro"
                })
        return result

    def add_attendance_record(self, student_id, date, time, status):
        attendance_ref = self.root.child("attendance")
        new_record = {
            "student_id": student_id,
            "date": date,
            "time": time,
            "status": status
        }
        record_ref = attendance_ref.push(new_record)
        return record_ref.key

    def get_attendance_records(self, start_date, end_date):
        attendance_ref = self.root.child("attendance")
        records = attendance_ref.order_by_child("date").start_at(start_date).end_at(end_date).get()
        result = []
        if records:
            for key, value in records.items():
                result.append(value)
            return result
        return []

    def close_connection(self):
        pass  # Not needed for Firebase

