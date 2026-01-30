#!/usr/bin/env python3
"""
Script para crear un usuario administrador en el sistema.
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

def crear_usuario_admin():
    """Crear un usuario administrador."""
    
    # Datos del nuevo usuario
    username = input("Nombre de usuario: ").strip()
    email = input("Email: ").strip()
    password = input("Contraseña: ").strip()
    
    if not username or not email or not password:
        print("❌ Todos los campos son obligatorios")
        return False
    
    # Generar hash de la contraseña
    password_hash = generate_password_hash(password)
    
    # Conectar a la base de datos
    db_path = project_root / 'instance' / 'oleoflores_dev.db'
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Verificar si el usuario ya existe
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                print(f"❌ El usuario '{username}' o email '{email}' ya existe")
                return False
            
            # Insertar nuevo usuario
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, is_active, fecha_creacion)
                VALUES (?, ?, ?, 1, ?)
            """, (username, email, password_hash, datetime.utcnow()))
            
            conn.commit()
            
            print(f"✅ Usuario '{username}' creado exitosamente")
            print(f"📧 Email: {email}")
            print(f"🔑 Contraseña: {password}")
            print(f"🌐 URL: http://127.0.0.1:5002/")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Crear Usuario Administrador")
    print("=" * 40)
    crear_usuario_admin() 