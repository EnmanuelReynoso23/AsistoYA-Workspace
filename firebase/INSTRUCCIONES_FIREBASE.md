# 🔥 INSTRUCCIONES PARA CONFIGURAR FIREBASE CORRECTAMENTE

## PASO 1: Generar Service Account Key (REQUERIDO)

Para que el sistema funcione completamente, necesitas generar un archivo de service account desde la consola de Firebase:

### Pasos para generar el Service Account:

1. Ve a la Consola de Firebase: https://console.firebase.google.com/
2. Selecciona tu proyecto: "un-estudiante-kgft8a"
3. Ve a "Configuración del proyecto" (ícono de engranaje)
4. Pestaña "Cuentas de servicio"
5. Haz clic en "Generar nueva clave privada"
6. Se descargará un archivo JSON

### Configuración del archivo:

1. Renombra el archivo descargado a: `service-account-key.json`
2. Colócalo en la carpeta: `firebase/service-account-key.json`
3. Reemplaza el archivo demo que creé

## PASO 2: Configuración actual

✅ Proyecto ID: un-estudiante-kgft8a
✅ Storage Bucket: un-estudiante-kgft8a.appspot.com
✅ google-services.json encontrado
⚠️  service-account-key.json necesita ser generado

## PASO 3: Habilitar servicios en Firebase

En la consola de Firebase, asegúrate de tener habilitados:
- Firestore Database
- Storage
- Authentication
- Cloud Messaging (opcional)

## ESTADO ACTUAL

El sistema está configurado para usar tus credenciales del proyecto "un-estudiante-kgft8a".
Una vez que coloques el service account correcto, el sistema funcionará al 100%.

## ALTERNATIVA (MODO LOCAL)

Si no quieres usar Firebase ahora, el sistema puede funcionar en modo local
con una base de datos SQLite temporal.
