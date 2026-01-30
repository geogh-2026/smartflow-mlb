#!/usr/bin/env python3
"""
Migración: Agregar campos tipo_vehiculo y capacidad_litros a maestro_vehiculos
Fecha: 2025-08-20
Descripción: Agrega campos adicionales al modelo MaestroVehiculo para mejorar la gestión de vehículos
"""

import sqlite3
import os
from pathlib import Path

def run_migration():
    """Ejecutar la migración para agregar campos a maestro_vehiculos"""
    
    # Ruta a la base de datos
    db_path = Path(__file__).parent.parent / "instance" / "oleoflores_dev.db"
    
    if not db_path.exists():
        print(f"❌ Base de datos no encontrada en: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("🔄 Iniciando migración: Agregar campos a maestro_vehiculos...")
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='maestro_vehiculos'
        """)
        
        if not cursor.fetchone():
            print("❌ Tabla maestro_vehiculos no existe")
            return False
        
        # Verificar si los campos ya existen
        cursor.execute("PRAGMA table_info(maestro_vehiculos)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Agregar tipo_vehiculo si no existe
        if 'tipo_vehiculo' not in columns:
            print("➕ Agregando campo tipo_vehiculo...")
            cursor.execute("""
                ALTER TABLE maestro_vehiculos 
                ADD COLUMN tipo_vehiculo VARCHAR(50)
            """)
            print("✅ Campo tipo_vehiculo agregado")
        else:
            print("ℹ️ Campo tipo_vehiculo ya existe")
        
        # Agregar capacidad_litros si no existe
        if 'capacidad_litros' not in columns:
            print("➕ Agregando campo capacidad_litros...")
            cursor.execute("""
                ALTER TABLE maestro_vehiculos 
                ADD COLUMN capacidad_litros INTEGER
            """)
            print("✅ Campo capacidad_litros agregado")
        else:
            print("ℹ️ Campo capacidad_litros ya existe")
        
        # Actualizar el vehículo VXG678 con datos de ejemplo
        cursor.execute("""
            UPDATE maestro_vehiculos 
            SET tipo_vehiculo = 'Carrotanque', 
                capacidad_litros = 35000 
            WHERE placa = 'VXG678'
        """)
        
        if cursor.rowcount > 0:
            print("✅ Vehículo VXG678 actualizado con datos de ejemplo")
        
        conn.commit()
        print("✅ Migración completada exitosamente")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error en la migración: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
