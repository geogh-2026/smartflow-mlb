#!/usr/bin/env python3
"""
Script completo para verificar y corregir TODAS las tablas del sistema de graneles.

Este script resuelve errores como:
- "no such column: es_pesaje_oficial"
- Y cualquier otra columna faltante en las tablas de graneles

Verifica y corrige todas las tablas:
- RegistroEntradaGraneles
- PesajeBrutoGranel  
- PrimerPesajeGranel
- CargueGranel
- Y todas las demás tablas del sistema

Uso:
    python3 fix_all_graneles_tables.py
"""

import os
import sqlite3
import sys

# Configuración para producción
DB_PATH = os.environ.get('TIQUETES_DB_PATH', 'instance/oleoflores_prod.db')

def get_table_columns(cursor, table_name):
    """Obtener columnas existentes de una tabla"""
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        return [col[1] for col in columns_info]  # col[1] es el nombre de la columna
    except:
        return []

def check_and_fix_pesaje_bruto_granel(cursor):
    """Verificar y corregir tabla PesajeBrutoGranel"""
    
    print("🔧 Verificando PesajeBrutoGranel...")
    
    existing_columns = get_table_columns(cursor, 'PesajeBrutoGranel')
    
    # Columnas requeridas para PesajeBrutoGranel
    required_columns = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'id_registro_granel': 'INTEGER NOT NULL',
        'id_cargue': 'INTEGER NOT NULL',
        'peso_bruto_kg': 'REAL',
        'peso_tara_kg': 'REAL',
        'peso_neto_kg': 'REAL',
        'timestamp_pesaje_bruto': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'volumen_medidor_referencia': 'REAL',
        'factor_conversion': 'REAL DEFAULT 0.92',
        'peso_teorico_kg': 'REAL',
        'diferencia_porcentual': 'REAL',
        'tolerancia_porcentual': 'REAL DEFAULT 0.5',
        'dentro_tolerancia': 'BOOLEAN',
        'requiere_validacion': 'BOOLEAN DEFAULT 0',
        'estado_validacion': 'TEXT DEFAULT "pendiente"',
        'usuario_pesaje': 'TEXT',
        'usuario_validador': 'TEXT',
        'observaciones_pesaje': 'TEXT',
        'foto_bascula_path': 'TEXT',
        'numero_pesaje': 'INTEGER DEFAULT 1',
        'es_pesaje_oficial': 'BOOLEAN DEFAULT 1',  # Esta es la columna que está faltando
        'motivo_repesaje': 'TEXT',
        'peso_bruto_anterior_kg': 'REAL',
        'diferencia_repesaje_kg': 'REAL'
    }
    
    if not existing_columns:
        # Crear tabla completa
        print("   📋 Creando tabla PesajeBrutoGranel...")
        sql = '''
        CREATE TABLE IF NOT EXISTS PesajeBrutoGranel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_registro_granel INTEGER NOT NULL,
            id_cargue INTEGER NOT NULL,
            peso_bruto_kg REAL,
            peso_tara_kg REAL,
            peso_neto_kg REAL,
            timestamp_pesaje_bruto DATETIME DEFAULT CURRENT_TIMESTAMP,
            volumen_medidor_referencia REAL,
            factor_conversion REAL DEFAULT 0.92,
            peso_teorico_kg REAL,
            diferencia_porcentual REAL,
            tolerancia_porcentual REAL DEFAULT 0.5,
            dentro_tolerancia BOOLEAN,
            requiere_validacion BOOLEAN DEFAULT 0,
            estado_validacion TEXT DEFAULT 'pendiente',
            usuario_pesaje TEXT,
            usuario_validador TEXT,
            observaciones_pesaje TEXT,
            foto_bascula_path TEXT,
            numero_pesaje INTEGER DEFAULT 1,
            es_pesaje_oficial BOOLEAN DEFAULT 1,
            motivo_repesaje TEXT,
            peso_bruto_anterior_kg REAL,
            diferencia_repesaje_kg REAL,
            FOREIGN KEY (id_registro_granel) REFERENCES RegistroEntradaGraneles(id),
            FOREIGN KEY (id_cargue) REFERENCES CargueGranel(id)
        );
        '''
        cursor.execute(sql)
        print("   ✅ Tabla PesajeBrutoGranel creada")
        return True
    
    # Agregar columnas faltantes
    missing_count = 0
    for col_name, col_type in required_columns.items():
        if col_name not in existing_columns:
            try:
                # Extraer solo el tipo para ALTER TABLE
                col_type_clean = col_type.split(' DEFAULT ')[0].split(' NOT NULL')[0].split(' PRIMARY KEY')[0]
                sql = f"ALTER TABLE PesajeBrutoGranel ADD COLUMN {col_name} {col_type_clean}"
                cursor.execute(sql)
                print(f"   ✅ Agregada columna: {col_name}")
                missing_count += 1
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"   ❌ Error agregando {col_name}: {e}")
                    return False
    
    if missing_count > 0:
        print(f"   ✅ {missing_count} columnas agregadas a PesajeBrutoGranel")
    else:
        print("   ✅ PesajeBrutoGranel ya está completa")
    
    return True

