import pandas as pd
from datetime import datetime
from fpdf import FPDF

class AttendanceManager:
    def __init__(self, database):
        self.database = database

    def mark_attendance(self, student_id, status):
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H:%M:%S")
        self.database.add_attendance_record(student_id, date, time, status)

    def get_attendance_report(self, start_date, end_date):
        records = self.database.get_attendance_records(start_date, end_date)
        report = pd.DataFrame(records, columns=["Student ID", "Date", "Time", "Status"])
        return report

    def export_report_to_excel(self, report, file_path):
        report.to_excel(file_path, index=False)

    def export_report_to_pdf(self, report, file_path):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add a title
        pdf.cell(200, 10, txt="Attendance Report", ln=True, align="C")

        # Add column headers
        pdf.cell(40, 10, txt="Student ID", border=1)
        pdf.cell(40, 10, txt="Date", border=1)
        pdf.cell(40, 10, txt="Time", border=1)
        pdf.cell(40, 10, txt="Status", border=1)
        pdf.ln()

        # Add data rows
        for index, row in report.iterrows():
            pdf.cell(40, 10, txt=str(row["Student ID"]), border=1)
            pdf.cell(40, 10, txt=row["Date"], border=1)
            pdf.cell(40, 10, txt=row["Time"], border=1)
            pdf.cell(40, 10, txt=row["Status"], border=1)
            pdf.ln()

        pdf.output(file_path)

    def edit_attendance_record(self, record_id, new_status):
        self.database.update_attendance_record(record_id, new_status)

    def delete_attendance_record(self, record_id):
        self.database.delete_attendance_record(record_id)
