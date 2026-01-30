#!/usr/bin/env python3
"""
Script para corregir estructura de tabla users - PythonAnywhere
Oleoflores Smart Flow
"""

import sqlite3
import os
import sys

# Configuración de rutas
BASE_DIR = '/home/enriquepabon/oleoflores-smart-flow'  # Ajustar según tu ruta
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
PROD_DB_PATH = os.path.join(INSTANCE_DIR, 'oleoflores_prod.db')

def analyze_current_structure():
    """Analizar la estructura actual de la tabla users"""
    print("🔍 ANALIZANDO ESTRUCTURA ACTUAL")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(PROD_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar si existe la tabla users
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users'
        """)
        
        if not cursor.fetchone():
            print("❌ Tabla 'users' no existe")
            conn.close()
            return False
        
        # Obtener estructura actual
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("📋 Columnas actuales:")
        current_columns = {}
        for col in columns:
            current_columns[col['name']] = col['type']
            nullable = "NULLABLE" if not col['notnull'] else "NOT NULL"
            default = f" DEFAULT {col['dflt_value']}" if col['dflt_value'] else ""
            pk = " (PRIMARY KEY)" if col['pk'] else ""
            print(f"   - {col['name']}: {col['type']} {nullable}{default}{pk}")
        
        # Verificar columnas faltantes
        required_columns = {
            'id': 'INTEGER',
            'username': 'VARCHAR(80)',
            'email': 'VARCHAR(120)', 
            'password_hash': 'VARCHAR(128)',
            'is_active': 'INTEGER',
            'is_admin': 'INTEGER',
            'user_role': 'VARCHAR(50)',
            'fecha_creacion': 'DATETIME',
            'last_login': 'TIMESTAMP'
        }
        
        missing_columns = []
        for col_name, col_type in required_columns.items():
            if col_name not in current_columns:
                missing_columns.append((col_name, col_type))
        
        if missing_columns:
            print(f"\n⚠️  COLUMNAS FALTANTES: {len(missing_columns)}")
            for col_name, col_type in missing_columns:
                print(f"   - {col_name}: {col_type}")
        else:
            print("\n✅ Estructura completa")
        
        # Contar usuarios existentes
        cursor.execute("SELECT COUNT(*) as count FROM users")
        count = cursor.fetchone()['count']
        print(f"\n📊 Usuarios existentes: {count}")
        
        conn.close()
        return missing_columns
        
    except Exception as e:
        print(f"❌ Error al analizar estructura: {e}")
        return False

def fix_table_structure(missing_columns):
    """Corregir la estructura de la tabla agregando columnas faltantes"""
    print(f"\n🔧 CORRIGIENDO ESTRUCTURA DE TABLA")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(PROD_DB_PATH)
        cursor = conn.cursor()
        
        for col_name, col_type in missing_columns:
            print(f"➕ Agregando columna: {col_name} ({col_type})")
            
            # Definir valores por defecto según la columna
            default_value = "DEFAULT 0"
            if col_name == 'user_role':
                default_value = "DEFAULT 'guarda'"
            elif col_name == 'fecha_creacion':
                default_value = "DEFAULT CURRENT_TIMESTAMP"
            elif col_name == 'last_login':
                default_value = ""  # Sin valor por defecto para TIMESTAMP
            
            # Agregar columna
            alter_sql = f"ALTER TABLE users ADD COLUMN {col_name} {col_type} {default_value}"
            
            try:
                cursor.execute(alter_sql)
                print(f"   ✅ Columna {col_name} agregada exitosamente")
            except Exception as e:
                print(f"   ❌ Error agregando {col_name}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Estructura corregida exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al corregir estructura: {e}")
        return False

def recreate_table_if_needed():
    """Recrear tabla completamente si es necesario"""
    print(f"\n🏗️  RECREANDO TABLA USERS")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(PROD_DB_PATH)
        cursor = conn.cursor()
        
        # Hacer backup de datos existentes
        cursor.execute("SELECT * FROM users")
        existing_data = cursor.fetchall()
        
        print(f"💾 Respaldando {len(existing_data)} usuarios existentes")
        
        # Eliminar tabla actual
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # Crear tabla con estructura completa
        cursor.execute("""
            CREATE TABLE users (
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
        
        # Restaurar datos existentes
        if existing_data:
            print("📥 Restaurando usuarios existentes...")
            for row in existing_data:
                # Adaptar datos existentes a nueva estructura
                values = list(row)
                # Agregar valores por defecto para columnas faltantes
                while len(values) < 9:  # 9 columnas totales
                    if len(values) == 4:  # is_active
                        values.append(1)  # Activo por defecto
                    elif len(values) == 5:  # is_admin
                        values.append(0)  # No admin por defecto
                    elif len(values) == 6:  # user_role
                        values.append('guarda')  # Rol por defecto
                    elif len(values) == 7:  # fecha_creacion
                        values.append('2025-01-01 00:00:00')  # Fecha por defecto
                    elif len(values) == 8:  # last_login
                        values.append(None)  # Null por defecto
                
                cursor.execute("""
                    INSERT INTO users (id, username, email, password_hash, is_active, 
                                     is_admin, user_role, fecha_creacion, last_login)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values[:9])
        
        # Crear índices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)")
        
        conn.commit()
        conn.close()
        
        print("✅ Tabla recreada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al recrear tabla: {e}")
        return False

def verify_final_structure():
    """Verificar la estructura final"""
    print(f"\n🔍 VERIFICANDO ESTRUCTURA FINAL")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(PROD_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar estructura
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("📋 Estructura final:")
        for col in columns:
            nullable = "NULLABLE" if not col['notnull'] else "NOT NULL"
            default = f" DEFAULT {col['dflt_value']}" if col['dflt_value'] else ""
            pk = " (PRIMARY KEY)" if col['pk'] else ""
            print(f"   ✅ {col['name']}: {col['type']} {nullable}{default}{pk}")
        
        # Verificar usuarios
        cursor.execute("SELECT username, is_active, is_admin, user_role FROM users")
        users = cursor.fetchall()
        
        print(f"\n👥 Usuarios verificados: {len(users)}")
        for user in users[:3]:  # Mostrar primeros 3
            print(f"   - {user['username']}: activo={user['is_active']}, admin={user['is_admin']}, rol={user['user_role']}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

def main():
    """Función principal"""
    print("🌟 CORRECCIÓN DE ESTRUCTURA DE TABLA USERS")
    print("🌟 PythonAnywhere - Oleoflores Smart Flow")
    print("=" * 60)
    
    # Analizar estructura actual
    missing_columns = analyze_current_structure()
    
    if missing_columns is False:
        print("❌ Error en análisis inicial")
        sys.exit(1)
    
    if not missing_columns:
        print("✅ La estructura ya está completa")
        verify_final_structure()
        return
    
    # Preguntar método de corrección
    print(f"\n🔧 Se encontraron {len(missing_columns)} columnas faltantes")
    print("Opciones:")
    print("1. Agregar columnas faltantes (recomendado)")
    print("2. Recrear tabla completa")
    
    choice = input("\nSeleccione opción (1-2): ").strip()
    
    if choice == '1':
        if fix_table_structure(missing_columns):
            verify_final_structure()
            print("\n🎉 ¡Corrección completada! Ahora ejecute create_users_pythonanywhere.py")
        else:
            print("\n❌ Error en corrección")
    
    elif choice == '2':
        confirm = input("⚠️  ¿Confirma recrear tabla completa? (s/n): ").strip().lower()
        if confirm in ['s', 'si', 'sí']:
            if recreate_table_if_needed():
                verify_final_structure()
                print("\n🎉 ¡Tabla recreada! Ahora ejecute create_users_pythonanywhere.py")
            else:
                print("\n❌ Error en recreación")
        else:
            print("❌ Operación cancelada")
    
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    main() 