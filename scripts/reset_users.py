#!/usr/bin/env python3
"""
Script para eliminar todos los usuarios y crear uno nuevo administrador.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from werkzeug.security import generate_password_hash
import sqlite3
from datetime import datetime

def reset_users():
    """Eliminar todos los usuarios y crear uno nuevo."""
    
    # Conectar a la base de datos
    db_path = project_root / 'instance' / 'oleoflores_dev.db'
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Mostrar usuarios actuales
            cursor.execute("SELECT id, username, email FROM users")
            usuarios_actuales = cursor.fetchall()
            
            print("👥 Usuarios actuales:")
            for user in usuarios_actuales:
                print(f"   ID: {user[0]}, Usuario: {user[1]}, Email: {user[2]}")
            
            # Confirmar eliminación
            respuesta = input("\n¿Eliminar TODOS los usuarios? (y/N): ").strip().lower()
            if respuesta not in ['y', 'yes', 'sí', 'si']:
                print("❌ Operación cancelada")
                return False
            
            # Eliminar todos los usuarios
            cursor.execute("DELETE FROM users")
            print("🗑️ Todos los usuarios eliminados")
            
            # Crear nuevo usuario administrador
            username = "admin"
            email = "admin@oleoflores.com"
            password = "123456"
            
            password_hash = generate_password_hash(password)
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, is_active, fecha_creacion)
                VALUES (?, ?, ?, 1, ?)
            """, (username, email, password_hash, datetime.utcnow()))
            
            conn.commit()
            
            print(f"\n✅ Nuevo usuario administrador creado:")
            print(f"👤 Usuario: {username}")
            print(f"📧 Email: {email}")
            print(f"🔑 Contraseña: {password}")
            print(f"🌐 URL: http://127.0.0.1:5002/")
            print(f"\n🚀 Ya puedes iniciar sesión con estas credenciales")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Reset de Usuarios del Sistema")
    print("=" * 50)
    reset_users() 