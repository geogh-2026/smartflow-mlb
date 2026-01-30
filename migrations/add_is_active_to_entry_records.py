#!/usr/bin/env python3
"""
Migración: Agregar columna is_active a tabla entry_records

Este script agrega la columna is_active a la tabla entry_records
para permitir que los admins puedan inactivar guías.

Uso:
    python migrations/add_is_active_to_entry_records.py
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

def migrate_is_active_column():
    """Ejecutar la migración para agregar columna is_active."""
    db_path = get_db_path()
    print(f"🔄 Iniciando migración en: {db_path}")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la tabla entry_records existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entry_records'")
        if not cursor.fetchone():
            print("❌ La tabla 'entry_records' no existe. Asegúrate de que la base de datos esté inicializada.")
            return False
        
        print("✅ Tabla 'entry_records' encontrada")
        
        # Verificar si la columna is_active ya existe
        if check_column_exists(conn, 'entry_records', 'is_active'):
            print("ℹ️  La columna 'is_active' ya existe en entry_records")
            
            # Verificar si hay valores NULL y actualizarlos
            cursor.execute("SELECT COUNT(*) FROM entry_records WHERE is_active IS NULL")
            null_count = cursor.fetchone()[0]
            
            if null_count > 0:
                print(f"🔧 Actualizando {null_count} registros con is_active NULL...")
                cursor.execute("UPDATE entry_records SET is_active = 1 WHERE is_active IS NULL")
                conn.commit()
                print(f"✅ {null_count} registros actualizados a is_active = 1")
            
        else:
            print("🔧 Agregando columna 'is_active' a entry_records...")
            cursor.execute("ALTER TABLE entry_records ADD COLUMN is_active INTEGER DEFAULT 1")
            print("✅ Columna 'is_active' agregada exitosamente")
            
            # Confirmar que todos los registros existentes tengan is_active = 1
            cursor.execute("UPDATE entry_records SET is_active = 1 WHERE is_active IS NULL")
            conn.commit()
            print("✅ Todos los registros existentes marcados como activos")
        
        # Mostrar estadísticas
        cursor.execute("SELECT COUNT(*) FROM entry_records WHERE is_active = 1")
        active_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM entry_records WHERE is_active = 0")
        inactive_count = cursor.fetchone()[0]
        
        print("\n📊 Estadísticas de entry_records:")
        print(f"   - Registros activos: {active_count}")
        print(f"   - Registros inactivos: {inactive_count}")
        print(f"   - Total: {active_count + inactive_count}")
        
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
    print("=" * 70)
    print("🔧 MIGRACIÓN: Agregar columna is_active a entry_records")
    print("=" * 70)
    
    if migrate_is_active_column():
        print("\n🎉 ¡Migración completada con éxito!")
        print("\nAhora los administradores pueden:")
        print("1. Inactivar guías desde el dashboard de fruta")
        print("2. Reactivar guías previamente inactivadas")
        print("3. Ver el estado visual de cada guía")
        print("\n🔄 Reinicia el servidor Flask para aplicar los cambios")
    else:
        print("\n💥 La migración falló. Revisa los errores arriba.")
        sys.exit(1)

if __name__ == '__main__':
    main() 