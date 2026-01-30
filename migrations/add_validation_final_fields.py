#!/usr/bin/env python3
"""
Migración: Agregar campos para validación final de sellos
Fecha: 2025-08-20
Descripción: Agrega campos fecha_validacion_final, usuario_validacion_final y foto_validacion_final a la tabla sellos
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Ejecutar la migración para agregar campos de validación final."""
    
    # Ruta a la base de datos
    db_path = os.path.join('instance', 'oleoflores_dev.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada en: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Iniciando migración: Agregar campos de validación final...")
        
        # Verificar si la tabla sellos existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='sellos'
        """)
        
        if not cursor.fetchone():
            print("❌ Tabla 'sellos' no encontrada")
            return False
        
        # Verificar si los campos ya existen
        cursor.execute("PRAGMA table_info(sellos)")
        columns = [row[1] for row in cursor.fetchall()]
        
        fields_to_add = [
            ('fecha_validacion_final', 'DATETIME'),
            ('usuario_validacion_final', 'VARCHAR(100)'),
            ('foto_validacion_final', 'TEXT')
        ]
        
        for field_name, field_type in fields_to_add:
            if field_name not in columns:
                print(f"➕ Agregando campo: {field_name}")
                cursor.execute(f"""
                    ALTER TABLE sellos 
                    ADD COLUMN {field_name} {field_type}
                """)
            else:
                print(f"✅ Campo {field_name} ya existe")
        
        # Confirmar cambios
        conn.commit()
        
        # Verificar que los campos se agregaron correctamente
        cursor.execute("PRAGMA table_info(sellos)")
        columns_after = [row[1] for row in cursor.fetchall()]
        
        print("\n📋 Campos en tabla 'sellos' después de la migración:")
        for col in columns_after:
            print(f"   - {col}")
        
        print(f"\n✅ Migración completada exitosamente")
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error en la migración: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
