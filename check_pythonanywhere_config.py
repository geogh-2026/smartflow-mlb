#!/usr/bin/env python3
"""
Oleoflores Smart Flow - Script de Verificación para PythonAnywhere

Este script verifica que todos los componentes estén correctamente
configurados antes del despliegue en PythonAnywhere.

Uso:
    python check_pythonanywhere_config.py
"""

import os
import sys
from pathlib import Path
import importlib.util

def print_header(title):
    """Imprimir encabezado con formato."""
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def print_check(description, status, details=""):
    """Imprimir resultado de verificación."""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {description}")
    if details:
        print(f"   {details}")

def check_file_exists(file_path, description):
    """Verificar que un archivo existe."""
    exists = Path(file_path).exists()
    print_check(description, exists, f"Ruta: {file_path}")
    return exists

def check_directory_exists(dir_path, description):
    """Verificar que un directorio existe."""
    exists = Path(dir_path).exists()
    print_check(description, exists, f"Ruta: {dir_path}")
    return exists

def check_env_var(var_name, description, required=True):
    """Verificar que una variable de entorno esté configurada."""
    value = os.environ.get(var_name)
    exists = value is not None and value.strip() != ""
    
    if not required and not exists:
        print_check(f"{description} (opcional)", True, "No configurada")
        return True
    
    status_text = "Configurada" if exists else "NO CONFIGURADA"
    if exists:
        # Ocultar claves sensibles
        if 'key' in var_name.lower() or 'password' in var_name.lower():
            display_value = value[:8] + "..." if len(value) > 8 else "***"
        else:
            display_value = value
        details = f"{status_text}: {display_value}"
    else:
        details = status_text
    
    print_check(description, exists, details)
    return exists

def check_python_import(module_name, description):
    """Verificar que un módulo Python se pueda importar."""
    try:
        __import__(module_name)
        print_check(description, True, f"Módulo: {module_name}")
        return True
    except ImportError as e:
        print_check(description, False, f"Error: {e}")
        return False

def check_flask_app():
    """Verificar que la aplicación Flask se pueda importar y crear."""
    try:
        from app import create_app
        from config.config import PythonAnywhereConfig
        
        app = create_app(PythonAnywhereConfig)
        print_check("Aplicación Flask creada correctamente", True)
        
        # Verificar configuración crítica
        with app.app_context():
            has_secret = bool(app.config.get('SECRET_KEY'))
            print_check("SECRET_KEY configurada", has_secret)
            
            db_path = app.config.get('DATABASE_URL', '')
            has_db = 'sqlite:///' in db_path or 'postgresql://' in db_path or 'mysql://' in db_path
            print_check("Base de datos configurada", has_db, f"URL: {db_path}")
        
        return True
    except Exception as e:
        print_check("Aplicación Flask", False, f"Error: {e}")
        return False

