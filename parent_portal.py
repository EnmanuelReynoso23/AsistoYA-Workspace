"""
🌐 AsistoYA - Portal Web para Padres
Portal simple para que los padres vean la asistencia de sus hijos
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

class ParentPortal:
    def __init__(self):
        self.users_file = "faces/registered_users.json"
        self.attendance_file = "faces/attendance_records.json"
    
    def load_registered_users(self):
        """Cargar usuarios registrados"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading users: {e}")
            return {}
    
    def load_attendance_records(self):
        """Cargar registros de asistencia"""
        try:
            if os.path.exists(self.attendance_file):
                with open(self.attendance_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading attendance: {e}")
            return []
    
    def get_student_by_token(self, parent_token):
        """Obtener estudiante por token de padre"""
        users = self.load_registered_users()
        for name, data in users.items():
            if data.get('parent_token') == parent_token:
                return name, data
        return None, None
    
    def get_student_attendance(self, student_name, days=30):
        """Obtener asistencia del estudiante"""
        attendance_records = self.load_attendance_records()
        student_records = []
        
        # Filtrar registros del estudiante
        for record in attendance_records:
            if record['name'] == student_name:
                student_records.append(record)
        
        # Ordenar por fecha (más reciente primero)
        student_records.sort(key=lambda x: x['date'], reverse=True)
        
        # Limitar a los últimos N días
        return student_records[:days]

portal = ParentPortal()

@app.route('/')
def home():
    """Página principal"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AsistoYA - Portal de Padres</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container { 
                max-width: 400px; 
                margin: 50px auto; 
                background: white; 
                padding: 30px; 
                border-radius: 10px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }
            h1 { 
                color: #333; 
                text-align: center; 
                margin-bottom: 30px;
            }
            .form-group { 
                margin-bottom: 20px; 
            }
            label { 
                display: block; 
                margin-bottom: 5px; 
                font-weight: bold;
                color: #555;
            }
            input[type="text"] { 
                width: 100%; 
                padding: 12px; 
                border: 2px solid #ddd; 
                border-radius: 5px; 
                font-size: 16px;
                box-sizing: border-box;
            }
            button { 
                width: 100%; 
                padding: 12px; 
                background: #667eea; 
                color: white; 
                border: none; 
                border-radius: 5px; 
                font-size: 16px; 
                cursor: pointer;
                transition: background 0.3s;
            }
            button:hover { 
                background: #5a6fd8; 
            }
            .info {
                background: #e3f2fd;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                border-left: 4px solid #2196f3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏫 AsistoYA</h1>
            <div class="info">
                <strong>Portal para Padres</strong><br>
                Ingrese el token que recibió al registrar a su hijo/a para ver su asistencia.
            </div>
            <form action="/parent" method="get">
                <div class="form-group">
                    <label for="token">Token de Acceso:</label>
                    <input type="text" id="token" name="token" placeholder="Ej: PAR_ER1234_567890" required>
                </div>
                <button type="submit">Ver Asistencia</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/parent/<token>')
@app.route('/parent')
def parent_dashboard(token=None):
    """Dashboard de padres"""
    if not token:
        token = request.args.get('token', '')
    
    if not token:
        return '''
        <div style="text-align: center; margin-top: 50px;">
            <h2>❌ Token requerido</h2>
            <p><a href="/">Volver al inicio</a></p>
        </div>
        '''
    
    # Buscar estudiante por token
    student_name, student_data = portal.get_student_by_token(token)
    
    if not student_name:
        return '''
        <div style="text-align: center; margin-top: 50px;">
            <h2>❌ Token inválido</h2>
            <p>No se encontró ningún estudiante asociado a este token.</p>
            <p><a href="/">Volver al inicio</a></p>
        </div>
        '''
    
    # Obtener asistencia
    attendance_records = portal.get_student_attendance(student_name)
    
    # Calcular estadísticas
    total_days = len(attendance_records)
    present_days = len([r for r in attendance_records if r['status'] == 'Present'])
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    
    # Generar HTML
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AsistoYA - Asistencia de {student_name}</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{ 
                max-width: 800px; 
                margin: 0 auto; 
                background: white; 
                border-radius: 10px; 
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }}
            .header {{
                background: #667eea;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .content {{
                padding: 30px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                border-left: 4px solid #667eea;
            }}
            .stat-number {{
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
            }}
            .attendance-list {{
                background: #f8f9fa;
                border-radius: 8px;
                overflow: hidden;
            }}
            .attendance-header {{
                background: #667eea;
                color: white;
                padding: 15px;
                font-weight: bold;
            }}
            .attendance-item {{
                padding: 15px;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .attendance-item:last-child {{
                border-bottom: none;
            }}
            .status-present {{
                color: #28a745;
                font-weight: bold;
            }}
            .status-absent {{
                color: #dc3545;
                font-weight: bold;
            }}
            .back-link {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: #6c757d;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background 0.3s;
            }}
            .back-link:hover {{
                background: #5a6268;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏫 AsistoYA - Portal de Padres</h1>
                <h2>👨‍🎓 {student_name}</h2>
                <p>Grado: {student_data.get('grade', 'N/A')} | Sección: {student_data.get('department', 'N/A')}</p>
            </div>
            
            <div class="content">
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{total_days}</div>
                        <div>Días Registrados</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{present_days}</div>
                        <div>Días Presente</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{attendance_percentage:.1f}%</div>
                        <div>Porcentaje de Asistencia</div>
                    </div>
                </div>
                
                <div class="attendance-list">
                    <div class="attendance-header">
                        📋 Historial de Asistencia (Últimos 30 días)
                    </div>
    '''
    
    if attendance_records:
        for record in attendance_records:
            status_class = "status-present" if record['status'] == 'Present' else "status-absent"
            status_icon = "✅" if record['status'] == 'Present' else "❌"
            
            html += f'''
                    <div class="attendance-item">
                        <div>
                            <strong>{record['date']}</strong> - {record['time']}
                        </div>
                        <div class="{status_class}">
                            {status_icon} {record['status']}
                        </div>
                    </div>
            '''
    else:
        html += '''
                    <div class="attendance-item">
                        <div style="text-align: center; padding: 20px;">
                            <em>No hay registros de asistencia aún</em>
                        </div>
                    </div>
        '''
    
    html += f'''
                </div>
                
                <a href="/" class="back-link">← Volver al inicio</a>
            </div>
        </div>
        
        <script>
            // Auto-refresh cada 30 segundos
            setTimeout(function(){{
                location.reload();
            }}, 30000);
        </script>
    </body>
    </html>
    '''
    
    return html

@app.route('/api/student/<token>')
def api_student_data(token):
    """API para obtener datos del estudiante"""
    student_name, student_data = portal.get_student_by_token(token)
    
    if not student_name:
        return jsonify({'error': 'Token inválido'}), 404
    
    attendance_records = portal.get_student_attendance(student_name)
    
    return jsonify({
        'student_name': student_name,
        'student_data': student_data,
        'attendance_records': attendance_records,
        'total_days': len(attendance_records),
        'present_days': len([r for r in attendance_records if r['status'] == 'Present'])
    })

if __name__ == '__main__':
    print("🌐 Iniciando Portal de Padres AsistoYA...")
    print("📡 Accesible en: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
