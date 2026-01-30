# Tasks - PRD: Finalización del Módulo de Graneles con Integración de Sellos

## Relevant Files

- `app/blueprints/graneles/routes.py` - Rutas principales del módulo, requiere nuevas rutas para fases 3-5
- `app/models/graneles_models.py` - Modelos existentes, requiere nuevos modelos para cargue y sellado
- `app/templates/graneles/` - Templates existentes, requiere templates para nuevas fases
- `app/utils/ocr_service.py` - Servicio OCR existente, requiere extensión para sellos
- `app/models/sellos_models.py` - Modelos de sellos existentes para integración
- `app/blueprints/sellos/routes.py` - Rutas de sellos para integración
- `app/utils/sellos_notification_service.py` - Servicio de notificaciones de sellos
- `app/utils/graneles_notification_service.py` - Servicio de notificaciones críticas para graneles
- `app/templates/graneles/lista_listos_cargue.html` - Template para mostrar vehículos listos para cargue
- `app/templates/graneles/proceso_cargue.html` - Template para proceso de cargue con cronómetro y OCR
- `app/templates/graneles/registrar_pesaje_bruto.html` - Template para registro de pesaje bruto con validaciones
- `app/static/js/graneles.js` - JavaScript para nuevas funcionalidades (por crear)
- `app/static/css/graneles.css` - Estilos específicos para graneles (por crear)

### Notes

- Reutilizar la infraestructura OCR + LangChain ya implementada
- Integrar con submódulo de sellos sin modificar su estructura
- Aprovechar templates y modelos existentes como base
- Mantener consistencia visual con Bootstrap 5 existente

## Tasks

- [x] 1.0 Implementar Fase 3: Sistema de Cargue y Control de Peso ✅ COMPLETADO
  - [x] 1.1 Crear modelo CargueGranel para registro de operaciones de cargue
  - [x] 1.2 Crear modelo PesajeBrutoGranel para segundo pesaje y validaciones
  - [x] 1.3 Implementar ruta /lista-listos-cargue para mostrar vehículos pendientes
  - [x] 1.4 Implementar ruta /iniciar-cargue/<id> con cronómetro y captura de medidor
  - [x] 1.5 Crear template lista_listos_cargue.html para operario de cargue
  - [x] 1.6 Crear template proceso_cargue.html con cronómetro y captura OCR
  - [x] 1.7 Implementar ruta /finalizar-cargue/<id> con validación volumen
  - [x] 1.8 Implementar ruta /pesaje-bruto/<id> con integración báscula
  - [x] 1.9 Desarrollar lógica de validación peso vs volumen con tolerancia
  - [x] 1.10 Implementar sistema de alertas para discrepancias fuera de tolerancia
  - [x] 1.11 Crear notificaciones automáticas a Líder de Proceso
  - [x] 1.12 Actualizar estados del flujo según nueva especificación (8 estados)
  - [x] 1.13 ✅ NUEVO: Mejorar UX del basculero con lista de pendientes primer pesaje
  - [x] 1.14 ✅ NUEVO: Definir y migrar estados del flujo a nueva especificación (36 registros actualizados)
  - [x] 1.15 ✅ NUEVO: Crear template lista_pendientes_primer_pesaje.html con filtros y priorización

- [ ] 2.0 Implementar Fase 4: Sistema de Sellado Integrado y Documentación
  - [ ] 2.1 Crear modelo SolicitudSellosGranel para gestión de sellos por despacho
  - [ ] 2.2 Crear modelo CertificadoAnalisis para gestión de documentos de laboratorio
  - [x] 2.3 Implementar ruta /gestionar-sellos/<id> con integración al inventario de sellos
  - [x] 2.4 Implementar ruta /validar-sello-ocr/<id> para verificación automática
  - [x] 2.5 Crear template gestion_sellos_granel.html para auxiliar de laboratorio
  - [x] 2.6 Crear template validacion_sellos.html con captura de fotos OCR
  - [x] 2.7 Implementar ruta /adjuntar-certificado/<id> para upload de PDF
  - [ ] 2.8 Implementar ruta /generar-paquete-documental/<id> con integración SAP OCR
  - [ ] 2.9 Desarrollar lógica de cambio de estados de sellos (asignado → instalado → verificado)
  - [ ] 2.10 Crear template paquete_documental.html para visualización consolidada
  - [ ] 2.11 Actualizar estados del flujo (pesado_bruto → sellado → documentado)

- [ ] 3.0 Implementar Fase 5: Verificación de Salida y Cierre de Proceso
  - [ ] 3.1 Crear modelo ValidacionSalida para registro de verificaciones finales
  - [ ] 3.2 Implementar ruta /portal-salida para búsqueda por QR/placa
  - [ ] 3.3 Implementar ruta /verificar-salida/<id> para validación visual de sellos
  - [ ] 3.4 Crear template portal_salida.html para guarda de seguridad
  - [ ] 3.5 Crear template verificacion_salida.html con comparación visual
  - [ ] 3.6 Implementar ruta /confirmar-salida/<id> para cambio estado final
  - [ ] 3.7 Implementar ruta /cerrar-despacho/<id> para cierre definitivo
  - [ ] 3.8 Desarrollar lógica de cambio de estados de sellos (verificado → validado_salida)
  - [ ] 3.9 Crear template cierre_despacho.html para analista logístico
  - [ ] 3.10 Actualizar estados del flujo (documentado → en_transito → cerrado)

- [ ] 4.0 Desarrollar Integración Completa con Submódulo de Sellos
  - [ ] 4.1 Implementar métodos de sincronización automática con tablas de sellos
  - [ ] 4.2 Crear ruta /sincronizar-sellos/<id> para actualización manual
  - [ ] 4.3 Desarrollar lógica de validación cruzada entre módulos
  - [ ] 4.4 Implementar ruta /reporte-integracion/<id> para diagnósticos
  - [ ] 4.5 Crear template reporte_integracion_sellos.html para visualización
  - [ ] 4.6 Desarrollar sistema de notificaciones automáticas entre módulos
  - [ ] 4.7 Implementar webhooks para cambios de estado en sellos
  - [ ] 4.8 Crear logs detallados de sincronización y errores

- [ ] 5.0 Actualizar Trazabilidad y Vista Centralizada del Proceso
  - [ ] 5.1 Extender guia_centralizada_graneles.html con todos los nuevos estados
  - [ ] 5.2 Implementar actualización en tiempo real de estados en vista centralizada
  - [ ] 5.3 Crear dashboard de métricas y KPIs del proceso graneles
  - [ ] 5.4 Implementar ruta /historial-cambios/<id> para auditoría completa
  - [ ] 5.5 Crear template dashboard_graneles.html con estadísticas
  - [ ] 5.6 Desarrollar sistema de logs inmutables para auditoría
  - [ ] 5.7 Implementar notificaciones push para cambios críticos de estado
  - [ ] 5.8 Crear reportes consolidados de desempeño del proceso