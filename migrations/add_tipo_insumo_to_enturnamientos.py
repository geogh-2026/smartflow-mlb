#!/usr/bin/env python3
"""
Migración: Agregar campo tipo_insumo a tabla enturnamientos_graneles

Cambios:
- Agregar columna tipo_insumo TEXT DEFAULT 'Granel'
- Actualizar registros existentes para que sean 'Granel'
- Crear índice para optimizar consultas por tipo

Nota: Mantiene compatibilidad con registros existentes
"""

import os
import sqlite3
from datetime import datetime

DB_PATH = os.environ.get('TIQUETES_DB_PATH', 'instance/oleoflores_dev.db')

def run_migration():
    """Ejecutar la migración"""
    print(f"🔄 Iniciando migración: Agregar tipo_insumo a enturnamientos_graneles")
    print(f"📂 Base de datos: {DB_PATH}")
    
    try:
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='enturnamientos_graneles'
        """)
        
        if not cursor.fetchone():
            print("⚠️  Tabla enturnamientos_graneles no existe. Creándola primero...")
            # Crear tabla si no existe
            cursor.execute("""
                CREATE TABLE enturnamientos_graneles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    placa TEXT NOT NULL,
                    foto_path TEXT,
                    timestamp_enturnado DATETIME DEFAULT CURRENT_TIMESTAMP,
                    estado TEXT DEFAULT 'en_turno',
                    usuario_guardia TEXT,
                    observacion TEXT,
                    registro_entrada_id INTEGER,
                    timestamp_asignado_recepcionista DATETIME,
                    usuario_recepcionista TEXT,
                    tipo_insumo TEXT DEFAULT 'Granel'
                )
            """)
            print("✅ Tabla enturnamientos_graneles creada con campo tipo_insumo")
        else:
            # Verificar si la columna ya existe
            cursor.execute("PRAGMA table_info(enturnamientos_graneles)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'tipo_insumo' not in columns:
                print("➕ Agregando columna tipo_insumo...")
                cursor.execute("""
                    ALTER TABLE enturnamientos_graneles 
                    ADD COLUMN tipo_insumo TEXT DEFAULT 'Granel'
                """)
                
                # Actualizar registros existentes para que sean 'Granel'
                cursor.execute("""
                    UPDATE enturnamientos_graneles 
                    SET tipo_insumo = 'Granel' 
                    WHERE tipo_insumo IS NULL
                """)
                
                print("✅ Columna tipo_insumo agregada y registros existentes actualizados")
            else:
                print("ℹ️  Columna tipo_insumo ya existe")
        
        # Crear índice para optimizar consultas por tipo
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_enturnamientos_tipo_estado 
            ON enturnamientos_graneles(tipo_insumo, estado)
        """)
        
        # Crear índice compuesto para consultas frecuentes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_enturnamientos_placa_tipo 
            ON enturnamientos_graneles(placa, tipo_insumo)
        """)
        
        conn.commit()
        print("✅ Índices creados exitosamente")
        
        # Verificar el resultado
        cursor.execute("SELECT COUNT(*) FROM enturnamientos_graneles")
        total_registros = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM enturnamientos_graneles WHERE tipo_insumo = 'Granel'")
        registros_granel = cursor.fetchone()[0]
        
        print(f"📊 Resumen de migración:")
        print(f"   - Total de registros: {total_registros}")
        print(f"   - Registros tipo Granel: {registros_granel}")
        print(f"   - Registros tipo Fruta: {total_registros - registros_granel}")
        
        conn.close()
        print("🎉 Migración completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        return False

def rollback_migration():
    """Revertir la migración (eliminar columna tipo_insumo)"""
    print("🔄 Iniciando rollback: Eliminar tipo_insumo de enturnamientos_graneles")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # SQLite no soporta DROP COLUMN directamente, necesitamos recrear la tabla
        print("⚠️  SQLite no soporta DROP COLUMN. Recreando tabla...")
        
        # Crear tabla temporal sin tipo_insumo
        cursor.execute("""
            CREATE TABLE enturnamientos_graneles_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                placa TEXT NOT NULL,
                foto_path TEXT,
                timestamp_enturnado DATETIME DEFAULT CURRENT_TIMESTAMP,
                estado TEXT DEFAULT 'en_turno',
                usuario_guardia TEXT,
                observacion TEXT,
                registro_entrada_id INTEGER,
                timestamp_asignado_recepcionista DATETIME,
                usuario_recepcionista TEXT
            )
        """)
        
        # Copiar datos (excluyendo tipo_insumo)
        cursor.execute("""
            INSERT INTO enturnamientos_graneles_temp 
            (id, placa, foto_path, timestamp_enturnado, estado, usuario_guardia, 
             observacion, registro_entrada_id, timestamp_asignado_recepcionista, usuario_recepcionista)
            SELECT id, placa, foto_path, timestamp_enturnado, estado, usuario_guardia,
                   observacion, registro_entrada_id, timestamp_asignado_recepcionista, usuario_recepcionista
            FROM enturnamientos_graneles
        """)
        
        # Eliminar tabla original
        cursor.execute("DROP TABLE enturnamientos_graneles")
        
        # Renombrar tabla temporal
        cursor.execute("ALTER TABLE enturnamientos_graneles_temp RENAME TO enturnamientos_graneles")
        
        # Recrear índices originales
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_enturnamientos_placa_estado 
            ON enturnamientos_graneles(placa, estado)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_enturnamientos_timestamp 
            ON enturnamientos_graneles(timestamp_enturnado)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Rollback completado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en rollback: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback_migration()
    else:
        run_migration()
