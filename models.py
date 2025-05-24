import random
import string
import os
import pandas as pd
import json
from datetime import datetime
from fpdf import FPDF

class SchoolManager:
    def __init__(self):
        self.courses = {}
        self.professors = {}
        self.students = {}
        self.load_data()
    
    def create_course(self, name):
        course = Course(name)
        self.courses[course.code] = course
        self.save_data()
        return course
    
    def register_professor(self, name, surname, email):
        professor = Professor(name, surname, email)
        self.professors[professor.code] = professor
        self.save_data()
        return professor
    
    def register_student(self, name, surname, email):
        student = Student(name, surname, email)
        self.students[student.code] = student
        self.save_data()
        return student
    
    def assign_professor_to_course(self, professor_code, course_code):
        """Assign a professor to a course"""
        if professor_code not in self.professors or course_code not in self.courses:
            return False
        
        professor = self.professors[professor_code]
        course = self.courses[course_code]
        
        # Create bidirectional reference
        professor.add_course(course)
        course.add_professor(professor)
        
        self.save_data()
        return True
        
    def enroll_student_in_course(self, student_code, course_code):
        """Enroll a student in a course"""
        if student_code not in self.students or course_code not in self.courses:
            return False
        
        student = self.students[student_code]
        course = self.courses[course_code]
        
        # Create bidirectional reference
        student.add_course(course)
        course.add_student(student)
        
        self.save_data()
        return True
        
    def mark_attendance(self, course_code, student_code, status):
        """Mark attendance for a student in a course"""
        if course_code not in self.courses or student_code not in self.students:
            return False
            
        course = self.courses[course_code]
        date_today = datetime.now().strftime("%Y-%m-%d")
        
        # Initialize attendance dictionary for today if it doesn't exist
        if date_today not in course.attendance:
            course.attendance[date_today] = {}
            
        # Record the attendance
        course.attendance[date_today][student_code] = status
        
        self.save_data()
        return True
        
    def get_student_attendance_summary(self, student_code):
        """Get attendance summary for a student across all courses"""
        if student_code not in self.students:
            return {}
            
        summary = {}
        for course_code, course in self.courses.items():
            if student_code not in course.students:
                continue
                
            course_summary = {"present": 0, "absent": 0, "late": 0, "total_days": 0}
            for date, attendance in course.attendance.items():
                if student_code in attendance:
                    course_summary["total_days"] += 1
                    status = attendance[student_code].lower()
                    if status == "presente":
                        course_summary["present"] += 1
                    elif status == "ausente":
                        course_summary["absent"] += 1
                    elif status == "tardanza":
                        course_summary["late"] += 1
            
            summary[course_code] = course_summary
        
        return summary
    
    def save_data(self):
        """Save all data to JSON files"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            
            # Save courses
            courses_data = {}
            for code, course in self.courses.items():
                courses_data[code] = {
                    "name": course.name,
                    "code": course.code,
                    "professors": list(course.professors.keys()),
                    "students": list(course.students.keys()),
                    "attendance": course.attendance
                }
            
            with open("data/courses.json", "w") as f:
                json.dump(courses_data, f)
                
            # Save professors
            professors_data = {}
            for code, prof in self.professors.items():
                professors_data[code] = {
                    "name": prof.name,
                    "surname": prof.surname,
                    "email": prof.email,
                    "code": prof.code,
                    "courses": list(prof.courses.keys())
                }
            
            with open("data/professors.json", "w") as f:
                json.dump(professors_data, f)
                
            # Save students
            students_data = {}
            for code, student in self.students.items():
                students_data[code] = {
                    "name": student.name,
                    "surname": student.surname,
                    "email": student.email,
                    "code": student.code,
                    "courses": list(student.courses.keys()),
                    "faces": student.faces
                }
            
            with open("data/students.json", "w") as f:
                json.dump(students_data, f)
                
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        """Load all data from JSON files"""
        try:
            # Load courses
            if os.path.exists("data/courses.json"):
                with open("data/courses.json", "r") as f:
                    courses_data = json.load(f)
                
                for code, data in courses_data.items():
                    course = Course(data["name"], code)
                    course.attendance = data["attendance"]
                    self.courses[code] = course
            
            # Load professors
            if os.path.exists("data/professors.json"):
                with open("data/professors.json", "r") as f:
                    professors_data = json.load(f)
                
                for code, data in professors_data.items():
                    professor = Professor(
                        data["name"], 
                        data["surname"], 
                        data["email"], 
                        code
                    )
                    self.professors[code] = professor
            
            # Load students
            if os.path.exists("data/students.json"):
                with open("data/students.json", "r") as f:
                    students_data = json.load(f)
                
                for code, data in students_data.items():
                    student = Student(
                        data["name"], 
                        data["surname"], 
                        data["email"], 
                        code
                    )
                    student.faces = data["faces"]
                    self.students[code] = student
            
            # Restore relationships
            if os.path.exists("data/courses.json") and os.path.exists("data/professors.json") and os.path.exists("data/students.json"):
                with open("data/courses.json", "r") as f:
                    courses_data = json.load(f)
                
                for code, data in courses_data.items():
                    if code in self.courses:
                        course = self.courses[code]
                        
                        # Connect professors
                        for prof_code in data["professors"]:
                            if prof_code in self.professors:
                                prof = self.professors[prof_code]
                                course.professors[prof_code] = prof
                                prof.courses[code] = course
                        
                        # Connect students
                        for student_code in data["students"]:
                            if student_code in self.students:
                                student = self.students[student_code]
                                course.students[student_code] = student
                                student.courses[code] = course
            
        except Exception as e:
            print(f"Error loading data: {e}")

class Course:
    def __init__(self, name, code=None):
        self.name = name
        self.code = code or "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.professors = {}
        self.students = {}
        self.attendance = {} # Format: {"YYYY-MM-DD": {"student_code": "status"}}
    
    def add_professor(self, professor):
        """Add a professor to this course"""
        self.professors[professor.code] = professor
    
    def add_student(self, student):
        """Add a student to this course"""
        self.students[student.code] = student
        
    def remove_student(self, student_code):
        """Remove a student from this course"""
        if student_code in self.students:
            del self.students[student_code]
            return True
        return False
    
    def get_attendance_for_date(self, date):
        """Get attendance records for a specific date"""
        return self.attendance.get(date, {})
    
    def get_attendance_summary(self):
        """Get summary of attendance records for this course"""
        summary = {}
        for student_code in self.students:
            summary[student_code] = {"present": 0, "absent": 0, "late": 0, "total": 0}
            
        for date, records in self.attendance.items():
            for student_code, status in records.items():
                if student_code in summary:
                    summary[student_code]["total"] += 1
                    status_lower = status.lower()
                    if "presente" in status_lower:
                        summary[student_code]["present"] += 1
                    elif "ausente" in status_lower:
                        summary[student_code]["absent"] += 1
                    elif "tardanza" in status_lower or "tarde" in status_lower:
                        summary[student_code]["late"] += 1
                        
        return summary

    def export_attendance_report(self, format_type="excel"):
        """Export attendance report in the specified format"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs("reports", exist_ok=True)
            
            # Prepare data for report
            data = []
            for date, records in self.attendance.items():
                for student_code, status in records.items():
                    if student_code in self.students:
                        student = self.students[student_code]
                        data.append({
                            "Fecha": date,
                            "Código": student_code,
                            "Nombre": student.full_name(),
                            "Estado": status
                        })
            
            if not data:
                return None, "No hay datos de asistencia para este curso"
                
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/asistencia_{self.code}_{timestamp}"
            
            if format_type.lower() == "excel":
                # Export to Excel
                df = pd.DataFrame(data)
                excel_file = f"{filename}.xlsx"
                df.to_excel(excel_file, index=False)
                return excel_file, "Reporte de asistencia exportado a Excel"
                
            elif format_type.lower() == "pdf":
                # Export to PDF
                pdf_file = f"{filename}.pdf"
                pdf = FPDF()
                pdf.add_page()
                
                # Title
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, f"Reporte de Asistencia - {self.name} ({self.code})", 0, 1, "C")
                pdf.ln(5)
                
                # Add metadata
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 5, f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
                pdf.cell(0, 5, f"Total de estudiantes: {len(self.students)}", 0, 1)
                pdf.cell(0, 5, f"Total de registros: {len(data)}", 0, 1)
                pdf.ln(5)
                
                # Table header
                pdf.set_font("Arial", "B", 10)
                pdf.cell(30, 7, "Fecha", 1, 0, "C")
                pdf.cell(30, 7, "Código", 1, 0, "C")
                pdf.cell(80, 7, "Nombre", 1, 0, "C")
                pdf.cell(50, 7, "Estado", 1, 1, "C")
                
                # Table content
                pdf.set_font("Arial", "", 10)
                for item in data:
                    pdf.cell(30, 7, item["Fecha"], 1, 0)
                    pdf.cell(30, 7, item["Código"], 1, 0)
                    pdf.cell(80, 7, item["Nombre"], 1, 0)
                    pdf.cell(50, 7, item["Estado"], 1, 1)
                
                pdf.output(pdf_file)
                return pdf_file, "Reporte de asistencia exportado a PDF"
                
            else:
                return None, "Formato no soportado"
                
        except Exception as e:
            print(f"Error exporting report: {e}")
            return None, f"Error al exportar el reporte: {str(e)}"

