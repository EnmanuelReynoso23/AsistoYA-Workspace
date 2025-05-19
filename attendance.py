import pandas as pd
from datetime import datetime

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
        # Placeholder for PDF export functionality
        pass
