#!/usr/bin/env python3
"""
Migración: Crear tablas del submódulo de sellos

Este script crea todas las tablas necesarias para el submódulo de sellos de graneles.
Incluye validaciones de integridad y datos iniciales básicos.

Fecha: 15 de enero de 2025
Autor: Sistema de migración automática
Versión: 1.0 MVP
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path para importar la app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.models import db
from app.models.sellos_models import (
    TipoSello, MaestroVehiculo, Sello, SolicitudSello, 
    MovimientoSello, EstadoSello
)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def crear_tablas_sellos():
    """Crear todas las tablas del submódulo de sellos"""
    try:
        app = create_app()
        
        with app.app_context():
            logger.info("Iniciando creación de tablas del submódulo de sellos...")
            
            # Crear todas las tablas definidas en los modelos
            db.create_all()
            
            logger.info("✅ Tablas del submódulo de sellos creadas exitosamente")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error creando tablas de sellos: {e}")
        return False


def verificar_integridad_tablas():
    """Verificar que todas las tablas se crearon correctamente"""
    try:
        app = create_app()
        
        with app.app_context():
            # Lista de tablas que deben existir
            tablas_esperadas = [
                'tipos_sello',
                'maestro_vehiculos', 
                'sellos',
                'solicitudes_sello',
                'movimientos_sello'
            ]
            
            # Verificar existencia de tablas usando SQLAlchemy inspector
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tablas_existentes = inspector.get_table_names()
            
            logger.info("Verificando integridad de tablas...")
            
            for tabla in tablas_esperadas:
                if tabla in tablas_existentes:
                    logger.info(f"✅ Tabla '{tabla}' existe")
                    
                    # Verificar columnas principales
                    columnas = [col['name'] for col in inspector.get_columns(tabla)]
                    logger.info(f"   Columnas: {len(columnas)} columnas encontradas")
                    
                    # Verificar indices y constraints
                    indices = inspector.get_indexes(tabla)
                    foreign_keys = inspector.get_foreign_keys(tabla)
                    
                    if indices:
                        logger.info(f"   Índices: {len(indices)} índices")
                    if foreign_keys:
                        logger.info(f"   Foreign Keys: {len(foreign_keys)} relaciones")
                        
                else:
                    logger.error(f"❌ Tabla '{tabla}' NO existe")
                    return False
            
            logger.info("✅ Verificación de integridad completada exitosamente")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error verificando integridad: {e}")
        return False


def crear_datos_iniciales():
    """Crear datos iniciales básicos para el submódulo de sellos"""
    try:
        app = create_app()
        
        with app.app_context():
            logger.info("Creando datos iniciales...")
            
            # 1. Crear tipos de sello básicos
            tipos_sello_iniciales = [
                {
                    'nombre': 'Sello Estándar Graneles',
                    'prefijo': 'GN ESP',
                    'longitud_serial': 8,
                    'proveedor': 'Proveedor Estándar',
                    'descripcion': 'Sello estándar para carrotanques de graneles',
                    'ejemplo_serial': 'GN ESP02128201',
                    'sellos_por_lote': 100,
                    'patron_validacion': r'^GN ESP\d{8}$',
                    'usuario_creacion': 'sistema_migracion'
                },
                {
                    'nombre': 'Sello Especial',
                    'prefijo': 'ESP',
                    'longitud_serial': 10,
                    'proveedor': 'Proveedor Especial',
                    'descripcion': 'Sello especial para casos específicos',
                    'ejemplo_serial': 'ESP0212820001',
                    'sellos_por_lote': 50,
                    'patron_validacion': r'^ESP\d{10}$',
                    'usuario_creacion': 'sistema_migracion'
                }
            ]
            
            for tipo_data in tipos_sello_iniciales:
                tipo_existente = TipoSello.query.filter_by(prefijo=tipo_data['prefijo']).first()
                if not tipo_existente:
                    tipo_sello = TipoSello(**tipo_data)
                    db.session.add(tipo_sello)
                    logger.info(f"✅ Tipo de sello creado: {tipo_data['nombre']}")
                else:
                    logger.info(f"ℹ️ Tipo de sello ya existe: {tipo_data['nombre']}")
            
            # 2. Crear vehículos de ejemplo (basados en datos reales si existen)
            vehiculos_ejemplo = [
                {
                    'placa': 'ABC123',
                    'cantidad_sellos_estandar': 4,
                    'puntos_sellado': '{"punto_1": "Válvula superior", "punto_2": "Válvula inferior", "punto_3": "Compartimiento 1", "punto_4": "Compartimiento 2"}',
                    'observaciones': 'Vehículo de ejemplo creado durante migración',
                    'usuario_creacion': 'sistema_migracion'
                },
                {
                    'placa': 'XYZ789',
                    'cantidad_sellos_estandar': 6,
                    'puntos_sellado': '{"punto_1": "Válvula A", "punto_2": "Válvula B", "punto_3": "Válvula C", "punto_4": "Compartimiento 1", "punto_5": "Compartimiento 2", "punto_6": "Compartimiento 3"}',
                    'observaciones': 'Vehículo de ejemplo con 6 sellos',
                    'usuario_creacion': 'sistema_migracion'
                }
            ]
            
            for vehiculo_data in vehiculos_ejemplo:
                vehiculo_existente = MaestroVehiculo.query.filter_by(placa=vehiculo_data['placa']).first()
                if not vehiculo_existente:
                    vehiculo = MaestroVehiculo(**vehiculo_data)
                    db.session.add(vehiculo)
                    logger.info(f"✅ Vehículo de ejemplo creado: {vehiculo_data['placa']}")
                else:
                    logger.info(f"ℹ️ Vehículo ya existe: {vehiculo_data['placa']}")
            
            # Commit de todos los cambios
            db.session.commit()
            logger.info("✅ Datos iniciales creados exitosamente")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error creando datos iniciales: {e}")
        db.session.rollback()
        return False


def migrar_datos_existentes():
    """Migrar datos existentes de sellos desde el sistema de inspección de graneles"""
    try:
        app = create_app()
        
        with app.app_context():
            logger.info("Iniciando migración de datos existentes...")
            
            # Buscar inspecciones existentes con sellos
            from app.models.graneles_models import InspeccionVehiculo
            
            inspecciones = InspeccionVehiculo.query.all()
            sellos_migrados = 0
            vehiculos_nuevos = 0
            
            for inspeccion in inspecciones:
                try:
                    # Verificar si el vehículo ya está en el maestro
                    vehiculo = MaestroVehiculo.query.filter_by(placa=inspeccion.registro.placa).first()
                    
                    if not vehiculo:
                        # Crear entrada en maestro de vehículos
                        sellos_inspeccion = inspeccion.get_sellos_carrotanque()
                        cantidad_sellos = len(sellos_inspeccion) if sellos_inspeccion else 4  # Default 4
                        
                        vehiculo = MaestroVehiculo(
                            placa=inspeccion.registro.placa,
                            cantidad_sellos_estandar=cantidad_sellos,
                            observaciones=f'Migrado desde inspección ID {inspeccion.id}',
                            usuario_creacion='sistema_migracion'
                        )
                        db.session.add(vehiculo)
                        vehiculos_nuevos += 1
                        logger.info(f"✅ Vehículo migrado al maestro: {inspeccion.registro.placa}")
                    
                    # Migrar sellos si existen
                    sellos_data = inspeccion.get_sellos_carrotanque()
                    if sellos_data:
                        for key, sello_info in sellos_data.items():
                            numero_serie = sello_info.get('numero_serie') if isinstance(sello_info, dict) else sello_info
                            
                            if numero_serie:
                                # Verificar si el sello ya existe
                                sello_existente = Sello.query.filter_by(numero_serie=numero_serie).first()
                                
                                if not sello_existente:
                                    # Identificar tipo de sello
                                    tipo_sello = TipoSello.identificar_tipo_por_serial(numero_serie)
                                    
                                    if not tipo_sello:
                                        # Usar tipo por defecto
                                        tipo_sello = TipoSello.query.first()
                                    
                                    if tipo_sello:
                                        # Crear sello en estado validado (ya fue usado)
                                        sello = Sello(
                                            numero_serie=numero_serie,
                                            tipo_sello_id=tipo_sello.id,
                                            estado=EstadoSello.VALIDADO_DESPACHADO,
                                            placa_vehiculo=inspeccion.registro.placa,
                                            fecha_instalacion=inspeccion.timestamp_inspeccion,
                                            fecha_validacion=inspeccion.timestamp_inspeccion,
                                            usuario_instalacion='sistema_migracion',
                                            usuario_validacion='sistema_migracion',
                                            usuario_ingreso='sistema_migracion',
                                            observaciones=f'Migrado desde inspección ID {inspeccion.id}'
                                        )
                                        db.session.add(sello)
                                        sellos_migrados += 1
                                        
                                        # Crear movimiento de migración
                                        movimiento = MovimientoSello(
                                            sello_id=sello.id,
                                            estado_anterior=None,
                                            estado_nuevo=EstadoSello.VALIDADO_DESPACHADO.value,
                                            usuario='sistema_migracion',
                                            timestamp=inspeccion.timestamp_inspeccion,
                                            placa_vehiculo=inspeccion.registro.placa,
                                            observaciones=f'Migración automática desde inspección ID {inspeccion.id}'
                                        )
                                        db.session.add(movimiento)
                                
                except Exception as e:
                    logger.warning(f"Error migrando inspección {inspeccion.id}: {e}")
                    continue
            
            # Commit de todos los cambios
            db.session.commit()
            
            logger.info(f"✅ Migración completada:")
            logger.info(f"   - Vehículos nuevos en maestro: {vehiculos_nuevos}")
            logger.info(f"   - Sellos migrados: {sellos_migrados}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error en migración de datos existentes: {e}")
        db.session.rollback()
        return False


def generar_reporte_migracion():
    """Generar reporte de la migración realizada"""
    try:
        app = create_app()
        
        with app.app_context():
            logger.info("Generando reporte de migración...")
            
            # Contar registros en cada tabla
            conteos = {
                'tipos_sello': TipoSello.query.count(),
                'maestro_vehiculos': MaestroVehiculo.query.count(),
                'sellos': Sello.query.count(),
                'solicitudes_sello': SolicitudSello.query.count(),
                'movimientos_sello': MovimientoSello.query.count()
            }
            
            # Estadísticas de sellos por estado
            from sqlalchemy import func
            estadisticas_estados = db.session.query(
                Sello.estado, func.count(Sello.id)
            ).group_by(Sello.estado).all()
            
            logger.info("📊 REPORTE DE MIGRACIÓN - SUBMÓDULO DE SELLOS")
            logger.info("=" * 60)
            logger.info(f"Fecha de migración: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("")
            
            logger.info("📋 TABLAS CREADAS:")
            for tabla, cantidad in conteos.items():
                logger.info(f"   {tabla}: {cantidad} registros")
            
            logger.info("")
            logger.info("📈 ESTADÍSTICAS DE SELLOS POR ESTADO:")
            for estado, cantidad in estadisticas_estados:
                logger.info(f"   {estado.value if hasattr(estado, 'value') else estado}: {cantidad} sellos")
            
            logger.info("")
            logger.info("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            logger.info("=" * 60)
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error generando reporte: {e}")
        return False


def main():
    """Función principal de migración"""
    logger.info("🚀 INICIANDO MIGRACIÓN DEL SUBMÓDULO DE SELLOS")
    logger.info("=" * 60)
    
    try:
        # Paso 1: Crear tablas
        if not crear_tablas_sellos():
            logger.error("❌ Falló la creación de tablas. Abortando migración.")
            return False
        
        # Paso 2: Verificar integridad
        if not verificar_integridad_tablas():
            logger.error("❌ Falló la verificación de integridad. Abortando migración.")
            return False
        
        # Paso 3: Crear datos iniciales
        if not crear_datos_iniciales():
            logger.error("❌ Falló la creación de datos iniciales. Continuando...")
        
        # Paso 4: Migrar datos existentes
        if not migrar_datos_existentes():
            logger.error("❌ Falló la migración de datos existentes. Continuando...")
        
        # Paso 5: Generar reporte
        generar_reporte_migracion()
        
        logger.info("🎉 MIGRACIÓN DEL SUBMÓDULO DE SELLOS COMPLETADA")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error crítico en migración: {e}")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 