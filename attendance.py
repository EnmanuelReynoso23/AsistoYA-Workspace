import pandas as pd
from datetime import datetime
from fpdf import FPDF



class AttendanceManager:
    def __init__(self, database=None):
        """Permite usar base de datos o almacenamiento en memoria si no hay base de datos."""
        self.database = database
        self.session_active = False
        self.session_paused = False
        self.session_start_time = None
        self.attendance_records = []  # En memoria si no hay base de datos

    def clear_memory_records(self):
        """Elimina todos los registros de asistencia en memoria."""
        self.attendance_records.clear()
        print("[INFO] Registros en memoria eliminados.")

    def list_memory_records(self, print_records=False):
        """Devuelve y opcionalmente imprime todos los registros de asistencia en memoria."""
        if print_records:
            for r in self.attendance_records:
                print(r)
        return self.attendance_records
    def get_attendance_summary(self):
        """Devuelve un resumen de asistencia por estudiante (conteo de asistencias)."""
        summary = {}
        for record in self.attendance_records:
            sid = record["Student ID"]
            if sid not in summary:
                summary[sid] = 0
            if record["Status"].lower() == "presente":
                summary[sid] += 1
        return summary
    def print_attendance_report(self, start_date, end_date):
        """Imprime un reporte de asistencia en consola para un rango de fechas."""
        report = self.get_attendance_report(start_date, end_date)
        if report.empty:
            print("No hay registros en el rango dado.")
        else:
            print(report.to_string(index=False))

    def start_session(self):
        """Start an attendance session"""
        self.session_active = True
        self.session_paused = False
        self.session_start_time = datetime.now()
        print(f"Attendance session started at {self.session_start_time}")

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
        """Stop the current attendance session"""
        if self.session_active:
            self.session_active = False
            self.session_paused = False
            session_end_time = datetime.now()
            duration = session_end_time - self.session_start_time
            print(f"Attendance session stopped. Duration: {duration}")
            self.generate_session_report()

    def generate_session_report(self):
        """Generate a report for the completed session"""
        date = self.session_start_time.strftime("%Y-%m-%d")
        # Here you would normally fetch session data from the database
        print(f"Generating report for session on {date}")


    def mark_attendance(self, student_id, status, code=None):
        """Registra la asistencia de un estudiante. Si no hay base de datos, almacena en memoria."""
        if not student_id or not status:
            print("[ERROR] student_id y status son obligatorios.")
            return
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H:%M:%S")
        if self.database:
            # Si tienes soporte de código en la base de datos, pásalo aquí
            self.database.add_attendance_record(student_id, date, time, status)
        else:
            # Evitar duplicados para el mismo estudiante y fecha
            for record in self.attendance_records:
                if record["Student ID"] == student_id and record["Date"] == date:
                    print(f"[WARN] Ya existe un registro para {student_id} en {date}.")
                    return
            self.attendance_records.append({
                "Student ID": student_id,
                "Date": date,
                "Time": time,
                "Status": status,
                "Code": code if code else ""
            })
            print(f"[INFO] Asistencia guardada en memoria para {student_id} (código: {code if code else ''}): {status}")


    def get_attendance_report(self, start_date, end_date):
        """Obtiene el reporte de asistencia entre dos fechas."""
        # Permitir fechas como string o datetime
        if isinstance(start_date, datetime):
            start_date = start_date.strftime("%Y-%m-%d")
        if isinstance(end_date, datetime):
            end_date = end_date.strftime("%Y-%m-%d")
        if self.database:
            records = self.database.get_attendance_records(start_date, end_date)
            # Si tu base de datos soporta código, agrega la columna aquí
            columns = ["Student ID", "Date", "Time", "Status"]
        else:
            # Filtrar registros en memoria
            records = [r for r in self.attendance_records if start_date <= r["Date"] <= end_date]
            columns = ["Student ID", "Date", "Time", "Status", "Code"]
        import pandas as pd
        report = pd.DataFrame(records, columns=columns)
        return report


    def export_report_to_excel(self, report, file_path):
        """Exporta el reporte a Excel si pandas está disponible."""
        try:
            report.to_excel(file_path, index=False)
            print(f"[INFO] Reporte exportado a {file_path}")
        except Exception as e:
            print(f"[ERROR] No se pudo exportar a Excel: {e}")


    def export_report_to_pdf(self, report, file_path):
        """Exporta el reporte a PDF si FPDF está disponible."""
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Attendance Report", ln=True, align="C")
            pdf.cell(40, 10, txt="Student ID", border=1)
            pdf.cell(40, 10, txt="Date", border=1)
            pdf.cell(40, 10, txt="Time", border=1)
            pdf.cell(40, 10, txt="Status", border=1)
            pdf.ln()
            for index, row in report.iterrows():
                pdf.cell(40, 10, txt=str(row["Student ID"]), border=1)
                pdf.cell(40, 10, txt=row["Date"], border=1)
                pdf.cell(40, 10, txt=row["Time"], border=1)
                pdf.cell(40, 10, txt=row["Status"], border=1)
                pdf.ln()
            pdf.output(file_path)
            print(f"[INFO] Reporte PDF exportado a {file_path}")
        except Exception as e:
            print(f"[ERROR] No se pudo exportar a PDF: {e}")


    def edit_attendance_record(self, record_id, new_status):
        """Edita el estado de un registro de asistencia."""
        if self.database:
            self.database.update_attendance_record(record_id, new_status)
        else:
            for record in self.attendance_records:
                if record["Student ID"] == record_id:
                    record["Status"] = new_status


    def delete_attendance_record(self, record_id):
        """Elimina un registro de asistencia."""
        if self.database:
            self.database.delete_attendance_record(record_id)
        else:
            self.attendance_records = [r for r in self.attendance_records if r["Student ID"] != record_id]

    def get_session_status(self):
        """Devuelve el estado actual de la sesión de asistencia."""
        return {
            "active": self.session_active,
            "paused": self.session_paused,
            "start_time": self.session_start_time
        }
