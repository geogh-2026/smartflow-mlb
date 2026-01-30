#!/usr/bin/env python3
"""
Script para aplicar la migración tipo_insumo en producción
"""

import os
import sys
import sqlite3
from datetime import datetime

def apply_tipo_insumo_migration():
    """Aplicar la migración de tipo_insumo a la base de datos de producción"""
    
    # Determinar la ruta de la base de datos de producción
    production_db_paths = [
        'instance/oleoflores_prod.db',
        'instance/oleoflores_dev.db',  # Fallback para desarrollo
        'oleoflores_prod.db',
        'tiquetes.db'
    ]
    
    db_path = None
    for path in production_db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ No se encontró la base de datos de producción")
        print("Rutas buscadas:")
        for path in production_db_paths:
            print(f"   - {path}")
        return False
    
    print(f"🗄️ Usando base de datos: {db_path}")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='enturnamientos_graneles'
        """)
        
        if not cursor.fetchone():
            print("❌ La tabla 'enturnamientos_graneles' no existe")
            return False
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(enturnamientos_graneles)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'tipo_insumo' in columns:
            print("✅ La columna 'tipo_insumo' ya existe en la tabla")
            return True
        
        print("🔧 Aplicando migración: agregando columna 'tipo_insumo'")
        
        # Crear backup antes de la migración
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"💾 Backup creado: {backup_path}")
        
        # Agregar la columna tipo_insumo
        cursor.execute("""
            ALTER TABLE enturnamientos_graneles 
            ADD COLUMN tipo_insumo TEXT DEFAULT 'Granel'
        """)
        
        # Actualizar registros existentes para que tengan 'Granel' como valor por defecto
        cursor.execute("""
            UPDATE enturnamientos_graneles 
            SET tipo_insumo = 'Granel' 
            WHERE tipo_insumo IS NULL
        """)
        
        # Confirmar cambios
        conn.commit()
        
        # Verificar que la migración fue exitosa
        cursor.execute("PRAGMA table_info(enturnamientos_graneles)")
        columns_after = [column[1] for column in cursor.fetchall()]
        
        if 'tipo_insumo' in columns_after:
            print("✅ Migración aplicada exitosamente")
            
            # Mostrar estadísticas
            cursor.execute("SELECT COUNT(*) FROM enturnamientos_graneles")
            total_records = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM enturnamientos_graneles WHERE tipo_insumo = 'Granel'")
            granel_records = cursor.fetchone()[0]
            
            print(f"📊 Estadísticas:")
            print(f"   - Total de registros: {total_records}")
            print(f"   - Registros con tipo 'Granel': {granel_records}")
            
            return True
        else:
            print("❌ Error: La columna no se agregó correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error aplicando migración: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def verify_migration():
    """Verificar que la migración se aplicó correctamente"""
    print("\n🔍 Verificando migración...")
    
    production_db_paths = [
        'instance/oleoflores_prod.db',
        'instance/oleoflores_dev.db',
        'oleoflores_prod.db',
        'tiquetes.db'
    ]
    
    for db_path in production_db_paths:
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Verificar estructura de la tabla
                cursor.execute("PRAGMA table_info(enturnamientos_graneles)")
                columns = cursor.fetchall()
                
                print(f"\n📋 Estructura de tabla en {db_path}:")
                for col in columns:
                    col_name = col[1]
                    col_type = col[2]
                    col_default = col[4] if col[4] else 'NULL'
                    marker = "✅" if col_name == 'tipo_insumo' else "  "
                    print(f"   {marker} {col_name} ({col_type}) - Default: {col_default}")
                
                conn.close()
                
            except Exception as e:
                print(f"❌ Error verificando {db_path}: {e}")

def main():
    """Función principal"""
    print("🚀 Aplicando migración tipo_insumo en producción")
    print("=" * 50)
    
    # Aplicar migración
    success = apply_tipo_insumo_migration()
    
    if success:
        print("\n🎉 ¡Migración aplicada exitosamente!")
        
        # Verificar migración
        verify_migration()
        
        print("\n📋 Próximos pasos:")
        print("   1. Reiniciar la aplicación en producción")
        print("   2. Probar el enturnamiento unificado")
        print("   3. Verificar que no hay más errores de 'tipo_insumo'")
        
    else:
        print("\n❌ Error aplicando la migración")
        print("   - Revisar los logs de error")
        print("   - Verificar permisos de la base de datos")
        print("   - Contactar al administrador si es necesario")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
