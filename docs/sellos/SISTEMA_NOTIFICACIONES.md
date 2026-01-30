# Sistema de Notificaciones - Módulo de Sellos

## Descripción General

El sistema de notificaciones automáticas del módulo de sellos facilita la comunicación entre todos los roles involucrados en el flujo de gestión de sellos, desde la recepción de inventario hasta el despacho final de vehículos.

## Arquitectura del Sistema

### Componentes Principales

1. **SelloNotificationService** (`app/utils/sellos_notification_service.py`)
   - Servicio principal de notificaciones
   - Maneja el envío a través de múltiples canales
   - Ejecuta verificaciones programadas

2. **Centro de Notificaciones** (`/sellos/notificaciones`)
   - Interfaz web para visualizar notificaciones
   - Filtros por tipo, prioridad y estado
   - Marcado de leído y confirmación

3. **Script de Verificaciones** (`scripts/verificaciones_sellos.py`)
   - Ejecuta verificaciones automáticas
   - Diseñado para ejecución programada (cron)
   - Genera logs detallados

## Tipos de Notificaciones

### 📦 Notificaciones de Inventario

| Tipo | Descripción | Destinatarios | Prioridad |
|------|-------------|---------------|-----------|
| `LOTE_RECIBIDO` | Nuevo lote ingresado al inventario | Admin, Supervisores | Normal |
| `INVENTARIO_BAJO` | Stock insuficiente de algún tipo | Admin, Supervisores | Alta |
| `TIPO_SELLO_AGOTADO` | Tipo de sello sin stock | Admin, Supervisores | Crítica |

### 📋 Notificaciones de Solicitudes

| Tipo | Descripción | Destinatarios | Prioridad |
|------|-------------|---------------|-----------|
| `SOLICITUD_CREADA` | Nueva solicitud (aprobación automática) | Almacén | Normal |
| `SOLICITUD_REQUIERE_APROBACION` | Solicitud requiere aprobación manual | Supervisores | Alta |
| `SOLICITUD_APROBADA` | Solicitud aprobada por supervisor | Inspector, Almacén | Normal |
| `SOLICITUD_RECHAZADA` | Solicitud rechazada con motivo | Inspector | Alta |

### 🚚 Notificaciones de Despacho

| Tipo | Descripción | Destinatarios | Prioridad |
|------|-------------|---------------|-----------|
| `SELLOS_DESPACHADOS` | Sellos listos para instalación | Inspector | Normal |
| `DESPACHO_COMPLETADO` | Despacho finalizado | Supervisores | Normal |

### 🔧 Notificaciones de Instalación

| Tipo | Descripción | Destinatarios | Prioridad |
|------|-------------|---------------|-----------|
| `INSTALACION_INICIADA` | Inspector inició instalación | Supervisores | Baja |
| `INSTALACION_COMPLETADA` | Todas las instalaciones completadas | Supervisores, Portería | Normal |
| `INSTALACION_RETRASADA` | Instalación excede tiempo límite | Supervisores, Admin | Alta |

### ✅ Notificaciones de Validación

| Tipo | Descripción | Destinatarios | Prioridad |
|------|-------------|---------------|-----------|
| `SELLO_VALIDADO` | Sello individual validado | Supervisores | Baja |
| `VEHICULO_LISTO_DESPACHO` | Vehículo listo para salida | Admin, Supervisores | Normal |
| `DESPACHO_FINAL_AUTORIZADO` | Despacho final autorizado | Todos los roles | Normal |

### 🚨 Notificaciones de Sistema

| Tipo | Descripción | Destinatarios | Prioridad |
|------|-------------|---------------|-----------|
| `ALERTA_SEGURIDAD` | Eventos de seguridad | Admin | Crítica |
| `PROCESO_COMPLETADO` | Procesos completados exitosamente | Supervisores | Baja |
| `ERROR_SISTEMA` | Errores técnicos del sistema | Admin | Alta |

## Canales de Notificación

