#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla RegistroEntradaGraneles.

Este script muestra qué columnas existen y cuáles faltan en la tabla RegistroEntradaGraneles.

Uso:
    python3 check_registro_graneles_structure.py
"""

import os
import sqlite3
import sys

# Configuración para producción
DB_PATH = os.environ.get('TIQUETES_DB_PATH', 'instance/oleoflores_prod.db')

def check_table_structure():
    """Verificar la estructura completa de RegistroEntradaGraneles"""
    
    print(f"🔍 Verificando estructura de RegistroEntradaGraneles...")
    print(f"📍 Base de datos: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ La base de datos no existe: {DB_PATH}")
        return False
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar que la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='RegistroEntradaGraneles'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ La tabla RegistroEntradaGraneles no existe")
            return False
        
        print("✅ La tabla RegistroEntradaGraneles existe")
        
        # Obtener información de columnas existentes
        cursor.execute("PRAGMA table_info(RegistroEntradaGraneles)")
        columns_info = cursor.fetchall()
        
        existing_columns = {}
        for col in columns_info:
            # col = (cid, name, type, notnull, dflt_value, pk)
            existing_columns[col[1]] = {
                'type': col[2],
                'not_null': bool(col[3]),
                'default': col[4],
                'primary_key': bool(col[5])
            }
        
        # Definir columnas requeridas
        required_columns = {
            'id': 'INTEGER',
            'guia_registro': 'TEXT',
            'producto': 'TEXT',
            'fecha_autorizacion': 'TEXT',
            'placa': 'TEXT',
            'trailer': 'TEXT',
            'cedula_conductor': 'TEXT',
            'nombre_conductor': 'TEXT',
            'telefono_conductor': 'TEXT',
            'transportadora': 'TEXT',
            'cliente': 'TEXT',
            'tipo_venta': 'TEXT',
            'origen': 'TEXT',
            'destino': 'TEXT',
            'kg_cargar': 'TEXT',
            'tipo_cargue': 'TEXT',
            'tipo_formulario': 'TEXT',
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
            'estado_registro': 'TEXT',
            'timestamp_registro': 'DATETIME',
            'tipo_registro': 'TEXT',
            'observaciones': 'TEXT',
            'usuario_registro': 'TEXT'
        }
        
        print(f"\n📊 ANÁLISIS DE COLUMNAS:")
        print("=" * 80)
        
        existing_cols = []
        missing_cols = []
        
        for col_name, expected_type in required_columns.items():
            if col_name in existing_columns:
                existing_cols.append(col_name)
                col_info = existing_columns[col_name]
                print(f"✅ {col_name:<30} | {col_info['type']:<15} | {'PK' if col_info['primary_key'] else 'Normal'}")
            else:
                missing_cols.append(col_name)
                print(f"❌ {col_name:<30} | {expected_type:<15} | FALTANTE")
        
        # Mostrar columnas extra (que existen pero no están en la lista requerida)
        extra_cols = []
        for col_name in existing_columns.keys():
            if col_name not in required_columns:
                extra_cols.append(col_name)
                col_info = existing_columns[col_name]
                print(f"📋 {col_name:<30} | {col_info['type']:<15} | Extra")
        
        print("\n" + "=" * 80)
        print(f"📈 RESUMEN:")
        print(f"   ✅ Columnas existentes: {len(existing_cols)}/{len(required_columns)}")
        print(f"   ❌ Columnas faltantes: {len(missing_cols)}")
        print(f"   📋 Columnas extra: {len(extra_cols)}")
        
        if missing_cols:
            print(f"\n🚨 COLUMNAS FALTANTES:")
            for col in missing_cols:
                print(f"   - {col}")
            
            print(f"\n💡 SOLUCIÓN:")
            print(f"   🔧 Ejecuta: python3 fix_registro_graneles_columns.py")
        else:
            print(f"\n🎉 ¡Todas las columnas requeridas están presentes!")
        
        if extra_cols:
            print(f"\n📋 COLUMNAS EXTRA (no requeridas pero presentes):")
            for col in extra_cols:
                print(f"   - {col}")
        
        # Verificar índices
        print(f"\n🔍 ÍNDICES EXISTENTES:")
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='RegistroEntradaGraneles'")
        indices = cursor.fetchall()
        
        if indices:
            for idx in indices:
                if idx[0] and not idx[0].startswith('sqlite_'):  # Excluir índices automáticos
                    print(f"   ✅ {idx[0]}")
        else:
            print(f"   ⚠️  No se encontraron índices personalizados")
        
        return len(missing_cols) == 0
        
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """Función principal"""
    
    print("=" * 80)
    print("🔍 VERIFICADOR DE ESTRUCTURA: RegistroEntradaGraneles")
    print("=" * 80)
    
    success = check_table_structure()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ Estructura verificada - Tabla completa")
    else:
        print("⚠️  Estructura verificada - Requiere corrección")
    print("=" * 80)
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
