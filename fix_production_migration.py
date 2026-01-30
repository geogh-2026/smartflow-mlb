#!/usr/bin/env python3
"""
Script simple para agregar la columna tipo_insumo en producción
EJECUTAR EN EL SERVIDOR DE PRODUCCIÓN
"""

import sqlite3
import os
from datetime import datetime

def fix_production_db():
    """Agregar columna tipo_insumo a la base de datos de producción"""
    
    # Buscar la base de datos de producción
    possible_paths = [
        '/home/enriquepabon/mysite/instance/oleoflores_prod.db',
        '/home/enriquepabon/mysite/tiquetes.db',
        'instance/oleoflores_prod.db',
        'tiquetes.db',
        'oleoflores_prod.db'
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ No se encontró la base de datos")
        return False
    
    print(f"🗄️ Base de datos encontrada: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(enturnamientos_graneles)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'tipo_insumo' in columns:
            print("✅ La columna 'tipo_insumo' ya existe")
            return True
        
        # Crear backup
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"💾 Backup: {backup_path}")
        
        # Agregar columna
        cursor.execute("""
            ALTER TABLE enturnamientos_graneles 
            ADD COLUMN tipo_insumo TEXT DEFAULT 'Granel'
        """)
        
        # Actualizar registros existentes
        cursor.execute("""
            UPDATE enturnamientos_graneles 
            SET tipo_insumo = 'Granel' 
            WHERE tipo_insumo IS NULL
        """)
        
        conn.commit()
        print("✅ Columna 'tipo_insumo' agregada exitosamente")
        
        # Verificar
        cursor.execute("SELECT COUNT(*) FROM enturnamientos_graneles")
        total = cursor.fetchone()[0]
        print(f"📊 Total registros actualizados: {total}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔧 Aplicando corrección de migración en producción...")
    success = fix_production_db()
    if success:
        print("🎉 ¡Corrección aplicada! Reinicia la aplicación.")
    else:
        print("❌ Error aplicando corrección.")
