# AsistoYA

## Project Description and Overview

AsistoYA es una aplicación de escritorio para gestionar la asistencia de estudiantes utilizando reconocimiento facial. El sistema permite registrar estudiantes, profesores y cursos, y llevar un registro automático de asistencia a través de la detección de rostros mediante una cámara.

### Características Principales

- **Reconocimiento facial** para identificar automáticamente estudiantes
- **Gestión de cursos y estudiantes** con interfaz gráfica intuitiva
- **Seguimiento de asistencia** con estados (Presente, Ausente, Tardanza)
- **Reportes exportables** en formato Excel y PDF
- **Notificaciones automáticas** para tutores vía correo electrónico o mensajería
- **Panel de control** con estadísticas y gráficos de asistencia
- **Sistema de usuarios** con permisos diferenciados para administradores y tutores
- **Seguridad y privacidad**: Encriptación de datos sensibles, login seguro y políticas de retención de datos
- **Cámara configurable**: Soporte para webcams y cámaras IP con ajuste automático
- **Códigos de acceso para tutores**: Sistema de generación de códigos temporales para tutores

## Requerimientos del Sistema

Antes de instalar AsistoYA, asegúrese de que su sistema cumple con los siguientes requisitos:

### Requerimientos de Hardware

- Procesador: Intel Core i3 o superior (recomendado i5 o equivalente)
- RAM: Mínimo 4GB (recomendado 8GB)
- Cámara web o cámara IP compatible
- Espacio en disco: 2GB mínimo

### Requerimientos de Software

- Sistema Operativo: Windows 10/11, macOS 10.14+, o Linux (Ubuntu 20.04+)
- Python 3.8 o superior
- Dependencias adicionales especificadas en requirements.txt

## Setting Up the Development Environment

Para configurar el entorno de desarrollo para AsistoYA, siga estos pasos:

1. **Clonar el repositorio**:

   ```bash
   git clone https://github.com/EnmanuelReynoso23/AsistoYA-Workspace.git
   cd AsistoYA-Workspace
   ```

2. **Crear un entorno virtual**:

   ```bash
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar dependencias**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la base de datos**:

   ```bash
   python database.py --setup
   ```
   
5. **Configurar modelo YOLOv8 (primera vez)**:

   ```bash
   # El sistema descargará automáticamente YOLOv8n al primer uso
   # O puede descargarlo manualmente ejecutando:
   python -c "from ultralytics import YOLO; YOLO('yolov8n-face.pt')"
   ```

### Solución de problemas comunes

- **Problemas con OpenCV**: Si experimenta problemas con la cámara, intente actualizar OpenCV:
  ```bash
  pip uninstall opencv-python
  pip install opencv-python-headless
  pip install opencv-python
  ```

- **Problemas con CUDA**: Si utiliza GPU NVIDIA y tiene problemas con torch, instale la versión correcta:
  ```bash
  pip uninstall torch
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```
  
- **No detecta cámaras**: Verifique los permisos del sistema para acceso a cámaras y ejecute el programa como administrador.

### Requisitos adicionales

- **Modelos preentrenados**: El sistema utiliza modelos preentrenados para reconocimiento facial que se descargarán automáticamente.
- **Almacenamiento**: Asegúrese de tener al menos 2GB de espacio disponible para los modelos y datos.

## Ejecutar la Aplicación

Para iniciar la aplicación, utilice el siguiente comando:

```bash
python main.py
```

## Guía de Uso

### Iniciar Sesión

- **Administrador**: Use las credenciales proporcionadas por el administrador del sistema (por defecto: admin/admin123)
- **Tutor**: Use el código de acceso proporcionado por la institución educativa para ver la asistencia de un estudiante específico

### Administración del Sistema

1. **Gestión de Cursos**:
   - Crear curso: Menú Cursos > Crear curso
   - Seleccionar curso: Menú Cursos > Seleccionar curso

2. **Gestión de Profesores**:
   - Registrar profesor: Menú Profesores > Registrar profesor
   - Asignar a curso: Menú Profesores > Asignar a curso

3. **Gestión de Estudiantes**:
   - Registrar estudiante: Menú Estudiantes > Registrar estudiante
   - Agregar rostro: Seleccione el botón "Guardar rostro con nombre" cuando el estudiante esté frente a la cámara

4. **Control de Asistencia**:
   - Iniciar sesión: Botón "Iniciar sesión" para comenzar a registrar asistencia
   - Pausar: Botón "Pausar" para pausar temporalmente el registro
   - Finalizar: Botón "Finalizar sesión" para terminar el registro de asistencia
   - Manual: Botón "Marcar manualmente" para registrar asistencia sin reconocimiento facial

5. **Reportes**:
   - Exportar: Menú Reportes > Exportar asistencia (Excel o PDF)
   - Dashboard: Menú Archivo > Dashboard para ver estadísticas

### Acceso para Tutores

Los tutores pueden acceder a la información de asistencia de sus estudiantes mediante un código de acceso. Para generar un código:

1. Seleccione un estudiante en la lista
2. Haga clic derecho y seleccione "Generar código para tutor"
3. Configure la duración del código
4. Comparta el código generado con el tutor

El tutor puede usar este código en la pantalla de inicio de sesión para ver:
- Resumen de asistencia del estudiante
- Historial completo de asistencia
- Gráficos mensuales de asistencia

## Configuración Avanzada

### Configuración de la Cámara

La aplicación permite configurar diferentes tipos de cámaras:

- **Webcam**: Seleccione en el menú desplegable
- **Cámara IP**: Seleccione "Cámara IP..." e introduzca la URL del stream

### Configuración de Notificaciones

Para habilitar notificaciones por correo electrónico o WhatsApp:

1. Edite el archivo `notifications.py`
2. Configure las credenciales de API necesarias
3. Reinicie la aplicación

### Seguridad y Acceso

El sistema utiliza encriptación para almacenar datos sensibles. Los archivos importantes son:

- `secret.key`: Clave de encriptación principal (generada automáticamente)
- `data/tutor_access_codes.json`: Códigos de acceso para tutores
- `data/students.json`: Información de estudiantes registrados

## Contribuir al Proyecto

Agradecemos contribuciones a AsistoYA. Para contribuir, siga estos pasos:

1. **Fork el repositorio** en GitHub.

2. **Clone su repositorio forkeado** a su máquina local.

3. **Cree una nueva rama** para su función o corrección:

   ```bash
   git checkout -b mi-rama-nueva
   ```

4. **Realice sus cambios** y haga commit con mensajes descriptivos.

5. **Envíe sus cambios** a su repositorio forkeado:

   ```bash
   git push origin mi-rama-nueva
   ```

6. **Cree un pull request** en el repositorio original.

Asegúrese de que su código siga nuestras normas de codificación e incluya las pruebas apropiadas.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulte el archivo [LICENSE](LICENSE) para más detalles.
