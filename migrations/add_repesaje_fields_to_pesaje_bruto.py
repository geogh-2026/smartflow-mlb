#!/usr/bin/env python3
"""
Migración: Agregar campos de repesaje a PesajeBrutoGranel
Fecha: 2025-01-25
Descripción: Agregar soporte para múltiples pesajes con trazabilidad
"""

import sqlite3
import logging
from datetime import datetime

def run_migration(db_path):
    """Ejecutar migración para agregar campos de repesaje"""
    
    logging.info("=== INICIANDO MIGRACIÓN: Campos de Repesaje en PesajeBrutoGranel ===")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si las columnas ya existen
        cursor.execute("PRAGMA table_info(PesajeBrutoGranel)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = [
            'es_pesaje_oficial',
            'numero_pesaje', 
            'id_pesaje_anterior',
            'motivo_repesaje'
        ]
        
        columns_to_add = [col for col in new_columns if col not in columns]
        
        if not columns_to_add:
            logging.info("✅ Todas las columnas de repesaje ya existen")
            return True
        
        # Agregar columnas nuevas
        migration_queries = []
        
        if 'es_pesaje_oficial' in columns_to_add:
            migration_queries.append(
                "ALTER TABLE PesajeBrutoGranel ADD COLUMN es_pesaje_oficial BOOLEAN DEFAULT 1"
            )
            
        if 'numero_pesaje' in columns_to_add:
            migration_queries.append(
                "ALTER TABLE PesajeBrutoGranel ADD COLUMN numero_pesaje INTEGER DEFAULT 1"
            )
            
        if 'id_pesaje_anterior' in columns_to_add:
            migration_queries.append(
                "ALTER TABLE PesajeBrutoGranel ADD COLUMN id_pesaje_anterior INTEGER"
            )
            
        if 'motivo_repesaje' in columns_to_add:
            migration_queries.append(
                "ALTER TABLE PesajeBrutoGranel ADD COLUMN motivo_repesaje TEXT"
            )
        
        # Ejecutar migraciones
        for query in migration_queries:
            logging.info(f"Ejecutando: {query}")
            cursor.execute(query)
        
        # Inicializar valores por defecto para registros existentes
        if columns_to_add:
            logging.info("Inicializando valores por defecto para registros existentes...")
            
            # Establecer todos los pesajes existentes como oficiales y número 1
            cursor.execute("""
                UPDATE PesajeBrutoGranel 
                SET es_pesaje_oficial = 1, numero_pesaje = 1
                WHERE es_pesaje_oficial IS NULL OR numero_pesaje IS NULL
            """)
            
            affected_rows = cursor.rowcount
            logging.info(f"✅ {affected_rows} registros actualizados con valores por defecto")
        
        conn.commit()
        logging.info("✅ Migración completada exitosamente")
        
        # Verificar migración
        cursor.execute("SELECT COUNT(*) FROM PesajeBrutoGranel WHERE es_pesaje_oficial = 1")
        count_oficiales = cursor.fetchone()[0]
        logging.info(f"📊 Total pesajes oficiales: {count_oficiales}")
        
        return True
        
    except sqlite3.Error as e:
        logging.error(f"❌ Error en migración de base de datos: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        logging.error(f"❌ Error inesperado en migración: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def rollback_migration(db_path):
    """Rollback de la migración (eliminar columnas agregadas)"""
    
    logging.warning("=== INICIANDO ROLLBACK: Campos de Repesaje ===")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SQLite no soporta DROP COLUMN directamente, necesitamos recrear la tabla
        logging.info("⚠️  SQLite no soporta DROP COLUMN. Se requiere recreación manual de la tabla.")
        logging.info("Para hacer rollback, restaure desde backup de base de datos.")
        
        return False
        
    except Exception as e:
        logging.error(f"❌ Error en rollback: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    import sys
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) < 2:
        print("Uso: python add_repesaje_fields_to_pesaje_bruto.py <ruta_db>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == "--rollback":
        success = rollback_migration(db_path)
    else:
        success = run_migration(db_path)
    
    if success:
        print("✅ Migración ejecutada exitosamente")
        sys.exit(0)
    else:
        print("❌ Error en migración")
        sys.exit(1)
