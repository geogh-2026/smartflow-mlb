#!/usr/bin/env python3
"""
Migración: Agregar campo password_encrypted a la tabla users
Fecha: 2024-09-02
Descripción: Agrega el campo password_encrypted para permitir visualización de contraseñas por admin
"""

import sqlite3
import os
import sys
from datetime import datetime

def add_password_encrypted_field():
    """Agregar campo password_encrypted a la tabla users"""
    
    # Rutas de las bases de datos
    databases = [
        'instance/oleoflores_dev.db',
        'instance/oleoflores_prod.db',
        'instance/oleoflores_smart_flow.db'
    ]
    
    for db_path in databases:
        if not os.path.exists(db_path):
            print(f"⚠️  Base de datos no encontrada: {db_path}")
            continue
            
        print(f"🔄 Procesando: {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar si la columna ya existe
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'password_encrypted' in columns:
                print(f"✅ Campo 'password_encrypted' ya existe en {db_path}")
                conn.close()
                continue
            
            # Agregar la nueva columna
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN password_encrypted TEXT
            """)
            
            conn.commit()
            print(f"✅ Campo 'password_encrypted' agregado exitosamente a {db_path}")
            
        except sqlite3.Error as e:
            print(f"❌ Error en {db_path}: {e}")
            
        finally:
            if conn:
                conn.close()

def main():
    """Función principal"""
    print("=" * 60)
    print("MIGRACIÓN: Agregar campo password_encrypted")
    print("=" * 60)
    
    # Cambiar al directorio del proyecto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    os.chdir(project_dir)
    
    print(f"📁 Directorio de trabajo: {os.getcwd()}")
    
    # Ejecutar migración
    add_password_encrypted_field()
    
    print("\n" + "=" * 60)
    print("✅ MIGRACIÓN COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    main()
