#!/usr/bin/env python3
"""
Script de migración completa para crear todas las tablas del sistema de graneles en producción.

Este script crea todas las tablas necesarias para el sistema de graneles:
- RegistroEntradaGraneles (tabla principal)
- enturnamientos_graneles (enturnamiento)
- PrimerPesajeGranel (primer pesaje/peso tara)
- CargueGranel (proceso de cargue/descargue)
- PesajeBrutoGranel (pesaje bruto final)
- ControlCalidadGranel (control de calidad)
- InspeccionVehiculo (inspección de vehículos)
- ResumenCargueGranel (resumen del proceso)
- CertificadoAnalisis (certificados de análisis)
- ManifiestoCarga (manifiesto de carga)
- TomaMuestraGranel (toma de muestra para descargue)
- remisiones (remisiones)
- codigos_despacho (códigos de despacho)
- facturas (facturas)

Uso:
    python3 create_graneles_tables_production.py
"""

import os
import sqlite3
import sys
from datetime import datetime

# Configuración de base de datos
DB_PATH = os.environ.get('TIQUETES_DB_PATH', 'instance/oleoflores_prod.db')

def create_registro_entrada_graneles():
    """Crear tabla principal RegistroEntradaGraneles"""
    return '''
    CREATE TABLE IF NOT EXISTS RegistroEntradaGraneles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guia_registro TEXT UNIQUE,
        producto TEXT,
        fecha_autorizacion TEXT,
        placa TEXT,
        trailer TEXT,
        cedula_conductor TEXT,
        nombre_conductor TEXT,
        telefono_conductor TEXT,
        transportadora TEXT,
        cliente TEXT,
        tipo_venta TEXT,
        origen TEXT,
        destino TEXT,
        kg_cargar TEXT,
        tipo_cargue TEXT DEFAULT 'Cargue',
        tipo_formulario TEXT DEFAULT 'Graneles Cliente',
        flete TEXT,
        pedido TEXT,
        localidad TEXT,
        transportadora_inspeccion TEXT,
        arl TEXT,
        eps TEXT,
        celular_inspeccion TEXT,
        vencimiento_arl TEXT,
        vencimiento_soat TEXT,
        vencimiento_tecnomecanica TEXT,
        vencimiento_licencia TEXT,
        foto_arl TEXT,
        foto_soat TEXT,
        foto_tecnomecanica TEXT,
        foto_licencia TEXT,
        observaciones_documentos TEXT,
        estado_registro TEXT DEFAULT 'registrado',
        timestamp_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        tipo_registro TEXT,
        observaciones TEXT,
        usuario_registro TEXT
    );
    '''

def create_enturnamientos_graneles():
    """Crear tabla enturnamientos_graneles"""
    return '''
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
    );
    '''

def create_primer_pesaje_granel():
    """Crear tabla PrimerPesajeGranel"""
    return '''
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

def create_cargue_granel():
    """Crear tabla CargueGranel"""
    return '''
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

def create_pesaje_bruto_granel():
    """Crear tabla PesajeBrutoGranel"""
    return '''
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

def create_control_calidad_granel():
    """Crear tabla ControlCalidadGranel"""
    return '''
    CREATE TABLE IF NOT EXISTS ControlCalidadGranel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_registro_granel INTEGER NOT NULL,
        resultado_calidad TEXT,
        parametros_calidad TEXT,
        observaciones_calidad TEXT,
        usuario_calidad TEXT,
        timestamp_calidad DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_registro_granel) REFERENCES RegistroEntradaGraneles(id)
    );
    '''

def create_inspeccion_vehiculo():
    """Crear tabla InspeccionVehiculo"""
    return '''
    CREATE TABLE IF NOT EXISTS InspeccionVehiculo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_registro_granel INTEGER NOT NULL,
        localidad TEXT,
        transportadora TEXT,
        arl TEXT,
        eps TEXT,
        celular TEXT,
        tipo_vehiculo TEXT,
        producto_cargar TEXT,
        elementos_seguridad TEXT,
        estado_vehiculo TEXT,
        carrotanques TEXT,
        vehiculo_apto_cargue TEXT,
        motivo_rechazo TEXT,
        segunda_aprobacion TEXT,
        numero_tanque_almacenamiento TEXT,
        temperatura_cargue REAL,
        numero_tiquete_bascula TEXT,
        sellos_carrotanque TEXT,
        observaciones_inspeccion TEXT,
        usuario_inspeccion TEXT,
        timestamp_inspeccion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_registro_granel) REFERENCES RegistroEntradaGraneles(id)
    );
    '''

def create_resumen_cargue_granel():
    """Crear tabla ResumenCargueGranel"""
    return '''
    CREATE TABLE IF NOT EXISTS ResumenCargueGranel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_registro_granel INTEGER NOT NULL,
        id_cargue INTEGER NOT NULL,
        peso_bruto_kg REAL,
        peso_tara_kg REAL,
        peso_neto_kg REAL,
        volumen_cargado_litros REAL,
        duracion_cargue_minutos REAL,
        rendimiento_cargue_lpm REAL,
        factor_conversion_usado REAL,
        diferencia_porcentual REAL,
        dentro_tolerancia BOOLEAN,
        estado_final TEXT,
        observaciones_finales TEXT,
        usuario_finalizacion TEXT,
        timestamp_finalizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_registro_granel) REFERENCES RegistroEntradaGraneles(id),
        FOREIGN KEY (id_cargue) REFERENCES CargueGranel(id)
    );
    '''

def create_certificado_analisis():
    """Crear tabla CertificadoAnalisis"""
    return '''
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

