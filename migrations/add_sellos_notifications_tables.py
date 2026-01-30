"""
Migración para crear tablas del sistema de notificaciones de sellos
"""

import sys
import os
from datetime import datetime
import json

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.models import db
from app.models.sellos_notifications_models import (
    TipoNotificacion, PrioridadNotificacion, CanalNotificacion, EstadoNotificacion,
    ConfiguracionNotificacion, PlantillaNotificacion, NotificacionSello, ConfiguracionCanal
)

def ejecutar_migracion():
    """Ejecutar la migración para crear tablas de notificaciones."""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🚀 INICIANDO MIGRACIÓN DE NOTIFICACIONES DE SELLOS")
            print("=" * 60)
            
            # ==================== CREAR TABLAS ====================
            print("\n📋 1. CREANDO TABLAS DE NOTIFICACIONES...")
            
            # Crear tablas
            db.create_all()
            print("   ✅ Tablas creadas exitosamente")
            
            # ==================== CONFIGURAR CANALES ====================
            print("\n📡 2. CONFIGURANDO CANALES DE NOTIFICACIÓN...")
            
            canales_config = [
                {
                    'canal': CanalNotificacion.SISTEMA,
                    'activo': True,
                    'configuracion': {
                        'descripcion': 'Notificaciones dentro de la aplicación',
                        'icono': 'fas fa-bell',
                        'color': '#007bff'
                    },
                    'limite_por_hora': 1000,
                    'limite_por_dia': 10000
                },
                {
                    'canal': CanalNotificacion.EMAIL,
                    'activo': True,
                    'configuracion': {
                        'servidor_smtp': 'smtp.gmail.com',
                        'puerto': 587,
                        'usar_tls': True,
                        'email_remitente': 'sistema@oleoflores.com',
                        'plantilla_base': 'email_base.html'
                    },
                    'limite_por_hora': 100,
                    'limite_por_dia': 500
                },
                {
                    'canal': CanalNotificacion.SMS,
                    'activo': False,
                    'configuracion': {
                        'proveedor': 'twilio',
                        'api_url': 'https://api.twilio.com/2010-04-01/Accounts',
                        'numero_remitente': '+1234567890'
                    },
                    'limite_por_hora': 50,
                    'limite_por_dia': 200
                },
                {
                    'canal': CanalNotificacion.WHATSAPP,
                    'activo': False,
                    'configuracion': {
                        'proveedor': 'whatsapp_business',
                        'api_url': 'https://graph.facebook.com/v18.0',
                        'numero_telefono_id': '1234567890'
                    },
                    'limite_por_hora': 30,
                    'limite_por_dia': 100
                },
                {
                    'canal': CanalNotificacion.SLACK,
                    'activo': False,
                    'configuracion': {
                        'webhook_url': 'https://hooks.slack.com/services/...',
                        'canal_default': '#notificaciones-sellos',
                        'bot_name': 'OleoFlores Bot'
                    },
                    'limite_por_hora': 200,
                    'limite_por_dia': 1000
                },
                {
                    'canal': CanalNotificacion.TEAMS,
                    'activo': False,
                    'configuracion': {
                        'webhook_url': 'https://outlook.office.com/webhook/...',
                        'tema_color': '#FF6600'
                    },
                    'limite_por_hora': 200,
                    'limite_por_dia': 1000
                }
            ]
            
            for config_data in canales_config:
                config_existente = ConfiguracionCanal.query.filter_by(
                    canal=config_data['canal']
                ).first()
                
                if not config_existente:
                    config = ConfiguracionCanal(
                        canal=config_data['canal'],
                        activo=config_data['activo'],
                        configuracion=json.dumps(config_data['configuracion']),
                        limite_por_hora=config_data['limite_por_hora'],
                        limite_por_dia=config_data['limite_por_dia'],
                        timeout_segundos=30,
                        actualizado_por='migracion'
                    )
                    db.session.add(config)
                    print(f"   ✅ Canal {config_data['canal'].value} configurado")
                else:
                    print(f"   ⚠️  Canal {config_data['canal'].value} ya existe")
            
            # ==================== CREAR PLANTILLAS ====================
            print("\n📝 3. CREANDO PLANTILLAS DE NOTIFICACIÓN...")
            
            plantillas = [
                # SOLICITUD_PENDIENTE
                {
                    'tipo': TipoNotificacion.SOLICITUD_PENDIENTE,
                    'canal': CanalNotificacion.SISTEMA,
                    'asunto': 'Nueva solicitud de sellos pendiente',
                    'titulo': 'Solicitud Pendiente',
                    'mensaje': 'Hay una nueva solicitud de sellos #{solicitud_id} de {usuario_solicitante} pendiente de revisión.',
                    'variables': ['solicitud_id', 'usuario_solicitante', 'cantidad_sellos', 'fecha_solicitud']
                },
                {
                    'tipo': TipoNotificacion.SOLICITUD_PENDIENTE,
                    'canal': CanalNotificacion.EMAIL,
                    'asunto': 'Nueva solicitud de sellos #{solicitud_id} - Revisión requerida',
                    'titulo': 'Solicitud de Sellos Pendiente',
                    'mensaje': '''Estimado/a {destinatario_nombre},
                    
Hay una nueva solicitud de sellos que requiere su revisión:

• Solicitud ID: #{solicitud_id}
• Solicitante: {usuario_solicitante}
• Cantidad: {cantidad_sellos} sellos
• Fecha: {fecha_solicitud}
• Justificación: {justificacion}

Por favor, ingrese al sistema para revisar y aprobar/rechazar esta solicitud.

Saludos,
Sistema OleoFlores''',
                    'variables': ['solicitud_id', 'usuario_solicitante', 'cantidad_sellos', 'fecha_solicitud', 'justificacion', 'destinatario_nombre']
                },
                
                # APROBACION_REQUERIDA
                {
                    'tipo': TipoNotificacion.APROBACION_REQUERIDA,
                    'canal': CanalNotificacion.SISTEMA,
                    'asunto': 'Aprobación requerida para solicitud #{solicitud_id}',
                    'titulo': 'Aprobación Requerida',
                    'mensaje': 'La solicitud #{solicitud_id} requiere su aprobación. Cantidad: {cantidad_sellos} sellos.',
                    'variables': ['solicitud_id', 'cantidad_sellos', 'usuario_solicitante']
                },
                
                # SOLICITUD_APROBADA
                {
                    'tipo': TipoNotificacion.SOLICITUD_APROBADA,
                    'canal': CanalNotificacion.SISTEMA,
                    'asunto': 'Solicitud #{solicitud_id} aprobada',
                    'titulo': 'Solicitud Aprobada',
                    'mensaje': 'Su solicitud #{solicitud_id} ha sido aprobada por {aprobador}. Los sellos estarán disponibles para despacho.',
                    'variables': ['solicitud_id', 'aprobador', 'fecha_aprobacion', 'cantidad_sellos']
                },
                {
                    'tipo': TipoNotificacion.SOLICITUD_APROBADA,
                    'canal': CanalNotificacion.EMAIL,
                    'asunto': 'Solicitud de sellos #{solicitud_id} aprobada',
                    'titulo': 'Solicitud Aprobada',
                    'mensaje': '''Estimado/a {destinatario_nombre},
                    
Su solicitud de sellos ha sido aprobada:

• Solicitud ID: #{solicitud_id}
• Cantidad aprobada: {cantidad_sellos} sellos
• Aprobado por: {aprobador}
• Fecha de aprobación: {fecha_aprobacion}

Los sellos estarán disponibles para despacho en el almacén.

Saludos,
Sistema OleoFlores''',
                    'variables': ['solicitud_id', 'cantidad_sellos', 'aprobador', 'fecha_aprobacion', 'destinatario_nombre']
                },
                
                # SOLICITUD_RECHAZADA
                {
                    'tipo': TipoNotificacion.SOLICITUD_RECHAZADA,
                    'canal': CanalNotificacion.SISTEMA,
                    'asunto': 'Solicitud #{solicitud_id} rechazada',
                    'titulo': 'Solicitud Rechazada',
                    'mensaje': 'Su solicitud #{solicitud_id} ha sido rechazada por {rechazador}. Motivo: {motivo_rechazo}',
                    'variables': ['solicitud_id', 'rechazador', 'motivo_rechazo', 'fecha_rechazo']
                },
                
                # DESPACHO_DISPONIBLE
                {
                    'tipo': TipoNotificacion.DESPACHO_DISPONIBLE,
                    'canal': CanalNotificacion.SISTEMA,
                    'asunto': 'Sellos listos para despacho - Solicitud #{solicitud_id}',
                    'titulo': 'Despacho Disponible',
                    'mensaje': 'Los sellos de la solicitud #{solicitud_id} están listos para despacho en el almacén.',
                    'variables': ['solicitud_id', 'cantidad_sellos', 'ubicacion_almacen']
                },
                
                # SELLOS_DESPACHADOS
                {
                    'tipo': TipoNotificacion.SELLOS_DESPACHADOS,
                    'canal': CanalNotificacion.SISTEMA,
                    'asunto': 'Sellos despachados - Solicitud #{solicitud_id}',
                    'titulo': 'Sellos Despachados',
                    'mensaje': 'Se han despachado {cantidad_sellos} sellos para la solicitud #{solicitud_id}. Despachado por: {despachador}',
                    'variables': ['solicitud_id', 'cantidad_sellos', 'despachador', 'fecha_despacho']
                },
                
                # INSTALACION_REQUERIDA
                {
                    'tipo': TipoNotificacion.INSTALACION_REQUERIDA,
                    'canal': CanalNotificacion.SISTEMA,
                    'asunto': 'Instalación de sellos requerida - Vehículo {placa_vehiculo}',
                    'titulo': 'Instalación Requerida',
                    'mensaje': 'Se requiere la instalación de sellos en el vehículo {placa_vehiculo}. Sellos asignados: {seriales_sellos}',
                    'variables': ['placa_vehiculo', 'seriales_sellos', 'ubicacion_instalacion']
                },
                
                # INSTALACION_COMPLETADA
                {
                    'tipo': TipoNotificacion.INSTALACION_COMPLETADA,
                    'canal': CanalNotificacion.SISTEMA,
                    'asunto': 'Instalación completada - Vehículo {placa_vehiculo}',
                    'titulo': 'Instalación Completada',
                    'mensaje': 'La instalación de sellos en el vehículo {placa_vehiculo} ha sido completada por {instalador}.',
                    'variables': ['placa_vehiculo', 'instalador', 'fecha_instalacion', 'seriales_instalados']
                },
                
                # VALIDACION_PORTERIA
                {
                    'tipo': TipoNotificacion.VALIDACION_PORTERIA,
                    'canal': CanalNotificacion.SISTEMA,
                    'asunto': 'Validación en portería requerida - Vehículo {placa_vehiculo}',
                    'titulo': 'Validación Portería',
                    'mensaje': 'El vehículo {placa_vehiculo} requiere validación de sellos en portería.',
                    'variables': ['placa_vehiculo', 'seriales_esperados', 'hora_llegada']
                },
                
                # ALERTA_STOCK_BAJO
                {
                    'tipo': TipoNotificacion.ALERTA_STOCK_BAJO,
                    'canal': CanalNotificacion.SISTEMA,
                    'asunto': 'Alerta: Stock bajo de sellos tipo {tipo_sello}',
                    'titulo': 'Stock Bajo',
                    'mensaje': 'El stock de sellos tipo {tipo_sello} está bajo. Stock actual: {stock_actual}, Mínimo: {stock_minimo}',
                    'variables': ['tipo_sello', 'stock_actual', 'stock_minimo']
                }
            ]
            
            for plantilla_data in plantillas:
                plantilla_existente = PlantillaNotificacion.query.filter_by(
                    tipo_notificacion=plantilla_data['tipo'],
                    canal=plantilla_data['canal']
                ).first()
                
                if not plantilla_existente:
                    plantilla = PlantillaNotificacion(
                        tipo_notificacion=plantilla_data['tipo'],
                        canal=plantilla_data['canal'],
                        idioma='es',
                        asunto=plantilla_data['asunto'],
                        titulo=plantilla_data.get('titulo'),
                        mensaje=plantilla_data['mensaje'],
                        variables_disponibles=json.dumps(plantilla_data['variables']),
                        activa=True,
                        version='1.0',
                        creado_por='migracion'
                    )
                    db.session.add(plantilla)
                    print(f"   ✅ Plantilla {plantilla_data['tipo'].value}:{plantilla_data['canal'].value}")
                else:
                    print(f"   ⚠️  Plantilla {plantilla_data['tipo'].value}:{plantilla_data['canal'].value} ya existe")
            
            # ==================== CONFIGURACIONES DEFAULT ====================
            print("\n⚙️  4. CONFIGURANDO NOTIFICACIONES POR DEFECTO...")
            
            # Obtener usuarios con roles de sellos para configurar notificaciones por defecto
            from app.models.sellos_rbac_models import UsuarioRolSello, RolSello
            
            usuarios_con_roles = db.session.query(UsuarioRolSello).filter_by(activo=True).all()
            
            # Configuraciones por rol
            configuraciones_por_rol = {
                RolSello.ADMIN_SELLOS: [
                    (TipoNotificacion.SOLICITUD_PENDIENTE, CanalNotificacion.SISTEMA),
                    (TipoNotificacion.SOLICITUD_PENDIENTE, CanalNotificacion.EMAIL),
                    (TipoNotificacion.ALERTA_STOCK_BAJO, CanalNotificacion.SISTEMA),
                    (TipoNotificacion.ALERTA_STOCK_BAJO, CanalNotificacion.EMAIL),
                    (TipoNotificacion.SISTEMA_ERROR, CanalNotificacion.EMAIL)
                ],
                RolSello.SUPERVISOR_SELLOS: [
                    (TipoNotificacion.SOLICITUD_PENDIENTE, CanalNotificacion.SISTEMA),
                    (TipoNotificacion.APROBACION_REQUERIDA, CanalNotificacion.SISTEMA),
                    (TipoNotificacion.APROBACION_REQUERIDA, CanalNotificacion.EMAIL),
                    (TipoNotificacion.ALERTA_STOCK_BAJO, CanalNotificacion.SISTEMA)
                ],
                RolSello.OPERADOR_SELLOS: [
                    (TipoNotificacion.SOLICITUD_APROBADA, CanalNotificacion.SISTEMA),
                    (TipoNotificacion.SOLICITUD_RECHAZADA, CanalNotificacion.SISTEMA),
                    (TipoNotificacion.DESPACHO_DISPONIBLE, CanalNotificacion.SISTEMA)
                ],
                RolSello.INSPECTOR_SELLOS: [
                    (TipoNotificacion.INSTALACION_REQUERIDA, CanalNotificacion.SISTEMA),
                    (TipoNotificacion.VALIDACION_PORTERIA, CanalNotificacion.SISTEMA),
                    (TipoNotificacion.INSTALACION_COMPLETADA, CanalNotificacion.SISTEMA)
                ]
            }
            
            configuraciones_creadas = 0
            for asignacion_rol in usuarios_con_roles:
                rol_enum = RolSello(asignacion_rol.rol.codigo)
                
                if rol_enum in configuraciones_por_rol:
                    for tipo_notif, canal in configuraciones_por_rol[rol_enum]:
                        config_existente = ConfiguracionNotificacion.query.filter_by(
                            usuario_id=asignacion_rol.usuario_id,
                            tipo_notificacion=tipo_notif,
                            canal=canal
                        ).first()
                        
                        if not config_existente:
                            config = ConfiguracionNotificacion(
                                usuario_id=asignacion_rol.usuario_id,
                                tipo_notificacion=tipo_notif,
                                canal=canal,
                                activo=True,
                                hora_inicio='08:00',
                                hora_fin='18:00',
                                dias_semana='1,2,3,4,5',
                                creado_por='migracion'
                            )
                            db.session.add(config)
                            configuraciones_creadas += 1
            
            print(f"   ✅ {configuraciones_creadas} configuraciones de notificación creadas")
            
            # ==================== COMMIT CAMBIOS ====================
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✅ MIGRACIÓN DE NOTIFICACIONES COMPLETADA EXITOSAMENTE")
            print("\n📊 RESUMEN:")
            print(f"   • {len(canales_config)} canales de notificación configurados")
            print(f"   • {len(plantillas)} plantillas de notificación creadas")
            print(f"   • {configuraciones_creadas} configuraciones de usuario creadas")
            print("\n🔧 PRÓXIMOS PASOS:")
            print("   1. Configurar credenciales SMTP para email")
            print("   2. Configurar APIs de terceros (SMS, WhatsApp, etc.)")
            print("   3. Probar envío de notificaciones")
            print("   4. Configurar tareas programadas para procesamiento")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR EN LA MIGRACIÓN: {e}")
            raise e

if __name__ == "__main__":
    ejecutar_migracion() 