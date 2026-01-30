#!/usr/bin/env python3
"""
Migración para agregar tablas RBAC del submódulo de sellos
Crea roles, permisos y configuración inicial de autorización
"""

import sys
import os
import logging
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db
from app.models.sellos_rbac_models import (
    RolSello, PermisoSello, RolSellosModel, PermisoSellosModel, 
    RolPermisoSello, UsuarioRolSello, AuditoriaRolSello
)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def crear_tablas_rbac():
    """Crear todas las tablas RBAC de sellos"""
    try:
        logger.info("Creando tablas RBAC de sellos...")
        
        # Crear las tablas
        db.create_all()
        
        logger.info("✅ Tablas RBAC de sellos creadas exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creando tablas RBAC: {e}")
        db.session.rollback()
        return False

def verificar_integridad_rbac():
    """Verificar que las tablas RBAC se crearon correctamente"""
    try:
        logger.info("Verificando integridad de tablas RBAC...")
        
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        tablas_esperadas = [
            'roles_sellos',
            'permisos_sellos', 
            'rol_permiso_sellos',
            'usuario_rol_sellos',
            'auditoria_rol_sellos'
        ]
        
        tablas_existentes = inspector.get_table_names()
        
        for tabla in tablas_esperadas:
            if tabla in tablas_existentes:
                columnas = inspector.get_columns(tabla)
                logger.info(f"✅ Tabla '{tabla}' existe")
                logger.info(f"   Columnas: {len(columnas)} columnas encontradas")
                
                # Verificar foreign keys
                fks = inspector.get_foreign_keys(tabla)
                if fks:
                    logger.info(f"   Foreign Keys: {len(fks)} relaciones")
            else:
                logger.error(f"❌ Tabla '{tabla}' NO existe")
                return False
        
        logger.info("✅ Verificación de integridad RBAC completada exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando integridad RBAC: {e}")
        return False

def crear_permisos_iniciales():
    """Crear todos los permisos iniciales del sistema"""
    try:
        logger.info("Creando permisos iniciales...")
        
        permisos_config = [
            # Gestión de tipos de sello
            (PermisoSello.CREAR_TIPO_SELLO, "Crear nuevos tipos de sello", "Tipos de Sello"),
            (PermisoSello.EDITAR_TIPO_SELLO, "Editar tipos de sello existentes", "Tipos de Sello"),
            (PermisoSello.ELIMINAR_TIPO_SELLO, "Eliminar/desactivar tipos de sello", "Tipos de Sello"),
            (PermisoSello.CONSULTAR_TIPO_SELLO, "Consultar información de tipos de sello", "Tipos de Sello"),
            
            # Gestión de maestro de vehículos
            (PermisoSello.CREAR_VEHICULO, "Crear vehículos en el maestro", "Maestro de Vehículos"),
            (PermisoSello.EDITAR_VEHICULO, "Editar vehículos del maestro", "Maestro de Vehículos"),
            (PermisoSello.ELIMINAR_VEHICULO, "Eliminar/desactivar vehículos", "Maestro de Vehículos"),
            (PermisoSello.CONSULTAR_VEHICULO, "Consultar información de vehículos", "Maestro de Vehículos"),
            
            # Gestión de sellos
            (PermisoSello.CREAR_SELLO, "Crear nuevos sellos en el sistema", "Gestión de Sellos"),
            (PermisoSello.EDITAR_SELLO, "Editar información de sellos", "Gestión de Sellos"),
            (PermisoSello.CAMBIAR_ESTADO_SELLO, "Cambiar estado de sellos", "Gestión de Sellos"),
            (PermisoSello.ANULAR_SELLO, "Anular sellos del sistema", "Gestión de Sellos"),
            (PermisoSello.CONSULTAR_SELLO, "Consultar información de sellos", "Gestión de Sellos"),
            
            # Operaciones de despacho
            (PermisoSello.DESPACHAR_SELLOS, "Despachar sellos a inspectores", "Operaciones"),
            (PermisoSello.RECIBIR_SELLOS, "Recibir sellos del laboratorio", "Operaciones"),
            (PermisoSello.VALIDAR_INSTALACION, "Validar instalación de sellos", "Operaciones"),
            
            # Solicitudes de sellos
            (PermisoSello.CREAR_SOLICITUD, "Crear solicitudes de sellos", "Solicitudes"),
            (PermisoSello.APROBAR_SOLICITUD, "Aprobar solicitudes de sellos", "Solicitudes"),
            (PermisoSello.RECHAZAR_SOLICITUD, "Rechazar solicitudes de sellos", "Solicitudes"),
            (PermisoSello.CONSULTAR_SOLICITUD, "Consultar solicitudes de sellos", "Solicitudes"),
            
            # Reportes y auditoría
            (PermisoSello.GENERAR_REPORTES, "Generar reportes del sistema", "Reportes"),
            (PermisoSello.CONSULTAR_AUDITORIA, "Consultar logs de auditoría", "Reportes"),
            (PermisoSello.EXPORTAR_DATOS, "Exportar datos del sistema", "Reportes"),
            
            # Administración general
            (PermisoSello.CONFIGURAR_SISTEMA, "Configurar parámetros del sistema", "Administración"),
            (PermisoSello.GESTIONAR_USUARIOS, "Gestionar usuarios y roles", "Administración"),
        ]
        
        permisos_creados = 0
        for permiso_enum, descripcion, categoria in permisos_config:
            # Verificar si ya existe
            existing = PermisoSellosModel.query.filter_by(nombre=permiso_enum.value).first()
            if not existing:
                permiso = PermisoSellosModel.crear_permiso(
                    permiso_enum, descripcion, categoria, 'sistema_migracion'
                )
                permisos_creados += 1
        
        db.session.commit()
        logger.info(f"✅ {permisos_creados} permisos creados exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creando permisos: {e}")
        db.session.rollback()
        return False