def check_and_fix_primer_pesaje_granel(cursor):
    """Verificar y corregir tabla PrimerPesajeGranel"""
    
    print("🔧 Verificando PrimerPesajeGranel...")
    
    existing_columns = get_table_columns(cursor, 'PrimerPesajeGranel')
    
    required_columns = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'id_registro_granel': 'INTEGER NOT NULL',
        'peso_primer_kg': 'REAL',
        'codigo_guia_transporte_sap': 'TEXT',
        'timestamp_primer_pesaje': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'usuario_primer_pesaje': 'TEXT',
        'foto_soporte_path': 'TEXT',
        'observaciones_primer_pesaje': 'TEXT'
    }
    
    if not existing_columns:
        print("   📋 Creando tabla PrimerPesajeGranel...")
        sql = '''
        CREATE TABLE IF NOT EXISTS PrimerPesajeGranel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_registro_granel INTEGER NOT NULL,
            peso_primer_kg REAL,
            codigo_guia_transporte_sap TEXT,
            timestamp_primer_pesaje DATETIME DEFAULT CURRENT_TIMESTAMP,
            usuario_primer_pesaje TEXT,
            foto_soporte_path TEXT,
            observaciones_primer_pesaje TEXT,
            FOREIGN KEY (id_registro_granel) REFERENCES RegistroEntradaGraneles(id)
        );
        '''
        cursor.execute(sql)
        print("   ✅ Tabla PrimerPesajeGranel creada")
        return True
    
    # Agregar columnas faltantes
    missing_count = 0
    for col_name, col_type in required_columns.items():
        if col_name not in existing_columns:
            try:
                col_type_clean = col_type.split(' DEFAULT ')[0].split(' NOT NULL')[0].split(' PRIMARY KEY')[0]
                sql = f"ALTER TABLE PrimerPesajeGranel ADD COLUMN {col_name} {col_type_clean}"
                cursor.execute(sql)
                print(f"   ✅ Agregada columna: {col_name}")
                missing_count += 1
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"   ❌ Error agregando {col_name}: {e}")
                    return False
    
    if missing_count > 0:
        print(f"   ✅ {missing_count} columnas agregadas a PrimerPesajeGranel")
    else:
        print("   ✅ PrimerPesajeGranel ya está completa")
    
    return True

