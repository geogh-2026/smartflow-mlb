#!/usr/bin/env python
"""
Script para limpiar la tabla de usuarios después del cambio de bcrypt a werkzeug.security
"""

import sys
import os

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import User, db
from config.config import DevelopmentConfig

def clean_users_table():
    """Limpia la tabla de usuarios para permitir recrear con nuevo sistema de hash"""
    
    app = create_app(DevelopmentConfig)
    
    with app.app_context():
        try:
            # Contar usuarios existentes
            user_count = User.query.count()
            print(f"📊 Usuarios encontrados: {user_count}")
            
            if user_count > 0:
                print("🗑️  Eliminando usuarios existentes (hashes incompatibles)...")
                
                # Eliminar todos los usuarios
                User.query.delete()
                db.session.commit()
                
                print("✅ Tabla de usuarios limpiada exitosamente")
                print("🔄 Ahora puedes registrar nuevos usuarios con el sistema de hash corregido")
            else:
                print("ℹ️  No hay usuarios para limpiar")
                
        except Exception as e:
            print(f"❌ Error al limpiar tabla de usuarios: {e}")
            db.session.rollback()
            return False
            
    return True

if __name__ == '__main__':
    print("🧹 Limpiando tabla de usuarios...")
    if clean_users_table():
        print("✅ Proceso completado")
    else:
        print("❌ Error en el proceso")
        sys.exit(1) 