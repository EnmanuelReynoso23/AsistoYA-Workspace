import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from PIL import Image, ImageTk
import json

class Dashboard:
    def __init__(self, root=None, school_manager=None, attendance_manager=None):
        """Initialize Dashboard with provided data sources or create a new window"""
        if root is None:
            self.root = ttk.Window(themename="darkly")
            self.root.title("AsistoYA - Dashboard")
            self.root.geometry("1024x768")
            self.standalone = True
        else:
            self.root = root
            self.standalone = False
            
        self.school_manager = school_manager
        self.attendance_manager = attendance_manager
        
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create dashboard components
        self.create_header()
        self.create_stats_cards()
        self.create_charts()
        self.create_recent_activity()
        
        # Update data
        self.update_dashboard_data()
        
        if self.standalone:
            self.root.mainloop()
    
    def create_header(self):
        """Create header with title and date"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Dashboard title
        title_label = ttk.Label(
            header_frame, 
            text="Panel de Control AsistoYA", 
            font=("Helvetica", 20, "bold"),
            bootstyle="inverse-light"
        )
        title_label.pack(side=tk.LEFT)
        
        # Current date
        self.date_label = ttk.Label(
            header_frame,
            text=f"Fecha: {datetime.now().strftime('%d/%m/%Y')}",
            font=("Helvetica", 12),
            bootstyle="inverse-light"
        )
        self.date_label.pack(side=tk.RIGHT, padx=10)
    
    def create_stats_cards(self):
        """Create statistics cards for quick overview"""
        stats_frame = ttk.Frame(self.main_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Create 4 metric cards in a row
        card_data = [
            {"title": "Estudiantes Registrados", "value": "0", "icon": "👨‍🎓", "style": "success"},
            {"title": "Cursos Activos", "value": "0", "icon": "📚", "style": "info"},
            {"title": "Asistencia Promedio", "value": "0%", "icon": "📊", "style": "warning"},
            {"title": "Alertas de Ausencia", "value": "0", "icon": "⚠️", "style": "danger"}
        ]
        
        self.stat_cards = []
        for i, data in enumerate(card_data):
            card = ttk.Frame(stats_frame, bootstyle=data["style"])
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)
            
            icon_label = ttk.Label(card, text=data["icon"], font=("Helvetica", 24))
            icon_label.pack(pady=(10, 0))
            
            title_label = ttk.Label(card, text=data["title"], font=("Helvetica", 12))
            title_label.pack()
            
            value_label = ttk.Label(card, text=data["value"], font=("Helvetica", 18, "bold"))
            value_label.pack(pady=(0, 10))
            
            self.stat_cards.append(value_label)
    
    def create_charts(self):
        """Create visualization charts"""
        charts_frame = ttk.Frame(self.main_frame)
        charts_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create two chart frames side by side
        left_chart = ttk.LabelFrame(charts_frame, text="Asistencia por Día", bootstyle="info")
        left_chart.grid(row=0, column=0, padx=5, sticky="nsew")
        
        right_chart = ttk.LabelFrame(charts_frame, text="Distribución por Estado", bootstyle="info")
        right_chart.grid(row=0, column=1, padx=5, sticky="nsew")
        
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize empty charts
        self.attendance_chart_frame = left_chart
        self.status_chart_frame = right_chart
        
        # We'll populate these with real data in the update method
        self.create_empty_chart(self.attendance_chart_frame, "Línea de tiempo")
        self.create_empty_chart(self.status_chart_frame, "Distribución")
    
    def create_empty_chart(self, parent, title):
        """Create an empty placeholder chart"""
        fig = plt.Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title(title)
        ax.text(0.5, 0.5, "No hay datos suficientes", 
                ha='center', va='center', fontsize=12, 
                transform=ax.transAxes)
        ax.set_axis_off()
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_recent_activity(self):
        """Create recent activity list"""
        recent_frame = ttk.LabelFrame(self.main_frame, text="Actividad Reciente", bootstyle="secondary")
        recent_frame.pack(fill=tk.X, pady=10)
        
        # Activity list using Treeview
        columns = ("time", "student", "course", "status")
        self.activity_tree = ttk.Treeview(
            recent_frame, 
            columns=columns,
            show="headings",
            height=5,
            bootstyle="info"
        )
        
        # Define headings
        self.activity_tree.heading("time", text="Hora")
        self.activity_tree.heading("student", text="Estudiante")
        self.activity_tree.heading("course", text="Curso")
        self.activity_tree.heading("status", text="Estado")
        
        # Define columns
        self.activity_tree.column("time", width=100)
        self.activity_tree.column("student", width=200)
        self.activity_tree.column("course", width=200)
        self.activity_tree.column("status", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL, command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.activity_tree.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def update_dashboard_data(self):
        """Update dashboard with real data"""
        if self.school_manager and self.attendance_manager:
            # Update stats cards
            student_count = len(self.school_manager.students) if hasattr(self.school_manager, 'students') else 0
            course_count = len(self.school_manager.courses) if hasattr(self.school_manager, 'courses') else 0
            
            # Calculate attendance rate and alerts
            attendance_rate = self.calculate_attendance_rate()
            absence_alerts = self.calculate_absence_alerts()
            
            # Update card values
            self.stat_cards[0].config(text=str(student_count))
            self.stat_cards[1].config(text=str(course_count))
            self.stat_cards[2].config(text=f"{attendance_rate:.1f}%")
            self.stat_cards[3].config(text=str(absence_alerts))
            
            # Update charts
            self.update_attendance_chart()
            self.update_status_chart()
            
            # Update recent activity
            self.update_recent_activity()
    
    def calculate_attendance_rate(self):
        """Calculate overall attendance rate"""
        try:
            if hasattr(self.attendance_manager, 'attendance_records') and self.attendance_manager.attendance_records:
                records = self.attendance_manager.attendance_records
                present_count = sum(1 for record in records 
                                  if 'Status' in record and 'presente' in record['Status'].lower())
                total_count = len(records)
                if total_count > 0:
                    return (present_count / total_count) * 100
            return 0
        except Exception as e:
            print(f"Error calculating attendance rate: {e}")
            return 0
    
    def calculate_absence_alerts(self):
        """Calculate number of absence alerts (students with >3 absences)"""
        try:
            if not hasattr(self.attendance_manager, 'attendance_records'):
                return 0
                
            student_absences = {}
            for record in self.attendance_manager.attendance_records:
                if 'Student ID' in record and 'Status' in record and 'ausente' in record['Status'].lower():
                    student_id = record['Student ID']
                    student_absences[student_id] = student_absences.get(student_id, 0) + 1
            
            # Count students with more than 3 absences
            alerts = sum(1 for absences in student_absences.values() if absences >= 3)
            return alerts
        except Exception as e:
            print(f"Error calculating absence alerts: {e}")
            return 0
    
    def update_attendance_chart(self):
        """Update attendance chart with real data"""
        try:
            # Clear previous chart
            for widget in self.attendance_chart_frame.winfo_children():
                widget.destroy()
            
            if not hasattr(self.attendance_manager, 'attendance_records') or not self.attendance_manager.attendance_records:
                self.create_empty_chart(self.attendance_chart_frame, "Asistencia por Día")
                return
                
            # Prepare data
            records = self.attendance_manager.attendance_records
            dates = {}
            
            # Group by date
            for record in records:
                if 'Date' in record:
                    date = record['Date']
                    if date not in dates:
                        dates[date] = {'present': 0, 'absent': 0, 'late': 0}
                    
                    if 'Status' in record:
                        status = record['Status'].lower()
                        if 'presente' in status:
                            dates[date]['present'] += 1
                        elif 'ausente' in status:
                            dates[date]['absent'] += 1
                        elif 'tard' in status:
                            dates[date]['late'] += 1
            
            # Sort dates
            sorted_dates = sorted(dates.keys())
            if not sorted_dates:
                self.create_empty_chart(self.attendance_chart_frame, "Asistencia por Día")
                return
                
            # Prepare chart data
            present_data = [dates[date]['present'] for date in sorted_dates]
            absent_data = [dates[date]['absent'] for date in sorted_dates]
            late_data = [dates[date]['late'] for date in sorted_dates]
            
            # Create matplotlib figure
            fig = plt.Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)
            
            # Plot data
            ax.plot(sorted_dates, present_data, 'g-', label='Presente')
            ax.plot(sorted_dates, absent_data, 'r-', label='Ausente')
            ax.plot(sorted_dates, late_data, 'y-', label='Tardanza')
            
            # Format chart
            ax.set_title('Asistencia por Día')
            ax.set_xlabel('Fecha')
            ax.set_ylabel('Cantidad')
            ax.legend()
            
            # Rotate date labels if more than 5 dates
            if len(sorted_dates) > 5:
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
                
            fig.tight_layout()
            
            # Display in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.attendance_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            print(f"Error updating attendance chart: {e}")
            self.create_empty_chart(self.attendance_chart_frame, "Asistencia por Día")
    
    def update_status_chart(self):
        """Update status distribution chart"""
        try:
            # Clear previous chart
            for widget in self.status_chart_frame.winfo_children():
                widget.destroy()
            
            if not hasattr(self.attendance_manager, 'attendance_records') or not self.attendance_manager.attendance_records:
                self.create_empty_chart(self.status_chart_frame, "Distribución por Estado")
                return
                
            # Count statuses
            records = self.attendance_manager.attendance_records
            statuses = {'Presente': 0, 'Ausente': 0, 'Tardanza': 0}
            
            for record in records:
                if 'Status' in record:
                    status = record['Status'].lower()
                    if 'presente' in status:
                        statuses['Presente'] += 1
                    elif 'ausente' in status:
                        statuses['Ausente'] += 1
                    elif 'tard' in status:
                        statuses['Tardanza'] += 1
            
            # Create pie chart
            fig = plt.Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)
            
            labels = list(statuses.keys())
            sizes = list(statuses.values())
            
            if sum(sizes) > 0:  # Only create pie if we have data
                colors = ['green', 'red', 'orange']
                ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                       startangle=90, shadow=True)
                ax.axis('equal')  # Equal aspect ratio ensures pie is circular
                ax.set_title('Distribución de Asistencia')
            else:
                ax.text(0.5, 0.5, "No hay datos de asistencia", 
                        ha='center', va='center', fontsize=12)
                ax.set_axis_off()
            
            # Display in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.status_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            print(f"Error updating status chart: {e}")
            self.create_empty_chart(self.status_chart_frame, "Distribución por Estado")
    
    def update_recent_activity(self):
        """Update recent activity list"""
        try:
            # Clear previous data
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)
            
            if not hasattr(self.attendance_manager, 'attendance_records') or not self.attendance_manager.attendance_records:
                return
                
            # Get recent records (last 10)
            records = self.attendance_manager.attendance_records
            recent_records = sorted(records, key=lambda x: x.get('Timestamp', ''), reverse=True)[:10]
            
            # Add to treeview
            for record in recent_records:
                time = record.get('Time', 'N/A')
                student = record.get('Student Name', 'Desconocido')
                course = record.get('Course Name', 'N/A')
                status = record.get('Status', 'N/A')
                
                self.activity_tree.insert('', tk.END, values=(time, student, course, status))
                
        except Exception as e:
            print(f"Error updating recent activity: {e}")
    
    def refresh(self):
        """Refresh dashboard data"""
        self.update_dashboard_data()

def main():
    """Run dashboard as standalone app"""
    dashboard = Dashboard()
    
if __name__ == "__main__":
    main()