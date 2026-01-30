#!/usr/bin/env python3
"""
Script rápido para crear la tabla enturnamientos_graneles que está faltando en producción.

Este script es específico para solucionar el error:
"no such table: enturnamientos_graneles"

Uso:
    python3 fix_missing_table_production.py
"""

import os
import sqlite3
import sys

# Configuración para producción
DB_PATH = os.environ.get('TIQUETES_DB_PATH', 'instance/oleoflores_prod.db')

def create_enturnamientos_table():
    """Crear solo la tabla enturnamientos_graneles que está faltando"""
    
    print(f"🔧 Creando tabla enturnamientos_graneles...")
    print(f"📍 Base de datos: {DB_PATH}")
    
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Crear la tabla enturnamientos_graneles
        sql = '''
        CREATE TABLE IF NOT EXISTS enturnamientos_graneles (
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
        );
        '''
        
        cursor.execute(sql)
        
        # Crear índices para optimizar consultas
        indices = [
            'CREATE INDEX IF NOT EXISTS idx_enturnamientos_placa_estado ON enturnamientos_graneles(placa, estado)',
            'CREATE INDEX IF NOT EXISTS idx_enturnamientos_timestamp ON enturnamientos_graneles(timestamp_enturnado)'
        ]
        
        for idx_sql in indices:
            cursor.execute(idx_sql)
        
        # Confirmar cambios
        conn.commit()
        
        print("✅ Tabla enturnamientos_graneles creada exitosamente")
        print("✅ Índices aplicados")
        
        # Verificar que la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='enturnamientos_graneles'")
        result = cursor.fetchone()
        
        if result:
            print("✅ Verificación: La tabla existe en la base de datos")
            return True
        else:
            print("❌ Error: La tabla no se encontró después de crearla")
            return False
        
    except Exception as e:
        print(f"❌ Error creando tabla: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def main():
    """Función principal"""
    
    print("=" * 60)
    print("🔧 FIX RÁPIDO: Crear tabla enturnamientos_graneles")
    print("=" * 60)
    
    success = create_enturnamientos_table()
    
    if success:
        print("\n🎉 ¡Tabla creada exitosamente!")
        print("\n📋 Próximos pasos:")
        print("   1. Reiniciar la aplicación en producción")
        print("   2. Probar el enturnamiento de graneles")
        print("   3. Si hay más tablas faltantes, ejecutar: create_graneles_tables_production.py")
        return True
    else:
        print("\n❌ Error creando la tabla. Revisa los mensajes anteriores.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
