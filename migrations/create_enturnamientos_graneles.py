#!/usr/bin/env python3
"""
Migración: Crear tabla de enturnamientos para módulo de graneles

Tabla: enturnamientos_graneles
Campos:
- id INTEGER PK
- placa TEXT NOT NULL
- foto_path TEXT
- timestamp_enturnado DATETIME DEFAULT CURRENT_TIMESTAMP
- estado TEXT DEFAULT 'en_turno'   -- en_turno, en_registro, registrado, cancelado, inactivo
- usuario_guardia TEXT
- observacion TEXT
- registro_entrada_id INTEGER  -- FK lógica a RegistroEntradaGraneles.id
- timestamp_asignado_recepcionista DATETIME
- usuario_recepcionista TEXT

Índices:
- idx_enturnamientos_placa_estado (placa, estado)
- idx_enturnamientos_timestamp (timestamp_enturnado)

Nota: Usa la misma BD definida por TIQUETES_DB_PATH (instance/oleoflores_dev.db por defecto)
"""

import os
import sqlite3

DB_PATH = os.environ.get('TIQUETES_DB_PATH', 'instance/oleoflores_dev.db')


def create_table():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute(
            '''
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
            )
            '''
        )

        indices = [
            'CREATE INDEX IF NOT EXISTS idx_enturnamientos_placa_estado ON enturnamientos_graneles(placa, estado)',
            'CREATE INDEX IF NOT EXISTS idx_enturnamientos_timestamp ON enturnamientos_graneles(timestamp_enturnado)'
        ]
        for idx in indices:
            cur.execute(idx)

        conn.commit()
        print('✅ Tabla enturnamientos_graneles creada/actualizada')
        return True
    except Exception as e:
        print(f'❌ Error creando tabla enturnamientos_graneles: {e}')
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def main():
    print('🚀 Ejecutando migración: enturnamientos_graneles...')
    ok = create_table()
    if ok:
        print('🎉 Migración completada')
    else:
        print('❌ Migración fallida')
    return ok


if __name__ == '__main__':
    main()


