#!/usr/bin/env python3
""" que
Oleoflores Smart Flow - Application Entry Point

Punto de entrada principal para la aplicación Flask.
Inicializa la aplicación y la ejecuta en modo desarrollo o producción.

Usage:
    python run.py                    # Desarrollo con debug
    python run.py --prod             # Producción sin debug
    python run.py --port 8000        # Puerto personalizado (default: 5001)
    python run.py --host 0.0.0.0     # Host personalizado
"""

import os
import sys
import argparse
from pathlib import Path

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    # Cargar .env desde el directorio raíz del proyecto
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Variables de entorno cargadas desde: {env_path}")
    else:
        print("⚠️  Archivo .env no encontrado")
except ImportError:
    print("⚠️  python-dotenv no instalado, variables de entorno manuales requeridas")

# Añadir el directorio raíz al path de Python
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app import create_app
    from config.config import DevelopmentConfig, ProductionConfig
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("💡 Asegúrate de que todas las dependencias estén instaladas:")
    print("   pip install -r requirements.txt")
    sys.exit(1)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Oleoflores Smart Flow - Sistema de Gestión Inteligente'
    )
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host IP para el servidor (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5001,
        help='Puerto para el servidor (default: 5001, evita conflicto con AirPlay en macOS)'
    )
    parser.add_argument(
        '--prod',
        action='store_true',
        help='Ejecutar en modo producción (sin debug)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Forzar modo debug (override de variables de entorno)'
    )
    return parser.parse_args()


def get_config_class(production_mode=False):
    """Determinar la clase de configuración a usar."""
    if production_mode:
        return ProductionConfig

    # Verificar variables de entorno
    flask_env = os.environ.get('FLASK_ENV', 'development').lower()
    if flask_env == 'production':
        return ProductionConfig

    return DevelopmentConfig


def check_environment():
    """Verificar que el entorno esté configurado correctamente."""
    required_vars = ['FLASK_SECRET_KEY']
    missing_vars = []

    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)

    if missing_vars:
        print("⚠️  Variables de entorno faltantes:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Crea un archivo .env con las variables requeridas")
        print("   o configúralas en tu sistema.")
        return False

    return True


def display_startup_info(app, host, port, debug_mode):
    """Mostrar información de inicio de la aplicación."""
    print("=" * 60)
    print("🌱 Oleoflores Smart Flow")
    print("   Sistema de Gestión Inteligente de Procesos Agrícolas")
    print("=" * 60)
    print(f"🚀 Servidor iniciando...")
    print(f"🌐 URL: http://{host}:{port}")
    print(f"🔧 Modo: {'Desarrollo (Debug)' if debug_mode else 'Producción'}")
    print(f"📊 Configuración: {app.config.__class__.__name__}")
    print(f"🗄️  Base de datos: {app.config.get('DATABASE_URL', 'No configurada')}")

    # Verificar APIs configuradas
    apis_configured = []
    if os.environ.get('OPENAI_API_KEY'):
        apis_configured.append('OpenAI')
    if os.environ.get('ROBOFLOW_API_KEY'):
        apis_configured.append('Roboflow')

    if apis_configured:
        print(f"🤖 APIs configuradas: {', '.join(apis_configured)}")
    else:
        print("⚠️  No hay APIs de IA configuradas")

    print("=" * 60)
    print("📋 Endpoints principales:")
    print("   /                    - Dashboard principal")
    print("   /entrada             - Registro de entrada")
    print("   /pesaje              - Sistema de pesaje")
    print("   /clasificacion       - Clasificación automática")
    print("   /graneles            - Sistema de graneles")
    print("   /admin               - Panel de administración")
    print("=" * 60)

    if debug_mode:
        print("🐛 Modo Debug ACTIVADO")
        print("   - Auto-reload en cambios de código")
        print("   - Debugger interactivo en errores")
        print("   - Información detallada de errores")
    else:
        print("🔒 Modo Producción ACTIVADO")
        print("   - Debug desactivado")
        print("   - Logs optimizados")
        print("   - Rendimiento optimizado")

    print("=" * 60)


def main():
    """Función principal."""
    # Parsear argumentos
    args = parse_arguments()

    # Verificar entorno
    if not check_environment():
        sys.exit(1)

    # Determinar configuración
    production_mode = args.prod or os.environ.get('FLASK_ENV') == 'production'
    config_class = get_config_class(production_mode)

    # Determinar modo debug
    debug_mode = False
    if args.debug:
        debug_mode = True
    elif not production_mode:
        debug_mode = True

    try:
        # Crear aplicación
        print("🔄 Creando aplicación Flask...")
        app = create_app(config_class)

        # Mostrar información de inicio
        display_startup_info(app, args.host, args.port, debug_mode)

        # Verificar directorio de instancia
        instance_path = Path(app.instance_path)
        if not instance_path.exists():
            print(f"📁 Creando directorio de instancia: {instance_path}")
            instance_path.mkdir(parents=True, exist_ok=True)

        # Ejecutar aplicación
        app.run(
            host=args.host,
            port=args.port,
            debug=debug_mode,
            threaded=True,
            use_reloader=debug_mode
        )

    except Exception as e:
        print(f"❌ Error al iniciar la aplicación: {e}")
        if debug_mode:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    # Configurar variables de entorno si no están definidas
    if not os.environ.get('FLASK_SECRET_KEY'):
        print("⚠️  FLASK_SECRET_KEY no definida, usando clave temporal")
        print("   Para producción, define esta variable en tu archivo .env")
        os.environ['FLASK_SECRET_KEY'] = 'dev-key-change-in-production'

    main()