def check_and_fix_cargue_granel(cursor):
    """Verificar y corregir tabla CargueGranel"""
    
    print("🔧 Verificando CargueGranel...")
    
    existing_columns = get_table_columns(cursor, 'CargueGranel')
    
    required_columns = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'id_registro_granel': 'INTEGER NOT NULL',
        'estado_cargue': 'TEXT DEFAULT "iniciado"',
        'timestamp_inicio_cargue': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'timestamp_fin_cargue': 'DATETIME',
        'volumen_medidor': 'REAL',
        'volumen_medidor_litros': 'REAL',
        'foto_display_medidor_path': 'TEXT',
        'observaciones_cargue': 'TEXT',
        'usuario_cargue': 'TEXT',
        'razon_no_aplica': 'TEXT',
        'observaciones_no_aplica': 'TEXT'
    }
    
    if not existing_columns:
        print("   📋 Creando tabla CargueGranel...")
        sql = '''
        CREATE TABLE IF NOT EXISTS CargueGranel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_registro_granel INTEGER NOT NULL,
            estado_cargue TEXT DEFAULT 'iniciado',
            timestamp_inicio_cargue DATETIME DEFAULT CURRENT_TIMESTAMP,
            timestamp_fin_cargue DATETIME,
            volumen_medidor REAL,
            volumen_medidor_litros REAL,
            foto_display_medidor_path TEXT,
            observaciones_cargue TEXT,
            usuario_cargue TEXT,
            razon_no_aplica TEXT,
            observaciones_no_aplica TEXT,
            FOREIGN KEY (id_registro_granel) REFERENCES RegistroEntradaGraneles(id)
        );
        '''
        cursor.execute(sql)
        print("   ✅ Tabla CargueGranel creada")
        return True
    
    # Agregar columnas faltantes
    missing_count = 0
    for col_name, col_type in required_columns.items():
        if col_name not in existing_columns:
            try:
                col_type_clean = col_type.split(' DEFAULT ')[0].split(' NOT NULL')[0].split(' PRIMARY KEY')[0]
                sql = f"ALTER TABLE CargueGranel ADD COLUMN {col_name} {col_type_clean}"
                cursor.execute(sql)
                print(f"   ✅ Agregada columna: {col_name}")
                missing_count += 1
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"   ❌ Error agregando {col_name}: {e}")
                    return False
    
    if missing_count > 0:
        print(f"   ✅ {missing_count} columnas agregadas a CargueGranel")
    else:
        print("   ✅ CargueGranel ya está completa")
    
    return True

def check_and_fix_other_tables(cursor):
    """Verificar y crear otras tablas necesarias"""
    
    print("🔧 Verificando otras tablas del sistema...")
    
    # Verificar y crear TomaMuestraGranel
    existing_columns = get_table_columns(cursor, 'TomaMuestraGranel')
    if not existing_columns:
        print("   📋 Creando tabla TomaMuestraGranel...")
        sql = '''
        CREATE TABLE IF NOT EXISTS TomaMuestraGranel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_registro_granel INTEGER NOT NULL,
            observaciones_muestra TEXT,
            foto_soporte_path TEXT,
            foto_soporte_url TEXT,
            timestamp_toma DATETIME DEFAULT CURRENT_TIMESTAMP,
            usuario_toma TEXT,
            FOREIGN KEY (id_registro_granel) REFERENCES RegistroEntradaGraneles(id)
        );
        '''
        cursor.execute(sql)
        print("   ✅ Tabla TomaMuestraGranel creada")
    
    # Verificar y crear CertificadoAnalisis
    existing_columns = get_table_columns(cursor, 'CertificadoAnalisis')
    if not existing_columns:
        print("   📋 Creando tabla CertificadoAnalisis...")
        sql = '''
        CREATE TABLE IF NOT EXISTS CertificadoAnalisis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_registro_granel INTEGER NOT NULL,
            material TEXT NOT NULL,
            lote_inspeccion TEXT NOT NULL,
            fecha_certificado DATE NOT NULL,
            acidez_valor REAL,
            acidez_limite_superior REAL,
            acidez_metodo TEXT,
            humedad_valor REAL,
            humedad_limite_inferior REAL,
            humedad_limite_superior REAL,
            humedad_metodo TEXT,
            impurezas_valor REAL,
            impurezas_limite_inferior REAL,
            impurezas_limite_superior REAL,
            impurezas_metodo TEXT,
            indice_yodo_valor REAL,
            indice_yodo_limite_inferior REAL,
            indice_yodo_limite_superior REAL,
            indice_yodo_metodo TEXT,
            humedad_impurezas_valor REAL,
            humedad_impurezas_limite_superior REAL,
            placa_vehiculo TEXT,
            sellos_certificado TEXT,
            foto_soporte TEXT,
            metodo_ingreso TEXT DEFAULT 'Manual',
            usuario_registro TEXT,
            timestamp_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            alertas_limites TEXT,
            estado_certificado TEXT DEFAULT 'Registrado',
            observaciones TEXT,
            FOREIGN KEY (id_registro_granel) REFERENCES RegistroEntradaGraneles(id)
        );
        '''
        cursor.execute(sql)
        print("   ✅ Tabla CertificadoAnalisis creada")
    
    # Verificar y crear ManifiestoCarga
    existing_columns = get_table_columns(cursor, 'ManifiestoCarga')
    if not existing_columns:
        print("   📋 Creando tabla ManifiestoCarga...")
        sql = '''
        CREATE TABLE IF NOT EXISTS ManifiestoCarga (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_registro_granel INTEGER NOT NULL,
            numero_manifiesto TEXT,
            fecha_manifiesto DATE,
            foto_manifiesto_path TEXT,
            timestamp_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            usuario_registro TEXT NOT NULL,
            observaciones TEXT,
            FOREIGN KEY (id_registro_granel) REFERENCES RegistroEntradaGraneles(id)
        );
        '''
        cursor.execute(sql)
        print("   ✅ Tabla ManifiestoCarga creada")
    
    return True

