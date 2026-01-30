#!/usr/bin/env python3
"""
Migración: Asegurar que pesajes_bruto tenga todos los campos necesarios
como tabla principal del sistema (reemplazando entry_records)

Este script verifica y agrega campos faltantes en pesajes_bruto
para que funcione como tabla principal.

Uso:
    python migrations/ensure_pesajes_bruto_fields.py
"""

import sqlite3
import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_column_exists(conn, table_name, column_name):
    """Verificar si una columna existe en una tabla"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def main():
    print("🔧 MIGRACIÓN: Asegurar campos en pesajes_bruto")
    print("=" * 60)
    
    try:
        # Usar la ruta de la base de datos principal
        db_path = 'instance/oleoflores_dev.db'
        
        if not os.path.exists(db_path):
            print(f"❌ Base de datos no encontrada: {db_path}")
            return False
        
        print(f"📂 Usando base de datos: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la tabla pesajes_bruto existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pesajes_bruto'")
        if not cursor.fetchone():
            print("❌ La tabla 'pesajes_bruto' no existe")
            return False
        
        print("✅ Tabla 'pesajes_bruto' encontrada")
        
        # Campos adicionales que podrían necesitarse en pesajes_bruto
        # para funcionar como tabla principal
        additional_fields = [
            ('cantidad_racimos', 'INTEGER'),
            ('placa', 'TEXT'),
            ('transportador', 'TEXT'),
            ('conductor', 'TEXT'),
            ('num_cedula', 'TEXT'),
            ('num_placa', 'TEXT'),
            ('codigo_transportador', 'TEXT'),
            ('tipo_fruta', 'TEXT'),
            ('acarreo', 'TEXT'),
            ('cargo', 'TEXT'),
            ('nota', 'TEXT'),
            ('lote', 'TEXT'),
            ('image_filename', 'TEXT'),
            ('pdf_filename', 'TEXT'),
            ('qr_filename', 'TEXT'),
            ('modified_fields', 'TEXT'),
            ('fecha_tiquete', 'TEXT'),
            ('is_madre', 'INTEGER DEFAULT 0'),
            ('hijas_str', 'TEXT'),
            ('is_active', 'INTEGER DEFAULT 1'),
            ('estado', 'TEXT DEFAULT "activo"'),
            ('timestamp_registro_utc', 'TEXT')
        ]
        
        added_fields = []
        existing_fields = []
        
        for field_name, field_type in additional_fields:
            if check_column_exists(conn, 'pesajes_bruto', field_name):
                existing_fields.append(field_name)
            else:
                try:
                    cursor.execute(f"ALTER TABLE pesajes_bruto ADD COLUMN {field_name} {field_type}")
                    added_fields.append(field_name)
                    print(f"  ✅ Agregado campo: {field_name} ({field_type})")
                except sqlite3.Error as e:
                    print(f"  ❌ Error agregando {field_name}: {e}")
        
        if added_fields:
            conn.commit()
            print(f"\n🔧 Se agregaron {len(added_fields)} campos nuevos")
        
        if existing_fields:
            print(f"ℹ️  {len(existing_fields)} campos ya existían")
        
        # Verificar estructura final
        cursor.execute("PRAGMA table_info(pesajes_bruto)")
        columns = cursor.fetchall()
        
        print(f"\n📊 Estructura final de pesajes_bruto ({len(columns)} columnas):")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM pesajes_bruto")
        count = cursor.fetchone()[0]
        print(f"\n📈 Total de registros: {count}")
        
        conn.close()
        print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN MIGRACIÓN: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 