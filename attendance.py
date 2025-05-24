import pandas as pd
import os
import json
from datetime import datetime, timedelta
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

class AttendanceManager:
    def __init__(self, database=None):
        """Manage attendance with database or memory storage"""
        self.database = database
        self.session_active = False
        self.session_paused = False
        self.session_start_time = None
        self.attendance_records = []  # In-memory storage if no database
        self.current_session_id = None
        self.load_records()

    def clear_memory_records(self):
        """Clear all attendance records in memory"""
        self.attendance_records.clear()
        self.save_records()
        print("[INFO] In-memory records cleared")

    def load_records(self):
        """Load attendance records from file if no database is used"""
        if not self.database:
            try:
                os.makedirs("data", exist_ok=True)
                if os.path.exists("data/attendance_records.json"):
                    with open("data/attendance_records.json", "r") as f:
                        self.attendance_records = json.load(f)
                    print(f"[INFO] Loaded {len(self.attendance_records)} attendance records from file")
            except Exception as e:
                print(f"[ERROR] Failed to load attendance records: {e}")
                self.attendance_records = []

    def save_records(self):
        """Save attendance records to file if no database is used"""
        if not self.database:
            try:
                os.makedirs("data", exist_ok=True)
                with open("data/attendance_records.json", "w") as f:
                    json.dump(self.attendance_records, f)
                print(f"[INFO] Saved {len(self.attendance_records)} attendance records to file")
            except Exception as e:
                print(f"[ERROR] Failed to save attendance records: {e}")

    def list_memory_records(self, print_records=False):
        """Return and optionally print all attendance records in memory"""
        if print_records:
            for r in self.attendance_records:
                print(r)
        return self.attendance_records

    def get_attendance_summary(self, start_date=None, end_date=None, course_code=None):
        """Get attendance summary by student"""
        summary = {}
        
        # Use today's date as default end date if not specified
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Use 30 days before end date as default start date if not specified
        if start_date is None:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            start_dt = end_dt - timedelta(days=30)
            start_date = start_dt.strftime("%Y-%m-%d")
        
        for record in self.attendance_records:
            # Filter by date range
            if start_date <= record["Date"] <= end_date:
                # Filter by course code if specified
                if course_code is not None and record.get("Course") != course_code:
                    continue
                    
                sid = record["Student ID"]
                if sid not in summary:
                    summary[sid] = {
                        "total": 0, 
                        "present": 0, 
                        "absent": 0,
                        "late": 0,
                        "name": record.get("Student Name", "Unknown"), 
                        "code": record.get("Code", "")
                    }
                
                summary[sid]["total"] += 1
                status_lower = record["Status"].lower()
                
                if "presente" in status_lower:
                    summary[sid]["present"] += 1
                elif "ausente" in status_lower:
                    summary[sid]["absent"] += 1
                elif "tard" in status_lower:  # Matches "tardanza" or "tarde"
                    summary[sid]["late"] += 1
        
        return summary

    def print_attendance_report(self, start_date, end_date, course_code=None):
        """Print attendance report for a date range"""
        report = self.get_attendance_report(start_date, end_date, course_code)
        if report.empty:
            print("No records in the given range.")
        else:
            print(report.to_string(index=False))

    def start_session(self, course_code=None, session_name=None):
        """Start an attendance session"""
        self.session_active = True
        self.session_paused = False
        self.session_start_time = datetime.now()
        
        # Generate a unique session ID
        self.current_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"Attendance session started at {self.session_start_time}")
        if course_code:
            print(f"Course: {course_code}")
        if session_name:
            print(f"Session: {session_name}")
            
        return self.current_session_id

    def pause_session(self):
        """Pause the current attendance session"""
        if self.session_active:
            self.session_paused = True
            print("Attendance session paused")

    def resume_session(self):
        """Resume a paused attendance session"""
        if self.session_active and self.session_paused:
            self.session_paused = False
            print("Attendance session resumed")

    def stop_session(self):
        """Stop the current attendance session and generate report"""
        if self.session_active:
            self.session_active = False
            self.session_paused = False
            session_end_time = datetime.now()
            duration = session_end_time - self.session_start_time
            print(f"Attendance session stopped. Duration: {duration}")
            return self.generate_session_report()
        return None

    def generate_session_report(self, session_id=None):
        """Generate report for the completed session"""
        session_id = session_id or self.current_session_id
        if not session_id:
            return None
            
        # Find all records for this session
        session_records = [r for r in self.attendance_records if r.get("Session ID") == session_id]
        
        if not session_records:
            print("No records found for this session")
            return None
            
        # Group data by student
        students = {}
        for record in session_records:
            sid = record["Student ID"]
            if sid not in students:
                students[sid] = {
                    "id": sid,
                    "name": record.get("Student Name", "Unknown"),
                    "code": record.get("Code", ""),
                    "status": record["Status"],
                    "time": record["Time"]
                }
                
        # Convert to list for easier reporting
        student_list = list(students.values())
        
        return {
            "session_id": session_id,
            "start_time": self.session_start_time,
            "students": student_list,
            "total_students": len(student_list)
        }

    def mark_attendance(self, student_id, status, code=None, course_code=None, student_name=None, session_id=None):
        """Record student attendance"""
        if not student_id or not status:
            print("[ERROR] student_id and status are required.")
            return False
            
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H:%M:%S")
        current_session = session_id or self.current_session_id
        
        if self.database:
            # If database integration available, store there
            return self.database.add_attendance_record(student_id, date, time, status, code, course_code, current_session)
        else:
            # Memory storage with duplicate prevention
            # Check for existing record for this student, date, and course
            for i, record in enumerate(self.attendance_records):
                if (record["Student ID"] == student_id and 
                    record["Date"] == date and 
                    record.get("Course") == course_code):
                    
                    # Update existing record
                    self.attendance_records[i]["Status"] = status
                    self.attendance_records[i]["Time"] = time
                    print(f"[INFO] Updated attendance for {student_id} ({student_name}) in {course_code or 'unknown course'}: {status}")
                    self.save_records()
                    return True
            
            # Create new record
            self.attendance_records.append({
                "Student ID": student_id,
                "Student Name": student_name or student_id,
                "Date": date,
                "Time": time,
                "Status": status,
                "Code": code or "",
                "Course": course_code,
                "Session ID": current_session
            })
            print(f"[INFO] Marked attendance for {student_id} ({student_name}) in {course_code or 'unknown course'}: {status}")
            self.save_records()
            return True

    def get_attendance_report(self, start_date, end_date, course_code=None):
        """Get attendance report between two dates"""
        # Convert dates to string format if they're datetime objects
        if isinstance(start_date, datetime):
            start_date = start_date.strftime("%Y-%m-%d")
        if isinstance(end_date, datetime):
            end_date = end_date.strftime("%Y-%m-%d")
            
        if self.database:
            # If database available, get records from there
            records = self.database.get_attendance_records(start_date, end_date, course_code)
            columns = ["Student ID", "Student Name", "Date", "Time", "Status", "Code", "Course"]
        else:
            # Filter records in memory
            records = [r for r in self.attendance_records 
                      if start_date <= r["Date"] <= end_date and 
                      (course_code is None or r.get("Course") == course_code)]
            columns = ["Student ID", "Student Name", "Date", "Time", "Status", "Code", "Course"]
            
        # Convert to pandas DataFrame
        try:
            import pandas as pd
            report = pd.DataFrame(records, columns=[c for c in columns if any(c in r for r in records)])
            return report
        except ImportError:
            print("[ERROR] Pandas not available for creating report")
            return records

    def export_report_to_excel(self, start_date=None, end_date=None, course_code=None, file_path=None):
        """Export attendance report to Excel"""
        # Generate default dates if not provided
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if start_date is None:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            start_dt = end_dt - timedelta(days=30)
            start_date = start_dt.strftime("%Y-%m-%d")
        
        # Generate default filename if not provided
        if not file_path:
            os.makedirs("reports", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            course_suffix = f"_{course_code}" if course_code else ""
            file_path = f"reports/attendance_report{course_suffix}_{timestamp}.xlsx"
        
        try:
            # Get report data
            report = self.get_attendance_report(start_date, end_date, course_code)
            
            if report.empty:
                print(f"[ERROR] No data to export for date range {start_date} to {end_date}")
                return None
                
            # Create a writer with multiple sheets
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Add the detailed report
                report.to_excel(writer, sheet_name='Detailed Report', index=False)
                
                # Add summary sheet
                summary = self.get_attendance_summary(start_date, end_date, course_code)
                summary_data = []
                for student_id, data in summary.items():
                    summary_data.append({
                        'Student ID': student_id,
                        'Name': data['name'],
                        'Code': data['code'],
                        'Present': data['present'],
                        'Absent': data['absent'],
                        'Late': data['late'],
                        'Total': data['total'],
                        'Attendance Rate': f"{(data['present'] + data['late']) / data['total']:.2%}" if data['total'] > 0 else "0%"
                    })
                
                if summary_data:
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            print(f"[INFO] Report exported to {file_path}")
            return file_path
            
        except Exception as e:
            print(f"[ERROR] Failed to export to Excel: {e}")
            return None

    def export_report_to_pdf(self, start_date=None, end_date=None, course_code=None, file_path=None, include_charts=True):
        """Export attendance report to PDF with optional charts"""
        # Generate default dates if not provided
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if start_date is None:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            start_dt = end_dt - timedelta(days=30)
            start_date = start_dt.strftime("%Y-%m-%d")
        
        # Generate default filename if not provided
        if not file_path:
            os.makedirs("reports", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            course_suffix = f"_{course_code}" if course_code else ""
            file_path = f"reports/attendance_report{course_suffix}_{timestamp}.pdf"
        
        try:
            # Get report data
            report = self.get_attendance_report(start_date, end_date, course_code)
            summary = self.get_attendance_summary(start_date, end_date, course_code)
            
            if report.empty:
                print(f"[ERROR] No data to export for date range {start_date} to {end_date}")
                return None
            
            if include_charts:
                # Create PDF with matplotlib charts
                with PdfPages(file_path) as pdf:
                    # Create title page
                    plt.figure(figsize=(11, 8.5))
                    plt.axis('off')
                    plt.text(0.5, 0.8, "ATTENDANCE REPORT", fontsize=24, ha='center', weight='bold')
                    plt.text(0.5, 0.7, f"Period: {start_date} to {end_date}", fontsize=14, ha='center')
                    if course_code:
                        plt.text(0.5, 0.65, f"Course: {course_code}", fontsize=14, ha='center')
                    plt.text(0.5, 0.6, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                            fontsize=12, ha='center')
                    plt.text(0.5, 0.2, "Asisto YA - Attendance System", fontsize=10, ha='center', alpha=0.7)
                    pdf.savefig()
                    plt.close()
                    
                    # Create summary chart
                    if summary:
                        plt.figure(figsize=(11, 8.5))
                        plt.subplot(2, 1, 1)
                        
                        names = []
                        present_rates = []
                        absent_rates = []
                        late_rates = []
                        
                        for student_id, data in summary.items():
                            if data['total'] > 0:
                                names.append(data['name'])
                                present_rates.append(data['present'] / data['total'] * 100)
                                absent_rates.append(data['absent'] / data['total'] * 100)
                                late_rates.append(data['late'] / data['total'] * 100)
                        
                        if names:
                            # Limit to 15 students per chart for readability
                            for i in range(0, len(names), 15):
                                end_idx = min(i+15, len(names))
                                plt.figure(figsize=(11, 8.5))
                                
                                # Bar chart
                                indices = range(end_idx - i)
                                width = 0.25
                                plt.bar([x - width for x in indices], present_rates[i:end_idx], width, label='Present', color='green')
                                plt.bar(indices, late_rates[i:end_idx], width, label='Late', color='orange')
                                plt.bar([x + width for x in indices], absent_rates[i:end_idx], width, label='Absent', color='red')
                                
                                plt.xlabel('Students')
                                plt.ylabel('Percentage (%)')
                                plt.title('Attendance Summary')
                                plt.xticks(indices, names[i:end_idx], rotation=45, ha='right')
                                plt.legend()
                                plt.tight_layout()
                                
                                # Add pie chart of overall attendance
                                plt.subplot(2, 2, 3)
                                total_present = sum(data['present'] for data in summary.values())
                                total_absent = sum(data['absent'] for data in summary.values())
                                total_late = sum(data['late'] for data in summary.values())
                                plt.pie([total_present, total_late, total_absent], 
                                        labels=['Present', 'Late', 'Absent'],
                                        colors=['green', 'orange', 'red'],
                                        autopct='%1.1f%%')
                                plt.title('Overall Attendance Distribution')
                                
                                pdf.savefig()
                                plt.close()
                    
                    # Create detailed table pages
                    max_rows_per_page = 25
                    for i in range(0, len(report), max_rows_per_page):
                        end_idx = min(i+max_rows_per_page, len(report))
                        chunk = report.iloc[i:end_idx]
                        
                        fig, ax = plt.subplots(figsize=(11, 8.5))
                        ax.axis('tight')
                        ax.axis('off')
                        ax.set_title("Attendance Detail Records")
                        
                        table = ax.table(
                            cellText=chunk.values,
                            colLabels=chunk.columns,
                            cellLoc='center',
                            loc='center'
                        )
                        table.auto_set_font_size(False)
                        table.set_fontsize(8)
                        table.scale(1, 1.5)
                        
                        pdf.savefig()
                        plt.close()
                    
                print(f"[INFO] PDF report with charts exported to {file_path}")
                return file_path
            else:
                # Use FPDF for simpler PDF without charts
                pdf = FPDF()
                pdf.add_page()
                
                # Title
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "ATTENDANCE REPORT", 0, 1, "C")
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, f"Period: {start_date} to {end_date}", 0, 1, "C")
                if course_code:
                    pdf.cell(0, 10, f"Course: {course_code}", 0, 1, "C")
                pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, "C")
                pdf.ln(10)
                
                # Summary table
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Attendance Summary", 0, 1)
                
                # Table header
                pdf.set_font("Arial", "B", 10)
                pdf.cell(25, 7, "Student ID", 1, 0, "C")
                pdf.cell(50, 7, "Name", 1, 0, "C")
                pdf.cell(20, 7, "Present", 1, 0, "C")
                pdf.cell(20, 7, "Absent", 1, 0, "C")
                pdf.cell(20, 7, "Late", 1, 0, "C")
                pdf.cell(25, 7, "Rate", 1, 1, "C")
                
                # Table content
                pdf.set_font("Arial", "", 8)
                for student_id, data in summary.items():
                    rate = f"{(data['present'] + data['late']) / data['total']:.1%}" if data['total'] > 0 else "0%"
                    pdf.cell(25, 6, student_id[:10], 1, 0)
                    pdf.cell(50, 6, data['name'][:25], 1, 0)
                    pdf.cell(20, 6, str(data['present']), 1, 0, "C")
                    pdf.cell(20, 6, str(data['absent']), 1, 0, "C")
                    pdf.cell(20, 6, str(data['late']), 1, 0, "C")
                    pdf.cell(25, 6, rate, 1, 1, "C")
                
                pdf.ln(10)
                
                # Detailed records
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Detailed Records", 0, 1)
                
                # Table header
                pdf.set_font("Arial", "B", 8)
                headers = ["Date", "Time", "Student ID", "Name", "Status"]
                widths = [25, 20, 30, 50, 25]
                
                for i, header in enumerate(headers):
                    pdf.cell(widths[i], 7, header, 1, 0, "C")
                pdf.ln()
                
                # Table content
                pdf.set_font("Arial", "", 8)
                for _, row in report.iterrows():
                    pdf.cell(widths[0], 6, str(row.get("Date", "")), 1, 0)
                    pdf.cell(widths[1], 6, str(row.get("Time", "")), 1, 0)
                    pdf.cell(widths[2], 6, str(row.get("Student ID", ""))[:15], 1, 0)
                    pdf.cell(widths[3], 6, str(row.get("Student Name", ""))[:25], 1, 0)
                    pdf.cell(widths[4], 6, str(row.get("Status", "")), 1, 1)
                    
                    # Add a new page if needed
                    if pdf.get_y() > 250:
                        pdf.add_page()
                        # Repeat the header
                        pdf.set_font("Arial", "B", 8)
                        for i, header in enumerate(headers):
                            pdf.cell(widths[i], 7, header, 1, 0, "C")
                        pdf.ln()
                        pdf.set_font("Arial", "", 8)
                
                pdf.output(file_path)
                print(f"[INFO] PDF report exported to {file_path}")
                return file_path
                
        except Exception as e:
            print(f"[ERROR] Failed to export to PDF: {e}")
            import traceback
            traceback.print_exc()
            return None

    def edit_attendance_record(self, student_id, date, new_status, course_code=None):
        """Edit an existing attendance record"""
        if self.database:
            return self.database.update_attendance_record(student_id, date, new_status, course_code)
        else:
            for i, record in enumerate(self.attendance_records):
                if (record["Student ID"] == student_id and 
                    record["Date"] == date and 
                    (course_code is None or record.get("Course") == course_code)):
                    
                    old_status = record["Status"]
                    self.attendance_records[i]["Status"] = new_status
                    self.save_records()
                    print(f"[INFO] Updated attendance for {student_id} on {date}: {old_status} -> {new_status}")
                    return True
            
            print(f"[ERROR] No matching record found for {student_id} on {date}")
            return False

    def delete_attendance_record(self, student_id, date, course_code=None):
        """Delete an attendance record"""
        if self.database:
            return self.database.delete_attendance_record(student_id, date, course_code)
        else:
            before_count = len(self.attendance_records)
            self.attendance_records = [r for r in self.attendance_records if not 
                                    (r["Student ID"] == student_id and 
                                     r["Date"] == date and 
                                     (course_code is None or r.get("Course") == course_code))]
            
            if len(self.attendance_records) < before_count:
                self.save_records()
                print(f"[INFO] Deleted attendance record for {student_id} on {date}")
                return True
            else:
                print(f"[ERROR] No matching record found for {student_id} on {date}")
                return False

    def get_session_status(self):
        """Get current session status"""
        return {
            "active": self.session_active,
            "paused": self.session_paused,
            "start_time": self.session_start_time,
            "session_id": self.current_session_id
        }
        
    def get_record(self, student_id, date, course_code=None):
        """Get a specific attendance record"""
        if self.database:
            return self.database.get_attendance_record(student_id, date, course_code)
        else:
            for record in self.attendance_records:
                if (record["Student ID"] == student_id and 
                    record["Date"] == date and 
                    (course_code is None or record.get("Course") == course_code)):
                    return record
            return None
