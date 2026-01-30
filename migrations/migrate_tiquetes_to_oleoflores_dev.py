#!/usr/bin/env python3
"""
Script de Migración: tiquetes.db → oleoflores_dev.db

Migra todos los datos de la base de datos original (tiquetes.db) 
a la nueva base de datos unificada (oleoflores_dev.db).

Fecha: 25 de julio de 2025
Propósito: Unificar base de datos para módulos legacy + sellos
"""

import sqlite3
import os
import sys
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

def verificar_bases_datos():
    """Verificar que ambas bases de datos existen."""
    if not SOURCE_DB.exists():
        logger.error(f"Base de datos origen no encontrada: {SOURCE_DB}")
        return False
    
    if not TARGET_DB.exists():
        logger.error(f"Base de datos destino no encontrada: {TARGET_DB}")
        return False
    
    logger.info(f"✅ Base de datos origen: {SOURCE_DB} ({SOURCE_DB.stat().st_size} bytes)")
    logger.info(f"✅ Base de datos destino: {TARGET_DB} ({TARGET_DB.stat().st_size} bytes)")
    return True

def obtener_tablas_origen():
    """Obtener lista de tablas en la base de datos origen."""
    with sqlite3.connect(SOURCE_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tablas = [row[0] for row in cursor.fetchall()]
    
    logger.info(f"📋 Tablas en origen: {tablas}")
    return tablas

def obtener_tablas_destino():
    """Obtener lista de tablas en la base de datos destino."""
    with sqlite3.connect(TARGET_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tablas = [row[0] for row in cursor.fetchall()]
    
    logger.info(f"📋 Tablas en destino: {tablas}")
    return tablas

def verificar_estructura_tabla(tabla, conn_origen, conn_destino):
    """Verificar si la estructura de una tabla es compatible entre origen y destino."""
    try:
        # Obtener estructura de origen
        cursor_origen = conn_origen.cursor()
        cursor_origen.execute(f"PRAGMA table_info({tabla})")
        estructura_origen = cursor_origen.fetchall()
        
        # Obtener estructura de destino
        cursor_destino = conn_destino.cursor()
        cursor_destino.execute(f"PRAGMA table_info({tabla})")
        estructura_destino = cursor_destino.fetchall()
        
        # Comparar columnas (nombre y tipo)
        columnas_origen = [(col[1], col[2]) for col in estructura_origen]  # (nombre, tipo)
        columnas_destino = [(col[1], col[2]) for col in estructura_destino]
        
        if columnas_origen == columnas_destino:
            logger.info(f"✅ Tabla {tabla}: Estructura compatible")
            return True, "compatible"
        else:
            # Verificar si origen es subconjunto de destino (destino tiene más columnas)
            columnas_origen_nombres = [col[0] for col in columnas_origen]
            columnas_destino_nombres = [col[0] for col in columnas_destino]
            
            if all(col in columnas_destino_nombres for col in columnas_origen_nombres):
                logger.info(f"⚠️ Tabla {tabla}: Origen es subconjunto de destino")
                return True, "subconjunto"
            else:
                logger.warning(f"❌ Tabla {tabla}: Estructuras incompatibles")
                logger.warning(f"   Origen: {columnas_origen}")
                logger.warning(f"   Destino: {columnas_destino}")
                return False, "incompatible"
    
    except Exception as e:
        logger.error(f"Error verificando estructura de tabla {tabla}: {e}")
        return False, "error"

def contar_registros(tabla, conexion):
    """Contar registros en una tabla."""
    try:
        cursor = conexion.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
        return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Error contando registros en tabla {tabla}: {e}")
        return 0

def crear_tabla_si_no_existe(tabla, conn_origen, conn_destino):
    """Crear tabla en destino si no existe, copiando estructura de origen."""
    try:
        cursor_origen = conn_origen.cursor()
        cursor_origen.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{tabla}'")
        create_sql = cursor_origen.fetchone()[0]
        
        cursor_destino = conn_destino.cursor()
        cursor_destino.execute(create_sql)
        conn_destino.commit()
        
        logger.info(f"✅ Tabla {tabla} creada en destino")
        return True
    except Exception as e:
        logger.error(f"Error creando tabla {tabla}: {e}")
        return False

def migrar_tabla(tabla, conn_origen, conn_destino, modo="replace"):
    """Migrar datos de una tabla específica."""
    try:
        # Contar registros en origen
        registros_origen = contar_registros(tabla, conn_origen)
        registros_destino_antes = contar_registros(tabla, conn_destino)
        
        logger.info(f"🔄 Migrando tabla {tabla}: {registros_origen} registros en origen, {registros_destino_antes} en destino")
        
        if registros_origen == 0:
            logger.info(f"⏭️ Tabla {tabla} vacía en origen, saltando")
            return True
        
        # Obtener datos de origen
        cursor_origen = conn_origen.cursor()
        cursor_origen.execute(f"SELECT * FROM {tabla}")
        datos = cursor_origen.fetchall()
        
        # Obtener nombres de columnas
        cursor_origen.execute(f"PRAGMA table_info({tabla})")
        columnas_info = cursor_origen.fetchall()
        nombres_columnas = [col[1] for col in columnas_info]
        
        # Verificar qué columnas existen en destino
        cursor_destino = conn_destino.cursor()
        cursor_destino.execute(f"PRAGMA table_info({tabla})")
        columnas_destino_info = cursor_destino.fetchall()
        nombres_columnas_destino = [col[1] for col in columnas_destino_info]
        
        # Filtrar columnas que existen en ambas tablas
        columnas_comunes = [col for col in nombres_columnas if col in nombres_columnas_destino]
        indices_columnas = [nombres_columnas.index(col) for col in columnas_comunes]
        
        logger.info(f"📊 Columnas a migrar: {columnas_comunes}")
        
        # Limpiar tabla destino si modo es replace
        if modo == "replace" and registros_destino_antes > 0:
            cursor_destino.execute(f"DELETE FROM {tabla}")
            logger.info(f"🗑️ Tabla {tabla} limpiada en destino")
        
        # Preparar query de inserción
        placeholders = ','.join(['?' for _ in columnas_comunes])
        columnas_str = ','.join(columnas_comunes)
        insert_query = f"INSERT INTO {tabla} ({columnas_str}) VALUES ({placeholders})"
        
        # Insertar datos
        datos_filtrados = []
        for fila in datos:
            fila_filtrada = tuple(fila[i] for i in indices_columnas)
            datos_filtrados.append(fila_filtrada)
        
        cursor_destino.executemany(insert_query, datos_filtrados)
        conn_destino.commit()
        
        # Verificar migración
        registros_destino_despues = contar_registros(tabla, conn_destino)
        
        logger.info(f"✅ Tabla {tabla} migrada: {registros_origen} → {registros_destino_despues} registros")
        
        if registros_destino_despues != registros_origen:
            logger.warning(f"⚠️ Discrepancia en tabla {tabla}: esperados {registros_origen}, obtenidos {registros_destino_despues}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error migrando tabla {tabla}: {e}")
        return False

def migrar_datos():
    """Función principal de migración."""
    logger.info("🚀 Iniciando migración de datos...")
    
    # Verificar bases de datos
    if not verificar_bases_datos():
        return False
    
    # Conectar a ambas bases de datos
    with sqlite3.connect(SOURCE_DB) as conn_origen, sqlite3.connect(TARGET_DB) as conn_destino:
        
        # Obtener tablas
        tablas_origen = obtener_tablas_origen()
        tablas_destino = obtener_tablas_destino()
        
        # Estadísticas de migración
        tablas_migradas = 0
        tablas_creadas = 0
        tablas_fallidas = 0
        
        # Procesar cada tabla de origen
        for tabla in tablas_origen:
            logger.info(f"\n📋 Procesando tabla: {tabla}")
            
            # Verificar si tabla existe en destino
            if tabla not in tablas_destino:
                logger.info(f"🆕 Tabla {tabla} no existe en destino, creando...")
                if crear_tabla_si_no_existe(tabla, conn_origen, conn_destino):
                    tablas_creadas += 1
                else:
                    tablas_fallidas += 1
                    continue
            
            # Verificar estructura
            compatible, tipo_compatibilidad = verificar_estructura_tabla(tabla, conn_origen, conn_destino)
            
            if not compatible:
                logger.error(f"❌ Tabla {tabla} incompatible, saltando")
                tablas_fallidas += 1
                continue
            
            # Migrar datos
            if migrar_tabla(tabla, conn_origen, conn_destino, modo="replace"):
                tablas_migradas += 1
            else:
                tablas_fallidas += 1
    
    # Resumen final
    logger.info(f"\n📊 RESUMEN DE MIGRACIÓN:")
    logger.info(f"✅ Tablas migradas exitosamente: {tablas_migradas}")
    logger.info(f"🆕 Tablas creadas: {tablas_creadas}")
    logger.info(f"❌ Tablas fallidas: {tablas_fallidas}")
    logger.info(f"📋 Total tablas procesadas: {len(tablas_origen)}")
    
    if tablas_fallidas == 0:
        logger.info("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        return True
    else:
        logger.warning(f"⚠️ Migración completada con {tablas_fallidas} errores")
        return False

def verificar_migracion():
    """Verificar que la migración fue exitosa comparando conteos."""
    logger.info("\n🔍 Verificando migración...")
    
    with sqlite3.connect(SOURCE_DB) as conn_origen, sqlite3.connect(TARGET_DB) as conn_destino:
        tablas_origen = obtener_tablas_origen()
        
        verificacion_exitosa = True
        
        for tabla in tablas_origen:
            registros_origen = contar_registros(tabla, conn_origen)
            registros_destino = contar_registros(tabla, conn_destino)
            
            if registros_origen == registros_destino:
                logger.info(f"✅ {tabla}: {registros_origen} registros (OK)")
            else:
                logger.error(f"❌ {tabla}: {registros_origen} → {registros_destino} (DISCREPANCIA)")
                verificacion_exitosa = False
        
        if verificacion_exitosa:
            logger.info("🎉 VERIFICACIÓN EXITOSA: Todos los datos migrados correctamente")
        else:
            logger.error("❌ VERIFICACIÓN FALLIDA: Hay discrepancias en los datos")
        
        return verificacion_exitosa

def main():
    """Función principal."""
    print("🔄 Script de Migración: tiquetes.db → oleoflores_dev.db")
    print("=" * 60)
    
    # Confirmar antes de proceder
    respuesta = input("¿Proceder con la migración? (y/N): ").strip().lower()
    if respuesta not in ['y', 'yes', 'sí', 'si']:
        print("❌ Migración cancelada por el usuario")
        return
    
    # Ejecutar migración
    inicio = datetime.now()
    
    if migrar_datos():
        if verificar_migracion():
            print(f"\n🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE en {datetime.now() - inicio}")
            print("📝 Próximo paso: Actualizar configuración TIQUETES_DB_PATH")
        else:
            print(f"\n⚠️ Migración completada con errores de verificación en {datetime.now() - inicio}")
    else:
        print(f"\n❌ MIGRACIÓN FALLIDA en {datetime.now() - inicio}")

if __name__ == "__main__":
    main() 