def main():
    """Función principal de verificación."""
    print("🚀 Oleoflores Smart Flow - Verificación de Configuración PythonAnywhere")
    print("="*80)
    
    # Cambiar al directorio del proyecto
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    all_checks_passed = True
    
    # 1. Verificar archivos esenciales
    print_header("ARCHIVOS ESENCIALES")
    checks = [
        ("wsgi.py", "Archivo WSGI principal"),
        ("run.py", "Script de ejecución"),
        ("app/__init__.py", "Módulo principal de la aplicación"),
        ("config/config.py", "Configuración de la aplicación"),
        ("requirements_pythonanywhere.txt", "Dependencias para PythonAnywhere"),
        ("env_template_production.txt", "Template de variables de entorno"),
        ("deploy_pythonanywhere.md", "Guía de despliegue"),
    ]
    
    for file_path, description in checks:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # 2. Verificar directorios
    print_header("ESTRUCTURA DE DIRECTORIOS")
    directories = [
        ("app/static", "Directorio de archivos estáticos"),
        ("app/templates", "Directorio de templates"),
        ("app/blueprints", "Directorio de blueprints"),
        ("instance", "Directorio de instancia (base de datos)"),
        ("logs", "Directorio de logs"),
    ]
    
    for dir_path, description in directories:
        if not check_directory_exists(dir_path, description):
            all_checks_passed = False
    
    # 3. Verificar variables de entorno
    print_header("VARIABLES DE ENTORNO")
    
    # Cargar .env si existe
    env_file = Path('.env')
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print_check("Archivo .env cargado", True, f"Archivo: {env_file}")
        except ImportError:
            print_check("python-dotenv disponible", False, "Instalar: pip install python-dotenv")
            all_checks_passed = False
    else:
        print_check("Archivo .env encontrado", False, "Crear desde env_template_production.txt")
    
    # Variables requeridas
    required_vars = [
        ("FLASK_SECRET_KEY", "Clave secreta de Flask"),
        ("FLASK_ENV", "Entorno de Flask"),
    ]
    
    # Variables opcionales pero recomendadas
    optional_vars = [
        ("OPENAI_API_KEY", "API Key de OpenAI", False),
        ("ROBOFLOW_API_KEY", "API Key de Roboflow", False),
        ("DATABASE_URL", "URL de base de datos", False),
        ("TIMEZONE", "Zona horaria", False),
    ]
    
    for var_name, description, *required in required_vars:
        is_required = required[0] if required else True
        if not check_env_var(var_name, description, is_required):
            all_checks_passed = False
    
    for var_name, description, is_required in optional_vars:
        check_env_var(var_name, description, is_required)
    
    # 4. Verificar dependencias Python
    print_header("DEPENDENCIAS PYTHON")
    dependencies = [
        ("flask", "Flask framework"),
        ("flask_login", "Flask-Login"),
        ("flask_sqlalchemy", "Flask-SQLAlchemy"),
        ("dotenv", "python-dotenv"),
        ("PIL", "Pillow (procesamiento de imágenes)"),
        ("cv2", "OpenCV"),
        ("easyocr", "EasyOCR"),
        ("langchain", "LangChain"),
        ("openai", "OpenAI Python client"),
        ("requests", "Requests HTTP library"),
        ("pandas", "Pandas"),
        ("qrcode", "QR Code generator"),
        ("reportlab", "ReportLab PDF"),
    ]
    
    for module, description in dependencies:
        if not check_python_import(module, description):
            all_checks_passed = False
    
    # 5. Verificar aplicación Flask
    print_header("CONFIGURACIÓN FLASK")
    if not check_flask_app():
        all_checks_passed = False
    
    # 6. Verificar configuración específica de PythonAnywhere
    print_header("CONFIGURACIÓN PYTHONANYWHERE")
    
    # Verificar que wsgi.py tenga la configuración correcta
    wsgi_file = Path('wsgi.py')
    if wsgi_file.exists():
        wsgi_content = wsgi_file.read_text()
        
        has_username = 'YOURUSERNAME' not in wsgi_content
        print_check("Usuario de PythonAnywhere actualizado en wsgi.py", has_username)
        if not has_username:
            all_checks_passed = False
        
        has_pythonanywhere_config = 'PythonAnywhereConfig' in wsgi_content
        print_check("Configuración PythonAnywhereConfig en uso", has_pythonanywhere_config)
        if not has_pythonanywhere_config:
            all_checks_passed = False
    
    # Resumen final
    print_header("RESUMEN DE VERIFICACIÓN")
    
    if all_checks_passed:
        print("🎉 ¡TODAS LAS VERIFICACIONES PASARON!")
        print("\n✅ Tu aplicación está lista para desplegar en PythonAnywhere")
        print("\n📋 Próximos pasos:")
        print("   1. Sube el código a tu cuenta de PythonAnywhere")
        print("   2. Crea el entorno virtual e instala dependencias")
        print("   3. Configura la web app siguiendo deploy_pythonanywhere.md")
        print("   4. Crea el archivo .env con tus credenciales reales")
        print("   5. ¡Lanza tu aplicación!")
        return 0
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("\n🔧 Revisa los errores marcados arriba y corrígelos antes de desplegar")
        print("\n📖 Consulta deploy_pythonanywhere.md para instrucciones detalladas")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 