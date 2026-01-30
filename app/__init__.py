"""
Oleoflores Smart Flow - Application Factory

Factory pattern para crear instancias de la aplicación Flask.
"""

import os
from flask import Flask, render_template
import logging
import secrets
from datetime import timedelta
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
# Importar la función del filtro
from .utils.common import format_datetime_filter, format_number_es
# Importar Flask-Login
from flask_login import LoginManager
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instanciar LoginManager globalmente o dentro de create_app
# Es común hacerlo globalmente y luego inicializarlo
login_manager = LoginManager()
# Configurar la vista a la que redirigir si el usuario no está logueado
# Usaremos 'auth.login' que crearemos más adelante en el blueprint 'auth'
login_manager.login_view = 'auth.login'
# Opcional: Mensaje flash que se mostrará al usuario redirigido
login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
login_manager.login_message_category = "info"
# Configuración adicional para mejorar la persistencia
login_manager.session_protection = "basic"  # Protección de sesión básica para evitar problemas

# Clase SimpleUser para Flask-Login (fuera del user_loader para evitar problemas de referencia)
class SimpleUser:
    """Clase de usuario compatible con Flask-Login usando SQL directo"""
    def __init__(self, id, username, email, password_hash, is_active, is_admin=0, user_role='guarda'):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self._is_active = bool(is_active)
        self._is_admin = bool(is_admin)
        self.user_role = user_role or 'guarda'
        
    def get_id(self):
        """Método requerido por Flask-Login"""
        return str(self.id)
        
    @property
    def is_authenticated(self):
        """Propiedad requerida por Flask-Login - usuario está autenticado"""
        return True
        
    @property
    def is_anonymous(self):
        """Propiedad requerida por Flask-Login - usuario no es anónimo"""
        return False
        
    @property
    def is_active(self):
        """Propiedad requerida por Flask-Login - usuario está activo"""
        return self._is_active
        
    @property
    def is_admin(self):
        """Propiedad para verificar si el usuario es administrador"""
        return self._is_admin  # Usar el campo is_admin de la base de datos
        
    def has_role(self, role):
        """Método para verificar si el usuario tiene un rol específico"""
        # Los administradores tienen acceso a todos los roles
        if self._is_admin:
            return True
        # Verificar rol específico
        return self.user_role == role
        
    def get_role_display_name(self):
        """Método para mostrar el rol del usuario en templates"""
        if self._is_admin:
            return "Administrador"
        
        role_names = {
            'admin': 'Administrador',
            'guarda': 'Guarda',
            'inspector_laboratorio': 'Inspector de Laboratorio',
            'basculero': 'Basculero',
            'jefe_calidad': 'Jefe de Calidad',
            'clasificacion_fruta': 'Clasificación de Fruta',
            'recepcion': 'Recepción'
        }
        return role_names.get(self.user_role, 'Usuario')
        
    def __repr__(self):
        return f'<SimpleUser {self.username} (admin: {self._is_admin}, role: {self.user_role})>'

