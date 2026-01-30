#!/usr/bin/env python3
"""
Script para agregar columnas faltantes a la tabla RegistroEntradaGraneles en producción.

Este script resuelve el error:
"no such column: RegistroEntradaGraneles.guia_registro"

Agrega todas las columnas que pueden estar faltantes en la tabla RegistroEntradaGraneles.

Uso:
    python3 fix_registro_graneles_columns.py
"""

import os
import sqlite3
import sys

# Configuración para producción
DB_PATH = os.environ.get('TIQUETES_DB_PATH', 'instance/oleoflores_prod.db')

def check_existing_columns():
    """Verificar qué columnas existen actualmente en RegistroEntradaGraneles"""
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Obtener información de columnas existentes
        cursor.execute("PRAGMA table_info(RegistroEntradaGraneles)")
        columns_info = cursor.fetchall()
        
        existing_columns = [col[1] for col in columns_info]  # col[1] es el nombre de la columna
        
        print(f"🔍 Columnas existentes en RegistroEntradaGraneles:")
        for col in existing_columns:
            print(f"   ✅ {col}")
        
        return existing_columns
        
    except Exception as e:
        print(f"❌ Error verificando columnas: {e}")
        return []
    finally:
        if conn:
            conn.close()

def add_missing_columns():
    """Agregar columnas faltantes a RegistroEntradaGraneles"""
    
    print(f"🔧 Agregando columnas faltantes a RegistroEntradaGraneles...")
    print(f"📍 Base de datos: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ La base de datos no existe: {DB_PATH}")
        return False
    
    # Obtener columnas existentes
    existing_columns = check_existing_columns()
    
    # Definir todas las columnas que deberían existir
    required_columns = {
        'guia_registro': 'TEXT',
        'tipo_cargue': 'TEXT DEFAULT "Cargue"',
        'tipo_formulario': 'TEXT DEFAULT "Graneles Cliente"',
        'flete': 'TEXT',
        'pedido': 'TEXT',
        'localidad': 'TEXT',
        'transportadora_inspeccion': 'TEXT',
        'arl': 'TEXT',
        'eps': 'TEXT',
        'celular_inspeccion': 'TEXT',
        'vencimiento_arl': 'TEXT',
        'vencimiento_soat': 'TEXT',
        'vencimiento_tecnomecanica': 'TEXT',
        'vencimiento_licencia': 'TEXT',
        'foto_arl': 'TEXT',
        'foto_soat': 'TEXT',
        'foto_tecnomecanica': 'TEXT',
        'foto_licencia': 'TEXT',
        'observaciones_documentos': 'TEXT',
        'estado_registro': 'TEXT DEFAULT "registrado"',
        'timestamp_registro': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'tipo_registro': 'TEXT',
        'observaciones': 'TEXT',
        'usuario_registro': 'TEXT'
    }
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Identificar columnas faltantes
        missing_columns = []
        for col_name, col_type in required_columns.items():
            if col_name not in existing_columns:
                missing_columns.append((col_name, col_type))
        
        if not missing_columns:
            print("✅ Todas las columnas requeridas ya existen")
            return True
        
        print(f"\n🔧 Columnas faltantes encontradas: {len(missing_columns)}")
        
        # Agregar cada columna faltante
        for col_name, col_type in missing_columns:
            try:
                sql = f"ALTER TABLE RegistroEntradaGraneles ADD COLUMN {col_name} {col_type}"
                cursor.execute(sql)
                print(f"   ✅ Agregada: {col_name} ({col_type})")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print(f"   ⚠️  Ya existe: {col_name}")
                else:
                    print(f"   ❌ Error agregando {col_name}: {e}")
                    return False
        
        # Confirmar cambios
        conn.commit()
        
        print(f"\n✅ Columnas agregadas exitosamente")
        
        # Verificar que todas las columnas ahora existen
        print(f"\n🔍 Verificando columnas después de la migración...")
        final_columns = check_existing_columns()
        
        missing_after = []
        for col_name in required_columns.keys():
            if col_name not in final_columns:
                missing_after.append(col_name)
        
        if missing_after:
            print(f"❌ Aún faltan columnas: {missing_after}")
            return False
        else:
            print(f"✅ Todas las columnas requeridas están presentes")
            return True
        
    except Exception as e:
        print(f"❌ Error agregando columnas: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def create_unique_index():
    """Crear índice único para guia_registro si no existe"""
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Crear índice único para guia_registro
        sql = "CREATE UNIQUE INDEX IF NOT EXISTS idx_registro_guia_unica ON RegistroEntradaGraneles(guia_registro)"
        cursor.execute(sql)
        
        # Crear otros índices útiles
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_registro_placa ON RegistroEntradaGraneles(placa)",
            "CREATE INDEX IF NOT EXISTS idx_registro_estado ON RegistroEntradaGraneles(estado_registro)",
            "CREATE INDEX IF NOT EXISTS idx_registro_timestamp ON RegistroEntradaGraneles(timestamp_registro)",
            "CREATE INDEX IF NOT EXISTS idx_registro_tipo_cargue ON RegistroEntradaGraneles(tipo_cargue)"
        ]
        
        for idx_sql in indices:
            cursor.execute(idx_sql)
        
        conn.commit()
        print("✅ Índices creados/actualizados")
        return True
        
    except Exception as e:
        print(f"⚠️  Error creando índices: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """Función principal"""
    
    print("=" * 70)
    print("🔧 FIX: Agregar columnas faltantes a RegistroEntradaGraneles")
    print("=" * 70)
    
    # Verificar que la tabla existe
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='RegistroEntradaGraneles'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ La tabla RegistroEntradaGraneles no existe")
            print("💡 Ejecuta primero: python3 create_graneles_tables_production.py")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando tabla: {e}")
        return False
    finally:
        if conn:
            conn.close()
    
    # Agregar columnas faltantes
    success = add_missing_columns()
    
    if success:
        # Crear índices
        create_unique_index()
        
        print("\n" + "=" * 70)
        print("🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print("=" * 70)
        print("\n✅ Todas las columnas han sido agregadas a RegistroEntradaGraneles")
        print("✅ Los índices han sido creados para optimizar consultas")
        
        print("\n📋 Próximos pasos:")
        print("   1. Reiniciar la aplicación en producción")
        print("   2. Probar el registro de entrada de graneles")
        print("   3. Verificar que no hay más errores de columnas faltantes")
        
        return True
    else:
        print("\n❌ La migración falló. Revisa los errores anteriores.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
