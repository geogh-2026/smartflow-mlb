#!/usr/bin/env python3
"""
Fix: Agregar columna is_active a entry_records en producción
"""

import sqlite3
import os
import sys

def fix_entry_records():
    """Agregar columna is_active a entry_records si no existe"""
    
    print("🔧 FIX: Agregar is_active a entry_records en producción")
    print("=" * 60)
    
    # Base de datos de producción según el análisis
    db_path = 'instance/oleoflores_prod.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si entry_records existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entry_records'")
        if not cursor.fetchone():
            print("❌ Tabla entry_records no existe")
            return False
        
        print("✅ Tabla entry_records encontrada")
        
        # Verificar si columna is_active existe
        cursor.execute("PRAGMA table_info(entry_records)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'is_active' in columns:
            print("ℹ️  Columna is_active ya existe")
            
            # Verificar valores actuales
            cursor.execute("SELECT COUNT(*) FROM entry_records WHERE is_active IS NULL")
            null_count = cursor.fetchone()[0]
            
            if null_count > 0:
                print(f"🔧 Actualizando {null_count} registros con is_active = NULL")
                cursor.execute("UPDATE entry_records SET is_active = 1 WHERE is_active IS NULL")
                conn.commit()
                print("✅ Registros actualizados")
        else:
            print("🔧 Agregando columna is_active...")
            cursor.execute("ALTER TABLE entry_records ADD COLUMN is_active INTEGER DEFAULT 1")
            conn.commit()
            print("✅ Columna is_active agregada")
            
            # Actualizar registros existentes
            cursor.execute("UPDATE entry_records SET is_active = 1 WHERE is_active IS NULL")
            conn.commit()
            print("✅ Registros existentes actualizados")
        
        # Mostrar estadísticas finales
        cursor.execute("SELECT COUNT(*) FROM entry_records")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM entry_records WHERE is_active = 1")
        active = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM entry_records WHERE is_active = 0")
        inactive = cursor.fetchone()[0]
        
        print(f"\n📊 Estadísticas finales:")
        print(f"   Total registros: {total}")
        print(f"   Activos: {active}")
        print(f"   Inactivos: {inactive}")
        
        # Mostrar algunos códigos de guía para verificar
        cursor.execute("SELECT codigo_guia, is_active FROM entry_records LIMIT 3")
        registros = cursor.fetchall()
        
        print(f"\n📋 Muestra de registros:")
        for codigo, estado in registros:
            print(f"   {codigo}: {'Activo' if estado == 1 else 'Inactivo'}")
        
        conn.close()
        print("\n✅ FIX COMPLETADO EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = fix_entry_records()
    sys.exit(0 if success else 1) 