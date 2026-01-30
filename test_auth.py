#!/usr/bin/env python3
"""
Script de prueba para verificar la autenticación mejorada
"""

import os
import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_auth_config():
    """Probar la configuración de autenticación"""
    try:
        from app import create_app
        from config.config import DevelopmentConfig
        
        print("=== PRUEBA DE CONFIGURACIÓN DE AUTENTICACIÓN ===")
        
        # Crear aplicación
        app = create_app(DevelopmentConfig)
        
        with app.app_context():
            print(f"✅ SECRET_KEY: {app.config['SECRET_KEY'][:20]}...")
            print(f"✅ SESSION_PERMANENT: {app.config.get('SESSION_PERMANENT', False)}")
            print(f"✅ PERMANENT_SESSION_LIFETIME: {app.config.get('PERMANENT_SESSION_LIFETIME', 'No configurado')}")
            
            # Probar conexión a base de datos
            from app.models import db
            from sqlalchemy import text
            
            result = db.session.execute(
                text('SELECT COUNT(*) as count FROM users WHERE username = :username'), 
                {'username': 'admin'}
            ).fetchone()
            
            if result and result[0] > 0:
                print("✅ Usuario admin encontrado en la base de datos")
            else:
                print("❌ Usuario admin no encontrado")
            
            print("\n🎯 CONFIGURACIÓN CORRECTA")
            return True
            
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_server():
    """Iniciar servidor de prueba"""
    try:
        from app import create_app
        from config.config import DevelopmentConfig
        
        app = create_app(DevelopmentConfig)
        
        print("\n=== INICIANDO SERVIDOR DE PRUEBA ===")
        print("🌐 URL: http://127.0.0.1:5003")
        print("👤 Usuario: admin")
        print("🔑 Contraseña: admin")
        print("\nPresiona Ctrl+C para detener\n")
        
        # Configurar para producción local
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        
        # Iniciar servidor
        app.run(
            host='127.0.0.1',
            port=5003,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Probar configuración primero
    if test_auth_config():
        # Si la configuración es correcta, iniciar servidor
        start_server()
    else:
        print("❌ No se puede iniciar el servidor debido a errores de configuración")
        sys.exit(1)
