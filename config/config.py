"""
Oleoflores Smart Flow - Configuration Classes

Configuraciones para diferentes entornos de la aplicación.
"""

import os
import secrets
from pathlib import Path
from typing import Type
from datetime import timedelta


class BaseConfig:
    """Configuración base para la aplicación."""
    
    # Configuración básica de Flask
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    if not SECRET_KEY:
        # Usar una clave fija para desarrollo (cambiar en producción)
        SECRET_KEY = 'oleoflores_smart_flow_development_secret_key_2025_fixed'
        print("🔧 INFO: Usando SECRET_KEY fija para desarrollo. Configure FLASK_SECRET_KEY en .env para producción")
    
    # Configuración de base de datos - RUTA ABSOLUTA FORZADA
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    
    # Asegurar que el directorio instance existe
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    
    # Configuración de SQLAlchemy con ruta absoluta explícita
    DB_PATH = os.path.join(INSTANCE_DIR, 'oleoflores_prod.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'check_same_thread': False,
            'timeout': 20
        }
    }

    # Base de datos legacy (SQLite directo) - Migrado a oleoflores_dev.db
    TIQUETES_DB_PATH = os.path.join(INSTANCE_DIR, 'oleoflores_dev.db')
    
    # Session Configuration - Mejorada para persistencia
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True  # Hacer sesiones permanentes por defecto
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'oleoflores:'
    SESSION_COOKIE_NAME = 'oleoflores_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # True en producción con HTTPS
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # 7 días de duración
    REMEMBER_COOKIE_DURATION = timedelta(days=30)  # 30 días para "recordarme"
    REMEMBER_COOKIE_SECURE = False  # True en producción
    REMEMBER_COOKIE_HTTPONLY = True
    
    # File uploads
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 64 * 1024 * 1024))  # 64MB
    UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.xlsx', '.xls']
    
    # Timezone
    TIMEZONE = os.environ.get('TIMEZONE', 'America/Bogota')
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    ROBOFLOW_API_KEY = os.environ.get('ROBOFLOW_API_KEY')
    GOOGLE_GEMINI_API_KEY = os.environ.get('GOOGLE_GEMINI_API_KEY')
    
    # SSL Verification
    VERIFY_SSL = os.environ.get('VERIFY_SSL', 'true').lower() == 'true'
    
    # Roboflow Config
    ROBOFLOW_WORKSPACE = os.environ.get('ROBOFLOW_WORKSPACE', 'enrique-p-workspace')
    ROBOFLOW_PROJECT = os.environ.get('ROBOFLOW_PROJECT', 'clasificacion-racimos')
    ROBOFLOW_VERSION = os.environ.get('ROBOFLOW_VERSION', '1')
    ROBOFLOW_WORKFLOW_ID = os.environ.get('ROBOFLOW_WORKFLOW_ID', 'clasificacion-racimos-3')
    ROBOFLOW_API_URL = os.environ.get('ROBOFLOW_API_URL', 'https://detect.roboflow.com')
    
    # OCR Config
    OCR_ENGINE = os.environ.get('OCR_ENGINE', 'easyocr')
    OCR_LANGUAGES = os.environ.get('OCR_LANGUAGES', 'es,en').split(',')
    OCR_GPU = os.environ.get('OCR_GPU', 'false').lower() == 'true'
    
    # LangChain Config
    LANGCHAIN_TEMPERATURE = float(os.environ.get('LANGCHAIN_TEMPERATURE', '0.1'))
    LANGCHAIN_MODEL = os.environ.get('LANGCHAIN_MODEL', 'gpt-3.5-turbo')
    LANGCHAIN_MAX_TOKENS = int(os.environ.get('LANGCHAIN_MAX_TOKENS', '1000'))
    
    # Pagination
    RECORDS_PER_PAGE = int(os.environ.get('RECORDS_PER_PAGE', '25'))
    
    # Cache
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300'))
    
    # Feature Flags
    USAR_NUEVOS_TEMPLATES_ENTRADA = os.environ.get('USAR_NUEVOS_TEMPLATES_ENTRADA', 'true').lower() == 'true'
    
    # Directories
    STATIC_FOLDER = Path(BASE_DIR) / 'app' / 'static'
    UPLOAD_FOLDER = STATIC_FOLDER / 'uploads'
    GENERATED_FOLDER = STATIC_FOLDER / 'generated'
    TEMP_FOLDER = STATIC_FOLDER / 'temp'
    QR_CODES_FOLDER = STATIC_FOLDER / 'qr'
    QR_FOLDER = str(QR_CODES_FOLDER)  # Alias para compatibilidad
    PDF_FOLDER = STATIC_FOLDER / 'pdfs'
    GUIAS_FOLDER = STATIC_FOLDER / 'guias'
    FOTOS_FOLDER = STATIC_FOLDER / 'fotos_racimos_temp'
    CLASIFICACIONES_FOLDER = STATIC_FOLDER / 'clasificaciones'
    FOTOS_PESAJE_NETO_FOLDER = STATIC_FOLDER / 'fotos_pesaje_neto'
    
    @classmethod
    def init_app(cls, app):
        """Inicialización específica para cada configuración."""
        
        # Crear directorios necesarios
        directories = [
            Path(cls.INSTANCE_DIR),
            cls.UPLOAD_FOLDER,
            cls.GENERATED_FOLDER,
            cls.TEMP_FOLDER,
            cls.QR_CODES_FOLDER,
            cls.PDF_FOLDER,
            cls.GUIAS_FOLDER,
            cls.FOTOS_FOLDER,
            cls.CLASIFICACIONES_FOLDER,
            cls.FOTOS_PESAJE_NETO_FOLDER
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(BaseConfig):
    """Configuración para desarrollo local."""
    
    DEBUG = True
    TESTING = False
    
    # Development database
    DATABASE_URL = os.environ.get('DEV_DATABASE_URL') or f'sqlite:///{BaseConfig.INSTANCE_DIR}/oleoflores_dev.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    # Disable CSRF for development (optional)
    WTF_CSRF_ENABLED = False

class ProductionConfig(BaseConfig):
    """Configuración para entorno de producción."""
    
    DEBUG = False
    TESTING = False
    
    # Configuración CSRF
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'true').lower() == 'false'
    
    # Production security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Forzar ruta absoluta para producción
    BASE_DIR = '/home/enriquepabon/oleoflores-smart-flow'
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    DB_PATH = os.path.join(INSTANCE_DIR, 'oleoflores_prod.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    
    # Configuración específica de producción
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'check_same_thread': False,
            'timeout': 30,  # Timeout más largo para producción
            'isolation_level': None
        }
    }

    # Base de datos legacy para producción
    TIQUETES_DB_PATH = os.path.join(INSTANCE_DIR, 'oleoflores_prod.db')
    
    # Production caching - Simple para PythonAnywhere básico
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    
    @classmethod
    def init_app(cls, app):
        """Configuración específica para producción."""
        BaseConfig.init_app(app)
        
        # Configurar logging para producción
        import logging
        from logging.handlers import RotatingFileHandler
        
        # File handler
        if not app.debug:
            log_dir = Path(cls.BASE_DIR) / 'logs'
            log_dir.mkdir(exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_dir / 'oleoflores.log',
                maxBytes=10240000,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('Oleoflores Smart Flow startup')

class TestingConfig(BaseConfig):
    """Configuración para testing."""
    
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    
    # Testing database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TIQUETES_DB_PATH = ':memory:'

# Configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: str = None) -> Type[BaseConfig]:
    """Obtener configuración por nombre o usando la variable de entorno FLASK_ENV."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default']) 