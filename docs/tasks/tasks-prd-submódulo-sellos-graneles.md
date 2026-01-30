# Tasks - PRD Submódulo de Sellos Graneles

**Basado en:** `docs/prd-submódulo-sellos-graneles.md`  
**Fecha:** 15 de enero de 2025  
**Versión MVP:** 1.0  

---

## Relevant Files

- `app/models/sellos_models.py` - Modelos de base de datos para el submódulo de sellos (Sello, SolicitudSello, MovimientoSello, MaestroVehiculo)
- `app/blueprints/sellos/__init__.py` - Inicialización del blueprint de sellos
- `app/blueprints/sellos/routes.py` - Rutas y controladores del submódulo de sellos
- `app/blueprints/sellos/forms.py` - Formularios WTForms para validación de datos
- `app/templates/sellos/` - Templates específicos para sellos
- `app/templates/sellos/dashboard.html` - Dashboard de sellos
- `app/templates/sellos/dashboard_widget.html` - Widget de resumen para dashboard principal del sistema
- `app/static/js/sellos.js` - JavaScript específico del submódulo
- `app/static/css/sellos.css` - Estilos específicos del submódulo
- `app/utils/sellos_ocr_service.py` - Servicio OCR especializado para reconocimiento de sellos (a crear)
- `migrations/add_sellos_tables.py` - Script de migración para crear tablas de sellos
- `tests/test_sellos_models.py` - Tests unitarios para modelos de sellos (a crear)
- `tests/test_sellos_routes.py` - Tests de integración para rutas de sellos (a crear)
- `tests/test_sellos_services.py` - Tests unitarios para servicios de sellos (a crear)

### Notes

- El submódulo se integra dentro del blueprint existente de graneles
- Utiliza el sistema OCR existente (`app/utils/ocr_service.py`) con adaptaciones específicas
- Mantiene compatibilidad con la estructura actual de permisos y autenticación
- Se implementa como MVP con flujo básico: recepción → despacho → instalación → validación
- Se agrega "Bandeja de Solicitudes" como vista central de trabajo para Auxiliar/Jefe

---

## Tasks

- [x] 1.0 Configurar Modelos y Base de Datos
  - [x] 1.1 Crear modelo Sello con estados (En Almacén Laboratorio, En Proceso de Instalación, Instalado, Validado y Despachado, Anulado)
  - [x] 1.2 Crear modelo MaestroVehiculo para definir cantidad estándar de sellos por placa
  - [x] 1.3 Crear modelo SolicitudSello para gestionar solicitudes de inspectores con aprobaciones diferidas
  - [x] 1.4 Crear modelo MovimientoSello para trazabilidad completa de cambios de estado
  - [x] 1.5 Crear modelo TipoSello para gestionar prefijos y proveedores de sellos
  - [x] 1.6 Actualizar modelos existentes en graneles_models.py para integración con sellos
  - [x] 1.7 Crear script de migración para todas las tablas de sellos
  - [x] 1.8 Ejecutar migraciones y verificar integridad de base de datos

- [ ] 2.0 Implementar Maestros y Configuración Básica
  - [x] 2.1 Crear formularios de administración para tipos de sello
  - [x] 2.2 Implementar CRUD de maestro de vehículos
  - [x] 2.3 Configurar roles y permisos específicos para sellos
  - [x] 2.4 Crear vistas de administración con validaciones
  - [x] 2.5 Crear sistema de configuración de notificaciones para aprobaciones
  - [x] 2.6 Implementar validaciones de negocio para maestros
  - [x] 2.7 Crear seeds/datos iniciales para testing y demostración

- [x] 3.0 Desarrollar Flujo Principal de Sellos
  - [x] 3.1 Implementar RF-001: Recepción de inventario con escaneo de rangos seriales
  - [x] 3.2 Implementar RF-002: Solicitud de sellos con sugerencia automática y justificación
  - [x] 3.3 Implementar RF-003: Despacho de sellos con notificaciones y escaneo individual
  - [x] 3.4 Implementar RF-004: Instalación con interfaz móvil y captura fotográfica
  - [x] 3.5 Implementar RF-005: Validación final en portería con doble verificación
  - [x] 3.6 Crear sistema de notificaciones automáticas entre roles
  - [x] 3.7 Implementar dashboard básico de estados de sellos en tiempo real
  - [x] 3.8 Integrar flujo completo con navegación entre etapas
  - [x] 3.9 Crear sistema de modales globales reutilizables (confirmación, información, escáner, ayuda, progreso)
  - [x] 3.10 Implementar JavaScript avanzado con validaciones en tiempo real y autocompletado
  - [x] 3.11 Crear CSS específico con variables, animaciones y componentes especializados
  - [x] 3.12 Integrar widget de sellos en dashboard principal del sistema
  - [x] 3.13 Agregar enlace de sellos en menú de navegación principal
  - [x] 3.14 Crear template base específico para sellos con herencia inteligente
  - [x] 3.15 Implementar sistema de scripts compartidos con funciones de utilidad

