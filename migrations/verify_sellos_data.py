"""
Script para verificar que los datos de seeding del submódulo de sellos
se crearon correctamente
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.models import db
from app.models.support_models import User
from app.models.sellos_models import TipoSello, MaestroVehiculo, Sello, SolicitudSello
from app.models.sellos_rbac_models import RolSellosModel, UsuarioRolSello
from app.models.sellos_notifications_models import ConfiguracionNotificacion, NotificacionSello

def verificar_datos():
    """Verificar que todos los datos de seeding se crearon correctamente."""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 VERIFICANDO DATOS DE SEEDING DEL SUBMÓDULO DE SELLOS")
            print("=" * 60)
            
            # ==================== VERIFICAR USUARIOS ====================
            print("\n👥 1. VERIFICANDO USUARIOS DE PRUEBA...")
            
            usuarios_esperados = ['admin_sellos', 'supervisor_sellos', 'operador_sellos', 'inspector_sellos']
            usuarios_encontrados = 0
            
            for username in usuarios_esperados:
                usuario = User.query.filter_by(username=username).first()
                if usuario:
                    usuarios_encontrados += 1
                    print(f"   ✅ Usuario encontrado: {username} (ID: {usuario.id}, Activo: {bool(usuario.is_active)})")
                else:
                    print(f"   ❌ Usuario NO encontrado: {username}")
            
            print(f"   📊 Usuarios encontrados: {usuarios_encontrados}/{len(usuarios_esperados)}")
            
            # ==================== VERIFICAR ASIGNACIONES DE ROLES ====================
            print("\n🔑 2. VERIFICANDO ASIGNACIONES DE ROLES...")
            
            total_asignaciones = UsuarioRolSello.query.filter_by(usuario_asignacion='sistema_seed').count()
            asignaciones_activas = UsuarioRolSello.query.filter_by(
                usuario_asignacion='sistema_seed',
                activo=True
            ).count()
            
            print(f"   ✅ Total asignaciones de roles: {total_asignaciones}")
            print(f"   ✅ Asignaciones activas: {asignaciones_activas}")
            
            # Detallar asignaciones por usuario
            for username in usuarios_esperados:
                usuario = User.query.filter_by(username=username).first()
                if usuario:
                    asignaciones = UsuarioRolSello.query.filter_by(usuario_id=usuario.id).all()
                    for asignacion in asignaciones:
                        print(f"   🔗 {username} → {asignacion.rol.nombre} (Activo: {asignacion.activo})")
            
            # ==================== VERIFICAR TIPOS DE SELLO ====================
            print("\n📝 3. VERIFICANDO TIPOS DE SELLO...")
            
            tipos_sello = TipoSello.query.filter_by(usuario_creacion='sistema_seed').all()
            print(f"   ✅ Tipos de sello creados: {len(tipos_sello)}")
            
            for tipo in tipos_sello:
                print(f"   🏷️  {tipo.nombre} (Prefijo: {tipo.prefijo}, Activo: {tipo.activo})")
                print(f"      • Proveedor: {tipo.proveedor}")
                print(f"      • Costo unitario: ${tipo.costo_unitario:,.2f}")
            
            # ==================== VERIFICAR VEHÍCULOS ====================
            print("\n🚗 4. VERIFICANDO MAESTRO DE VEHÍCULOS...")
            
            vehiculos = MaestroVehiculo.query.filter_by(usuario_creacion='sistema_seed').all()
            print(f"   ✅ Vehículos creados: {len(vehiculos)}")
            
            for vehiculo in vehiculos:
                puntos_count = len(eval(vehiculo.puntos_sellado)) if vehiculo.puntos_sellado else 0
                print(f"   🚛 {vehiculo.placa} (Sellos estándar: {vehiculo.cantidad_sellos_estandar}, Puntos: {puntos_count})")
                print(f"      • Observaciones: {vehiculo.observaciones}")
            
            # ==================== VERIFICAR SELLOS DE INVENTARIO ====================
            print("\n🏷️  5. VERIFICANDO SELLOS DE INVENTARIO...")
            
            sellos = Sello.query.filter_by(usuario_ingreso='sistema_seed').all()
            print(f"   ✅ Sellos creados: {len(sellos)}")
            
            # Contar por estado
            estados_count = {}
            for sello in sellos:
                estado = sello.estado.value if hasattr(sello.estado, 'value') else str(sello.estado)
                estados_count[estado] = estados_count.get(estado, 0) + 1
            
            for estado, count in estados_count.items():
                print(f"   📦 Estado {estado}: {count} sellos")
            
            # Contar por tipo
            tipos_count = {}
            for sello in sellos:
                if sello.tipo_sello_id:
                    tipo = TipoSello.query.get(sello.tipo_sello_id)
                    if tipo:
                        tipos_count[tipo.nombre] = tipos_count.get(tipo.nombre, 0) + 1
            
            for tipo_nombre, count in tipos_count.items():
                print(f"   🔖 {tipo_nombre}: {count} sellos")
            
            # ==================== VERIFICAR SOLICITUDES ====================
            print("\n📋 6. VERIFICANDO SOLICITUDES DE DEMOSTRACIÓN...")
            
            # Buscar solicitudes de usuarios de prueba
            solicitudes = SolicitudSello.query.filter(
                SolicitudSello.usuario_solicita.in_(usuarios_esperados)
            ).all()
            
            print(f"   ✅ Solicitudes creadas: {len(solicitudes)}")
            
            # Contar por estado
            estados_solicitudes = {}
            for solicitud in solicitudes:
                estados_solicitudes[solicitud.estado] = estados_solicitudes.get(solicitud.estado, 0) + 1
            
            for estado, count in estados_solicitudes.items():
                print(f"   📄 Estado {estado}: {count} solicitudes")
            
            # Detallar solicitudes
            for solicitud in solicitudes:
                print(f"   📝 Solicitud #{solicitud.id}: {solicitud.placa_vehiculo} - {solicitud.estado}")
                print(f"      • Solicitante: {solicitud.usuario_solicita}")
                print(f"      • Cantidad: {solicitud.cantidad_solicitada}")
                if solicitud.aprobada is not None:
                    print(f"      • Aprobada: {'Sí' if solicitud.aprobada else 'No'}")
            
            # ==================== VERIFICAR CONFIGURACIONES DE NOTIFICACIÓN ====================
            print("\n🔔 7. VERIFICANDO CONFIGURACIONES DE NOTIFICACIÓN...")
            
            configs = ConfiguracionNotificacion.query.filter_by(creado_por='sistema_seed').all()
            print(f"   ✅ Configuraciones creadas: {len(configs)}")
            
            # Agrupar por usuario
            configs_por_usuario = {}
            for config in configs:
                usuario = User.query.get(config.usuario_id)
                if usuario:
                    if usuario.username not in configs_por_usuario:
                        configs_por_usuario[usuario.username] = []
                    configs_por_usuario[usuario.username].append(config)
            
            for username, user_configs in configs_por_usuario.items():
                print(f"   👤 {username}: {len(user_configs)} configuraciones")
                for config in user_configs:
                    estado = "Activa" if config.activo else "Inactiva"
                    print(f"      • {config.tipo_notificacion.value} → {config.canal.value} ({estado})")
            
            # ==================== VERIFICAR NOTIFICACIONES ====================
            print("\n📨 8. VERIFICANDO NOTIFICACIONES DE DEMOSTRACIÓN...")
            
            notificaciones = NotificacionSello.query.filter_by(creado_por='sistema_seed').all()
            print(f"   ✅ Notificaciones creadas: {len(notificaciones)}")
            
            for notif in notificaciones:
                usuario = User.query.get(notif.usuario_id)
                estado_lectura = "Leída" if notif.leida_en else "No leída"
                print(f"   📧 {notif.asunto} → {usuario.username if usuario else 'Usuario desconocido'}")
                print(f"      • Estado: {notif.estado.value} ({estado_lectura})")
                print(f"      • Tipo: {notif.tipo_notificacion.value}")
                print(f"      • Canal: {notif.canal.value}")
            
            # ==================== RESUMEN GENERAL ====================
            print("\n" + "=" * 60)
            print("📊 RESUMEN DE VERIFICACIÓN:")
            print(f"   • ✅ Usuarios de prueba: {usuarios_encontrados}/{len(usuarios_esperados)}")
            print(f"   • ✅ Asignaciones de roles: {asignaciones_activas}")
            print(f"   • ✅ Tipos de sello: {len(tipos_sello)}")
            print(f"   • ✅ Vehículos maestro: {len(vehiculos)}")
            print(f"   • ✅ Sellos de inventario: {len(sellos)}")
            print(f"   • ✅ Solicitudes: {len(solicitudes)}")
            print(f"   • ✅ Configuraciones de notificación: {len(configs)}")
            print(f"   • ✅ Notificaciones: {len(notificaciones)}")
            
            # Verificar integridad
            errores = []
            
            if usuarios_encontrados != len(usuarios_esperados):
                errores.append(f"Faltan {len(usuarios_esperados) - usuarios_encontrados} usuarios")
            
            if len(tipos_sello) == 0:
                errores.append("No se encontraron tipos de sello")
            
            if len(sellos) == 0:
                errores.append("No se encontraron sellos de inventario")
            
            if errores:
                print("\n⚠️  PROBLEMAS DETECTADOS:")
                for error in errores:
                    print(f"   • {error}")
                print("\n❌ VERIFICACIÓN COMPLETADA CON ERRORES")
            else:
                print("\n✅ VERIFICACIÓN COMPLETADA EXITOSAMENTE")
                print("🎯 TODOS LOS DATOS DE SEEDING ESTÁN CORRECTOS")
                print("\n🚀 EL SUBMÓDULO DE SELLOS ESTÁ LISTO PARA:")
                print("   • Pruebas de funcionalidad completas")
                print("   • Demostraciones del sistema")
                print("   • Validación de flujos de trabajo")
                print("   • Testing de notificaciones y alertas")
                print("   • Capacitación de usuarios")
            
        except Exception as e:
            print(f"\n❌ ERROR EN LA VERIFICACIÓN: {e}")
            raise e

if __name__ == "__main__":
    verificar_datos() 