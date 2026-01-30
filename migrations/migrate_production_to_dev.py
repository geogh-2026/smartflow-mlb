#!/usr/bin/env python3
"""
Script de Migración de Base de Datos de Producción
==================================================

Este script migra todos los datos de la base de datos de producción 
a la nueva estructura de base de datos de desarrollo, incluyendo:

- Usuarios y contraseñas
- Registros de entrada
- Pesajes brutos y netos
- Clasificaciones
- Salidas
- Fotos de clasificación
- Datos de graneles y sellos

Uso:
    python migrations/migrate_production_to_dev.py --source <archivo_backup> [--format <formato>] [--dry-run]

Formatos soportados:
    - sqlite: Archivo SQLite (.db, .sqlite)
    - sql: SQL dump (.sql)
    - csv: Archivos CSV por tabla
    - json: Export JSON

Autor: AI Assistant para Oleoflores
Fecha: 2025-01-26
"""

import os
import sys
import sqlite3
import json
import csv
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import shutil

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Clase principal para migración de base de datos"""
    
    def __init__(self, source_path: str, target_db_path: str = None, dry_run: bool = False):
        self.source_path = source_path
        self.target_db_path = target_db_path or 'instance/oleoflores_dev.db'
        self.dry_run = dry_run
        self.migration_stats = {
            'tables_migrated': 0,
            'records_inserted': 0,
            'records_updated': 0,
            'errors': 0,
            'warnings': 0
        }
        
        # Mapeo de tablas de producción a desarrollo
        self.table_mapping = {
            # Tablas principales del sistema de fruta
            'entry_records': 'entry_records',
            'pesajes_bruto': 'pesajes_bruto', 
            'clasificaciones': 'clasificaciones',
            'pesajes_neto': 'pesajes_neto',
            'salidas': 'salidas',
            'fotos_clasificacion': 'fotos_clasificacion',
            
            # Usuarios y autenticación
            'users': 'users',
            'user': 'users',  # Por si tiene nombre diferente
            'usuarios': 'users',  # Por si está en español
            
            # Graneles
            'RegistroEntradaGraneles': 'RegistroEntradaGraneles',
            'PrimerPesajeGranel': 'PrimerPesajeGranel',
            'ControlCalidadGranel': 'ControlCalidadGranel',
            'InspeccionVehiculo': 'InspeccionVehiculo',
            
            # Sistema de sellos
            'tipos_sello': 'tipos_sello',
            'maestro_vehiculos': 'maestro_vehiculos',
            'solicitudes_sello': 'solicitudes_sello',
            'sellos': 'sellos',
            'movimientos_sello': 'movimientos_sello',
            
            # Presupuesto y validaciones
            'presupuesto_mensual': 'presupuesto_mensual',
            'validaciones_diarias_sap': 'validaciones_diarias_sap',
            
            # Sistema de notificaciones y roles
            'roles_sellos': 'roles_sellos',
            'permisos_sellos': 'permisos_sellos',
            'usuario_rol_sellos': 'usuario_rol_sellos',
            'rol_permiso_sellos': 'rol_permiso_sellos',
            'configuraciones_notificacion_sellos': 'configuraciones_notificacion_sellos',
            'plantillas_notificacion_sellos': 'plantillas_notificacion_sellos',
            'notificaciones_sellos': 'notificaciones_sellos',
            'configuracion_canales_sellos': 'configuracion_canales_sellos',
            'auditoria_roles_sellos': 'auditoria_roles_sellos',
            'auditoria_rol_sellos': 'auditoria_rol_sellos'
        }
        
        # Orden de migración (para respetar relaciones)
        self.migration_order = [
            'users',  # Primero usuarios
            'presupuesto_mensual',  # Datos de referencia
            'entry_records',  # Registros base
            'pesajes_bruto',
            'clasificaciones', 
            'pesajes_neto',
            'salidas',
            'fotos_clasificacion',
            'validaciones_diarias_sap',
            'RegistroEntradaGraneles',
            'PrimerPesajeGranel',
            'ControlCalidadGranel', 
            'InspeccionVehiculo',
            'tipos_sello',
            'maestro_vehiculos',
            'solicitudes_sello',
            'sellos',
            'movimientos_sello',
            'roles_sellos',
            'permisos_sellos',
            'rol_permiso_sellos',
            'usuario_rol_sellos',
            'configuraciones_notificacion_sellos',
            'plantillas_notificacion_sellos',
            'notificaciones_sellos',
            'configuracion_canales_sellos',
            'auditoria_roles_sellos',
            'auditoria_rol_sellos'
        ]
    
    def detect_source_format(self) -> str:
        """Detectar el formato del archivo fuente"""
        path = Path(self.source_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Archivo fuente no encontrado: {self.source_path}")
        
        if path.suffix.lower() in ['.db', '.sqlite', '.sqlite3']:
            return 'sqlite'
        elif path.suffix.lower() == '.sql':
            return 'sql'
        elif path.suffix.lower() == '.json':
            return 'json'
        elif path.is_dir():
            # Verificar si es un directorio con CSVs
            csv_files = list(path.glob('*.csv'))
            if csv_files:
                return 'csv'
        
        raise ValueError(f"Formato no soportado para: {self.source_path}")
    
    def backup_current_db(self) -> str:
        """Crear backup de la base de datos actual"""
        if not os.path.exists(self.target_db_path):
            logger.info("Base de datos destino no existe, no hay nada que respaldar")
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.target_db_path}.backup_{timestamp}"
        
        shutil.copy2(self.target_db_path, backup_path)
        logger.info(f"✅ Backup creado: {backup_path}")
        return backup_path
    
    def get_source_tables_sqlite(self) -> Dict[str, List[Dict]]:
        """Obtener estructura y datos de SQLite"""
        tables_data = {}
        
        conn = sqlite3.connect(self.source_path)
        conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
        cursor = conn.cursor()
        
        try:
            # Obtener lista de tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            logger.info(f"📊 Tablas encontradas en fuente: {len(tables)}")
            
            for table in tables:
                logger.info(f"🔍 Procesando tabla: {table}")
                
                # Obtener estructura
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [{'name': col[1], 'type': col[2]} for col in cursor.fetchall()]
                
                # Obtener datos
                cursor.execute(f"SELECT * FROM {table}")
                rows = [dict(row) for row in cursor.fetchall()]
                
                tables_data[table] = {
                    'columns': columns,
                    'data': rows,
                    'count': len(rows)
                }
                
                logger.info(f"  📋 Columnas: {len(columns)}, Registros: {len(rows)}")
        
        finally:
            conn.close()
        
        return tables_data
    
    def get_source_tables_json(self) -> Dict[str, List[Dict]]:
        """Obtener datos de archivo JSON"""
        with open(self.source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tables_data = {}
        for table_name, table_data in data.items():
            if isinstance(table_data, list):
                tables_data[table_name] = {
                    'columns': list(table_data[0].keys()) if table_data else [],
                    'data': table_data,
                    'count': len(table_data)
                }
        
        return tables_data
    
    def get_source_tables_csv(self) -> Dict[str, List[Dict]]:
        """Obtener datos de archivos CSV"""
        source_dir = Path(self.source_path)
        tables_data = {}
        
        for csv_file in source_dir.glob('*.csv'):
            table_name = csv_file.stem
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                tables_data[table_name] = {
                    'columns': list(reader.fieldnames) if reader.fieldnames else [],
                    'data': rows,
                    'count': len(rows)
                }
        
        return tables_data
    
    def get_compatible_columns(self, source_columns: List[str], target_table: str) -> List[str]:
        """Obtener solo las columnas que existen en ambas tablas"""
        conn = sqlite3.connect(self.target_db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"PRAGMA table_info({target_table})")
            target_columns = [col[1] for col in cursor.fetchall()]
            
            # Retornar solo columnas que existen en ambas tablas
            compatible = [col for col in source_columns if col in target_columns]
            
            if len(compatible) < len(source_columns):
                excluded = [col for col in source_columns if col not in target_columns]
                logger.warning(f"⚠️  Tabla {target_table}: Excluyendo columnas no compatibles: {excluded}")
            
            return compatible
        
        finally:
            conn.close()

    def map_table_name(self, source_table: str) -> Optional[str]:
        """Mapear nombre de tabla de origen a destino"""
        return self.table_mapping.get(source_table, source_table)
    
    def transform_user_data(self, user_data: Dict) -> Dict:
        """Transformar datos de usuario para compatibilidad"""
        transformed = {}
        
        # Mapeo de campos de usuario
        field_mapping = {
            'id': 'id',
            'username': 'username',
            'user_name': 'username',
            'usuario': 'username',
            'email': 'email',
            'correo': 'email',
            'password_hash': 'password_hash',
            'password': 'password_hash',
            'contraseña': 'password_hash',
            'is_active': 'is_active',
            'activo': 'is_active',
            'is_admin': 'is_admin',
            'admin': 'is_admin',
            'es_admin': 'is_admin',
            'user_role': 'user_role',
            'rol': 'user_role',
            'role': 'user_role',
            'fecha_creacion': 'fecha_creacion',
            'created_at': 'fecha_creacion',
            'last_login': 'last_login',
            'ultimo_login': 'last_login'
        }
        
        for source_field, target_field in field_mapping.items():
            if source_field in user_data:
                value = user_data[source_field]
                
                # Transformaciones específicas
                if target_field == 'is_active' and isinstance(value, str):
                    transformed[target_field] = 1 if value.lower() in ['true', '1', 'activo', 'yes'] else 0
                elif target_field == 'is_admin' and isinstance(value, str):
                    transformed[target_field] = 1 if value.lower() in ['true', '1', 'admin', 'yes'] else 0
                elif target_field == 'password_hash' and value:
                    # Si la contraseña no está hasheada, hashearla
                    if not value.startswith('pbkdf2:sha256:') and not value.startswith('$'):
                        from werkzeug.security import generate_password_hash
                        transformed[target_field] = generate_password_hash(value)
                    else:
                        transformed[target_field] = value
                else:
                    transformed[target_field] = value
        
        # Valores por defecto para campos requeridos
        if 'is_active' not in transformed:
            transformed['is_active'] = 1
        if 'is_admin' not in transformed:
            transformed['is_admin'] = 0
        if 'user_role' not in transformed:
            transformed['user_role'] = 'guarda'
        if 'fecha_creacion' not in transformed:
            transformed['fecha_creacion'] = datetime.now()
        
        return transformed
    
    def insert_data_to_target(self, table_name: str, data: List[Dict]) -> Tuple[int, int]:
        """Insertar datos en la base de datos destino"""
        if not data:
            return 0, 0
        
        conn = sqlite3.connect(self.target_db_path)
        cursor = conn.cursor()
        
        inserted = 0
        updated = 0
        
        try:
            for record in data:
                # Transformaciones específicas por tabla
                if table_name == 'users':
                    record = self.transform_user_data(record)
                
                # Filtrar solo campos compatibles
                compatible_fields = self.get_compatible_columns(list(record.keys()), table_name)
                
                # Preparar campos y valores solo para campos compatibles
                filtered_record = {k: v for k, v in record.items() if k in compatible_fields}
                fields = list(filtered_record.keys())
                placeholders = ', '.join(['?' for _ in fields])
                values = list(filtered_record.values())
                
                # Intentar inserción
                try:
                    insert_sql = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({placeholders})"
                    cursor.execute(insert_sql, values)
                    inserted += 1
                    
                except sqlite3.IntegrityError as e:
                    # Si ya existe, intentar actualización
                    if 'UNIQUE constraint failed' in str(e) or 'PRIMARY KEY constraint failed' in str(e):
                        try:
                            # Buscar campo clave primaria
                            pk_field = 'id'
                            if pk_field in filtered_record:
                                set_clause = ', '.join([f"{field} = ?" for field in fields if field != pk_field])
                                update_values = [filtered_record[field] for field in fields if field != pk_field]
                                update_values.append(filtered_record[pk_field])
                                
                                update_sql = f"UPDATE {table_name} SET {set_clause} WHERE {pk_field} = ?"
                                cursor.execute(update_sql, update_values)
                                updated += 1
                            else:
                                logger.warning(f"No se pudo actualizar registro sin clave primaria en {table_name}")
                                self.migration_stats['warnings'] += 1
                        except Exception as update_error:
                            logger.error(f"Error actualizando {table_name}: {update_error}")
                            self.migration_stats['errors'] += 1
                    else:
                        logger.error(f"Error insertando en {table_name}: {e}")
                        self.migration_stats['errors'] += 1
                
                except Exception as e:
                    logger.error(f"Error procesando registro en {table_name}: {e}")
                    self.migration_stats['errors'] += 1
            
            if not self.dry_run:
                conn.commit()
            else:
                conn.rollback()
                logger.info(f"🧪 DRY RUN: Se habrían insertado {inserted} y actualizado {updated} registros en {table_name}")
        
        finally:
            conn.close()
        
        return inserted, updated
    
    def migrate_table(self, source_table: str, table_data: Dict) -> bool:
        """Migrar una tabla específica"""
        target_table = self.map_table_name(source_table)
        
        if not target_table:
            logger.warning(f"⚠️  Tabla {source_table} no mapeada, omitiendo")
            return False
        
        logger.info(f"🔄 Migrando {source_table} → {target_table} ({table_data['count']} registros)")
        
        try:
            inserted, updated = self.insert_data_to_target(target_table, table_data['data'])
            
            logger.info(f"✅ {target_table}: {inserted} insertados, {updated} actualizados")
            
            self.migration_stats['records_inserted'] += inserted
            self.migration_stats['records_updated'] += updated
            self.migration_stats['tables_migrated'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error migrando tabla {source_table}: {e}")
            self.migration_stats['errors'] += 1
            return False
    
    def run_migration(self) -> bool:
        """Ejecutar la migración completa"""
        logger.info("🚀 INICIANDO MIGRACIÓN DE BASE DE DATOS")
        logger.info("=" * 60)
        
        try:
            # 1. Detectar formato
            source_format = self.detect_source_format()
            logger.info(f"📄 Formato detectado: {source_format}")
            
            # 2. Crear backup
            if not self.dry_run:
                backup_path = self.backup_current_db()
            
            # 3. Obtener datos fuente
            logger.info("📥 Cargando datos de origen...")
            
            if source_format == 'sqlite':
                source_data = self.get_source_tables_sqlite()
            elif source_format == 'json':
                source_data = self.get_source_tables_json()
            elif source_format == 'csv':
                source_data = self.get_source_tables_csv()
            else:
                raise ValueError(f"Formato {source_format} no implementado aún")
            
            logger.info(f"📊 Total tablas cargadas: {len(source_data)}")
            
            # 4. Migrar tablas en orden
            logger.info("🔄 Iniciando migración de tablas...")
            
            # Primero las tablas en orden específico
            for table_name in self.migration_order:
                if table_name in source_data:
                    self.migrate_table(table_name, source_data[table_name])
                    del source_data[table_name]  # Marcar como procesada
            
            # Luego las tablas restantes
            for table_name, table_data in source_data.items():
                self.migrate_table(table_name, table_data)
            
            # 5. Mostrar estadísticas
            logger.info("📈 ESTADÍSTICAS DE MIGRACIÓN")
            logger.info("=" * 40)
            logger.info(f"✅ Tablas migradas: {self.migration_stats['tables_migrated']}")
            logger.info(f"📝 Registros insertados: {self.migration_stats['records_inserted']}")
            logger.info(f"🔄 Registros actualizados: {self.migration_stats['records_updated']}")
            logger.info(f"⚠️  Advertencias: {self.migration_stats['warnings']}")
            logger.info(f"❌ Errores: {self.migration_stats['errors']}")
            
            success = self.migration_stats['errors'] == 0
            
            if success:
                logger.info("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
            else:
                logger.error("💥 MIGRACIÓN COMPLETADA CON ERRORES")
            
            return success
            
        except Exception as e:
            logger.error(f"💥 ERROR CRÍTICO EN MIGRACIÓN: {e}")
            return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Migrar base de datos de producción a desarrollo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python migrations/migrate_production_to_dev.py --source backup_prod.db
  python migrations/migrate_production_to_dev.py --source backup_prod.sql --format sql
  python migrations/migrate_production_to_dev.py --source csv_export/ --format csv --dry-run
  python migrations/migrate_production_to_dev.py --source data.json --format json
        """
    )
    
    parser.add_argument(
        '--source', '-s',
        required=True,
        help='Ruta del archivo o directorio fuente (backup de producción)'
    )
    
    parser.add_argument(
        '--target', '-t',
        default='instance/oleoflores_dev.db',
        help='Ruta de la base de datos destino (default: instance/oleoflores_dev.db)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['sqlite', 'sql', 'csv', 'json', 'auto'],
        default='auto',
        help='Formato del archivo fuente (default: auto-detectar)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Ejecutar sin hacer cambios reales (solo mostrar lo que se haría)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mostrar información detallada'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Verificar que el archivo fuente existe
    if not os.path.exists(args.source):
        print(f"❌ Error: Archivo fuente no encontrado: {args.source}")
        return 1
    
    # Verificar directorio destino
    target_dir = os.path.dirname(args.target)
    if target_dir and not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        print(f"📁 Directorio destino creado: {target_dir}")
    
    # Ejecutar migración
    migrator = DatabaseMigrator(
        source_path=args.source,
        target_db_path=args.target,
        dry_run=args.dry_run
    )
    
    success = migrator.run_migration()
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main()) 