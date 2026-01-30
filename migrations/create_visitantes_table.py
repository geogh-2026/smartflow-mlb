#!/usr/bin/env python3
"""
Migración: Crear tabla de registro_visitantes
Fecha: 2025-01-02
Descripción: Crear tabla para el módulo de visitantes y proveedores
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Ejecutar la migración para crear la tabla registro_visitantes"""
    
    # Obtener la ruta de la base de datos
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'oleoflores_dev.db')
    
    print(f"🔄 Ejecutando migración: Crear tabla registro_visitantes")
    print(f"📍 Base de datos: {db_path}")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear la tabla registro_visitantes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registro_visitantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_completo VARCHAR(200) NOT NULL,
                numero_documento VARCHAR(50) NOT NULL,
                empresa VARCHAR(200) NOT NULL,
                ciudad_origen VARCHAR(100) NOT NULL,
                tipo_visitante VARCHAR(20) NOT NULL CHECK (tipo_visitante IN ('visitante', 'proveedor')),
                timestamp_ingreso_utc VARCHAR(50) NOT NULL,
                timestamp_salida_utc VARCHAR(50),
                estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'salida', 'cancelado')),
                observaciones TEXT,
                orden_compra_path VARCHAR(500),
                orden_compra_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear índices para mejorar el rendimiento
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_visitantes_tipo ON registro_visitantes(tipo_visitante)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_visitantes_estado ON registro_visitantes(estado)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_visitantes_fecha ON registro_visitantes(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_visitantes_documento ON registro_visitantes(numero_documento)')
        
        # Confirmar cambios
        conn.commit()
        
        print("✅ Tabla 'registro_visitantes' creada exitosamente")
        print("✅ Índices creados exitosamente")
        
        # Verificar que la tabla se creó correctamente
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='registro_visitantes'")
        if cursor.fetchone():
            print("✅ Verificación: Tabla existe en la base de datos")
        else:
            print("❌ Error: La tabla no se encontró después de la creación")
            
    except Exception as e:
        print(f"❌ Error ejecutando migración: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()
        print("🔒 Conexión a base de datos cerrada")

if __name__ == "__main__":
    run_migration()
    print("🎉 Migración completada exitosamente")
