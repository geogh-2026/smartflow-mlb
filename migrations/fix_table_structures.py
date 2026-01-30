#!/usr/bin/env python3
"""
Script para corregir estructuras de tablas después de la migración.

Agrega columnas faltantes que no se migraron correctamente.
"""

import sqlite3
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths de las bases de datos
PROJECT_ROOT = Path(__file__).parent.parent
INSTANCE_PATH = PROJECT_ROOT / 'instance'
TARGET_DB = INSTANCE_PATH / 'oleoflores_dev.db'

def agregar_columna_si_no_existe(cursor, tabla, columna, tipo_datos, valor_default=None):
    """Agregar una columna a una tabla si no existe."""
    try:
        # Verificar si la columna ya existe
        cursor.execute(f"PRAGMA table_info({tabla})")
        columnas_existentes = [row[1] for row in cursor.fetchall()]
        
        if columna not in columnas_existentes:
            # Construir comando ALTER TABLE
            comando = f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo_datos}"
            if valor_default:
                comando += f" DEFAULT {valor_default}"
            
            cursor.execute(comando)
            logger.info(f"✅ Columna '{columna}' agregada a tabla '{tabla}'")
            return True
        else:
            logger.info(f"ℹ️  Columna '{columna}' ya existe en tabla '{tabla}'")
            return False
    except Exception as e:
        logger.error(f"❌ Error agregando columna '{columna}' a tabla '{tabla}': {e}")
        return False

def corregir_estructuras_tablas():
    """Corregir las estructuras de las tablas principales."""
    
    logger.info("🔧 Iniciando corrección de estructuras de tablas...")
    
    try:
        with sqlite3.connect(TARGET_DB) as conn:
            cursor = conn.cursor()
            
            # Correcciones para tabla pesajes_bruto
            logger.info("📊 Corrigiendo tabla pesajes_bruto...")
            agregar_columna_si_no_existe(cursor, "pesajes_bruto", "usuario_pesaje", "TEXT")
            
            # Correcciones para tabla users (campos faltantes)
            logger.info("👥 Corrigiendo tabla users...")
            agregar_columna_si_no_existe(cursor, "users", "is_admin", "BOOLEAN", "0")
            agregar_columna_si_no_existe(cursor, "users", "created_at", "TIMESTAMP", "CURRENT_TIMESTAMP")
            agregar_columna_si_no_existe(cursor, "users", "last_login", "TIMESTAMP")
            
            # Correcciones para tabla clasificaciones (si es necesario)
            logger.info("🏷️  Verificando tabla clasificaciones...")
            cursor.execute("PRAGMA table_info(clasificaciones)")
            clasificaciones_cols = [row[1] for row in cursor.fetchall()]
            logger.info(f"Columnas en clasificaciones: {len(clasificaciones_cols)}")
            
            # Correcciones para tabla pesajes_neto (si es necesario)
            logger.info("⚖️  Verificando tabla pesajes_neto...")
            cursor.execute("PRAGMA table_info(pesajes_neto)")
            pesajes_neto_cols = [row[1] for row in cursor.fetchall()]
            logger.info(f"Columnas en pesajes_neto: {len(pesajes_neto_cols)}")
            
            # Verificar que las tablas principales existen
            tablas_requeridas = [
                'entry_records', 'pesajes_bruto', 'pesajes_neto', 
                'clasificaciones', 'users', 'graneles'
            ]
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tablas_existentes = [row[0] for row in cursor.fetchall()]
            
            logger.info("📋 Verificando tablas requeridas...")
            for tabla in tablas_requeridas:
                if tabla in tablas_existentes:
                    logger.info(f"✅ Tabla '{tabla}' existe")
                else:
                    logger.warning(f"⚠️  Tabla '{tabla}' NO existe")
            
            # Commit de todos los cambios
            conn.commit()
            logger.info("💾 Cambios guardados exitosamente")
            
    except Exception as e:
        logger.error(f"❌ Error en corrección de estructuras: {e}")
        return False
    
    return True

def verificar_consulta_problematica():
    """Verificar que la consulta que estaba fallando ahora funcione."""
    
    logger.info("🧪 Verificando consulta de datos de guía...")
    
    try:
        with sqlite3.connect(TARGET_DB) as conn:
            cursor = conn.cursor()
            
            # Consulta simplificada para verificar las columnas
            query_test = """
            SELECT 
                er.codigo_guia,
                pb.usuario_pesaje
            FROM entry_records er
            LEFT JOIN pesajes_bruto pb ON er.codigo_guia = pb.codigo_guia
            LIMIT 1
            """
            
            cursor.execute(query_test)
            resultado = cursor.fetchone()
            
            if resultado:
                logger.info("✅ Consulta de verificación exitosa")
                logger.info(f"Resultado de prueba: {resultado}")
                return True
            else:
                logger.info("ℹ️  Consulta ejecutada correctamente (sin resultados)")
                return True
                
    except Exception as e:
        logger.error(f"❌ Error en consulta de verificación: {e}")
        return False

def main():
    """Función principal."""
    
    logger.info("=" * 60)
    logger.info("🔧 CORRECCIÓN DE ESTRUCTURAS DE TABLAS")
    logger.info("=" * 60)
    
    # Verificar que la base de datos existe
    if not TARGET_DB.exists():
        logger.error(f"❌ Base de datos no encontrada: {TARGET_DB}")
        return False
    
    # Ejecutar correcciones
    if not corregir_estructuras_tablas():
        logger.error("❌ Falló la corrección de estructuras")
        return False
    
    # Verificar que las correcciones funcionan
    if not verificar_consulta_problematica():
        logger.error("❌ Las consultas siguen fallando después de las correcciones")
        return False
    
    logger.info("=" * 60)
    logger.info("✅ CORRECCIÓN COMPLETADA EXITOSAMENTE")
    logger.info("=" * 60)
    logger.info("🚀 La aplicación debería funcionar correctamente ahora")
    
    return True

if __name__ == '__main__':
    main() 