#!/usr/bin/env python3
"""
Migración: Agregar campos para 'Pesaje sin SAP'
Fecha: 2025-01-13
Descripción: Agrega campos foto_bascula_sin_sap_path y peso_sin_sap_kg a las tablas PesajeBrutoGranel y PrimerPesajeGranel
"""

import sqlite3
import sys
import os
from datetime import datetime

def run_migration(db_path):
    """
    Ejecuta la migración para agregar campos de pesaje sin SAP
    
    Args:
        db_path: Ruta a la base de datos SQLite
    """
    print(f"\n{'='*60}")
    print(f"🔄 MIGRACIÓN: Agregar campos Pesaje sin SAP")
    print(f"{'='*60}")
    print(f"Base de datos: {db_path}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if not os.path.exists(db_path):
        print(f"❌ Error: No se encontró la base de datos en {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # ===== TABLA: PesajeBrutoGranel =====
        print("📋 Verificando tabla PesajeBrutoGranel...")
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='PesajeBrutoGranel'
        """)
        
        if not cursor.fetchone():
            print("   ⚠️  Tabla PesajeBrutoGranel no existe, omitiendo...")
        else:
            # Obtener columnas existentes
            cursor.execute("PRAGMA table_info(PesajeBrutoGranel)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Agregar foto_bascula_sin_sap_path si no existe
            if 'foto_bascula_sin_sap_path' not in columns:
                print("   ➕ Agregando columna 'foto_bascula_sin_sap_path'...")
                cursor.execute("""
                    ALTER TABLE PesajeBrutoGranel 
                    ADD COLUMN foto_bascula_sin_sap_path TEXT
                """)
                print("   ✅ Columna 'foto_bascula_sin_sap_path' agregada")
            else:
                print("   ✓  Columna 'foto_bascula_sin_sap_path' ya existe")
            
            # Agregar peso_sin_sap_kg si no existe
            if 'peso_sin_sap_kg' not in columns:
                print("   ➕ Agregando columna 'peso_sin_sap_kg'...")
                cursor.execute("""
                    ALTER TABLE PesajeBrutoGranel 
                    ADD COLUMN peso_sin_sap_kg REAL
                """)
                print("   ✅ Columna 'peso_sin_sap_kg' agregada")
            else:
                print("   ✓  Columna 'peso_sin_sap_kg' ya existe")
        
        # ===== TABLA: PrimerPesajeGranel =====
        print("\n📋 Verificando tabla PrimerPesajeGranel...")
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='PrimerPesajeGranel'
        """)
        
        if not cursor.fetchone():
            print("   ⚠️  Tabla PrimerPesajeGranel no existe, omitiendo...")
        else:
            # Obtener columnas existentes
            cursor.execute("PRAGMA table_info(PrimerPesajeGranel)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Agregar foto_bascula_sin_sap_path si no existe
            if 'foto_bascula_sin_sap_path' not in columns:
                print("   ➕ Agregando columna 'foto_bascula_sin_sap_path'...")
                cursor.execute("""
                    ALTER TABLE PrimerPesajeGranel 
                    ADD COLUMN foto_bascula_sin_sap_path TEXT
                """)
                print("   ✅ Columna 'foto_bascula_sin_sap_path' agregada")
            else:
                print("   ✓  Columna 'foto_bascula_sin_sap_path' ya existe")
            
            # Agregar peso_sin_sap_kg si no existe
            if 'peso_sin_sap_kg' not in columns:
                print("   ➕ Agregando columna 'peso_sin_sap_kg'...")
                cursor.execute("""
                    ALTER TABLE PrimerPesajeGranel 
                    ADD COLUMN peso_sin_sap_kg REAL
                """)
                print("   ✅ Columna 'peso_sin_sap_kg' agregada")
            else:
                print("   ✓  Columna 'peso_sin_sap_kg' ya existe")
        
        # Commit de los cambios
        conn.commit()
        
        print(f"\n{'='*60}")
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print(f"{'='*60}\n")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Error de SQLite: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal para ejecutar la migración"""
    
    # Rutas posibles de la base de datos
    possible_paths = [
        'instance/oleoflores_dev.db',
        'instance/oleoflores_prod.db',
        'instance/oleoflores_smart_flow.db',
        'instance/tiquetes.db'
    ]
    
    # Si se proporciona un argumento, usarlo
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
        if not os.path.exists(db_path):
            print(f"❌ Error: La base de datos {db_path} no existe")
            sys.exit(1)
        success = run_migration(db_path)
        sys.exit(0 if success else 1)
    
    # Si no, intentar con las rutas conocidas
    print("🔍 Buscando bases de datos...")
    migrated = False
    
    for db_path in possible_paths:
        if os.path.exists(db_path):
            print(f"\n📁 Encontrada: {db_path}")
            response = input(f"¿Migrar esta base de datos? (s/n): ").lower()
            if response == 's':
                success = run_migration(db_path)
                if success:
                    migrated = True
    
    if not migrated:
        print("\n⚠️  No se ejecutó ninguna migración")
        print("Uso: python migrations/add_pesaje_sin_sap_fields.py [ruta_base_datos]")
        sys.exit(1)
    
    print("\n✅ Proceso de migración completado")
    sys.exit(0)


if __name__ == "__main__":
    main()

