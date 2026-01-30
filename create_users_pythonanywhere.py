#!/usr/bin/env python3
"""
Script para crear usuarios en PythonAnywhere - Oleoflores Smart Flow
Ejecutar ÚNICAMENTE en el servidor PythonAnywhere
"""

import sqlite3
import os
import sys
from datetime import datetime

# Configuración de rutas para PythonAnywhere
# IMPORTANTE: Ajustar esta ruta según tu configuración en PythonAnywhere
BASE_DIR = '/home/enriquepabon/oleoflores-smart-flow'  # ⚠️ CAMBIAR por tu ruta real en PythonAnywhere
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
PROD_DB_PATH = os.path.join(INSTANCE_DIR, 'oleoflores_prod.db')

# Usuarios con sus password_hash ORIGINALES de desarrollo
USUARIOS_MIGRADOS = [
    {
        'username': 'admin',
        'email': 'admin@oleoflores.com',
        'password_hash': 'pbkdf2:sha256:600000$sLCs7PotT4BT1OGn$3c13dd22cdc63008345511d72f82f0d21f638d17b5f2e80d660a09b77b705237',
        'is_active': 1,
        'is_admin': 1,
        'user_role': 'admin',
        'fecha_creacion': '2025-07-25 23:21:56.008168'
    },
    {
        'username': 'epabon',
        'email': 'epabon@oleoflores.com',
        'password_hash': 'pbkdf2:sha256:600000$kO7Fpb9b8XQrFhup$6834b85ac4f38b9d1ec71228773789f953306d594c13279740e986cdba5e200a',
        'is_active': 1,
        'is_admin': 1,
        'user_role': 'admin',
        'fecha_creacion': '2025-04-30 15:52:39'
    },
    {
        'username': 'Jbossa',
        'email': 'jbossa@oleoflores.com',
        'password_hash': 'pbkdf2:sha256:600000$HnHf9wU1ZWX7qaad$2be37b4f8d516082d67566d2bd5b02520cc428088a31c0b24ed7cb04a36385d8',
        'is_active': 1,
        'is_admin': 0,
        'user_role': 'guarda',
        'fecha_creacion': '2025-04-30 15:56:43'
    },
    {
        'username': 'dperez',
        'email': 'recepcionmlb@oleoflores.com',
        'password_hash': 'pbkdf2:sha256:600000$Dsoms2WQblmkJq4v$e07be0ae94d44eb73572078b4dfbc38b4a0bc99a6d08a1f737e4d0e46220362c',
        'is_active': 1,
        'is_admin': 0,
        'user_role': 'recepcion',
        'fecha_creacion': '2025-04-30 15:56:49'
    },
    {
        'username': 'vigilancia',
        'email': 'recepcionmlb_1@oleoflores.com',
        'password_hash': 'pbkdf2:sha256:600000$ZVJGDUdMBgaUQQbm$7386705e17b790cdcf44458c7e7190b8ac4a5de9c7b1c5dca4011ef5812421aa',
        'is_active': 1,
        'is_admin': 0,
        'user_role': 'guarda',
        'fecha_creacion': '2025-04-30 15:58:12'
    },
    {
        'username': 'mjimenez',
        'email': 'mjimenez@oleoflores.com',
        'password_hash': 'pbkdf2:sha256:600000$z2KDqOwFTSpdIiWJ$d18f34f2afcdc20695c637cf95610608c4b622129010ed06c579d26b055ee6e2',
        'is_active': 1,
        'is_admin': 0,
        'user_role': 'guarda',
        'fecha_creacion': '2025-04-30 15:59:07'
    },
    {
        'username': 'kpadilla',
        'email': 'basculamlb@oleoflores.com',
        'password_hash': 'pbkdf2:sha256:600000$nJfNR9IItjRPIdrp$0c45c0c70eba43c323529c66f9b18382b028c8a8d4d5b091c457c2afb305b104',
        'is_active': 1,
        'is_admin': 0,
        'user_role': 'basculero',
        'fecha_creacion': '2025-04-30 19:16:11'
    },
    {
        'username': 'jtroconis',
        'email': 'calidadmlb@oleoflores.com',
        'password_hash': 'pbkdf2:sha256:600000$ssnh8CPurNtveAXe$d53579dae12eb42a0c5d0ed37a14a8af6fb20e4cbc319c2b92b87df6ba9cc329',
        'is_active': 1,
        'is_admin': 0,
        'user_role': 'clasificacion_fruta',
        'fecha_creacion': '2025-04-30 19:18:06'
    },
    {
        'username': 'kimpadilla',
        'email': 'basculamln@oleoflores.com',
        'password_hash': 'pbkdf2:sha256:600000$vFi6MniKWklDazYZ$525f77c8aaca9b06b8dbbaeaaa545f5ba3923e7320b9daf4707a8f5dfbba5e0d',
        'is_active': 1,
        'is_admin': 0,
        'user_role': 'basculero',
        'fecha_creacion': '2025-05-02 13:00:23'
    },
    {
        'username': 'bcaraballo',
        'email': 'basculambl1@oleflores.com',
        'password_hash': 'pbkdf2:sha256:600000$rkZvYGTNHF7tcEYl$b24f971b0d59a2bd79996286aaaf63d0274ebb0f0343db028b22990e3aa7ee13',
        'is_active': 1,
        'is_admin': 0,
        'user_role': 'basculero',
        'fecha_creacion': '2025-05-03 17:05:30'
    }
]

