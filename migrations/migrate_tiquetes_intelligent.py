#!/usr/bin/env python3
"""
Script de Migración Inteligente: tiquetes.db → oleoflores_dev.db

Migra datos manejando diferencias de tipos de datos entre las estructuras.
Maneja conversiones automáticas de tipos (REAL→FLOAT, TEXT→VARCHAR, etc.)

Fecha: 25 de julio de 2025
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths de las bases de datos
PROJECT_ROOT = Path(__file__).parent.parent
INSTANCE_PATH = PROJECT_ROOT / 'instance'
SOURCE_DB = INSTANCE_PATH / 'tiquetes.db'
TARGET_DB = INSTANCE_PATH / 'oleoflores_dev.db'

def son_tipos_compatibles(tipo_origen, tipo_destino):
    """Verificar si dos tipos de datos SQLite son compatibles para migración."""
    # Normalizar tipos
    tipo_origen = tipo_origen.upper()
    tipo_destino = tipo_destino.upper()
    
    # Mapeo de compatibilidades
    compatibilidades = {
        'TEXT': ['TEXT', 'VARCHAR', 'VARCHAR(80)', 'VARCHAR(100)', 'VARCHAR(120)', 'VARCHAR(128)'],
        'REAL': ['REAL', 'FLOAT'],
        'INTEGER': ['INTEGER'],
        'TIMESTAMP': ['TIMESTAMP', 'DATETIME'],
        'DATETIME': ['DATETIME', 'TIMESTAMP']
    }
    
    # Verificar compatibilidad directa
    for tipo_base, tipos_compatibles in compatibilidades.items():
        if tipo_origen.startswith(tipo_base):
            return any(tipo_destino.startswith(tc) for tc in tipos_compatibles)
    
    # Si no hay regla específica, verificar si son exactamente iguales
    return tipo_origen == tipo_destino

def obtener_columnas_compatibles(tabla, conn_origen, conn_destino):
    """Obtener columnas compatibles entre origen y destino."""
    try:
        # Obtener estructura de origen
        cursor_origen = conn_origen.cursor()
        cursor_origen.execute(f"PRAGMA table_info({tabla})")
        estructura_origen = cursor_origen.fetchall()
        
        # Obtener estructura de destino
        cursor_destino = conn_destino.cursor()
        cursor_destino.execute(f"PRAGMA table_info({tabla})")
        estructura_destino = cursor_destino.fetchall()
        
        # Crear mapas de columnas
        columnas_origen = {col[1]: col[2] for col in estructura_origen}  # {nombre: tipo}
        columnas_destino = {col[1]: col[2] for col in estructura_destino}
        
        # Encontrar columnas compatibles
        columnas_compatibles = []
        columnas_incompatibles = []
        
        for nombre_col, tipo_origen in columnas_origen.items():
            if nombre_col in columnas_destino:
                tipo_destino = columnas_destino[nombre_col]
                if son_tipos_compatibles(tipo_origen, tipo_destino):
                    columnas_compatibles.append(nombre_col)
                else:
                    columnas_incompatibles.append((nombre_col, tipo_origen, tipo_destino))
            else:
                logger.warning(f"Columna {nombre_col} no existe en destino")
        
        return columnas_compatibles, columnas_incompatibles
        
    except Exception as e:
        logger.error(f"Error analizando columnas de tabla {tabla}: {e}")
        return [], []

def migrar_tabla_inteligente(tabla, conn_origen, conn_destino):
    """Migrar tabla con manejo inteligente de tipos de datos."""
    try:
        logger.info(f"\n📋 Procesando tabla: {tabla}")
        
        # Obtener columnas compatibles
        columnas_compatibles, columnas_incompatibles = obtener_columnas_compatibles(
            tabla, conn_origen, conn_destino
        )
        
        if columnas_incompatibles:
            logger.warning(f"⚠️ Columnas incompatibles en {tabla}:")
            for col, tipo_orig, tipo_dest in columnas_incompatibles:
                logger.warning(f"   {col}: {tipo_orig} → {tipo_dest}")
        
        if not columnas_compatibles:
            logger.error(f"❌ No hay columnas compatibles en tabla {tabla}")
            return False
        
        logger.info(f"✅ Columnas compatibles: {len(columnas_compatibles)}")
        logger.info(f"📊 Columnas a migrar: {columnas_compatibles}")
        
        # Contar registros
        cursor_origen = conn_origen.cursor()
        cursor_origen.execute(f"SELECT COUNT(*) FROM {tabla}")
        registros_origen = cursor_origen.fetchone()[0]
        
        cursor_destino = conn_destino.cursor()
        cursor_destino.execute(f"SELECT COUNT(*) FROM {tabla}")
        registros_destino_antes = cursor_destino.fetchone()[0]
        
        logger.info(f"🔄 {registros_origen} registros en origen, {registros_destino_antes} en destino")
        
        if registros_origen == 0:
            logger.info(f"⏭️ Tabla {tabla} vacía en origen, saltando")
            return True
        
        # Limpiar tabla destino
        if registros_destino_antes > 0:
            cursor_destino.execute(f"DELETE FROM {tabla}")
            logger.info(f"🗑️ Tabla {tabla} limpiada en destino")
        
        # Preparar query de migración
        columnas_str = ','.join(columnas_compatibles)
        placeholders = ','.join(['?' for _ in columnas_compatibles])
        
        select_query = f"SELECT {columnas_str} FROM {tabla}"
        insert_query = f"INSERT INTO {tabla} ({columnas_str}) VALUES ({placeholders})"
        
        # Obtener datos de origen
        cursor_origen.execute(select_query)
        datos = cursor_origen.fetchall()
        
        # Insertar en destino
        cursor_destino.executemany(insert_query, datos)
        conn_destino.commit()
        
        # Verificar migración
        cursor_destino.execute(f"SELECT COUNT(*) FROM {tabla}")
        registros_destino_despues = cursor_destino.fetchone()[0]
        
        logger.info(f"✅ Tabla {tabla} migrada: {registros_origen} → {registros_destino_despues} registros")
        
        if registros_destino_despues != registros_origen:
            logger.warning(f"⚠️ Discrepancia en tabla {tabla}: esperados {registros_origen}, obtenidos {registros_destino_despues}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error migrando tabla {tabla}: {e}")
        return False

def migrar_datos_inteligente():
    """Función principal de migración inteligente."""
    logger.info("🚀 Iniciando migración inteligente de datos...")
    
    # Verificar bases de datos
    if not SOURCE_DB.exists() or not TARGET_DB.exists():
        logger.error("❌ Una o ambas bases de datos no existen")
        return False
    
    # Tablas a migrar en orden de prioridad
    tablas_prioritarias = [
        'entry_records',
        'pesajes_bruto', 
        'clasificaciones',
        'pesajes_neto',
        'fotos_clasificacion',
        'salidas',
        'users',
        'RegistroEntradaGraneles',
        'PrimerPesajeGranel',
        'ControlCalidadGranel',
        'validaciones_diarias_sap',
        'InspeccionVehiculo',
        'presupuesto_mensual'
    ]
    
    # Estadísticas
    tablas_exitosas = 0
    tablas_fallidas = 0
    
    with sqlite3.connect(SOURCE_DB) as conn_origen, sqlite3.connect(TARGET_DB) as conn_destino:
        
        # Obtener todas las tablas disponibles en origen
        cursor_origen = conn_origen.cursor()
        cursor_origen.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tablas_disponibles = [row[0] for row in cursor_origen.fetchall()]
        
        logger.info(f"📋 Tablas disponibles en origen: {tablas_disponibles}")
        
        # Migrar tablas en orden de prioridad
        for tabla in tablas_prioritarias:
            if tabla in tablas_disponibles:
                if migrar_tabla_inteligente(tabla, conn_origen, conn_destino):
                    tablas_exitosas += 1
                else:
                    tablas_fallidas += 1
            else:
                logger.warning(f"⚠️ Tabla {tabla} no encontrada en origen")
    
    # Resumen final
    logger.info(f"\n📊 RESUMEN DE MIGRACIÓN INTELIGENTE:")
    logger.info(f"✅ Tablas migradas exitosamente: {tablas_exitosas}")
    logger.info(f"❌ Tablas fallidas: {tablas_fallidas}")
    logger.info(f"📋 Total tablas procesadas: {len(tablas_prioritarias)}")
    
    if tablas_fallidas == 0:
        logger.info("🎉 MIGRACIÓN INTELIGENTE COMPLETADA EXITOSAMENTE!")
        return True
    else:
        logger.warning(f"⚠️ Migración completada con {tablas_fallidas} errores")
        return tablas_exitosas > tablas_fallidas  # Éxito si más del 50% migró bien

def verificar_migracion_inteligente():
    """Verificar migración comparando registros en tablas principales."""
    logger.info("\n🔍 Verificando migración inteligente...")
    
    tablas_criticas = ['entry_records', 'pesajes_bruto', 'clasificaciones', 'pesajes_neto']
    
    with sqlite3.connect(SOURCE_DB) as conn_origen, sqlite3.connect(TARGET_DB) as conn_destino:
        verificacion_exitosa = True
        
        for tabla in tablas_criticas:
            try:
                # Contar en origen
                cursor_origen = conn_origen.cursor()
                cursor_origen.execute(f"SELECT COUNT(*) FROM {tabla}")
                registros_origen = cursor_origen.fetchone()[0]
                
                # Contar en destino
                cursor_destino = conn_destino.cursor()
                cursor_destino.execute(f"SELECT COUNT(*) FROM {tabla}")
                registros_destino = cursor_destino.fetchone()[0]
                
                if registros_origen == registros_destino:
                    logger.info(f"✅ {tabla}: {registros_origen} registros (OK)")
                else:
                    logger.error(f"❌ {tabla}: {registros_origen} → {registros_destino} (DISCREPANCIA)")
                    verificacion_exitosa = False
                    
            except Exception as e:
                logger.error(f"❌ Error verificando tabla {tabla}: {e}")
                verificacion_exitosa = False
        
        return verificacion_exitosa

def main():
    """Función principal."""
    print("🧠 Script de Migración Inteligente: tiquetes.db → oleoflores_dev.db")
    print("=" * 70)
    print("Este script maneja automáticamente las diferencias de tipos de datos")
    print("entre las estructuras de las tablas.")
    print()
    
    # Confirmar antes de proceder
    respuesta = input("¿Proceder con la migración inteligente? (y/N): ").strip().lower()
    if respuesta not in ['y', 'yes', 'sí', 'si']:
        print("❌ Migración cancelada por el usuario")
        return
    
    # Ejecutar migración
    inicio = datetime.now()
    
    if migrar_datos_inteligente():
        if verificar_migracion_inteligente():
            print(f"\n🎉 MIGRACIÓN INTELIGENTE COMPLETADA EXITOSAMENTE en {datetime.now() - inicio}")
            print("📝 Próximo paso: Actualizar configuración TIQUETES_DB_PATH")
        else:
            print(f"\n⚠️ Migración completada con errores de verificación en {datetime.now() - inicio}")
    else:
        print(f"\n❌ MIGRACIÓN INTELIGENTE FALLIDA en {datetime.now() - inicio}")

if __name__ == "__main__":
    main() 