def create_manifiesto_carga():
    """Crear tabla ManifiestoCarga"""
    return '''
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

def create_toma_muestra_granel():
    """Crear tabla TomaMuestraGranel"""
    return '''
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

def create_remisiones():
    """Crear tabla remisiones"""
    return '''
    CREATE TABLE IF NOT EXISTS remisiones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_registro_granel INTEGER NOT NULL,
        numero_remision TEXT,
        fecha_remision DATE,
        destinatario TEXT,
        origen TEXT,
        destino TEXT,
        producto TEXT,
        cantidad TEXT,
        unidad_medida TEXT,
        observaciones TEXT,
        foto_remision_path TEXT,
        metodo_ingreso TEXT DEFAULT 'Manual',
        usuario_registro TEXT,
        timestamp_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_registro_granel) REFERENCES RegistroEntradaGraneles(id)
    );
    '''

def create_codigos_despacho():
    """Crear tabla codigos_despacho"""
    return '''
    CREATE TABLE IF NOT EXISTS codigos_despacho (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_registro_granel INTEGER NOT NULL,
        codigo_despacho TEXT,
        fecha_despacho DATE,
        destino TEXT,
        transportadora TEXT,
        observaciones TEXT,
        foto_codigo_path TEXT,
        metodo_ingreso TEXT DEFAULT 'Manual',
        usuario_registro TEXT,
        timestamp_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_registro_granel) REFERENCES RegistroEntradaGraneles(id)
    );
    '''

def create_facturas():
    """Crear tabla facturas"""
    return '''
    CREATE TABLE IF NOT EXISTS facturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_registro_granel INTEGER NOT NULL,
        numero_factura TEXT,
        fecha_factura DATE,
        cliente TEXT,
        valor_total REAL,
        observaciones TEXT,
        foto_factura_path TEXT,
        metodo_ingreso TEXT DEFAULT 'Manual',
        usuario_registro TEXT,
        timestamp_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_registro_granel) REFERENCES RegistroEntradaGraneles(id)
    );
    '''

def create_indices():
    """Crear índices para optimizar consultas"""
    return [
        'CREATE INDEX IF NOT EXISTS idx_registro_placa ON RegistroEntradaGraneles(placa)',
        'CREATE INDEX IF NOT EXISTS idx_registro_estado ON RegistroEntradaGraneles(estado_registro)',
        'CREATE INDEX IF NOT EXISTS idx_registro_timestamp ON RegistroEntradaGraneles(timestamp_registro)',
        'CREATE INDEX IF NOT EXISTS idx_registro_tipo_cargue ON RegistroEntradaGraneles(tipo_cargue)',
        'CREATE INDEX IF NOT EXISTS idx_enturnamientos_placa_estado ON enturnamientos_graneles(placa, estado)',
        'CREATE INDEX IF NOT EXISTS idx_enturnamientos_timestamp ON enturnamientos_graneles(timestamp_enturnado)',
        'CREATE INDEX IF NOT EXISTS idx_primer_pesaje_registro ON PrimerPesajeGranel(id_registro_granel)',
        'CREATE INDEX IF NOT EXISTS idx_cargue_registro ON CargueGranel(id_registro_granel)',
        'CREATE INDEX IF NOT EXISTS idx_pesaje_bruto_registro ON PesajeBrutoGranel(id_registro_granel)',
        'CREATE INDEX IF NOT EXISTS idx_certificado_registro ON CertificadoAnalisis(id_registro_granel)',
        'CREATE INDEX IF NOT EXISTS idx_manifiesto_registro ON ManifiestoCarga(id_registro_granel)',
        'CREATE INDEX IF NOT EXISTS idx_muestra_registro ON TomaMuestraGranel(id_registro_granel)',
        'CREATE INDEX IF NOT EXISTS idx_remisiones_registro ON remisiones(id_registro_granel)',
        'CREATE INDEX IF NOT EXISTS idx_codigos_registro ON codigos_despacho(id_registro_granel)',
        'CREATE INDEX IF NOT EXISTS idx_facturas_registro ON facturas(id_registro_granel)'
    ]

