#!/usr/bin/env python3
"""
Oleoflores Smart Flow - WSGI Application Entry Point for PythonAnywhere
"""

import os
import sys

# Configuración de rutas
PROJECT_PATH = '/home/enriquepabon/oleoflores-smart-flow'

# Agregar al path
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    env_path = os.path.join(PROJECT_PATH, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print("✅ Variables de entorno cargadas")
    else:
        print("⚠️ Archivo .env no encontrado")
except ImportError:
    print("⚠️ python-dotenv no instalado")

# Configurar entorno
os.environ['FLASK_ENV'] = 'production'

# Importar y crear aplicación
try:
    from app import create_app
    from config.config import ProductionConfig
    
    application = create_app(ProductionConfig)
    print("✅ Aplicación Flask creada exitosamente")
    
except Exception as e:
    print(f"❌ Error: {e}")
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error_page():
        return f'<h1>Error de Configuración</h1><p>{str(e)}</p>'

# Configurar proxy para PythonAnywhere
if hasattr(application, 'wsgi_app'):
    try:
        from werkzeug.middleware.proxy_fix import ProxyFix
        application.wsgi_app = ProxyFix(application.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    except ImportError:
        pass 