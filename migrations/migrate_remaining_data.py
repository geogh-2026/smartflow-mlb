#!/usr/bin/env python3
"""
Script especializado para migrar datos restantes que fallaron en la migración principal.
Enfoque: Lotes pequeños + reintentos + manejo robusto de bloqueos de DB.
"""

import sqlite3
import json
import sys
import time
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RemainingDataMigrator:
    def __init__(self, source_db: str, target_db: str = "instance/oleoflores_dev.db"):
        self.source_db = source_db
        self.target_db = target_db
        self.batch_size = 50  # Lotes pequeños para evitar bloqueos
        self.max_retries = 3
        self.retry_delay = 2  # segundos
        
    def connect_with_timeout(self, db_path: str, timeout: int = 10):
        """Conectar con timeout para evitar bloqueos indefinidos"""
        conn = sqlite3.connect(db_path, timeout=timeout)
        conn.row_factory = sqlite3.Row
        return conn
        
    def wait_for_db_unlock(self, db_path: str, max_wait: int = 30):
        """Esperar hasta que la DB esté disponible"""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                conn = self.connect_with_timeout(db_path, timeout=1)
                conn.close()
                logger.info(f"✅ Base de datos {db_path} disponible")
                return True
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower():
                    logger.info(f"⏳ Esperando que se libere {db_path}...")
                    time.sleep(1)
                    continue
                else:
                    raise e
        
        logger.error(f"❌ Timeout esperando que se libere {db_path}")
        return False
    
    def get_missing_records(self, table_name: str):
        """Obtener registros que faltan en la tabla destino"""
        logger.info(f"🔍 Identificando registros faltantes en {table_name}...")
        
        # Esperar que ambas DBs estén disponibles
        if not self.wait_for_db_unlock(self.source_db) or not self.wait_for_db_unlock(self.target_db):
            raise Exception("No se pudo acceder a las bases de datos")
        
        source_conn = self.connect_with_timeout(self.source_db)
        target_conn = self.connect_with_timeout(self.target_db)
        
        try:
            # Obtener IDs presentes en target
            target_cursor = target_conn.cursor()
            if table_name == "entry_records":
                target_cursor.execute("SELECT codigo_guia FROM entry_records")
                existing_ids = {row[0] for row in target_cursor.fetchall()}
                id_column = "codigo_guia"
            else:  # pesajes_neto
                target_cursor.execute("SELECT id FROM pesajes_neto WHERE id IS NOT NULL")
                existing_ids = {row[0] for row in target_cursor.fetchall()}
                id_column = "id"
            
            # Obtener registros faltantes del source
            source_cursor = source_conn.cursor()
            if table_name == "entry_records":
                source_cursor.execute("SELECT * FROM entry_records")
            else:
                source_cursor.execute("SELECT * FROM pesajes_neto")
            
            missing_records = []
            for row in source_cursor.fetchall():
                row_dict = dict(row)
                record_id = row_dict.get(id_column)
                
                if record_id not in existing_ids:
                    missing_records.append(row_dict)
            
            logger.info(f"📊 Encontrados {len(missing_records)} registros faltantes en {table_name}")
            return missing_records
            
        finally:
            source_conn.close()
            target_conn.close()
    
    def migrate_batch(self, table_name: str, records_batch: list):
        """Migrar un lote de registros con reintentos"""
        for attempt in range(self.max_retries):
            try:
                if not self.wait_for_db_unlock(self.target_db):
                    raise Exception("DB target no disponible")
                
                target_conn = self.connect_with_timeout(self.target_db)
                cursor = target_conn.cursor()
                
                success_count = 0
                for record in records_batch:
                    try:
                        # Filtrar columnas que existen en target
                        compatible_columns = self.get_compatible_columns(list(record.keys()), table_name)
                        filtered_record = {k: v for k, v in record.items() if k in compatible_columns}
                        
                        if not filtered_record:
                            continue
                        
                        # Preparar inserción
                        columns = list(filtered_record.keys())
                        placeholders = ', '.join(['?' for _ in columns])
                        values = list(filtered_record.values())
                        
                        insert_sql = f"INSERT OR IGNORE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                        cursor.execute(insert_sql, values)
                        success_count += 1
                        
                    except Exception as e:
                        logger.warning(f"⚠️  Error insertando registro individual: {e}")
                        continue
                
                target_conn.commit()
                logger.info(f"✅ Migrado lote: {success_count}/{len(records_batch)} registros en {table_name}")
                return success_count
                
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower() and attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    logger.warning(f"⏳ DB bloqueada, reintentando en {wait_time}s... (intento {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise e
            finally:
                if 'target_conn' in locals():
                    target_conn.close()
        
        raise Exception(f"No se pudo migrar el lote después de {self.max_retries} intentos")
    
    def get_compatible_columns(self, source_columns: list, table_name: str):
        """Obtener columnas compatibles entre source y target"""
        target_conn = self.connect_with_timeout(self.target_db)
        try:
            cursor = target_conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            target_columns = [col[1] for col in cursor.fetchall()]
            return [col for col in source_columns if col in target_columns]
        finally:
            target_conn.close()
    
    def migrate_table_completely(self, table_name: str):
        """Migrar una tabla completamente por lotes"""
        logger.info(f"🚀 Iniciando migración completa de {table_name}")
        
        # Obtener registros faltantes
        missing_records = self.get_missing_records(table_name)
        
        if not missing_records:
            logger.info(f"✅ No hay registros faltantes en {table_name}")
            return 0
        
        # Migrar por lotes
        total_migrated = 0
        for i in range(0, len(missing_records), self.batch_size):
            batch = missing_records[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (len(missing_records) + self.batch_size - 1) // self.batch_size
            
            logger.info(f"📦 Procesando lote {batch_num}/{total_batches} de {table_name}")
            
            try:
                migrated = self.migrate_batch(table_name, batch)
                total_migrated += migrated
                
                # Pausa breve entre lotes para no saturar la DB
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ Error en lote {batch_num}: {e}")
                continue
        
        logger.info(f"🎯 {table_name}: {total_migrated} registros migrados exitosamente")
        return total_migrated
    
    def run_complete_migration(self):
        """Ejecutar migración completa de datos faltantes"""
        logger.info("🚀 INICIANDO MIGRACIÓN DE DATOS RESTANTES")
        logger.info("=" * 60)
        
        total_migrated = 0
        
        # Migrar entry_records
        try:
            migrated = self.migrate_table_completely("entry_records")
            total_migrated += migrated
        except Exception as e:
            logger.error(f"❌ Error migrando entry_records: {e}")
        
        # Migrar pesajes_neto
        try:
            migrated = self.migrate_table_completely("pesajes_neto")
            total_migrated += migrated
        except Exception as e:
            logger.error(f"❌ Error migrando pesajes_neto: {e}")
        
        logger.info("=" * 60)
        logger.info(f"🎉 MIGRACIÓN COMPLETADA: {total_migrated} registros totales")
        
        return total_migrated

def main():
    if len(sys.argv) < 2:
        print("Uso: python migrate_remaining_data.py <archivo_backup.db>")
        sys.exit(1)
    
    source_db = sys.argv[1]
    
    if not Path(source_db).exists():
        logger.error(f"❌ Archivo fuente no encontrado: {source_db}")
        sys.exit(1)
    
    migrator = RemainingDataMigrator(source_db)
    migrator.run_complete_migration()

if __name__ == "__main__":
    main() 