### 🖥️ Sistema (Activo)
- Notificaciones dentro de la aplicación web
- Persistentes hasta ser marcadas como leídas
- Centro de notificaciones con filtros avanzados

### 📧 Email (Configurable)
- Envío por correo electrónico
- Plantillas HTML personalizadas
- Configuración SMTP requerida

### 💬 Slack (Configurable)
- Integración con canales de Slack
- Webhook configurable
- Notificaciones en tiempo real

### 📱 SMS (Futuro)
- Mensajes de texto para alertas críticas
- Integración con proveedores SMS
- Solo para notificaciones de alta prioridad

## Integración en el Flujo

### 1. Recepción de Inventario
```python
# En routes.py - procesar_lote_inventario()
notificar_lote_recibido(
    lote_id=lote_id,
    cantidad_sellos=len(sellos_creados),
    tipo_sello=tipo_sello.nombre,
    usuario_recepcion=usuario_ingreso,
    proveedor=proveedor
)
```

### 2. Creación de Solicitudes
```python
# En routes.py - crear_solicitud()
notificar_solicitud_creada(
    solicitud_id=solicitud.id,
    placa_vehiculo=solicitud.placa_vehiculo,
    cantidad_solicitada=solicitud.cantidad_solicitada,
    inspector=current_user.username,
    requiere_aprobacion=requiere_aprobacion
)
```

### 3. Aprobación/Rechazo
```python
# En routes.py - procesar_aprobacion()
if accion == 'aprobar':
    notificar_solicitud_aprobada(...)
else:
    notificar_solicitud_rechazada(...)
```

### 4. Despacho de Sellos
```python
# En routes.py - finalizar_despacho()
notificar_sellos_despachados(
    solicitud_id=solicitud.id,
    placa_vehiculo=solicitud.placa_vehiculo,
    cantidad_sellos=len(sellos_despachados),
    inspector=solicitud.usuario_solicita,
    usuario_despacho=current_user.username
)
```

### 5. Instalación Completada
```python
# En routes.py - completar_instalaciones()
notificar_instalacion_completada(
    vehiculo_placa=vehiculo_placa,
    inspector=inspector,
    cantidad_sellos=total_sellos
)
```

### 6. Validación en Portería
```python
# En routes.py - confirmar_validacion_final()
if vehiculo_completo:
    notificar_vehiculo_listo_despacho(...)
else:
    notificar_sello_validado(...)
```

### 7. Despacho Final
```python
# En routes.py - autorizar_despacho_final()
notificar_despacho_final_autorizado(
    placa_vehiculo=placa_vehiculo,
    portero=portero,
    total_sellos=len(sellos),
    observaciones=observaciones
)
```

## Verificaciones Programadas

### Configuración de Cron
```bash
# Ejecutar cada hora
0 * * * * cd /ruta/al/proyecto && python scripts/verificaciones_sellos.py

# Ejecutar cada 30 minutos
*/30 * * * * cd /ruta/al/proyecto && python scripts/verificaciones_sellos.py
```

### Verificaciones Incluidas

1. **Inventario Bajo**
   - Verifica stock de cada tipo de sello activo
   - Compara con umbral configurado (default: 50)
   - Envía alerta si está por debajo del mínimo

2. **Instalaciones Retrasadas**
   - Identifica sellos en proceso de instalación
   - Verifica tiempo transcurrido desde despacho
   - Alerta si excede límite configurado (default: 24 horas)

### Ejecución Manual
```bash
# Ejecución normal
python scripts/verificaciones_sellos.py

# Verificar configuración
python scripts/verificaciones_sellos.py --check-config

# Modo verbose
python scripts/verificaciones_sellos.py --verbose
```

## Configuración

### Variables de Entorno
```python
# En config.py
SELLOS_NOTIFICATION_CHANNELS = ['sistema', 'email']  # Canales activos
SELLOS_INVENTARIO_MINIMO = 50                        # Umbral inventario bajo
SELLOS_MAX_INSTALACION_HORAS = 24                    # Límite instalación
MAIL_DEFAULT_SENDER = 'sistema@oleoflores.com'       # Email remitente
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/...'    # Webhook Slack
BASE_URL = 'https://sistema.oleoflores.com'          # URL base
```

