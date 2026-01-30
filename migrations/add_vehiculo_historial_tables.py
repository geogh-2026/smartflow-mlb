#!/usr/bin/env python3
"""
Migración: Agregar Tablas de Historial de Vehículos
Fecha: 20 de enero de 2025
Descripción: Nuevas tablas para historial de conductores y observaciones de vehículos
"""

import sqlite3
import os
from datetime import datetime

def crear_tablas_historial_vehiculos():
    """Crear las nuevas tablas para historial de vehículos."""
    
    # Ruta de la base de datos
    db_path = 'instance/oleoflores_dev.db'
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Creando tablas de historial de vehículos...")
        
        # 1. Tabla de historial de conductores por vehículo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehiculo_conductores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                placa_vehiculo TEXT NOT NULL,
                conductor_cedula TEXT NOT NULL,
                conductor_nombre TEXT NOT NULL,
                conductor_telefono TEXT,
                conductor_empresa TEXT,
                fecha_desde DATETIME NOT NULL,
                fecha_hasta DATETIME,
                activo BOOLEAN DEFAULT 1,
                observaciones TEXT,
                usuario_registro TEXT NOT NULL,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (placa_vehiculo) REFERENCES maestro_vehiculos(placa)
            )
        ''')
        
        # 2. Tabla de historial de observaciones de vehículos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehiculo_observaciones_historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                placa_vehiculo TEXT NOT NULL,
                tipo_observacion TEXT NOT NULL,  -- 'cambio_sellos', 'inspeccion', 'mantenimiento', 'incidente'
                observacion TEXT NOT NULL,
                cantidad_sellos_anterior INTEGER,
                cantidad_sellos_nueva INTEGER,
                motivo_cambio TEXT,
                usuario_observacion TEXT NOT NULL,
                fecha_observacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                solicitud_id INTEGER,  -- Referencia a la solicitud que generó la observación
                aprobado_por TEXT,
                fecha_aprobacion DATETIME,
                FOREIGN KEY (placa_vehiculo) REFERENCES maestro_vehiculos(placa),
                FOREIGN KEY (solicitud_id) REFERENCES solicitudes_sello(id)
            )
        ''')
        
        # 3. Tabla de aprobaciones para cambios de sellos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehiculo_aprobaciones_sellos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                solicitud_id INTEGER NOT NULL,
                placa_vehiculo TEXT NOT NULL,
                cantidad_actual INTEGER NOT NULL,      -- Cantidad en hoja de vida
                cantidad_solicitada INTEGER NOT NULL,  -- Cantidad solicitada por inspector
                diferencia INTEGER NOT NULL,           -- Diferencia calculada
                justificacion TEXT NOT NULL,           -- Justificación del inspector
                
                -- Estados: 'pendiente', 'aprobada', 'rechazada'
                estado TEXT DEFAULT 'pendiente',
                
                -- Datos del solicitante
                inspector_usuario TEXT NOT NULL,
                fecha_solicitud DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                -- Datos del aprobador (Jefe de Calidad)
                jefe_usuario TEXT,
                fecha_aprobacion DATETIME,
                observaciones_aprobacion TEXT,
                
                FOREIGN KEY (solicitud_id) REFERENCES solicitudes_sello(id),
                FOREIGN KEY (placa_vehiculo) REFERENCES maestro_vehiculos(placa)
            )
        ''')
        
        # 4. Índices para optimizar consultas
        indices = [
            'CREATE INDEX IF NOT EXISTS idx_vehiculo_conductores_placa ON vehiculo_conductores(placa_vehiculo)',
            'CREATE INDEX IF NOT EXISTS idx_vehiculo_conductores_activo ON vehiculo_conductores(activo)',
            'CREATE INDEX IF NOT EXISTS idx_vehiculo_conductores_fechas ON vehiculo_conductores(fecha_desde, fecha_hasta)',
            
            'CREATE INDEX IF NOT EXISTS idx_vehiculo_observaciones_placa ON vehiculo_observaciones_historial(placa_vehiculo)',
            'CREATE INDEX IF NOT EXISTS idx_vehiculo_observaciones_fecha ON vehiculo_observaciones_historial(fecha_observacion)',
            'CREATE INDEX IF NOT EXISTS idx_vehiculo_observaciones_tipo ON vehiculo_observaciones_historial(tipo_observacion)',
            
            'CREATE INDEX IF NOT EXISTS idx_vehiculo_aprobaciones_solicitud ON vehiculo_aprobaciones_sellos(solicitud_id)',
            'CREATE INDEX IF NOT EXISTS idx_vehiculo_aprobaciones_estado ON vehiculo_aprobaciones_sellos(estado)',
            'CREATE INDEX IF NOT EXISTS idx_vehiculo_aprobaciones_placa ON vehiculo_aprobaciones_sellos(placa_vehiculo)'
        ]
        
        for indice in indices:
            cursor.execute(indice)
        
        conn.commit()
        print("✅ Tablas de historial de vehículos creadas exitosamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando tablas de historial: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()

def agregar_campos_solicitudes():
    """Agregar campos necesarios a la tabla solicitudes_sello."""
    
    db_path = 'instance/oleoflores_dev.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Agregando campos a solicitudes_sello...")
        
        # Campos para integración con módulo de entrada
        nuevos_campos = [
            'ALTER TABLE solicitudes_sello ADD COLUMN conductor_cedula TEXT',
            'ALTER TABLE solicitudes_sello ADD COLUMN conductor_nombre TEXT', 
            'ALTER TABLE solicitudes_sello ADD COLUMN actualizar_hoja_vida BOOLEAN DEFAULT 1',
            'ALTER TABLE solicitudes_sello ADD COLUMN requiere_aprobacion_sellos BOOLEAN DEFAULT 0',
            'ALTER TABLE solicitudes_sello ADD COLUMN aprobacion_sellos_id INTEGER'
        ]
        
        for campo in nuevos_campos:
            try:
                cursor.execute(campo)
                print(f"  ✅ {campo.split('ADD COLUMN')[1].split()[0]} agregado")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"  ⏭️  {campo.split('ADD COLUMN')[1].split()[0]} ya existe")
                else:
                    print(f"  ❌ Error: {e}")
        
        conn.commit()
        print("✅ Campos agregados a solicitudes_sello")
        
        return True
        
    except Exception as e:
        print(f"❌ Error agregando campos: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

def crear_datos_iniciales():
    """Crear algunos datos iniciales de prueba."""
    
    db_path = 'instance/oleoflores_dev.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Creando datos iniciales...")
        
        # Ejemplo de conductor histórico (si hay vehículos)
        cursor.execute("SELECT placa FROM maestro_vehiculos LIMIT 1")
        vehiculo = cursor.fetchone()
        
        if vehiculo:
            placa = vehiculo[0]
            cursor.execute('''
                INSERT OR IGNORE INTO vehiculo_conductores (
                    placa_vehiculo, conductor_cedula, conductor_nombre,
                    conductor_telefono, conductor_empresa, fecha_desde,
                    usuario_registro
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (placa, '12345678', 'Juan Pérez Ejemplo', '3001234567', 
                  'Transportes ABC', datetime.now(), 'admin'))
            
            print(f"  ✅ Conductor ejemplo agregado para vehículo {placa}")
        
        conn.commit()
        print("✅ Datos iniciales creados")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando datos iniciales: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

def main():
    """Ejecutar todas las migraciones."""
    print("🚀 Iniciando migración de historial de vehículos...")
    print("=" * 60)
    
    success = True
    
    # 1. Crear nuevas tablas
    if not crear_tablas_historial_vehiculos():
        success = False
    
    # 2. Agregar campos a solicitudes
    if not agregar_campos_solicitudes():
        success = False
    
    # 3. Crear datos iniciales
    if not crear_datos_iniciales():
        success = False
    
    print("=" * 60)
    if success:
        print("🎉 Migración de historial de vehículos completada exitosamente!")
        print("\nNuevas tablas creadas:")
        print("  📋 vehiculo_conductores - Historial de conductores por vehículo")
        print("  📝 vehiculo_observaciones_historial - Observaciones y cambios")
        print("  ✅ vehiculo_aprobaciones_sellos - Aprobaciones de cambios")
        print("\nCampos agregados a solicitudes_sello:")
        print("  👤 conductor_cedula, conductor_nombre")
        print("  ☑️  actualizar_hoja_vida, requiere_aprobacion_sellos")
    else:
        print("❌ Hubo errores durante la migración. Revisa los mensajes anteriores.")
    
    return success

if __name__ == "__main__":
    main() 