- [ ] 4.0 Integrar Validación por IA con OCR Existente
  - [ ] 4.1 Crear `app/utils/sellos_ocr_service.py` adaptando `ocr_service.py` existente
  - [ ] 4.2 Implementar prompt específico para reconocimiento de números de serie de sellos
  - [ ] 4.3 Integrar GPT-4o Vision para análisis directo de fotos de sellos
  - [ ] 4.4 Crear fallback a OCR local (EasyOCR/Tesseract) para casos sin OpenAI
  - [ ] 4.5 Implementar validación cruzada: serial reconocido vs sellos asignados
  - [ ] 4.6 Crear sistema de almacenamiento permanente de evidencia fotográfica
  - [ ] 4.7 Implementar manejo de errores y validación manual como fallback
  - [ ] 4.8 Optimizar rendimiento para respuesta < 3 segundos según PRD

- [ ] 4.9 Integrar OCR de sellos en `graneles.gestionar_sellos_granel` y `graneles.validar_sello_ocr`
  - [x] 4.9.1 Endpoint API `graneles.api_ocr_sello` recibe imagen (archivo o Base64) y retorna serial reconocido con score y bounding box
  - [x] 4.9.2 Persistir evidencia en `static/uploads/graneles/sellos/ocr/` (y rutas de instalación/validación definidas)
  - [ ] 4.9.3 Validación contra lista de seriales despachados asociados a la guía

- [ ] 5.0 Implementar Gestión de Excepciones y Testing
  - [ ] 5.1 Implementar RF-008: Devolución de sellos sobrantes con confirmación
  - [ ] 5.2 Implementar RF-009: Anulación de sellos defectuosos con motivos y evidencia
  - [ ] 5.3 Crear sistema de aprobaciones diferidas para solicitudes extras
  - [ ] 5.4 Implementar alertas automáticas para sellos en proceso > tiempo límite
  - [ ] 5.5 Crear tests unitarios para todos los modelos de sellos
  - [ ] 5.6 Crear tests de integración para flujo completo de sellos
  - [ ] 5.7 Implementar tests de carga para validación OCR masiva
  - [ ] 5.8 Crear documentación técnica y manual de usuario
  - [ ] 5.9 Realizar testing integral con usuarios reales
  - [ ] 5.10 Preparar datos de migración para inventario actual 

---

## 6. Subtareas de Integración entre Graneles y Sellos

- [x] 6.1 Crear "Bandeja de Solicitudes" en submódulo sellos
  - [x] 6.1.1 Ruta `sellos/gestionar-solicitudes` con filtros por urgencia/solicitante/placa/orden
  - [x] 6.1.2 Columnas y chips: placa, fecha/hora, solicitante, cantidades (solicitada/estándar), estado, enlace a detalle de inspección de calidad
  - [x] 6.1.3 Acciones: Revisar, Despachar, Ver Detalle (enlace al despacho si aprobada)

- [ ] 6.2 Ajustes en creación automática de `SolicitudSello` desde `graneles.inspeccion_calidad`
  - [ ] 6.2.1 Asegurar enlace a `registro_entrada_granel_id` y `placa`
  - [ ] 6.2.2 Guardar `cantidad_sugerida` desde `MaestroVehiculo` y `requiere_aprobacion` cuando haya discrepancia
  - [ ] 6.2.3 Redirigir a `graneles.detalle_inspeccion_calidad` con tarjeta de "Sellos solicitados"

- [ ] 6.3 Despacho de sellos
  - [ ] 6.3.1 UI para escaneo/ingreso de seriales a despachar y validación de cantidad
  - [ ] 6.3.2 Cambio de estado de solicitud a `Despachada/En Instalación` y de sellos a `En Proceso de Instalación`
  - [ ] 6.3.3 Registro de `MovimientoSello` por serial

- [ ] 6.4 Instalación con OCR
  - [ ] 6.4.1 Interfaz móvil por guía para subir/tomar foto por cada sello
  - [ ] 6.4.2 OCR y validación vs sellos despachados; permitir confirmación manual
  - [ ] 6.4.3 Cambio a `Instalado` por serial; cierre parcial si faltan

- [ ] 6.5 Validación final en portería
  - [ ] 6.5.1 Interfaz para captura fotográfica final y OCR
  - [ ] 6.5.2 Cambio a `Validado y Despachado`; alertar sellos no validados
  - [ ] 6.5.3 Tarjeta de estado en `graneles.gestionar_sellos_granel`

- [ ] 6.6 Reportería y auditoría
  - [ ] 6.6.1 Dashboard básico de estados y tiempos
  - [ ] 6.6.2 Historial de `MovimientoSello` por serial y por solicitud