### Configuración de Email
```python
# Configuración SMTP
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'sistema@oleoflores.com'
MAIL_PASSWORD = 'password_aplicacion'
```

## Roles y Permisos

### Destinatarios por Rol

| Rol | Recibe Notificaciones De |
|-----|--------------------------|
| **ADMIN_SELLOS** | Todas las notificaciones |
| **SUPERVISOR_SELLOS** | Solicitudes, instalaciones, validaciones, alertas |
| **OPERADOR_SELLOS** | Solicitudes aprobadas, despachos |
| **INSPECTOR_SELLOS** | Sus propias solicitudes y despachos |
| **CONSULTA_SELLOS** | Validaciones en portería |

### Permisos Requeridos
- `CONSULTAR_SELLO`: Ver centro de notificaciones
- `GESTIONAR_INVENTARIO`: Notificaciones de inventario
- `GESTIONAR_SOLICITUDES`: Notificaciones de aprobación
- `DESPACHAR_SELLOS`: Notificaciones de despacho

## Centro de Notificaciones Web

### Características
- **Filtros Avanzados**: Por tipo, prioridad, estado
- **Búsqueda**: Texto libre en título y mensaje
- **Estados**: Todas, Pendientes, Leídas
- **Acciones**: Marcar como leída, confirmar recepción
- **Auto-refresh**: Cada 30 segundos
- **Paginación**: Para manejar grandes volúmenes

### Interfaz
- **Iconos Distintivos**: Cada tipo tiene su icono y color
- **Indicadores de Prioridad**: Badges para alta y crítica
- **Datos Adicionales**: Información contextual expandible
- **Enlaces Directos**: Botones para ir a las pantallas relevantes

## Logs y Monitoreo

### Archivos de Log
- `logs/verificaciones_sellos.log`: Verificaciones programadas
- `logs/flask.log`: Notificaciones desde la aplicación web

### Información Registrada
- Timestamp de cada notificación enviada
- Destinatarios y canales utilizados
- Errores en el envío
- Resultados de verificaciones programadas
- Estadísticas de uso

## Mantenimiento

### Tareas Periódicas
1. **Limpieza de Logs**: Rotar logs mensualmente
2. **Verificación de Canales**: Probar conectividad email/Slack
3. **Actualización de Destinatarios**: Mantener roles actualizados
4. **Revisión de Umbrales**: Ajustar límites según necesidades

### Solución de Problemas
1. **Notificaciones no llegan**: Verificar configuración de canales
2. **Error en verificaciones**: Revisar logs y permisos de base de datos
3. **Spam de notificaciones**: Ajustar umbrales y frecuencia
4. **Destinatarios incorrectos**: Verificar asignación de roles

## Extensibilidad

### Agregar Nuevos Tipos
1. Definir en `TipoNotificacion` enum
2. Crear función específica en el servicio
3. Integrar en las rutas correspondientes
4. Actualizar documentación

### Nuevos Canales
1. Agregar a `CanalNotificacion` enum
2. Implementar método `_enviar_notificacion_[canal]`
3. Configurar credenciales necesarias
4. Probar integración

### Personalización por Usuario
- Tabla de configuraciones personales
- Preferencias de canal por tipo
- Horarios de envío
- Filtros personalizados

## Estado Actual

✅ **Completado**:
- Servicio base de notificaciones
- Integración en todas las rutas principales
- Centro de notificaciones web
- Script de verificaciones programadas
- Documentación completa

🔄 **En Progreso**:
- Implementación de canales email y Slack
- Persistencia en base de datos
- Configuración personalizada por usuario

📋 **Pendiente**:
- Plantillas HTML para emails
- Integración SMS
- Dashboard de estadísticas
- API REST para notificaciones

---

**Última actualización**: 15 de enero de 2025
**Versión**: 1.0.0
**Autor**: Sistema Oleoflores Smart Flow 