#!/usr/bin/env python3
"""
Script para verificar qué tablas existen en la base de datos de producción
"""

import sqlite3
import os
import sys

def check_production_db():
    """Verificar tablas en base de datos de producción"""
    
    # Probar diferentes rutas de BD que podrían existir
    possible_dbs = [
        'instance/oleoflores_prod.db',
        'instance/oleoflores_dev.db',
        'instance/tiquetes.db',
        'tiquetes.db',
        'database.db'
    ]
    
    print("🔍 VERIFICANDO BASES DE DATOS EN PRODUCCIÓN")
    print("=" * 60)
    
    for db_path in possible_dbs:
        print(f"\n📂 Verificando: {db_path}")
        
        if not os.path.exists(db_path):
            print(f"   ❌ No existe")
            continue
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Obtener todas las tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            
            if not tables:
                print(f"   ⚠️  Base de datos vacía")
                conn.close()
                continue
                
            print(f"   ✅ {len(tables)} tablas encontradas:")
            
            for table in tables:
                table_name = table[0]
                
                # Contar registros en cada tabla
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"      - {table_name}: {count} registros")
                    
                    # Si encontramos una tabla que parece ser la principal, mostrar estructura
                    if table_name in ['pesajes_bruto', 'entry_records', 'tiquetes_info']:
                        print(f"         📋 Estructura de {table_name}:")
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = cursor.fetchall()
                        for col in columns[:10]:  # Solo primeras 10 columnas
                            print(f"            • {col[1]} ({col[2]})")
                        if len(columns) > 10:
                            print(f"            ... y {len(columns) - 10} columnas más")
                            
                except Exception as e:
                    print(f"      - {table_name}: Error contando registros")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Error accediendo BD: {e}")
    
    print(f"\n🎯 RECOMENDACIÓN:")
    print(f"Use la base de datos con más registros y que contenga las tablas principales")

if __name__ == "__main__":
    check_production_db() 