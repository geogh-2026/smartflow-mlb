#!/usr/bin/env python3
"""
Migración: Agregar columnas de roles a tabla users

Este script agrega las columnas is_admin y user_role a la tabla users
existente para soportar el sistema de roles.

Uso:
    python migrations/add_user_roles.py
"""

import sqlite3
import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_db_path():
    """Obtener la ruta de la base de datos."""
    # Buscar en diferentes ubicaciones posibles
    possible_paths = [
        'instance/oleoflores_dev.db',
        'instance/tiquetes.db',
        'tiquetes.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Si no existe, usar la por defecto
    return 'instance/oleoflores_dev.db'

def check_column_exists(conn, table_name, column_name):
    """Verificar si una columna existe en una tabla."""
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def migrate_user_roles():
    """Ejecutar la migración de roles de usuario."""
    db_path = get_db_path()
    print(f"🔄 Iniciando migración en: {db_path}")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la tabla users existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ La tabla 'users' no existe. Asegúrate de que la base de datos esté inicializada.")
            return False
        
        print("✅ Tabla 'users' encontrada")
        
        # Verificar y agregar columna is_admin
        if not check_column_exists(conn, 'users', 'is_admin'):
            print("🔧 Agregando columna 'is_admin'...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
            print("✅ Columna 'is_admin' agregada")
        else:
            print("ℹ️  Columna 'is_admin' ya existe")
        
        # Verificar y agregar columna user_role
        if not check_column_exists(conn, 'users', 'user_role'):
            print("🔧 Agregando columna 'user_role'...")
            cursor.execute("ALTER TABLE users ADD COLUMN user_role TEXT DEFAULT 'guarda'")
            print("✅ Columna 'user_role' agregada")
        else:
            print("ℹ️  Columna 'user_role' ya existe")
        
        # Actualizar usuarios existentes
        print("🔧 Actualizando usuarios existentes...")
        
        # Establecer el primer usuario como admin si no hay admins
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print("🛡️  No hay administradores. Convirtiendo al primer usuario en admin...")
            cursor.execute("""
                UPDATE users 
                SET is_admin = 1, user_role = 'admin' 
                WHERE id = (SELECT MIN(id) FROM users)
            """)
            cursor.execute("SELECT username FROM users WHERE is_admin = 1 LIMIT 1")
            admin_user = cursor.fetchone()
            if admin_user:
                print(f"✅ Usuario '{admin_user[0]}' establecido como administrador")
        else:
            print(f"ℹ️  Ya existen {admin_count} administrador(es)")
        
        # Establecer role 'guarda' para usuarios sin rol específico
        cursor.execute("UPDATE users SET user_role = 'guarda' WHERE user_role IS NULL OR user_role = ''")
        
        # Confirmar cambios
        conn.commit()
        
        # Mostrar resumen
        cursor.execute("""
            SELECT user_role, COUNT(*) as count 
            FROM users 
            GROUP BY user_role 
            ORDER BY user_role
        """)
        roles_summary = cursor.fetchall()
        
        print("\n📊 Resumen de usuarios por rol:")
        for role, count in roles_summary:
            print(f"   - {role}: {count} usuario(s)")
        
        conn.close()
        print("\n✅ Migración completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def main():
    """Función principal."""
    print("=" * 60)
    print("🔧 MIGRACIÓN: Agregar Roles de Usuario")
    print("=" * 60)
    
    if migrate_user_roles():
        print("\n🎉 ¡Migración completada con éxito!")
        print("\nAhora puedes:")
        print("1. Acceder al sistema con tu usuario")
        print("2. Si eres admin, verás el botón 'Admin' en el home")
        print("3. Desde allí puedes gestionar usuarios y roles")
    else:
        print("\n💥 La migración falló. Revisa los errores arriba.")
        sys.exit(1)

if __name__ == '__main__':
    main() 