#!/usr/bin/env python3
"""
Script de Validación Post-Migración
===================================

Este script valida que la migración de datos se realizó correctamente,
comparando conteos, integridad referencial y datos críticos.

Uso:
    python migrations/validate_migration.py [--source <backup_original>] [--target <db_migrada>]

Autor: AI Assistant para Oleoflores
Fecha: 2025-01-26
"""

import sqlite3
import argparse
import logging
from typing import Dict, List, Tuple
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MigrationValidator:
    """Validador de migración de datos"""
    
    def __init__(self, source_db: str = None, target_db: str = 'instance/oleoflores_dev.db'):
        self.source_db = source_db
        self.target_db = target_db
        self.validation_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
    
    def get_table_counts(self, db_path: str) -> Dict[str, int]:
        """Obtener conteos de registros por tabla"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        counts = {}
        
        try:
            # Obtener todas las tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
        
        finally:
            conn.close()
        
        return counts
    
    def validate_record_counts(self) -> bool:
        """Validar que los conteos de registros coincidan"""
        logger.info("🔍 Validando conteos de registros...")
        
        if not self.source_db:
            logger.warning("⚠️  No se proporcionó DB fuente, omitiendo validación de conteos")
            return True
        
        source_counts = self.get_table_counts(self.source_db)
        target_counts = self.get_table_counts(self.target_db)
        
        all_passed = True
        
        for table, source_count in source_counts.items():
            target_count = target_counts.get(table, 0)
            
            if target_count == source_count:
                logger.info(f"✅ {table}: {source_count} = {target_count}")
                self.validation_results['passed'] += 1
            elif target_count > source_count:
                logger.warning(f"⚠️  {table}: Target tiene más registros ({target_count} > {source_count})")
                self.validation_results['warnings'] += 1
            else:
                logger.error(f"❌ {table}: Faltan registros ({target_count} < {source_count})")
                self.validation_results['failed'] += 1
                all_passed = False
        
        # Verificar tablas solo en target
        for table, target_count in target_counts.items():
            if table not in source_counts and target_count > 0:
                logger.info(f"ℹ️  {table}: Solo en target ({target_count} registros)")
        
        return all_passed
    
    def validate_users(self) -> bool:
        """Validar que los usuarios se migraron correctamente"""
        logger.info("👤 Validando usuarios...")
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        try:
            # Verificar estructura de tabla users
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            
            required_columns = ['id', 'username', 'email', 'password_hash', 'is_active']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                logger.error(f"❌ Faltan columnas en users: {missing_columns}")
                self.validation_results['failed'] += 1
                return False
            
            # Verificar que hay al menos un usuario activo
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            active_users = cursor.fetchone()[0]
            
            if active_users == 0:
                logger.error("❌ No hay usuarios activos")
                self.validation_results['failed'] += 1
                return False
            
            # Verificar que hay al menos un admin
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
            admin_users = cursor.fetchone()[0]
            
            if admin_users == 0:
                logger.warning("⚠️  No hay usuarios admin")
                self.validation_results['warnings'] += 1
            
            # Verificar que las contraseñas están hasheadas
            cursor.execute("SELECT username, password_hash FROM users")
            users = cursor.fetchall()
            
            for username, password_hash in users:
                if not password_hash or len(password_hash) < 20:
                    logger.error(f"❌ Usuario {username} tiene contraseña inválida")
                    self.validation_results['failed'] += 1
                    return False
            
            logger.info(f"✅ Usuarios: {len(users)} total, {active_users} activos, {admin_users} admin")
            self.validation_results['passed'] += 1
            return True
        
        finally:
            conn.close()
    
    def validate_referential_integrity(self) -> bool:
        """Validar integridad referencial básica"""
        logger.info("🔗 Validando integridad referencial...")
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        try:
            validations = [
                # (descripción, query, condición_éxito)
                (
                    "Pesajes bruto sin entry_record",
                    """SELECT COUNT(*) FROM pesajes_bruto pb 
                       WHERE NOT EXISTS (SELECT 1 FROM entry_records er WHERE er.codigo_guia = pb.codigo_guia)""",
                    lambda x: x == 0
                ),
                (
                    "Clasificaciones sin entry_record",
                    """SELECT COUNT(*) FROM clasificaciones c
                       WHERE NOT EXISTS (SELECT 1 FROM entry_records er WHERE er.codigo_guia = c.codigo_guia)""",
                    lambda x: x == 0
                ),
                (
                    "Pesajes neto sin entry_record",
                    """SELECT COUNT(*) FROM pesajes_neto pn
                       WHERE NOT EXISTS (SELECT 1 FROM entry_records er WHERE er.codigo_guia = pn.codigo_guia)""",
                    lambda x: x == 0
                ),
                (
                    "Fotos sin clasificación",
                    """SELECT COUNT(*) FROM fotos_clasificacion fc
                       WHERE NOT EXISTS (SELECT 1 FROM clasificaciones c WHERE c.codigo_guia = fc.codigo_guia)""",
                    lambda x: x == 0
                )
            ]
            
            all_passed = True
            
            for description, query, success_condition in validations:
                cursor.execute(query)
                result = cursor.fetchone()[0]
                
                if success_condition(result):
                    logger.info(f"✅ {description}: OK")
                    self.validation_results['passed'] += 1
                else:
                    logger.error(f"❌ {description}: {result} inconsistencias")
                    self.validation_results['failed'] += 1
                    all_passed = False
            
            return all_passed
        
        finally:
            conn.close()
    
    def validate_data_samples(self) -> bool:
        """Validar muestras de datos críticos"""
        logger.info("🎯 Validando muestras de datos...")
        
        conn = sqlite3.connect(self.target_db)
        cursor = conn.cursor()
        
        try:
            # Verificar que hay datos en tablas principales
            main_tables = ['entry_records', 'pesajes_bruto', 'clasificaciones', 'pesajes_neto']
            
            for table in main_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    logger.info(f"✅ {table}: {count} registros")
                    self.validation_results['passed'] += 1
                else:
                    logger.warning(f"⚠️  {table}: Sin datos")
                    self.validation_results['warnings'] += 1
            
            # Verificar códigos de guía válidos
            cursor.execute("""
                SELECT codigo_guia FROM entry_records 
                WHERE codigo_guia IS NULL OR codigo_guia = '' OR LENGTH(codigo_guia) < 5
                LIMIT 5
            """)
            invalid_codes = cursor.fetchall()
            
            if invalid_codes:
                logger.error(f"❌ Códigos de guía inválidos encontrados: {len(invalid_codes)}")
                self.validation_results['failed'] += 1
                return False
            else:
                logger.info("✅ Códigos de guía: Válidos")
                self.validation_results['passed'] += 1
            
            return True
        
        finally:
            conn.close()
    
    def generate_report(self) -> None:
        """Generar reporte de validación"""
        logger.info("\n" + "="*60)
        logger.info("📊 REPORTE DE VALIDACIÓN DE MIGRACIÓN")
        logger.info("="*60)
        logger.info(f"✅ Validaciones exitosas: {self.validation_results['passed']}")
        logger.info(f"❌ Validaciones fallidas: {self.validation_results['failed']}")
        logger.info(f"⚠️  Advertencias: {self.validation_results['warnings']}")
        
        total = sum(self.validation_results.values())
        if total > 0:
            success_rate = (self.validation_results['passed'] / total) * 100
            logger.info(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        if self.validation_results['failed'] == 0:
            logger.info("🎉 VALIDACIÓN EXITOSA: La migración se completó correctamente")
        else:
            logger.error("💥 VALIDACIÓN FALLIDA: Se encontraron problemas en la migración")
    
    def run_validation(self) -> bool:
        """Ejecutar todas las validaciones"""
        logger.info("🚀 INICIANDO VALIDACIÓN DE MIGRACIÓN")
        logger.info("="*50)
        
        validations = [
            ("Conteos de registros", self.validate_record_counts),
            ("Usuarios", self.validate_users),
            ("Integridad referencial", self.validate_referential_integrity),
            ("Muestras de datos", self.validate_data_samples)
        ]
        
        for name, validation_func in validations:
            try:
                logger.info(f"\n📋 {name}...")
                validation_func()
            except Exception as e:
                logger.error(f"❌ Error en validación '{name}': {e}")
                self.validation_results['failed'] += 1
        
        self.generate_report()
        return self.validation_results['failed'] == 0

def main():
    parser = argparse.ArgumentParser(description='Validar migración de base de datos')
    parser.add_argument('--source', '-s', help='Base de datos original (para comparar conteos)')
    parser.add_argument('--target', '-t', default='instance/oleoflores_dev.db', 
                       help='Base de datos migrada (default: instance/oleoflores_dev.db)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Salida detallada')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    validator = MigrationValidator(args.source, args.target)
    success = validator.run_validation()
    
    return 0 if success else 1

if __name__ == '__main__':
    import sys
    sys.exit(main()) 