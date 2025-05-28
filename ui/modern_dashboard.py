"""
🏢 Dashboard Profesional Moderno - AsistoYA Empresarial
Interfaz avanzada con métricas en tiempo real
"""

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk_bootstrap
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path
import threading
from typing import Dict, List, Optional

class ModernDashboard:
    """Dashboard empresarial moderno con métricas avanzadas"""
    
    def __init__(self, parent, auth_manager, firebase_config):
        self.parent = parent
        self.auth_manager = auth_manager
        self.firebase = firebase_config
        self.current_user = None
        self.current_token = None
        
        # Configurar tema moderno
        self.style = ttk_bootstrap.Style(theme="superhero")  # Tema oscuro profesional
        
        # Variables de estado
        self.auto_refresh = tk.BooleanVar(value=True)
        self.refresh_interval = 30000  # 30 segundos
        
        # Métricas en tiempo real
        self.metrics = {
            'total_students': tk.StringVar(value="0"),
            'present_today': tk.StringVar(value="0"),
            'absent_today': tk.StringVar(value="0"),
            'attendance_rate': tk.StringVar(value="0%"),
            'last_recognition': tk.StringVar(value="Ninguno"),
            'active_cameras': tk.StringVar(value="1")
        }
        
        self.setup_dashboard()
        self.start_auto_refresh()
    
    def setup_dashboard(self):
        """Configurar dashboard principal"""
        # Frame principal
        self.main_frame = ttk_bootstrap.Frame(self.parent)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Header con información del usuario
        self.create_header()
        
        # Panel de métricas principales
        self.create_metrics_panel()
        
        # Panel de gráficos
        self.create_charts_panel()
        
        # Panel de actividad reciente
        self.create_activity_panel()
        
        # Panel de acciones rápidas
        self.create_quick_actions()
        
        # Barra de estado
        self.create_status_bar()
    
    def create_header(self):
        """Crear header del dashboard"""
        header_frame = ttk_bootstrap.Frame(self.main_frame)
        header_frame.pack(fill=X, pady=(0, 20))
        
        # Logo y título
        title_frame = ttk_bootstrap.Frame(header_frame)
        title_frame.pack(side=LEFT)
        
        title_label = ttk_bootstrap.Label(
            title_frame,
            text="🏢 AsistoYA Dashboard Empresarial",
            font=("Segoe UI", 24, "bold"),
            bootstyle=PRIMARY
        )
        title_label.pack(anchor=W)
        
        subtitle_label = ttk_bootstrap.Label(
            title_frame,
            text=f"Sistema de Control de Asistencia Avanzado",
            font=("Segoe UI", 12),
            bootstyle=SECONDARY
        )
        subtitle_label.pack(anchor=W)
        
        # Panel de usuario
        user_frame = ttk_bootstrap.Frame(header_frame)
        user_frame.pack(side=RIGHT)
        
        # Info del usuario (se actualizará después del login)
        self.user_info_label = ttk_bootstrap.Label(
            user_frame,
            text="👤 Usuario no autenticado",
            font=("Segoe UI", 10),
            bootstyle=INFO
        )
        self.user_info_label.pack(anchor=E)
        
        # Hora actual
        self.time_label = ttk_bootstrap.Label(
            user_frame,
            text="",
            font=("Segoe UI", 10),
            bootstyle=SECONDARY
        )
        self.time_label.pack(anchor=E)
        
        self.update_time()
    
    def create_metrics_panel(self):
        """Crear panel de métricas principales"""
        metrics_frame = ttk_bootstrap.LabelFrame(
            self.main_frame,
            text="📊 Métricas en Tiempo Real",
            bootstyle=PRIMARY
        )
        metrics_frame.pack(fill=X, pady=(0, 10))
        
        # Grid de métricas
        metrics_grid = ttk_bootstrap.Frame(metrics_frame)
        metrics_grid.pack(fill=X, padx=10, pady=10)
        
        # Configurar grid
        for i in range(6):
            metrics_grid.columnconfigure(i, weight=1)
        
        # Métricas individuales
        self.create_metric_card(metrics_grid, "👥 Total Estudiantes", 
                               self.metrics['total_students'], SUCCESS, 0, 0)
        
        self.create_metric_card(metrics_grid, "✅ Presentes Hoy", 
                               self.metrics['present_today'], PRIMARY, 0, 1)
        
        self.create_metric_card(metrics_grid, "❌ Ausentes Hoy", 
                               self.metrics['absent_today'], DANGER, 0, 2)
        
        self.create_metric_card(metrics_grid, "📈 Tasa de Asistencia", 
                               self.metrics['attendance_rate'], INFO, 0, 3)
        
        self.create_metric_card(metrics_grid, "🎯 Último Reconocimiento", 
                               self.metrics['last_recognition'], WARNING, 0, 4)
        
        self.create_metric_card(metrics_grid, "📹 Cámaras Activas", 
                               self.metrics['active_cameras'], SECONDARY, 0, 5)
    
    def create_metric_card(self, parent, title, variable, style, row, col):
        """Crear tarjeta de métrica individual"""
        card = ttk_bootstrap.Frame(parent, bootstyle=style)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        title_label = ttk_bootstrap.Label(
            card,
            text=title,
            font=("Segoe UI", 9, "bold"),
            bootstyle=f"{style}-inverse"
        )
        title_label.pack(pady=(10, 5))
        
        value_label = ttk_bootstrap.Label(
            card,
            textvariable=variable,
            font=("Segoe UI", 16, "bold"),
            bootstyle=f"{style}-inverse"
        )
        value_label.pack(pady=(0, 10))
    
    def create_charts_panel(self):
        """Crear panel de gráficos"""
        charts_frame = ttk_bootstrap.LabelFrame(
            self.main_frame,
            text="📈 Análisis Visual",
            bootstyle=INFO
        )
        charts_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # Notebook para múltiples gráficos
        chart_notebook = ttk_bootstrap.Notebook(charts_frame)
        chart_notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Gráfico de asistencia semanal
        self.create_attendance_chart(chart_notebook)
        
        # Gráfico de tendencias
        self.create_trends_chart(chart_notebook)
        
        # Gráfico de distribución por horas
        self.create_hourly_chart(chart_notebook)
    
    def create_attendance_chart(self, parent):
        """Crear gráfico de asistencia semanal"""
        frame = ttk_bootstrap.Frame(parent)
        parent.add(frame, text="Asistencia Semanal")
        
        # Crear figura matplotlib
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#2b3e50')  # Fondo oscuro
        ax.set_facecolor('#34495e')
        
        # Datos de ejemplo (se actualizarán con datos reales)
        days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        attendance = [85, 92, 78, 95, 88, 45, 23]
        
        bars = ax.bar(days, attendance, color='#3498db', alpha=0.8)
        ax.set_ylabel('Porcentaje de Asistencia', color='white')
        ax.set_title('Asistencia por Día de la Semana', color='white', fontweight='bold')
        ax.tick_params(colors='white')
        
        # Personalizar apariencia
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Agregar valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{height}%', ha='center', va='bottom', color='white')
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
    
    def create_trends_chart(self, parent):
        """Crear gráfico de tendencias mensuales"""
        frame = ttk_bootstrap.Frame(parent)
        parent.add(frame, text="Tendencias Mensuales")
        
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#2b3e50')
        ax.set_facecolor('#34495e')
        
        # Datos de ejemplo
        months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
        attendance_trend = [82, 85, 88, 92, 89, 91]
        
        ax.plot(months, attendance_trend, marker='o', linewidth=3, 
                markersize=8, color='#e74c3c')
        ax.fill_between(months, attendance_trend, alpha=0.3, color='#e74c3c')
        
        ax.set_ylabel('Asistencia Promedio (%)', color='white')
        ax.set_title('Tendencia de Asistencia Mensual', color='white', fontweight='bold')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3)
        
        # Personalizar apariencia
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
    
    def create_hourly_chart(self, parent):
        """Crear gráfico de distribución por horas"""
        frame = ttk_bootstrap.Frame(parent)
        parent.add(frame, text="Distribución Horaria")
        
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#2b3e50')
        ax.set_facecolor('#34495e')
        
        # Datos de ejemplo
        hours = ['7:00', '7:30', '8:00', '8:30', '9:00', '9:30', '10:00']
        arrivals = [5, 15, 45, 25, 8, 3, 1]
        
        ax.bar(hours, arrivals, color='#f39c12', alpha=0.8)
        ax.set_ylabel('Número de Llegadas', color='white')
        ax.set_title('Distribución de Llegadas por Hora', color='white', fontweight='bold')
        ax.tick_params(colors='white')
        
        # Personalizar apariencia
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
    
    def create_activity_panel(self):
        """Crear panel de actividad reciente"""
        activity_frame = ttk_bootstrap.LabelFrame(
            self.main_frame,
            text="🕐 Actividad Reciente",
            bootstyle=WARNING
        )
        activity_frame.pack(fill=X, pady=(0, 10))
        
        # Crear Treeview para actividad
        columns = ("Hora", "Estudiante", "Acción", "Estado")
        self.activity_tree = ttk_bootstrap.Treeview(
            activity_frame,
            columns=columns,
            show="headings",
            height=6,
            bootstyle=WARNING
        )
        
        # Configurar columnas
        for col in columns:
            self.activity_tree.heading(col, text=col)
            self.activity_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk_bootstrap.Scrollbar(
            activity_frame,
            orient=VERTICAL,
            command=self.activity_tree.yview
        )
        self.activity_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.activity_tree.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=RIGHT, fill=Y, pady=10)
        
        # Agregar datos de ejemplo
        self.update_activity_log()
    
    def create_quick_actions(self):
        """Crear panel de acciones rápidas"""
        actions_frame = ttk_bootstrap.LabelFrame(
            self.main_frame,
            text="⚡ Acciones Rápidas",
            bootstyle=SUCCESS
        )
        actions_frame.pack(fill=X, pady=(0, 10))
        
        buttons_frame = ttk_bootstrap.Frame(actions_frame)
        buttons_frame.pack(fill=X, padx=10, pady=10)
        
        # Botones de acción
        ttk_bootstrap.Button(
            buttons_frame,
            text="🚀 Iniciar Reconocimiento",
            bootstyle=SUCCESS,
            width=20,
            command=self.start_recognition
        ).pack(side=LEFT, padx=5)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="📋 Exportar Reporte",
            bootstyle=INFO,
            width=20,
            command=self.export_report
        ).pack(side=LEFT, padx=5)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="👥 Gestionar Estudiantes",
            bootstyle=PRIMARY,
            width=20,
            command=self.manage_students
        ).pack(side=LEFT, padx=5)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="🔔 Enviar Notificaciones",
            bootstyle=WARNING,
            width=20,
            command=self.send_notifications
        ).pack(side=LEFT, padx=5)
        
        ttk_bootstrap.Button(
            buttons_frame,
            text="⚙️ Configuración",
            bootstyle=SECONDARY,
            width=20,
            command=self.open_settings
        ).pack(side=LEFT, padx=5)
    
    def create_status_bar(self):
        """Crear barra de estado"""
        status_frame = ttk_bootstrap.Frame(self.main_frame, bootstyle=DARK)
        status_frame.pack(fill=X, side=BOTTOM)
        
        # Estado de sistemas
        self.firebase_status = ttk_bootstrap.Label(
            status_frame,
            text="🔥 Firebase: Conectado",
            bootstyle=SUCCESS,
            font=("Segoe UI", 9)
        )
        self.firebase_status.pack(side=LEFT, padx=5, pady=2)
        
        self.camera_status = ttk_bootstrap.Label(
            status_frame,
            text="📹 Cámara: Lista",
            bootstyle=SUCCESS,
            font=("Segoe UI", 9)
        )
        self.camera_status.pack(side=LEFT, padx=5, pady=2)
        
        # Auto-refresh toggle
        refresh_frame = ttk_bootstrap.Frame(status_frame)
        refresh_frame.pack(side=RIGHT, padx=5, pady=2)
        
        ttk_bootstrap.Checkbutton(
            refresh_frame,
            text="Auto-refresh",
            variable=self.auto_refresh,
            bootstyle="round-toggle"
        ).pack(side=RIGHT)
    
    def update_time(self):
        """Actualizar hora en tiempo real"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"🕐 {current_time}")
        self.parent.after(1000, self.update_time)
    
    def start_auto_refresh(self):
        """Iniciar actualización automática"""
        if self.auto_refresh.get():
            self.refresh_metrics()
        self.parent.after(self.refresh_interval, self.start_auto_refresh)
    
    def refresh_metrics(self):
        """Actualizar métricas del dashboard"""
        try:
            # Aquí se conectaría con la base de datos real
            # Por ahora, datos simulados
            
            # Simular datos en tiempo real
            import random
            
            total_students = 150 + random.randint(-5, 5)
            present_today = int(total_students * (0.85 + random.uniform(-0.1, 0.1)))
            absent_today = total_students - present_today
            attendance_rate = (present_today / total_students) * 100
            
            # Actualizar variables
            self.metrics['total_students'].set(str(total_students))
            self.metrics['present_today'].set(str(present_today))
            self.metrics['absent_today'].set(str(absent_today))
            self.metrics['attendance_rate'].set(f"{attendance_rate:.1f}%")
            self.metrics['last_recognition'].set("Juan Pérez - 10:35 AM")
            
            # Actualizar actividad
            self.update_activity_log()
            
        except Exception as e:
            print(f"Error actualizando métricas: {e}")
    
    def update_activity_log(self):
        """Actualizar log de actividad"""
        # Limpiar actividad anterior
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        # Agregar actividad simulada
        activities = [
            ("10:35:22", "Juan Pérez", "Reconocimiento facial", "✅ Exitoso"),
            ("10:34:15", "María García", "Reconocimiento facial", "✅ Exitoso"),
            ("10:33:08", "Carlos López", "Reconocimiento facial", "❌ Fallido"),
            ("10:32:45", "Ana Martínez", "Reconocimiento facial", "✅ Exitoso"),
            ("10:31:20", "Pedro Sánchez", "Reconocimiento facial", "✅ Exitoso")
        ]
        
        for activity in activities:
            self.activity_tree.insert("", "end", values=activity)
    
    def set_user(self, user: Dict, token: str):
        """Establecer usuario autenticado"""
        self.current_user = user
        self.current_token = token
        
        user_text = f"👤 {user['full_name']} ({user['role'].title()})"
        self.user_info_label.config(text=user_text)
    
    # Métodos para acciones rápidas
    def start_recognition(self):
        """Iniciar reconocimiento facial"""
        messagebox.showinfo("Acción", "🚀 Iniciando sistema de reconocimiento facial...")
    
    def export_report(self):
        """Exportar reporte"""
        messagebox.showinfo("Acción", "📋 Exportando reporte de asistencia...")
    
    def manage_students(self):
        """Gestionar estudiantes"""
        messagebox.showinfo("Acción", "👥 Abriendo gestión de estudiantes...")
    
    def send_notifications(self):
        """Enviar notificaciones"""
        messagebox.showinfo("Acción", "🔔 Enviando notificaciones...")
    
    def open_settings(self):
        """Abrir configuración"""
        messagebox.showinfo("Acción", "⚙️ Abriendo configuración del sistema...")
