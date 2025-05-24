"""
Script de configuraci�n para instalar correctamente todas las dependencias de AsistoYA
"""
import os
import subprocess
import sys
import platform

def check_python_version():
    """Verificar versi�n de Python"""
    print("Verificando versi�n de Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"[ERROR] Se requiere Python 3.8 o superior. Versi�n actual: {sys.version}")
        print("Por favor, actualice Python e intente nuevamente.")
        return False
    print(f"[OK] Versi�n de Python compatible: {sys.version}")
    return True

def install_package(package, extra_index_url=None):
    """Instalar un paquete utilizando pip"""
    print(f"Instalando {package}...")
    cmd = [sys.executable, "-m", "pip", "install", package]
    
    if extra_index_url:
        cmd.extend(["--extra-index-url", extra_index_url])
    
    try:
        subprocess.check_call(cmd)
        print(f"[OK] {package} instalado correctamente")
        return True
    except subprocess.CalledProcessError:
        print(f"[ERROR] Error al instalar {package}")
        return False

def uninstall_package(package):
    """Desinstalar un paquete"""
    print(f"Desinstalando {package}...")
    cmd = [sys.executable, "-m", "pip", "uninstall", "-y", package]
    try:
        subprocess.check_call(cmd)
        print(f"[OK] {package} desinstalado correctamente")
        return True
    except subprocess.CalledProcessError:
        print(f"[ERROR] Error al desinstalar {package}")
        return False

def fix_torch_installation():
    """Corregir instalaci�n de PyTorch"""
    print("\nReparando instalaci�n de PyTorch...")
    
    # Desinstalar PyTorch existente
    uninstall_package("torch")
    uninstall_package("torchvision")
    uninstall_package("torchaudio")
    
    # Instalar la versi�n correcta para la plataforma
    if platform.system() == "Windows":
        if install_package("torch==2.0.0+cpu torchvision==0.15.0+cpu torchaudio==2.0.0+cpu", "https://download.pytorch.org/whl/cpu"):
            print("[OK] PyTorch instalado correctamente para CPU en Windows")
            return True
    else:
        # Para Linux/Mac, usar la versi�n est�ndar
        if install_package("torch==2.0.0 torchvision==0.15.0 torchaudio==2.0.0"):
            print("[OK] PyTorch instalado correctamente")
            return True
    
    print("[ERROR] No se pudo instalar PyTorch correctamente")
    return False

def fix_ultralytics_installation():
    """Corregir instalaci�n de Ultralytics"""
    print("\nReparando instalaci�n de Ultralytics...")
    
    # Desinstalar Ultralytics existente
    uninstall_package("ultralytics")
    
    # Instalar una versi�n compatible
    if install_package("ultralytics==8.0.0"):
        print("[OK] Ultralytics instalado correctamente")
        return True
    
    print("[ERROR] No se pudo instalar Ultralytics correctamente")
    return False

def check_opencv():
    """Verificar instalaci�n de OpenCV"""
    print("\nVerificando OpenCV...")
    try:
        import cv2
        print(f"[OK] OpenCV instalado correctamente (versi�n {cv2.__version__})")
        return True
    except ImportError:
        print("[ERROR] OpenCV no est� instalado")
        if install_package("opencv-python>=4.8.0"):
            print("[OK] OpenCV instalado correctamente")
            return True
        return False

def check_other_dependencies():
    """Verificar otras dependencias cr�ticas"""
    print("\nVerificando otras dependencias cr�ticas...")
    
    dependencies = [
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "fpdf>=1.7.2",
        "ttkbootstrap>=1.10.0",
        "pillow>=10.0.0",
        "openpyxl>=3.1.0",
        "cryptography>=41.0.0"
    ]
    
    all_ok = True
    for dep in dependencies:
        package = dep.split(">=")[0]
        try:
            __import__(package)
            print(f"[OK] {package} ya est� instalado")
        except ImportError:
            print(f"[INFO] Instalando {dep}...")
            if not install_package(dep):
                all_ok = False
    
    return all_ok

def create_fallback_mode():
    """Crear un modo alternativo sin YOLO para sistemas con recursos limitados"""
    print("\nCreando modo alternativo sin YOLO...")
    
    # Crear archivo de configuraci�n
    config = {
        "USE_YOLO": False,
        "CAMERA_INDEX": 0,
        "FACE_CONFIDENCE_THRESHOLD": 80,
        "SEND_NOTIFICATIONS": False
    }
    
    try:
        import json
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        print("[OK] Archivo de configuraci�n creado correctamente")
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo crear el archivo de configuraci�n: {e}")
        return False

def main():
    """Funci�n principal"""
    print("=" * 80)
    print("CONFIGURACI�N DE DEPENDENCIAS DE ASISTOYA")
    print("=" * 80)
    
    if not check_python_version():
        sys.exit(1)
    
    # Verificar y arreglar dependencias
    cv_ok = check_opencv()
    torch_ok = fix_torch_installation()
    ultralytics_ok = fix_ultralytics_installation() 
    other_ok = check_other_dependencies()
    
    # Verificar si todas las dependencias est�n OK
    all_ok = cv_ok and torch_ok and ultralytics_ok and other_ok
    
    if all_ok:
        print("\n[�XITO] Todas las dependencias instaladas correctamente!")
        print("Puede ejecutar la aplicaci�n con el comando: python main.py")
    else:
        print("\n[ADVERTENCIA] Algunas dependencias no se pudieron instalar correctamente.")
        print("Se crear� un modo alternativo que no requiere YOLO.")
        create_fallback_mode()
        print("Puede ejecutar la aplicaci�n con el comando: python main.py --fallback")
    
    print("\nGracias por utilizar AsistoYA!")
    input("Presione ENTER para salir...")

if __name__ == "__main__":
    main()
