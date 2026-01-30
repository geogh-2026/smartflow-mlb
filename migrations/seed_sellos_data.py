"""
Script para crear datos iniciales de testing y demostración
para el submódulo de sellos
"""

import sys
import os
from datetime import datetime, timedelta
import json
import random

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.models import db
from app.models.support_models import User
from app.models.sellos_models import TipoSello, MaestroVehiculo, Sello, SolicitudSello, MovimientoSello, EstadoSello
from app.models.sellos_rbac_models import (
    RolSello, PermisoSello, RolSellosModel, PermisoSellosModel, 
    UsuarioRolSello, AuditoriaRolSello
)
from app.models.sellos_notifications_models import (
    TipoNotificacion, CanalNotificacion, ConfiguracionNotificacion, 
    PlantillaNotificacion, NotificacionSello, EstadoNotificacion
)

def ejecutar_seeding():
    """Ejecutar el proceso completo de seeding."""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🌱 INICIANDO SEEDING DE DATOS PARA SELLOS")
            print("=" * 60)
            
            # ==================== CREAR USUARIOS DE PRUEBA ====================
            print("\n👥 1. CREANDO USUARIOS DE PRUEBA...")
            
            usuarios_prueba = [
                {
                    'username': 'admin_sellos',
                    'email': 'admin.sellos@oleoflores.com',
                    'password': 'admin123',
                    'role': 'admin_sellos',
                    'is_active': 1
                },
                {
                    'username': 'supervisor_sellos',
                    'email': 'supervisor.sellos@oleoflores.com',
                    'password': 'super123',
                    'role': 'supervisor_sellos',
                    'is_active': 1
                },
                {
                    'username': 'operador_sellos',
                    'email': 'operador.sellos@oleoflores.com',
                    'password': 'oper123',
                    'role': 'operador_sellos',
                    'is_active': 1
                },
                {
                    'username': 'inspector_sellos',
                    'email': 'inspector.sellos@oleoflores.com',
                    'password': 'insp123',
                    'role': 'inspector_sellos',
                    'is_active': 1
                }
            ]
            
            usuarios_creados = []
            for user_data in usuarios_prueba:
                usuario_existente = User.query.filter_by(username=user_data['username']).first()
                if not usuario_existente:
                    usuario = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        password_hash=user_data['password'],  # En producción usar hash
                        is_active=user_data['is_active']
                    )
                    db.session.add(usuario)
                    db.session.flush()
                    usuarios_creados.append(usuario)
                    print(f"   ✅ Usuario creado: {user_data['username']}")
                else:
                    usuarios_creados.append(usuario_existente)
                    print(f"   ⚠️  Usuario ya existe: {user_data['username']}")
            
            # ==================== ASIGNAR ROLES A USUARIOS ====================
            print("\n🔑 2. ASIGNANDO ROLES A USUARIOS...")
            
            roles_asignaciones = [
                ('admin_sellos', RolSello.ADMIN_SELLOS),
                ('supervisor_sellos', RolSello.SUPERVISOR_SELLOS),
                ('operador_sellos', RolSello.OPERADOR_SELLOS),
                ('inspector_sellos', RolSello.INSPECTOR_SELLOS)
            ]
            
            for username, rol_enum in roles_asignaciones:
                usuario = User.query.filter_by(username=username).first()
                if usuario:
                    rol = RolSellosModel.query.filter_by(nombre=rol_enum.value).first()
                    if rol:
                        asignacion_existente = UsuarioRolSello.query.filter_by(
                            usuario_id=usuario.id,
                            rol_id=rol.id
                        ).first()
                        
                        if not asignacion_existente:
                            asignacion = UsuarioRolSello.asignar_rol(
                                usuario_id=usuario.id,
                                usuario_username=usuario.username,
                                rol_id=rol.id,
                                usuario_asignacion='sistema_seed',
                                observaciones=f'Asignación automática para testing - {rol.nombre}'
                            )
                            print(f"   ✅ Rol {rol.nombre} asignado a {username}")
                        else:
                            print(f"   ⚠️  {username} ya tiene el rol {rol.nombre}")
            
            # ==================== CREAR TIPOS DE SELLO ====================
            print("\n📝 3. CREANDO TIPOS DE SELLO...")
            
            tipos_sello_data = [
                {
                    'nombre': 'Sello Estándar Tipo A',
                    'prefijo': 'SA',
                    'proveedor': 'Seguridad Industrial S.A.',
                    'descripcion': 'Sello de seguridad estándar para uso general en vehículos de carga',
                    'longitud_serie': 6,
                    'costo_unitario': 2500.00,
                    'rango_inicial': '001000',
                    'rango_final': '050000',
                    'activo': True
                },
                {
                    'nombre': 'Sello Alta Seguridad Tipo B',
                    'prefijo': 'SB',
                    'proveedor': 'SecureTech Colombia',
                    'descripcion': 'Sello de alta seguridad con tecnología RFID para cargas especiales',
                    'longitud_serie': 6,
                    'costo_unitario': 4500.00,
                    'rango_inicial': '100000',
                    'rango_final': '120000',
                    'activo': True
                },
                {
                    'nombre': 'Sello Temporal Tipo C',
                    'prefijo': 'SC',
                    'proveedor': 'Temporal Security',
                    'descripcion': 'Sello temporal para inspecciones y mantenimiento',
                    'longitud_serie': 6,
                    'costo_unitario': 1200.00,
                    'rango_inicial': '200000',
                    'rango_final': '210000',
                    'activo': True
                },
                {
                    'nombre': 'Sello Especial Graneles',
                    'prefijo': 'SG',
                    'proveedor': 'Agro Security',
                    'descripcion': 'Sello especializado para transporte de graneles agrícolas',
                    'longitud_serie': 6,
                    'costo_unitario': 3200.00,
                    'rango_inicial': '300000',
                    'rango_final': '320000',
                    'activo': True
                }
            ]
            
            tipos_creados = []
            for tipo_data in tipos_sello_data:
                tipo_existente = TipoSello.query.filter_by(prefijo=tipo_data['prefijo']).first()
                if not tipo_existente:
                    tipo_sello = TipoSello(
                        nombre=tipo_data['nombre'],
                        prefijo=tipo_data['prefijo'],
                        proveedor=tipo_data['proveedor'],
                        descripcion=tipo_data['descripcion'],
                        longitud_serial=tipo_data['longitud_serie'],
                        costo_unitario=tipo_data['costo_unitario'],
                        activo=tipo_data['activo'],
                        usuario_creacion='sistema_seed',
                        fecha_creacion=datetime.utcnow()
                    )
                    db.session.add(tipo_sello)
                    db.session.flush()
                    tipos_creados.append(tipo_sello)
                    print(f"   ✅ Tipo de sello creado: {tipo_data['nombre']}")
                else:
                    tipos_creados.append(tipo_existente)
                    print(f"   ⚠️  Tipo de sello ya existe: {tipo_data['nombre']}")
            
            # ==================== CREAR MAESTRO DE VEHÍCULOS ====================
            print("\n🚗 4. CREANDO MAESTRO DE VEHÍCULOS...")
            
            vehiculos_data = [
                {
                    'placa': 'ABC123',
                    'cantidad_sellos_estandar': 4,
                    'puntos_sellado': {
                        'puerta_trasera': {'x': 100, 'y': 200, 'descripcion': 'Puerta trasera principal'},
                        'compuerta_lateral': {'x': 50, 'y': 150, 'descripcion': 'Compuerta lateral izquierda'},
                        'tapa_superior': {'x': 150, 'y': 100, 'descripcion': 'Tapa superior del contenedor'},
                        'valvula_descarga': {'x': 75, 'y': 250, 'descripcion': 'Válvula de descarga inferior'}
                    },
                    'observaciones': 'Vehículo estándar para transporte de graneles',
                    'activo': True
                },
                {
                    'placa': 'DEF456',
                    'cantidad_sellos_estandar': 6,
                    'puntos_sellado': {
                        'puerta_principal': {'x': 120, 'y': 180, 'descripcion': 'Puerta principal de carga'},
                        'puerta_secundaria': {'x': 80, 'y': 180, 'descripcion': 'Puerta secundaria'},
                        'compuerta_izq': {'x': 40, 'y': 140, 'descripcion': 'Compuerta lateral izquierda'},
                        'compuerta_der': {'x': 160, 'y': 140, 'descripcion': 'Compuerta lateral derecha'},
                        'tapa_frontal': {'x': 100, 'y': 80, 'descripcion': 'Tapa frontal'},
                        'valvula_central': {'x': 100, 'y': 220, 'descripcion': 'Válvula central de descarga'}
                    },
                    'observaciones': 'Vehículo de alta capacidad con múltiples puntos de sellado',
                    'activo': True
                },
                {
                    'placa': 'GHI789',
                    'cantidad_sellos_estandar': 2,
                    'puntos_sellado': {
                        'puerta_unica': {'x': 100, 'y': 200, 'descripcion': 'Puerta única de acceso'},
                        'valvula_descarga': {'x': 100, 'y': 250, 'descripcion': 'Válvula de descarga'}
                    },
                    'observaciones': 'Vehículo pequeño para transporte local',
                    'activo': True
                },
                {
                    'placa': 'JKL012',
                    'cantidad_sellos_estandar': 8,
                    'puntos_sellado': {
                        'puerta_1': {'x': 60, 'y': 160, 'descripcion': 'Puerta compartimento 1'},
                        'puerta_2': {'x': 100, 'y': 160, 'descripcion': 'Puerta compartimento 2'},
                        'puerta_3': {'x': 140, 'y': 160, 'descripcion': 'Puerta compartimento 3'},
                        'puerta_4': {'x': 180, 'y': 160, 'descripcion': 'Puerta compartimento 4'},
                        'valvula_1': {'x': 60, 'y': 240, 'descripcion': 'Válvula compartimento 1'},
                        'valvula_2': {'x': 100, 'y': 240, 'descripcion': 'Válvula compartimento 2'},
                        'valvula_3': {'x': 140, 'y': 240, 'descripcion': 'Válvula compartimento 3'},
                        'valvula_4': {'x': 180, 'y': 240, 'descripcion': 'Válvula compartimento 4'}
                    },
                    'observaciones': 'Vehículo especializado con múltiples compartimentos',
                    'activo': True
                }
            ]
            
            vehiculos_creados = []
            for vehiculo_data in vehiculos_data:
                vehiculo_existente = MaestroVehiculo.query.filter_by(placa=vehiculo_data['placa']).first()
                if not vehiculo_existente:
                    vehiculo = MaestroVehiculo(
                        placa=vehiculo_data['placa'],
                        cantidad_sellos_estandar=vehiculo_data['cantidad_sellos_estandar'],
                        puntos_sellado=json.dumps(vehiculo_data['puntos_sellado']),
                        observaciones=vehiculo_data['observaciones'],
                        activo=vehiculo_data['activo'],
                        usuario_creacion='sistema_seed',
                        fecha_creacion=datetime.utcnow()
                    )
                    db.session.add(vehiculo)
                    db.session.flush()
                    vehiculos_creados.append(vehiculo)
                    print(f"   ✅ Vehículo creado: {vehiculo_data['placa']}")
                else:
                    vehiculos_creados.append(vehiculo_existente)
                    print(f"   ⚠️  Vehículo ya existe: {vehiculo_data['placa']}")
            
            # ==================== CREAR SELLOS DE INVENTARIO ====================
            print("\n🏷️  5. CREANDO SELLOS DE INVENTARIO...")
            
            sellos_creados = []
            for tipo_sello in tipos_creados:
                # Crear 50 sellos por cada tipo para demostración
                cantidad_sellos = 50
                
                for i in range(cantidad_sellos):
                    numero_serie = str(1000 + i).zfill(6)
                    serial_completo = f"{tipo_sello.prefijo}{numero_serie}"
                    
                    sello_existente = Sello.query.filter_by(numero_serie=serial_completo).first()
                    if not sello_existente:
                        sello = Sello(
                            numero_serie=serial_completo,
                            tipo_sello_id=tipo_sello.id,
                            estado=EstadoSello.EN_ALMACEN_LABORATORIO,
                            fecha_ingreso=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                            lote_ingreso=f"LOTE-{tipo_sello.prefijo}-2024-{random.randint(1, 12):02d}",
                            usuario_ingreso='sistema_seed',
                            observaciones='Sello de demostración creado por seeding'
                        )
                        db.session.add(sello)
                        sellos_creados.append(sello)
                
                print(f"   ✅ {cantidad_sellos} sellos creados para {tipo_sello.nombre}")
            
            # ==================== CREAR SOLICITUDES DE DEMOSTRACIÓN ====================
            print("\n📋 6. CREANDO SOLICITUDES DE DEMOSTRACIÓN...")
            
            # Obtener usuarios para las solicitudes
            admin_user = User.query.filter_by(username='admin_sellos').first()
            supervisor_user = User.query.filter_by(username='supervisor_sellos').first()
            operador_user = User.query.filter_by(username='operador_sellos').first()
            
            solicitudes_data = [
                {
                    'vehiculo': vehiculos_creados[0],
                    'tipo_sello': tipos_creados[0],
                    'cantidad': 4,
                    'usuario_solicita': operador_user,
                    'estado': 'pendiente',
                    'justificacion': 'Solicitud para transporte de maíz a Medellín',
                    'dias_atras': 1
                },
                {
                    'vehiculo': vehiculos_creados[1],
                    'tipo_sello': tipos_creados[1],
                    'cantidad': 6,
                    'usuario_solicita': operador_user,
                    'estado': 'aprobada',
                    'justificacion': 'Transporte especial de soya con alta seguridad',
                    'usuario_aprueba': supervisor_user,
                    'dias_atras': 2
                },
                {
                    'vehiculo': vehiculos_creados[2],
                    'tipo_sello': tipos_creados[2],
                    'cantidad': 2,
                    'usuario_solicita': operador_user,
                    'estado': 'despachada',
                    'justificacion': 'Transporte local de arroz',
                    'usuario_aprueba': supervisor_user,
                    'usuario_despacha': admin_user,
                    'dias_atras': 3
                },
                {
                    'vehiculo': vehiculos_creados[3],
                    'tipo_sello': tipos_creados[3],
                    'cantidad': 8,
                    'usuario_solicita': operador_user,
                    'estado': 'rechazada',
                    'justificacion': 'Solicitud de emergencia para frijol',
                    'usuario_aprueba': supervisor_user,
                    'motivo_rechazo': 'No hay disponibilidad de sellos tipo SG',
                    'dias_atras': 4
                }
            ]
            
            solicitudes_creadas = []
            for sol_data in solicitudes_data:
                fecha_solicitud = datetime.utcnow() - timedelta(days=sol_data['dias_atras'])
                
                solicitud = SolicitudSello(
                    placa_vehiculo=sol_data['vehiculo'].placa,
                    cantidad_solicitada=sol_data['cantidad'],
                    usuario_solicita=sol_data['usuario_solicita'].username,
                    estado=sol_data['estado'],
                    justificacion_extra=sol_data['justificacion'],
                    fecha_solicitud=fecha_solicitud,
                    fecha_creacion=fecha_solicitud
                )
                
                # Configurar campos según el estado
                if sol_data['estado'] in ['aprobada', 'despachada', 'rechazada']:
                    solicitud.usuario_aprobacion = sol_data['usuario_aprueba'].username
                    solicitud.fecha_aprobacion = fecha_solicitud + timedelta(hours=2)
                    solicitud.aprobada = sol_data['estado'] != 'rechazada'
                    
                    if sol_data['estado'] == 'despachada':
                        solicitud.usuario_despacha = sol_data['usuario_despacha'].username
                        solicitud.fecha_despacho = fecha_solicitud + timedelta(hours=4)
                    elif sol_data['estado'] == 'rechazada':
                        solicitud.observaciones_aprobacion = sol_data['motivo_rechazo']
                
                db.session.add(solicitud)
                db.session.flush()
                solicitudes_creadas.append(solicitud)
                print(f"   ✅ Solicitud creada: {sol_data['vehiculo'].placa} - {sol_data['estado']}")
            
            # ==================== ACTUALIZAR SELLOS DESPACHADOS ====================
            print("\n📦 7. ACTUALIZANDO SELLOS DESPACHADOS...")
            
            sellos_actualizados = 0
            for solicitud in solicitudes_creadas:
                if solicitud.estado == 'despachada':
                    # Actualizar sellos para mostrar como despachados
                    sellos_disponibles = [s for s in sellos_creados][:solicitud.cantidad_solicitada]
                    
                    for sello in sellos_disponibles:
                        # Actualizar estado del sello
                        sello.estado = EstadoSello.VALIDADO_DESPACHADO
                        sello.placa_vehiculo = solicitud.placa_vehiculo
                        sello.fecha_despacho = solicitud.fecha_despacho
                        sello.usuario_despacho = solicitud.usuario_despacha
                        
                        sellos_actualizados += 1
            
            print(f"   ✅ {sellos_actualizados} sellos actualizados como despachados")
            
            # ==================== CONFIGURAR NOTIFICACIONES DE PRUEBA ====================
            print("\n🔔 8. CONFIGURANDO NOTIFICACIONES DE PRUEBA...")
            
            # Configurar notificaciones para usuarios de prueba
            configuraciones_notif = [
                ('admin_sellos', TipoNotificacion.SOLICITUD_PENDIENTE, CanalNotificacion.SISTEMA),
                ('admin_sellos', TipoNotificacion.ALERTA_STOCK_BAJO, CanalNotificacion.EMAIL),
                ('supervisor_sellos', TipoNotificacion.APROBACION_REQUERIDA, CanalNotificacion.SISTEMA),
                ('operador_sellos', TipoNotificacion.SOLICITUD_APROBADA, CanalNotificacion.SISTEMA),
                ('inspector_sellos', TipoNotificacion.INSTALACION_REQUERIDA, CanalNotificacion.SISTEMA)
            ]
            
            notif_configuradas = 0
            for username, tipo_notif, canal in configuraciones_notif:
                usuario = User.query.filter_by(username=username).first()
                if usuario:
                    config_existente = ConfiguracionNotificacion.query.filter_by(
                        usuario_id=usuario.id,
                        tipo_notificacion=tipo_notif,
                        canal=canal
                    ).first()
                    
                    if not config_existente:
                        config = ConfiguracionNotificacion(
                            usuario_id=usuario.id,
                            tipo_notificacion=tipo_notif,
                            canal=canal,
                            activo=True,
                            hora_inicio='08:00',
                            hora_fin='18:00',
                            dias_semana='1,2,3,4,5',
                            creado_por='sistema_seed'
                        )
                        db.session.add(config)
                        notif_configuradas += 1
            
            print(f"   ✅ {notif_configuradas} configuraciones de notificación creadas")
            
            # ==================== CREAR NOTIFICACIONES DE DEMOSTRACIÓN ====================
            print("\n📨 9. CREANDO NOTIFICACIONES DE DEMOSTRACIÓN...")
            
            # Crear algunas notificaciones de ejemplo
            admin_user = User.query.filter_by(username='admin_sellos').first()
            if admin_user:
                # Notificación de solicitud pendiente
                notif1 = NotificacionSello(
                    usuario_id=admin_user.id,
                    tipo_notificacion=TipoNotificacion.SOLICITUD_PENDIENTE,
                    canal=CanalNotificacion.SISTEMA,
                    asunto='Nueva solicitud de sellos pendiente',
                    mensaje=f'Hay una nueva solicitud de sellos #{solicitudes_creadas[0].id} pendiente de revisión.',
                    estado=EstadoNotificacion.ENTREGADA,
                    programada_para=datetime.utcnow(),
                    enviada_en=datetime.utcnow(),
                    entregada_en=datetime.utcnow(),
                    referencia_tipo='solicitud_sello',
                    referencia_id=solicitudes_creadas[0].id,
                    creado_por='sistema_seed'
                )
                db.session.add(notif1)
                
                # Notificación de stock bajo
                notif2 = NotificacionSello(
                    usuario_id=admin_user.id,
                    tipo_notificacion=TipoNotificacion.ALERTA_STOCK_BAJO,
                    canal=CanalNotificacion.SISTEMA,
                    asunto='Alerta: Stock bajo de sellos',
                    mensaje=f'El stock de sellos tipo {tipos_creados[0].nombre} está bajo. Stock actual: 46, Mínimo: 50',
                    estado=EstadoNotificacion.ENTREGADA,
                    programada_para=datetime.utcnow() - timedelta(hours=2),
                    enviada_en=datetime.utcnow() - timedelta(hours=2),
                    entregada_en=datetime.utcnow() - timedelta(hours=2),
                    referencia_tipo='tipo_sello',
                    referencia_id=tipos_creados[0].id,
                    creado_por='sistema_seed'
                )
                db.session.add(notif2)
                
                print(f"   ✅ 2 notificaciones de demostración creadas")
            
            # ==================== COMMIT TODOS LOS CAMBIOS ====================
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✅ SEEDING COMPLETADO EXITOSAMENTE")
            print("\n📊 RESUMEN DE DATOS CREADOS:")
            print(f"   • {len(usuarios_creados)} usuarios de prueba")
            print(f"   • {len(tipos_creados)} tipos de sello")
            print(f"   • {len(vehiculos_creados)} vehículos maestro")
            print(f"   • {len(sellos_creados)} sellos de inventario")
            print(f"   • {len(solicitudes_creadas)} solicitudes de demostración")
            print(f"   • {sellos_actualizados} sellos actualizados como despachados")
            print(f"   • {notif_configuradas} configuraciones de notificación")
            print(f"   • 2 notificaciones de demostración")
            
            print("\n🔑 CREDENCIALES DE ACCESO:")
            print("   • admin_sellos / admin123")
            print("   • supervisor_sellos / super123")
            print("   • operador_sellos / oper123")
            print("   • inspector_sellos / insp123")
            
            print("\n🎯 DATOS LISTOS PARA:")
            print("   • Pruebas de funcionalidad")
            print("   • Demostraciones del sistema")
            print("   • Validación de flujos completos")
            print("   • Testing de notificaciones")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR EN EL SEEDING: {e}")
            raise e

if __name__ == "__main__":
    ejecutar_seeding() 