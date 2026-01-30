#!/usr/bin/env python3
"""
Script para verificar qué tablas del sistema de graneles existen en la base de datos.

Este script te ayuda a identificar qué tablas faltan antes de ejecutar las migraciones.

Uso:
    python3 check_graneles_tables.py
"""

import os
import sqlite3
import sys

# Configuración de base de datos
DB_PATH = os.environ.get('TIQUETES_DB_PATH', 'instance/oleoflores_prod.db')

def check_tables():
    """Verificar qué tablas del sistema de graneles existen"""
    
    print(f"🔍 Verificando tablas del sistema de graneles...")
    print(f"📍 Base de datos: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ La base de datos no existe: {DB_PATH}")
        return False
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Obtener lista de todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        all_tables = [table[0] for table in cursor.fetchall()]
        
        # Tablas requeridas para el sistema de graneles
        required_tables = [
            'RegistroEntradaGraneles',
            'enturnamientos_graneles',
            'PrimerPesajeGranel', 
            'CargueGranel',
            'PesajeBrutoGranel',
            'ControlCalidadGranel',
            'InspeccionVehiculo',
            'ResumenCargueGranel',
            'CertificadoAnalisis',
            'ManifiestoCarga',
            'TomaMuestraGranel',
            'remisiones',
            'codigos_despacho',
            'facturas'
        ]
        
        print(f"\n📊 ESTADO DE LAS TABLAS DEL SISTEMA DE GRANELES:")
        print("=" * 60)
        
        existing_tables = []
        missing_tables = []
        
        for table in required_tables:
            if table in all_tables:
                print(f"✅ {table}")
                existing_tables.append(table)
            else:
                print(f"❌ {table} - FALTANTE")
                missing_tables.append(table)
        
        print("\n" + "=" * 60)
        print(f"📈 RESUMEN:")
        print(f"   ✅ Tablas existentes: {len(existing_tables)}/{len(required_tables)}")
        print(f"   ❌ Tablas faltantes: {len(missing_tables)}")
        
        if missing_tables:
            print(f"\n🚨 TABLAS FALTANTES:")
            for table in missing_tables:
                print(f"   - {table}")
            
            print(f"\n💡 SOLUCIONES:")
            if 'enturnamientos_graneles' in missing_tables and len(missing_tables) == 1:
                print(f"   🔧 Solo falta una tabla. Ejecuta:")
                print(f"      python3 fix_missing_table_production.py")
            else:
                print(f"   🔧 Faltan múltiples tablas. Ejecuta:")
                print(f"      python3 create_graneles_tables_production.py")
        else:
            print(f"\n🎉 ¡Todas las tablas del sistema de graneles están presentes!")
        
        # Mostrar también otras tablas que existen
        other_tables = [t for t in all_tables if t not in required_tables]
        if other_tables:
            print(f"\n📋 OTRAS TABLAS EN LA BASE DE DATOS:")
            for table in other_tables[:10]:  # Mostrar solo las primeras 10
                print(f"   📋 {table}")
            if len(other_tables) > 10:
                print(f"   ... y {len(other_tables) - 10} más")
        
        return len(missing_tables) == 0
        
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """Función principal"""
    
    print("=" * 60)
    print("🔍 VERIFICADOR DE TABLAS DEL SISTEMA DE GRANELES")
    print("=" * 60)
    
    success = check_tables()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Verificación completada - Sistema listo")
    else:
        print("⚠️  Verificación completada - Requiere acción")
    print("=" * 60)
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
