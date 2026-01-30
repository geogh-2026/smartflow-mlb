"""
Script para limpiar datos de prueba del submódulo de sellos
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.models import db
from app.models.support_models import User
from app.models.sellos_models import TipoSello, MaestroVehiculo, Sello, SolicitudSello, MovimientoSello
from app.models.sellos_rbac_models import UsuarioRolSello, AuditoriaRolSello
from app.models.sellos_notifications_models import ConfiguracionNotificacion, NotificacionSello

def limpiar_datos_prueba():
    """Limpiar todos los datos de prueba del submódulo de sellos."""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🧹 INICIANDO LIMPIEZA DE DATOS DE PRUEBA")
            print("=" * 50)
            
            # ==================== LIMPIAR NOTIFICACIONES ====================
            print("\n📨 1. LIMPIANDO NOTIFICACIONES...")
            
            # Eliminar notificaciones de prueba
            notificaciones_eliminadas = NotificacionSello.query.filter_by(creado_por='sistema_seed').delete()
            print(f"   ✅ {notificaciones_eliminadas} notificaciones eliminadas")
            
            # Eliminar configuraciones de notificación de prueba
            configs_eliminadas = ConfiguracionNotificacion.query.filter_by(creado_por='sistema_seed').delete()
            print(f"   ✅ {configs_eliminadas} configuraciones de notificación eliminadas")
            
            # ==================== LIMPIAR MOVIMIENTOS ====================
            print("\n📦 2. LIMPIANDO MOVIMIENTOS DE SELLOS...")
            
            # Obtener solicitudes de prueba para limpiar movimientos relacionados
            usuarios_prueba = ['admin_sellos', 'supervisor_sellos', 'operador_sellos', 'inspector_sellos']
            solicitudes_prueba = SolicitudSello.query.filter(
                SolicitudSello.usuario_solicita.in_(usuarios_prueba)
            ).all()
            
            movimientos_eliminados = 0
            for solicitud in solicitudes_prueba:
                movimientos = MovimientoSello.query.filter_by(solicitud_id=solicitud.id).all()
                for movimiento in movimientos:
                    db.session.delete(movimiento)
                    movimientos_eliminados += 1
            
            print(f"   ✅ {movimientos_eliminados} movimientos eliminados")
            
            # ==================== LIMPIAR SOLICITUDES ====================
            print("\n📋 3. LIMPIANDO SOLICITUDES...")
            
            solicitudes_eliminadas = len(solicitudes_prueba)
            for solicitud in solicitudes_prueba:
                db.session.delete(solicitud)
            
            print(f"   ✅ {solicitudes_eliminadas} solicitudes eliminadas")
            
            # ==================== LIMPIAR SELLOS ====================
            print("\n🏷️  4. LIMPIANDO SELLOS DE INVENTARIO...")
            
            # Restaurar estado de sellos que fueron despachados en las pruebas
            from app.models.sellos_models import EstadoSello
            sellos_actualizados = Sello.query.filter_by(usuario_ingreso='sistema_seed').update({
                'estado': EstadoSello.EN_ALMACEN_LABORATORIO,
                'placa_vehiculo': None,
                'fecha_despacho': None
            })
            
            # Eliminar sellos de prueba
            sellos_eliminados = Sello.query.filter_by(usuario_ingreso='sistema_seed').delete()
            print(f"   ✅ {sellos_eliminados} sellos eliminados")
            
            # ==================== LIMPIAR VEHÍCULOS ====================
            print("\n🚗 5. LIMPIANDO MAESTRO DE VEHÍCULOS...")
            
            vehiculos_eliminados = MaestroVehiculo.query.filter_by(usuario_creacion='sistema_seed').delete()
            print(f"   ✅ {vehiculos_eliminados} vehículos eliminados")
            
            # ==================== LIMPIAR TIPOS DE SELLO ====================
            print("\n📝 6. LIMPIANDO TIPOS DE SELLO...")
            
            tipos_eliminados = TipoSello.query.filter_by(usuario_creacion='sistema_seed').delete()
            print(f"   ✅ {tipos_eliminados} tipos de sello eliminados")
            
            # ==================== LIMPIAR ASIGNACIONES DE ROLES ====================
            print("\n🔑 7. LIMPIANDO ASIGNACIONES DE ROLES...")
            
            # Eliminar asignaciones de roles de prueba
            asignaciones_eliminadas = UsuarioRolSello.query.filter_by(usuario_asignacion='sistema_seed').delete()
            print(f"   ✅ {asignaciones_eliminadas} asignaciones de roles eliminadas")
            
            # Eliminar auditorías de prueba
            auditorias_eliminadas = AuditoriaRolSello.query.filter_by(usuario_accion='sistema_seed').delete()
            print(f"   ✅ {auditorias_eliminadas} registros de auditoría eliminados")
            
            # ==================== LIMPIAR USUARIOS DE PRUEBA ====================
            print("\n👥 8. LIMPIANDO USUARIOS DE PRUEBA...")
            
            usuarios_prueba = ['admin_sellos', 'supervisor_sellos', 'operador_sellos', 'inspector_sellos']
            usuarios_eliminados = 0
            
            for username in usuarios_prueba:
                usuario = User.query.filter_by(username=username).first()
                if usuario:
                    # Verificar que no tenga datos reales asociados antes de eliminar
                    # Por seguridad, solo marcar como inactivo en lugar de eliminar
                    usuario.is_active = 0
                    usuarios_eliminados += 1
                    print(f"   ⚠️  Usuario {username} marcado como inactivo (no eliminado por seguridad)")
            
            # ==================== COMMIT CAMBIOS ====================
            db.session.commit()
            
            print("\n" + "=" * 50)
            print("✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
            print("\n📊 RESUMEN DE LIMPIEZA:")
            print(f"   • {notificaciones_eliminadas} notificaciones eliminadas")
            print(f"   • {configs_eliminadas} configuraciones de notificación eliminadas")
            print(f"   • {movimientos_eliminados} movimientos eliminados")
            print(f"   • {solicitudes_eliminadas} solicitudes eliminadas")
            print(f"   • {sellos_eliminados} sellos eliminados")
            print(f"   • {vehiculos_eliminados} vehículos eliminados")
            print(f"   • {tipos_eliminados} tipos de sello eliminados")
            print(f"   • {asignaciones_eliminadas} asignaciones de roles eliminadas")
            print(f"   • {auditorias_eliminadas} registros de auditoría eliminados")
            print(f"   • {usuarios_eliminados} usuarios marcados como inactivos")
            
            print("\n⚠️  NOTA: Los usuarios de prueba fueron marcados como inactivos")
            print("   por seguridad, no eliminados completamente.")
            print("\n🎯 BASE DE DATOS LIMPIA Y LISTA PARA PRODUCCIÓN")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR EN LA LIMPIEZA: {e}")
            raise e

if __name__ == "__main__":
    respuesta = input("¿Está seguro de que desea limpiar todos los datos de prueba? (si/no): ")
    if respuesta.lower() in ['si', 'sí', 's', 'yes', 'y']:
        limpiar_datos_prueba()
    else:
        print("Operación cancelada.") 