def crear_roles_iniciales():
    """Crear roles iniciales del sistema"""
    try:
        logger.info("Creando roles iniciales...")
        
        roles_config = [
            (RolSello.ADMIN_SELLOS, "Administrador de Sellos - Acceso completo al sistema"),
            (RolSello.SUPERVISOR_SELLOS, "Supervisor de Sellos - Gestión operativa y aprobaciones"),
            (RolSello.OPERADOR_SELLOS, "Operador de Sellos - Operaciones básicas de sellos"),
            (RolSello.INSPECTOR_SELLOS, "Inspector de Sellos - Instalación y validación"),
            (RolSello.CONSULTA_SELLOS, "Consulta de Sellos - Solo lectura del sistema"),
        ]
        
        roles_creados = 0
        for rol_enum, descripcion in roles_config:
            # Verificar si ya existe
            existing = RolSellosModel.query.filter_by(nombre=rol_enum.value).first()
            if not existing:
                rol = RolSellosModel.crear_rol(
                    rol_enum, descripcion, 'sistema_migracion'
                )
                roles_creados += 1
        
        db.session.commit()
        logger.info(f"✅ {roles_creados} roles creados exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creando roles: {e}")
        db.session.rollback()
        return False

def asignar_permisos_a_roles():
    """Asignar permisos a cada rol según su nivel de acceso"""
    try:
        logger.info("Asignando permisos a roles...")
        
        # Configuración de permisos por rol
        configuracion_roles = {
            RolSello.ADMIN_SELLOS: [
                # Todos los permisos para administrador
                p for p in PermisoSello
            ],
            
            RolSello.SUPERVISOR_SELLOS: [
                # Gestión completa excepto configuración del sistema
                PermisoSello.CREAR_TIPO_SELLO, PermisoSello.EDITAR_TIPO_SELLO, PermisoSello.CONSULTAR_TIPO_SELLO,
                PermisoSello.CREAR_VEHICULO, PermisoSello.EDITAR_VEHICULO, PermisoSello.CONSULTAR_VEHICULO,
                PermisoSello.CREAR_SELLO, PermisoSello.EDITAR_SELLO, PermisoSello.CAMBIAR_ESTADO_SELLO, PermisoSello.CONSULTAR_SELLO,
                PermisoSello.DESPACHAR_SELLOS, PermisoSello.RECIBIR_SELLOS, PermisoSello.VALIDAR_INSTALACION,
                PermisoSello.APROBAR_SOLICITUD, PermisoSello.RECHAZAR_SOLICITUD, PermisoSello.CONSULTAR_SOLICITUD,
                PermisoSello.GENERAR_REPORTES, PermisoSello.CONSULTAR_AUDITORIA, PermisoSello.EXPORTAR_DATOS,
            ],
            
            RolSello.OPERADOR_SELLOS: [
                # Operaciones básicas de sellos
                PermisoSello.CONSULTAR_TIPO_SELLO, PermisoSello.CONSULTAR_VEHICULO,
                PermisoSello.CREAR_SELLO, PermisoSello.EDITAR_SELLO, PermisoSello.CAMBIAR_ESTADO_SELLO, PermisoSello.CONSULTAR_SELLO,
                PermisoSello.RECIBIR_SELLOS, PermisoSello.CREAR_SOLICITUD, PermisoSello.CONSULTAR_SOLICITUD,
            ],
            
            RolSello.INSPECTOR_SELLOS: [
                # Operaciones de campo e instalación
                PermisoSello.CONSULTAR_TIPO_SELLO, PermisoSello.CONSULTAR_VEHICULO, PermisoSello.CONSULTAR_SELLO,
                PermisoSello.CAMBIAR_ESTADO_SELLO, PermisoSello.VALIDAR_INSTALACION,
                PermisoSello.CREAR_SOLICITUD, PermisoSello.CONSULTAR_SOLICITUD,
            ],
            
            RolSello.CONSULTA_SELLOS: [
                # Solo lectura
                PermisoSello.CONSULTAR_TIPO_SELLO, PermisoSello.CONSULTAR_VEHICULO, 
                PermisoSello.CONSULTAR_SELLO, PermisoSello.CONSULTAR_SOLICITUD,
            ]
        }
        
        asignaciones_creadas = 0
        for rol_enum, permisos in configuracion_roles.items():
            rol = RolSellosModel.buscar_por_nombre(rol_enum)
            if not rol:
                logger.warning(f"Rol {rol_enum.value} no encontrado")
                continue
            
            for permiso_enum in permisos:
                permiso = PermisoSellosModel.buscar_por_nombre(permiso_enum)
                if not permiso:
                    logger.warning(f"Permiso {permiso_enum.value} no encontrado")
                    continue
                
                # Verificar si ya existe la asignación
                existing = RolPermisoSello.query.filter_by(
                    rol_id=rol.id, 
                    permiso_id=permiso.id
                ).first()
                
                if not existing:
                    rol.agregar_permiso(permiso.id, 'sistema_migracion')
                    asignaciones_creadas += 1
        
        db.session.commit()
        logger.info(f"✅ {asignaciones_creadas} asignaciones de permisos creadas")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error asignando permisos a roles: {e}")
        db.session.rollback()
        return False