def check_environment():
    """Verificar que estamos en PythonAnywhere"""
    print("🔍 VERIFICANDO ENTORNO")
    print("=" * 50)
    
    print(f"📂 Directorio base: {BASE_DIR}")
    print(f"📂 Directorio instance: {INSTANCE_DIR}")
    print(f"🗄️  Ruta BD producción: {PROD_DB_PATH}")
    
    # Verificar si estamos en PythonAnywhere
    hostname = os.uname().nodename if hasattr(os, 'uname') else 'unknown'
    print(f"🖥️  Hostname: {hostname}")
    
    if 'pythonanywhere' not in hostname.lower():
        print("⚠️  ADVERTENCIA: No parece ser PythonAnywhere")
        response = input("¿Continuar de todos modos? (s/n): ")
        if response.lower() not in ['s', 'si', 'sí']:
            return False
    
    return True

def create_database_structure():
    """Crear la estructura de base de datos si no existe"""
    print("\n🏗️  CREANDO ESTRUCTURA DE BASE DE DATOS")
    print("=" * 50)
    
    try:
        # Asegurar que el directorio existe
        os.makedirs(INSTANCE_DIR, exist_ok=True)
        print(f"✅ Directorio creado: {INSTANCE_DIR}")
        
        conn = sqlite3.connect(PROD_DB_PATH)
        cursor = conn.cursor()
        
        # Crear tabla users con estructura completa
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(128) NOT NULL,
                is_active INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0,
                user_role VARCHAR(50) DEFAULT 'guarda',
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Crear otras tablas necesarias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS presupuesto_mensual (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_presupuesto VARCHAR(10) UNIQUE NOT NULL,
                toneladas_proyectadas REAL,
                fecha_carga DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validaciones_diarias_sap (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_aplicable_validacion TEXT,
                timestamp_creacion_utc TEXT,
                peso_neto_total_validado REAL,
                mensaje_webhook TEXT,
                exito_webhook INTEGER,
                ruta_foto_validacion TEXT,
                filtros_aplicados_json TEXT,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crear índices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)")
        
        conn.commit()
        conn.close()
        
        print("✅ Base de datos creada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear base de datos: {e}")
        return False

def migrate_users():
    """Migrar usuarios con sus hashes originales"""
    print("\n👥 MIGRANDO USUARIOS A PYTHONANYWHERE")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(PROD_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar usuarios existentes
        cursor.execute("SELECT username FROM users")
        existing_users = {row['username'] for row in cursor.fetchall()}
        
        created_count = 0
        skipped_count = 0
        
        for user_data in USUARIOS_MIGRADOS:
            username = user_data['username']
            
            if username in existing_users:
                print(f"⏭️  Usuario '{username}' ya existe - omitiendo")
                skipped_count += 1
                continue
            
            # Insertar usuario con hash original
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, is_active, 
                                 is_admin, user_role, fecha_creacion, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
            """, (
                user_data['username'],
                user_data['email'],
                user_data['password_hash'],
                user_data['is_active'],
                user_data['is_admin'],
                user_data['user_role'],
                user_data['fecha_creacion']
            ))
            
            print(f"✅ Usuario '{username}' migrado ({user_data['user_role']})")
            created_count += 1
        
        conn.commit()
        conn.close()
        
        # Resumen
        print(f"\n📊 RESUMEN:")
        print(f"✅ Usuarios creados: {created_count}")
        print(f"⏭️  Usuarios existentes: {skipped_count}")
        
        return created_count > 0
        
    except Exception as e:
        print(f"❌ Error al migrar usuarios: {e}")
        return False

def verify_users():
    """Verificar usuarios creados"""
    print("\n🔍 VERIFICANDO USUARIOS CREADOS")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(PROD_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT username, email, is_active, is_admin, user_role
            FROM users
            ORDER BY id
        """)
        
        users = cursor.fetchall()
        conn.close()
        
        print(f"{'Username':<15} {'Email':<30} {'Activo':<7} {'Admin':<6} {'Rol':<15}")
        print("-" * 80)
        
        for user in users:
            active_status = "✅ Sí" if user['is_active'] else "❌ No"
            admin_status = "👑 Sí" if user['is_admin'] else "👤 No"
            
            print(f"{user['username']:<15} {user['email']:<30} "
                  f"{active_status:<7} {admin_status:<6} {user['user_role'] or 'N/A':<15}")
        
        print(f"\n📊 Total usuarios en PythonAnywhere: {len(users)}")
        
    except Exception as e:
        print(f"❌ Error al verificar usuarios: {e}")

def main():
    """Función principal"""
    print("🌟 MIGRACIÓN DE USUARIOS A PYTHONANYWHERE")
    print("🌟 Oleoflores Smart Flow")
    print("=" * 60)
    
    # Verificar entorno
    if not check_environment():
        sys.exit(1)
    
    # Crear estructura de base de datos
    if not create_database_structure():
        sys.exit(1)
    
    # Migrar usuarios
    if migrate_users():
        verify_users()
        print("\n🎉 ¡Migración a PythonAnywhere completada!")
        print("\n💡 Los usuarios pueden loggearse con sus contraseñas originales")
    else:
        print("\n⚠️  No se crearon usuarios nuevos (posiblemente ya existen)")
        verify_users()

if __name__ == "__main__":
    main() 