#!/usr/bin/env python3
"""
Migración: Agregar campo fecha_validacion_final a solicitudes_sello
Fecha: 2025-08-20
Descripción: Agrega campo fecha_validacion_final a la tabla solicitudes_sello
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Ejecutar la migración para agregar campo de fecha de validación final."""
    
    # Ruta a la base de datos
    db_path = os.path.join('instance', 'oleoflores_dev.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada en: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Iniciando migración: Agregar campo fecha_validacion_final a solicitudes_sello...")
        
        # Verificar si la tabla solicitudes_sello existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='solicitudes_sello'
        """)
        
        if not cursor.fetchone():
            print("❌ Tabla 'solicitudes_sello' no encontrada")
            return False
        
        # Verificar si el campo ya existe
        cursor.execute("PRAGMA table_info(solicitudes_sello)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'fecha_validacion_final' not in columns:
            print("➕ Agregando campo: fecha_validacion_final")
            cursor.execute("""
                ALTER TABLE solicitudes_sello 
                ADD COLUMN fecha_validacion_final DATETIME
            """)
        else:
            print("✅ Campo fecha_validacion_final ya existe")
        
        # Confirmar cambios
        conn.commit()
        
        # Verificar que el campo se agregó correctamente
        cursor.execute("PRAGMA table_info(solicitudes_sello)")
        columns_after = [row[1] for row in cursor.fetchall()]
        
        print("\n📋 Campos en tabla 'solicitudes_sello' después de la migración:")
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
