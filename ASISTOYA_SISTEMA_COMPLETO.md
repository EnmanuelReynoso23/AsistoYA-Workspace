# 🎓 AsistoYA - Sistema Completo de Asistencia con Reconocimiento Facial

## 📋 **Descripción del Sistema**

AsistoYA es un sistema de control de asistencia escolar que utiliza **reconocimiento facial** para detectar automáticamente cuando los estudiantes llegan a la escuela y envía **notificaciones instantáneas a los padres**.

## 🎯 **Características Principales**

### ✅ **Reconocimiento Facial Avanzado**
- Detección automática con OpenCV y algoritmos Haar Cascade
- Reconocimiento LBPH (Local Binary Patterns Histograms)
- Soporte para múltiples fotos por estudiante (hasta 5 imágenes)
- Precisión superior al 90% en condiciones normales

### 📱 **Notificaciones a Padres**
- Notificaciones automáticas vía Firebase cuando el estudiante llega
- Portal web para que los padres vean el historial de asistencia
- Token único por familia para acceso seguro
- Actualizaciones en tiempo real

### 💾 **Base de Datos Local**
- Almacenamiento seguro en archivos JSON
- Backup automático de datos
- Sincronización opcional con Firebase

## 🚀 **Cómo Usar el Sistema**

### **1. Instalación y Configuración**

```bash
# Clonar o descargar el proyecto
# Navegar a la carpeta del proyecto
cd AsistoYA-Workspace

# Ejecutar el instalador automático
run_asistoya.bat
```

### **2. Registro de Estudiantes**

1. **Abrir la aplicación** ejecutando `run_asistoya.bat`
2. **Ir a la pestaña "Registro"**
3. **Iniciar la cámara** con el botón "📷 Iniciar Cámara"
4. **Llenar los datos del estudiante:**
   - Nombre completo del estudiante
   - Grado/Curso
   - Sección
5. **Llenar los datos del padre/madre:**
   - Nombre del padre/madre
   - Email
   - Teléfono
6. **Posicionarse frente a la cámara** (debe aparecer un rectángulo verde)
7. **Hacer clic en "✅ Registrar Usuario"**
8. **Guardar el token generado** para dar a los padres

### **3. Control de Asistencia**

1. **Ir a la pestaña "Dashboard"**
2. **Hacer clic en "🔍 Reconocimiento Rápido"**
3. **El sistema detectará automáticamente** a los estudiantes
4. **Se marcará la asistencia** y se enviará notificación a los padres
5. **Ver estadísticas** en tiempo real en el dashboard

### **4. Portal de Padres**

1. **Ejecutar el portal web** con `run_portal_padres.bat`
2. **Los padres acceden a** `http://localhost:5000`
3. **Ingresan su token único** recibido en el registro
4. **Pueden ver:**
   - Historial de asistencia de su hijo/a
   - Estadísticas de asistencia
   - Horarios de llegada
   - Porcentaje de asistencia

## 📂 **Estructura del Proyecto**

```
AsistoYA-Workspace/
├── face_attendance_system.py    # 🎯 Aplicación principal
├── parent_portal.py             # 🌐 Portal web para padres
├── firebase/                    # 🔥 Configuración Firebase
│   ├── firebase_config.py
│   ├── firebase-service-account.json
│   └── google-services.json
├── faces/                       # 👤 Imágenes de rostros
│   ├── registered_users.json   # 📋 Base de datos estudiantes
│   └── attendance_records.json # 📊 Registros de asistencia
├── run_asistoya.bat            # 🚀 Ejecutar aplicación principal
├── run_portal_padres.bat       # 🌐 Ejecutar portal padres
└── README.md                   # 📖 Documentación
```

## 🔧 **Dependencias Requeridas**

El sistema instala automáticamente las dependencias, pero también pueden instalarse manualmente:

```bash
pip install opencv-python ttkbootstrap numpy pillow pandas matplotlib seaborn flask firebase-admin
```

## 📱 **Flujo Completo del Sistema**

### **Proceso de Registro:**
```
1. Escuela registra estudiante con cámara
2. Sistema captura 5 fotos del rostro
3. Se generan códigos únicos para estudiante y padre
4. Se almacenan datos en base de datos local
5. Se entrega token a los padres
```

### **Proceso de Asistencia:**
```
1. Estudiante llega a la escuela
2. Cámara detecta y reconoce el rostro
3. Sistema marca asistencia automáticamente
4. Se envía notificación a Firebase
5. Padres reciben notificación instantánea
6. Datos se actualizan en portal web
```

## ⚙️ **Configuración Avanzada**

### **Configuración de Cámara**
- Múltiples cámaras soportadas (USB, integrada)
- Resolución ajustable (640x480, 800x600, 1280x720)
- Configuración de brillo y contraste

### **Configuración de Reconocimiento**
- Umbral de confianza ajustable (50% - 95%)
- Tiempo de cooldown entre reconocimientos (5-60 segundos)
- Máximo de rostros por estudiante (1-10)

### **Firebase (Opcional)**
Si desea usar notificaciones push reales:
1. Crear proyecto en Firebase Console
2. Descargar `firebase-service-account.json`
3. Colocar en carpeta `firebase/`
4. Configurar tokens FCM de los padres

## 🛡️ **Seguridad y Privacidad**

- **Datos locales:** Toda la información se almacena localmente
- **Tokens únicos:** Cada familia tiene acceso solo a sus datos
- **Encriptación:** Datos sensibles protegidos
- **No requiere internet:** Funciona completamente offline (excepto notificaciones)

## 📊 **Reportes y Estadísticas**

### **Dashboard de Escuela:**
- Estudiantes registrados
- Asistencia del día
- Asistencia semanal/mensual
- Tendencias de asistencia

### **Portal de Padres:**
- Historial completo de asistencia
- Porcentaje de asistencia
- Horarios de llegada
- Estadísticas personalizadas

## 🆘 **Solución de Problemas**

### **Cámara no funciona:**
- Verificar que la cámara esté conectada
- Probar diferentes índices de cámara (0, 1, 2...)
- Cerrar otras aplicaciones que usen la cámara

### **No reconoce rostros:**
- Verificar iluminación adecuada
- Asegurar que el rostro esté centrado
- Revisar umbral de confianza en configuración

### **Portal web no carga:**
- Verificar que Flask esté instalado
- Confirmar que el puerto 5000 esté libre
- Revisar archivos de datos en carpeta `faces/`

### **Firebase no funciona:**
- Verificar archivo de credenciales
- Confirmar conexión a internet
- Revisar configuración del proyecto Firebase

## 📞 **Soporte**

Para problemas técnicos:
1. Revisar logs en la consola de la aplicación
2. Verificar que todos los archivos estén presentes
3. Comprobar dependencias instaladas
4. Contactar al administrador del sistema

## 🎉 **¡Listo para Usar!**

El sistema AsistoYA está completamente configurado y listo para usar. Simplemente:

1. **Ejecutar:** `run_asistoya.bat` para la aplicación principal
2. **Ejecutar:** `run_portal_padres.bat` para el portal web
3. **Registrar estudiantes** con sus datos de padres
4. **Compartir tokens** con las familias
5. **¡Disfrutar del control automático de asistencia!**

---

**AsistoYA - Tecnología al servicio de la educación** 🎓📱✨