def generar_reporte_rbac():
    """Generar reporte de la configuración RBAC"""
    try:
        logger.info("📊 REPORTE DE CONFIGURACIÓN RBAC - SELLOS")
        logger.info("=" * 60)
        logger.info(f"Fecha de configuración: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Estadísticas generales
        total_roles = RolSellosModel.query.filter_by(activo=True).count()
        total_permisos = PermisoSellosModel.query.filter_by(activo=True).count()
        total_asignaciones = RolPermisoSello.query.count()
        
        logger.info(f"\n📋 ESTADÍSTICAS GENERALES:")
        logger.info(f"   Roles activos: {total_roles}")
        logger.info(f"   Permisos activos: {total_permisos}")
        logger.info(f"   Asignaciones rol-permiso: {total_asignaciones}")
        
        # Detalle por rol
        logger.info(f"\n🎭 CONFIGURACIÓN POR ROL:")
        roles = RolSellosModel.query.filter_by(activo=True).all()
        for rol in roles:
            permisos_rol = len(rol.get_permisos())
            logger.info(f"   {rol.nombre}: {permisos_rol} permisos")
        
        # Permisos por categoría
        logger.info(f"\n📂 PERMISOS POR CATEGORÍA:")
        from sqlalchemy import func
        categorias = db.session.query(
            PermisoSellosModel.categoria, 
            func.count(PermisoSellosModel.id)
        ).filter_by(activo=True).group_by(PermisoSellosModel.categoria).all()
        
        for categoria, count in categorias:
            logger.info(f"   {categoria}: {count} permisos")
        
        logger.info(f"\n✅ CONFIGURACIÓN RBAC COMPLETADA EXITOSAMENTE")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"❌ Error generando reporte RBAC: {e}")
        return False

def main():
    """Función principal de migración"""
    logger.info("🚀 INICIANDO MIGRACIÓN RBAC - SUBMÓDULO DE SELLOS")
    logger.info("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Paso 1: Crear tablas
            if not crear_tablas_rbac():
                logger.error("❌ Error en creación de tablas")
                return False
            
            # Paso 2: Verificar integridad
            if not verificar_integridad_rbac():
                logger.error("❌ Error en verificación de integridad")
                return False
            
            # Paso 3: Crear permisos
            if not crear_permisos_iniciales():
                logger.error("❌ Error creando permisos")
                return False
            
            # Paso 4: Crear roles
            if not crear_roles_iniciales():
                logger.error("❌ Error creando roles")
                return False
            
            # Paso 5: Asignar permisos a roles
            if not asignar_permisos_a_roles():
                logger.error("❌ Error asignando permisos")
                return False
            
            # Paso 6: Generar reporte
            if not generar_reporte_rbac():
                logger.error("❌ Error generando reporte")
                return False
            
            logger.info("🎉 MIGRACIÓN RBAC COMPLETADA EXITOSAMENTE")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error general en migración RBAC: {e}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 