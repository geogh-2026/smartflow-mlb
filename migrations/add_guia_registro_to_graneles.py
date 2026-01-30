#!/usr/bin/env python3
"""
Migración: Agregar campo 'guia_registro' a tabla RegistroEntradaGraneles
Fecha: 2025-01-30
Descripción: Agrega el campo guia_registro para generar códigos únicos tipo GR-YYYYMMDD-XXXX
"""

import sqlite3
import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path para importar módulos de la app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def ejecutar_migracion(db_path):
    """Ejecutar la migración para agregar guia_registro"""
    print(f"🔄 Iniciando migración en: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(RegistroEntradaGraneles)")
        columnas = [columna[1] for columna in cursor.fetchall()]
        
        if 'guia_registro' in columnas:
            print("✅ La columna 'guia_registro' ya existe en RegistroEntradaGraneles")
            return True
        
        print("📝 Agregando columna 'guia_registro' a RegistroEntradaGraneles...")
        
        # Agregar la nueva columna
        cursor.execute("""
            ALTER TABLE RegistroEntradaGraneles 
            ADD COLUMN guia_registro TEXT
        """)
        
        # Generar guías para registros existentes
        print("🔢 Generando guías para registros existentes...")
        cursor.execute("SELECT id, timestamp_registro FROM RegistroEntradaGraneles ORDER BY id")
        registros = cursor.fetchall()
        
        for registro_id, timestamp_registro in registros:
            # Usar la fecha del registro si existe, sino la fecha actual
            if timestamp_registro:
                try:
                    fecha_registro = datetime.fromisoformat(timestamp_registro.replace('Z', '+00:00'))
                    fecha_str = fecha_registro.strftime("%Y%m%d")
                except:
                    fecha_str = datetime.now().strftime("%Y%m%d")
            else:
                fecha_str = datetime.now().strftime("%Y%m%d")
            
            # Generar guía con formato: GR-YYYYMMDD-ID_con_padding
            guia_registro = f"GR-{fecha_str}-{registro_id:04d}"
            
            cursor.execute("""
                UPDATE RegistroEntradaGraneles 
                SET guia_registro = ? 
                WHERE id = ?
            """, (guia_registro, registro_id))
            
            print(f"  ✓ ID {registro_id}: {guia_registro}")
        
        # Crear índice único para la nueva columna
        print("📚 Creando índice único para guia_registro...")
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_guia_registro 
            ON RegistroEntradaGraneles(guia_registro)
        """)
        
        conn.commit()
        print("✅ Migración completada exitosamente")
        
        # Verificar resultados
        cursor.execute("SELECT COUNT(*) FROM RegistroEntradaGraneles WHERE guia_registro IS NOT NULL")
        registros_con_guia = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM RegistroEntradaGraneles")
        total_registros = cursor.fetchone()[0]
        
        print(f"📊 Resumen: {registros_con_guia}/{total_registros} registros con guía asignada")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """Función principal de la migración"""
    print("🚀 Migración: Agregar guia_registro a RegistroEntradaGraneles")
    print("=" * 60)
    
    # Determinar la ruta de la base de datos
    db_path = os.environ.get('TIQUETES_DB_PATH')
    if not db_path:
        # Buscar la base de datos en ubicaciones comunes
        posibles_rutas = [
            'tiquetes.db',
            'instance/tiquetes.db',
            '../tiquetes.db',
            '../instance/tiquetes.db'
        ]
        
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                db_path = ruta
                break
        
        if not db_path:
            print("❌ No se pudo encontrar la base de datos tiquetes.db")
            print("   Ubicaciones buscadas:", posibles_rutas)
            return False
    
    if not os.path.exists(db_path):
        print(f"❌ No se encontró la base de datos en: {db_path}")
        return False
    
    print(f"📍 Base de datos encontrada: {db_path}")
    
    # Crear backup antes de la migración
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"💾 Backup creado: {backup_path}")
    except Exception as e:
        print(f"⚠️  No se pudo crear backup: {e}")
        respuesta = input("¿Continuar sin backup? (y/N): ")
        if respuesta.lower() != 'y':
            return False
    
    # Ejecutar migración
    exito = ejecutar_migracion(db_path)
    
    if exito:
        print("\n🎉 ¡Migración completada exitosamente!")
        print("📝 La columna 'guia_registro' se agregó a RegistroEntradaGraneles")
        print("🔢 Se generaron guías para todos los registros existentes")
    else:
        print("\n❌ La migración falló")
        if os.path.exists(backup_path):
            print(f"💾 Puedes restaurar desde: {backup_path}")
    
    return exito

if __name__ == "__main__":
    main()