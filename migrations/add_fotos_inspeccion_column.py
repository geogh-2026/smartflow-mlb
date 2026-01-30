#!/usr/bin/env python3
"""
Migración: Agregar columna 'foto_soporte_calidad_path' a InspeccionVehiculo

Guarda rutas (JSON) de hasta 3 fotos de observaciones capturadas por el guarda.
"""
import os
import sqlite3

DB_PATH = os.environ.get('TIQUETES_DB_PATH', 'instance/oleoflores_dev.db')

def run():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(InspeccionVehiculo)")
        cols = [r[1] for r in cur.fetchall()]
        if 'foto_soporte_calidad_path' not in cols:
            cur.execute("ALTER TABLE InspeccionVehiculo ADD COLUMN foto_soporte_calidad_path TEXT")
            conn.commit()
            print('✅ Columna foto_soporte_calidad_path agregada a InspeccionVehiculo')
        else:
            print('⏭️  Columna ya existe, no se realizan cambios')
    finally:
        conn.close()

if __name__ == '__main__':
    run()