class Person:
    def __init__(self, name, surname, email, code=None):
        self.name = name
        self.surname = surname
        self.email = email
        self.code = code
    
    def full_name(self):
        return f"{self.name} {self.surname}"

class Professor(Person):
    def __init__(self, name, surname, email, code=None):
        super().__init__(name, surname, email, code or "PROF-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5)))
        self.courses = {}
    
    def add_course(self, course):
        self.courses[course.code] = course

class Student(Person):
    def __init__(self, name, surname, email, code=None):
        super().__init__(name, surname, email, code or "EST-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5)))
        self.courses = {}
        self.faces = []
        self.guardian_contacts = []  # List of guardian contact information
    
    def add_course(self, course):
        self.courses[course.code] = course
    
    def add_face(self, face_file):
        if face_file not in self.faces:
            self.faces.append(face_file)
            
    def add_guardian_contact(self, name, email, phone):
        """Add a guardian contact for this student"""
        self.guardian_contacts.append({
            "name": name,
            "email": email,
            "phone": phone
        })
        return len(self.guardian_contacts) - 1  # Return index of added contact
    
    def update_guardian_contact(self, index, name=None, email=None, phone=None):
        """Update a guardian contact"""
        if 0 <= index < len(self.guardian_contacts):
            if name is not None:
                self.guardian_contacts[index]["name"] = name
            if email is not None:
                self.guardian_contacts[index]["email"] = email
            if phone is not None:
                self.guardian_contacts[index]["phone"] = phone
            return True
        return False
    
    def remove_guardian_contact(self, index):
        """Remove a guardian contact"""
        if 0 <= index < len(self.guardian_contacts):
            self.guardian_contacts.pop(index)
            return True
        return False
    
    def get_guardian_contacts(self):
        """Get all guardian contacts"""
        return self.guardian_contacts