# Callback para recargar el objeto usuario desde el ID de usuario almacenado en la sesión
@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario para Flask-Login usando SQL directo"""
    logger.info(f"🔍 DEBUG: Flask-Login cargando usuario ID: {user_id}")
    try:
        from sqlalchemy import text
        from app.models import db
        
        result = db.session.execute(
            text('SELECT id, username, email, password_hash, is_active, is_admin, user_role FROM users WHERE id = :user_id'), 
            {'user_id': int(user_id)}
        ).fetchone()
        
        if result:
            logger.info(f"🔍 DEBUG: Usuario recargado exitosamente: {result[1]} (admin: {bool(result[5])}, role: {result[6]})")
            return SimpleUser(result[0], result[1], result[2], result[3], result[4], result[5], result[6])
        else:
            logger.info(f"🔍 DEBUG: Usuario ID {user_id} no encontrado para recarga")
        return None
    except Exception as e:
        logger.error(f"❌ ERROR recargando usuario: {e}")
        return None

def create_app(config_class=None):
    """Factory para crear la aplicación Flask."""
    
    # Usar la configuración por defecto si no se especifica
    if config_class is None:
        from config.config import get_config
        config_class = get_config()
    
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    
    # Asegurar que el límite de tamaño de archivos se aplique correctamente
    app.config['MAX_CONTENT_LENGTH'] = config_class.MAX_CONTENT_LENGTH
    
    # Inicializar extensiones
    init_extensions(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Configurar logging
    configure_logging(app)
    
    # Configurar manejo de errores
    configure_error_handlers(app)
    
    # Configurar filtros de templates
    configure_template_filters(app)
    
    return app

def init_extensions(app):
    """Inicializar extensiones de Flask."""
    
    # SQLAlchemy
    from app.models import db
    db.init_app(app)
    
    # Flask-Login
    login_manager.init_app(app)
    
    # Crear tablas si no existen
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
    
    logger.info("Extensions initialized successfully")

def register_blueprints(app):
    """Registrar todos los blueprints."""
    
    # Blueprint principal (dashboard)
    from app.blueprints.entrada import entrada_bp
    from app.blueprints.pesaje import pesaje_bp
    from app.blueprints.clasificacion import clasificacion_bp
    from app.blueprints.graneles import graneles_bp
    from app.blueprints.pesaje_neto import pesaje_neto_bp
    from app.blueprints.salida import salida_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.api import api_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.misc import misc_bp
    from app.blueprints.utils import utils_bp
    from app.blueprints.sellos import sellos_bp
    from app.blueprints.certificados import certificados_bp
    from app.blueprints.remisiones import remisiones_bp
    from app.blueprints.codigos_despacho import codigos_despacho_bp
    from app.blueprints.facturas import facturas_bp
    from app.blueprints.visitantes import visitantes_bp
    from app.blueprints.test_access import test_bp
    # from app.blueprints.presupuesto import bp as presupuesto_bp  # Comentado temporalmente - requiere pandas
    
    # Registrar blueprints con sus prefijos
    app.register_blueprint(entrada_bp)  # Sin prefijo - módulo principal
    app.register_blueprint(pesaje_bp, url_prefix='/pesaje')
    app.register_blueprint(clasificacion_bp, url_prefix='/clasificacion')
    app.register_blueprint(graneles_bp, url_prefix='/graneles')
    app.register_blueprint(pesaje_neto_bp, url_prefix='/pesaje-neto')
    app.register_blueprint(salida_bp, url_prefix='/salida')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(misc_bp, url_prefix='/misc')
    app.register_blueprint(utils_bp, url_prefix='/utils')
    app.register_blueprint(sellos_bp, url_prefix='/sellos')
    app.register_blueprint(certificados_bp, url_prefix='/certificados')
    app.register_blueprint(remisiones_bp, url_prefix='/remisiones')
    app.register_blueprint(codigos_despacho_bp, url_prefix='/codigos-despacho')
    app.register_blueprint(facturas_bp, url_prefix='/facturas')
    app.register_blueprint(visitantes_bp, url_prefix='/visitantes')
    app.register_blueprint(test_bp)  # Blueprint de prueba
    # app.register_blueprint(presupuesto_bp)  # Comentado temporalmente - requiere pandas

def configure_logging(app):
    """Configurar logging para la aplicación."""
    if not app.debug and not app.testing:
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Crear directorio de logs
        log_dir = Path(app.config['BASE_DIR']) / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # Configurar handler de archivos
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

def configure_error_handlers(app):
    """Configurar manejo de errores."""
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        app.logger.warning(f'File too large: {error}')
        return render_template('errors/413.html'), 413

def configure_template_filters(app):
    """Configurar filtros personalizados para templates."""
    
    # Importar el filtro que está definido en utils/common.py
    from app.utils.common import format_datetime_filter, format_number_es
    
    @app.template_filter('datetime')
    def datetime_filter(value, format='%d/%m/%Y %H:%M'):
        """Formatear datetime para templates."""
        if value is None:
            return ''
        return value.strftime(format)
    
    @app.template_filter('currency')
    def currency_filter(value):
        """Formatear valores monetarios."""
        if value is None:
            return '$0'
        return f'${value:,.2f}'
    
    @app.template_filter('from_json')
    def from_json_filter(value):
        """Parsear JSON string a objeto Python."""
        if not value:
            return {}
        try:
            import json
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @app.template_filter('filesize')
    def filesize_filter(bytes):
        """Formatear tamaño de archivos."""
        if bytes is None or bytes == 0:
            return '0 B'
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f'{bytes:.1f} {unit}'
            bytes /= 1024.0
        return f'{bytes:.1f} TB'
    
    # Registrar el filtro format_datetime que falta
    @app.template_filter('format_datetime')
    def register_format_datetime_filter(value, format='%d/%m/%Y %H:%M:%S'):
        """Filtro para formatear timestamps UTC a hora local de Bogotá."""
        return format_datetime_filter(value, format)
    
    # Registrar el filtro format_number_es si existe
    try:
        @app.template_filter('format_number_es')
        def register_format_number_es_filter(value):
            """Filtro para formatear números en español."""
            return format_number_es(value)
    except ImportError:
        pass  # Si no existe format_number_es, continuar sin errores
    
    # Función de template para verificar permisos de sellos
    @app.template_global()
    def usuario_tiene_permiso_sello(permiso):
        """Verificar si el usuario actual tiene un permiso específico de sellos."""
        from flask_login import current_user
        from app.models.sellos_rbac_models import UsuarioRolSello
        
        if not current_user.is_authenticated:
            return False
        
        # Bypass seguro para administradores de la app (igual que en decoradores)
        try:
            if getattr(current_user, 'is_admin', False) or str(getattr(current_user, 'username', '')).lower() == 'admin':
                return True
        except Exception:
            pass
        
        return UsuarioRolSello.usuario_tiene_permiso(current_user.id, permiso)

# Funciones de utilidad globales
def render_template(template_name_or_list, **context):
    """Wrapper para render_template con contexto global."""
    from flask import render_template as flask_render_template
    
    # Agregar variables globales al contexto
    context.update({
        'app_name': 'Oleoflores Smart Flow',
        'app_version': '1.0.0-beta',
    })
    
    return flask_render_template(template_name_or_list, **context)