def execute_migration():
    """Ejecutar la migración completa"""
    
    print(f"🚀 Iniciando migración completa del sistema de graneles...")
    print(f"📍 Base de datos: {DB_PATH}")
    
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Lista de todas las tablas a crear
        tables = [
            ("RegistroEntradaGraneles", create_registro_entrada_graneles()),
            ("enturnamientos_graneles", create_enturnamientos_graneles()),
            ("PrimerPesajeGranel", create_primer_pesaje_granel()),
            ("CargueGranel", create_cargue_granel()),
            ("PesajeBrutoGranel", create_pesaje_bruto_granel()),
            ("ControlCalidadGranel", create_control_calidad_granel()),
            ("InspeccionVehiculo", create_inspeccion_vehiculo()),
            ("ResumenCargueGranel", create_resumen_cargue_granel()),
            ("CertificadoAnalisis", create_certificado_analisis()),
            ("ManifiestoCarga", create_manifiesto_carga()),
            ("TomaMuestraGranel", create_toma_muestra_granel()),
            ("remisiones", create_remisiones()),
            ("codigos_despacho", create_codigos_despacho()),
            ("facturas", create_facturas())
        ]
        
        # Crear todas las tablas
        for table_name, sql in tables:
            try:
                cursor.execute(sql)
                print(f"✅ Tabla {table_name} creada/actualizada")
            except Exception as e:
                print(f"❌ Error creando tabla {table_name}: {e}")
                return False
        
        # Crear índices
        print("\n📊 Creando índices...")
        indices = create_indices()
        for idx_sql in indices:
            try:
                cursor.execute(idx_sql)
            except Exception as e:
                print(f"⚠️  Error creando índice: {e}")
        
        print("✅ Índices creados")
        
        # Confirmar cambios
        conn.commit()
        
        print("\n🎉 ¡Migración completada exitosamente!")
        print("\n📋 Tablas creadas:")
        for table_name, _ in tables:
            print(f"   ✅ {table_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def verify_tables():
    """Verificar que todas las tablas fueron creadas correctamente"""
    
    print("\n🔍 Verificando tablas creadas...")
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Obtener lista de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        expected_tables = [
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
        
        existing_tables = [table[0] for table in tables]
        
        print(f"\n📊 Tablas encontradas en la base de datos:")
        for table in existing_tables:
            if table in expected_tables:
                print(f"   ✅ {table}")
            else:
                print(f"   📋 {table} (otra tabla)")
        
        print(f"\n🔍 Verificación de tablas del sistema de graneles:")
        missing_tables = []
        for expected in expected_tables:
            if expected in existing_tables:
                print(f"   ✅ {expected}")
            else:
                print(f"   ❌ {expected} - FALTANTE")
                missing_tables.append(expected)
        
        if missing_tables:
            print(f"\n⚠️  Tablas faltantes: {', '.join(missing_tables)}")
            return False
        else:
            print(f"\n🎉 ¡Todas las tablas del sistema de graneles están presentes!")
            return True
            
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """Función principal"""
    
    print("=" * 80)
    print("🏭 MIGRACIÓN COMPLETA DEL SISTEMA DE GRANELES PARA PRODUCCIÓN")
    print("=" * 80)
    
    # Ejecutar migración
    success = execute_migration()
    
    if success:
        # Verificar que todo esté correcto
        verify_success = verify_tables()
        
        if verify_success:
            print("\n" + "=" * 80)
            print("🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
            print("=" * 80)
            print("\n✅ El sistema de graneles está listo para usar en producción.")
            print("✅ Todas las tablas han sido creadas correctamente.")
            print("✅ Los índices han sido aplicados para optimizar el rendimiento.")
            
            print("\n📋 Próximos pasos:")
            print("   1. Reiniciar la aplicación en producción")
            print("   2. Verificar que no hay más errores de tablas faltantes")
            print("   3. Probar el flujo completo de graneles")
            
            return True
        else:
            print("\n❌ La verificación falló. Algunas tablas pueden no haberse creado correctamente.")
            return False
    else:
        print("\n❌ La migración falló. Revisa los errores anteriores.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
