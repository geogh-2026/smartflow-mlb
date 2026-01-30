#!/usr/bin/env python3
"""
Migración: Agregar tabla de aprobaciones de ingreso de sellos y nuevos estados
Fecha: 2025-08-20
"""

import sqlite3
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def ejecutar_migracion():
    """Ejecutar la migración para agregar aprobaciones de ingreso"""
    
    # Determinar la ruta de la base de datos
    if os.path.exists('instance/oleoflores_dev.db'):
        db_path = 'instance/oleoflores_dev.db'
    elif os.path.exists('/home/epabon/oleoflores_smart_flow/instance/oleoflores_production.db'):
        db_path = '/home/epabon/oleoflores_smart_flow/instance/oleoflores_production.db'
    else:
        print("❌ No se encontró la base de datos")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"🔄 Ejecutando migración en: {db_path}")
        
        # 1. Crear tabla de aprobaciones de ingreso
        print("📝 Creando tabla aprobaciones_ingreso_sellos...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aprobaciones_ingreso_sellos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lote_ingreso VARCHAR(100) NOT NULL,
                cantidad_sellos INTEGER NOT NULL,
                rango_inicial VARCHAR(50) NOT NULL,
                rango_final VARCHAR(50) NOT NULL,
                tipo_sello_id INTEGER,
                usuario_solicita VARCHAR(100) NOT NULL,
                fecha_solicitud DATETIME DEFAULT CURRENT_TIMESTAMP,
                observaciones_solicitud TEXT,
                estado VARCHAR(50) DEFAULT 'pendiente',
                usuario_aprueba VARCHAR(100),
                fecha_aprobacion DATETIME,
                observaciones_aprobacion TEXT,
                FOREIGN KEY (tipo_sello_id) REFERENCES tipos_sello (id)
            )
        ''')
        
        # 2. Verificar si necesitamos actualizar el enum de estados
        print("🔄 Verificando estados de sellos...")
        cursor.execute("SELECT DISTINCT estado FROM sellos LIMIT 5")
        estados_existentes = [row[0] for row in cursor.fetchall()]
        print(f"Estados encontrados: {estados_existentes}")
        
        # Los nuevos estados se manejarán automáticamente por SQLAlchemy
        # ya que los enums en SQLite se almacenan como strings
        
        conn.commit()
        print("✅ Migración completada exitosamente")
        
        # Verificar la tabla creada
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='aprobaciones_ingreso_sellos'")
        if cursor.fetchone():
            print("✅ Tabla aprobaciones_ingreso_sellos creada correctamente")
        else:
            print("❌ Error: Tabla no fue creada")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Iniciando migración: Aprobaciones de Ingreso de Sellos")
    print("=" * 60)
    
    if ejecutar_migracion():
        print("=" * 60)
        print("✅ Migración completada exitosamente")
    else:
        print("=" * 60)
        print("❌ Migración falló")
        sys.exit(1)