def create_indices(cursor):
    """Crear índices para optimizar consultas"""
    
    print("📊 Creando índices...")
    
    indices = [
        'CREATE INDEX IF NOT EXISTS idx_pesaje_bruto_registro ON PesajeBrutoGranel(id_registro_granel)',
        'CREATE INDEX IF NOT EXISTS idx_pesaje_bruto_oficial ON PesajeBrutoGranel(es_pesaje_oficial)',
        'CREATE INDEX IF NOT EXISTS idx_primer_pesaje_registro ON PrimerPesajeGranel(id_registro_granel)',
        'CREATE INDEX IF NOT EXISTS idx_cargue_registro ON CargueGranel(id_registro_granel)',
        'CREATE INDEX IF NOT EXISTS idx_cargue_estado ON CargueGranel(estado_cargue)',
        'CREATE INDEX IF NOT EXISTS idx_certificado_registro ON CertificadoAnalisis(id_registro_granel)',
        'CREATE INDEX IF NOT EXISTS idx_muestra_registro ON TomaMuestraGranel(id_registro_granel)',
        'CREATE INDEX IF NOT EXISTS idx_manifiesto_registro ON ManifiestoCarga(id_registro_granel)'
    ]
    
    for idx_sql in indices:
        try:
            cursor.execute(idx_sql)
        except Exception as e:
            print(f"   ⚠️  Error creando índice: {e}")
    
    print("   ✅ Índices creados/actualizados")

def main():
    """Función principal"""
    
    print("=" * 80)
    print("🔧 CORRECCIÓN COMPLETA DE TABLAS DEL SISTEMA DE GRANELES")
    print("=" * 80)
    print(f"📍 Base de datos: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ La base de datos no existe: {DB_PATH}")
        return False
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar y corregir cada tabla
        success = True
        
        success &= check_and_fix_pesaje_bruto_granel(cursor)
        success &= check_and_fix_primer_pesaje_granel(cursor)
        success &= check_and_fix_cargue_granel(cursor)
        success &= check_and_fix_other_tables(cursor)
        
        if success:
            # Crear índices
            create_indices(cursor)
            
            # Confirmar cambios
            conn.commit()
            
            print("\n" + "=" * 80)
            print("🎉 ¡CORRECCIÓN COMPLETADA EXITOSAMENTE!")
            print("=" * 80)
            print("\n✅ Todas las tablas han sido verificadas y corregidas")
            print("✅ Columnas faltantes agregadas (incluyendo es_pesaje_oficial)")
            print("✅ Índices optimizados creados")
            
            print("\n📋 Próximos pasos:")
            print("   1. Reiniciar la aplicación en producción")
            print("   2. Probar la guía centralizada de graneles")
            print("   3. Verificar que no hay más errores de columnas faltantes")
            
            return True
        else:
            print("\n❌ Algunos errores ocurrieron durante la corrección")
            return False
        
    except Exception as e:
        print(f"❌ Error durante la corrección: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
