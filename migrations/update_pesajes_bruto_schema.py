#!/usr/bin/env python3
"""
Migración para actualizar el esquema de pesajes_bruto
Agrega columnas faltantes: usuario_pesaje, imagen_pesaje, tipo_pesaje
"""

import sqlite3
import logging
import sys
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_migration(db_path):
    """Ejecuta la migración para agregar columnas faltantes a pesajes_bruto"""
    conn = None
    try:
        logger.info(f"📂 Conectando a base de datos: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar que la tabla pesajes_bruto existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pesajes_bruto'")
        if not cursor.fetchone():
            logger.error("❌ La tabla 'pesajes_bruto' no existe en la base de datos")
            return False
        
        logger.info("📋 Verificando esquema de tabla pesajes_bruto...")
        cursor.execute("PRAGMA table_info(pesajes_bruto)")
        columns = [col[1] for col in cursor.fetchall()]
        logger.info(f"   Columnas actuales: {', '.join(columns)}")
        
        # Lista de columnas a agregar con sus definiciones
        columns_to_add = [
            ('usuario_pesaje', 'TEXT'),
            ('imagen_pesaje', 'TEXT'),
            ('tipo_pesaje', 'TEXT')
        ]
        
        changes_made = False
        
        for col_name, col_type in columns_to_add:
            if col_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE pesajes_bruto ADD COLUMN {col_name} {col_type}")
                    logger.info(f"   ✅ Columna '{col_name}' agregada exitosamente")
                    changes_made = True
                except sqlite3.Error as e:
                    logger.error(f"   ❌ Error agregando columna '{col_name}': {e}")
                    return False
            else:
                logger.info(f"   ⏩ Columna '{col_name}' ya existe")
        
        if changes_made:
            conn.commit()
            logger.info("✅ MIGRACIÓN COMPLETADA - Cambios guardados")
        else:
            logger.info("ℹ️  No se requirieron cambios - Esquema ya está actualizado")
        
        # Verificar el resultado final
        cursor.execute("PRAGMA table_info(pesajes_bruto)")
        final_columns = [col[1] for col in cursor.fetchall()]
        logger.info(f"📋 Columnas finales en pesajes_bruto: {', '.join(final_columns)}")
        
        return True
        
    except sqlite3.Error as e:
        logger.error(f"❌ Error de base de datos durante la migración: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado durante la migración: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
            logger.info("🔌 Conexión a base de datos cerrada")

if __name__ == '__main__':
    # Determinar la ruta de la base de datos
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Intentar detectar automáticamente
        possible_paths = [
            'instance/oleoflores_prod.db',
            'instance/oleoflores_dev.db',
            '/home/enriquepabon/oleoflores-smart-flow/instance/oleoflores_prod.db'
        ]
        
        db_path = None
        for path in possible_paths:
            if os.path.exists(path):
                db_path = path
                break
        
        if not db_path:
            logger.error("❌ No se pudo encontrar la base de datos")
            logger.info("💡 Uso: python update_pesajes_bruto_schema.py <ruta_a_db>")
            sys.exit(1)
    
    logger.info("=" * 70)
    logger.info("🚀 INICIANDO MIGRACIÓN: Actualización de esquema pesajes_bruto")
    logger.info("=" * 70)
    
    success = run_migration(db_path)
    
    logger.info("=" * 70)
    if success:
        logger.info("🎉 MIGRACIÓN FINALIZADA EXITOSAMENTE")
        sys.exit(0)
    else:
        logger.error("💥 MIGRACIÓN FALLÓ - Revisa los errores anteriores")
        sys.exit(1)

