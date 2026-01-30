# PRD: Finalización del Módulo de Graneles con Integración de Sellos

## Introducción/Overview

El módulo de graneles de OleoFlores Smart Flow requiere completar su implementación para cubrir el flujo completo de despacho de productos a granel, desde la autorización inicial hasta el cierre del proceso. Actualmente el sistema tiene implementadas las fases 1-2 (Autorización, Recepción, Inspección y Pesaje Inicial), pero faltan las fases críticas 3-5 que incluyen el cargue, control de calidad, sellado con integración al submódulo de sellos existente, documentación y cierre del proceso.

El problema que resuelve es la automatización completa del proceso de despacho de graneles, integrando sistemas desconectados (SAP, báscula, medidor de flujo, sistema de sellos) y proporcionando trazabilidad completa desde la autorización hasta la entrega final.

## Goals

1. **Completar Fase 3**: Implementar el proceso de cargue con integración al medidor de flujo y pesaje bruto
2. **Completar Fase 4**: Desarrollar el sistema de sellado integrado con el submódulo de sellos existente y generación de documentos
3. **Completar Fase 5**: Implementar la verificación de salida y cierre del proceso
4. **Integración Total**: Conectar todas las fases en un flujo unificado con el sistema de sellos
5. **Trazabilidad Completa**: Asegurar visibilidad del estado del proceso en tiempo real
6. **OCR Integral**: Completar la integración OCR para todos los puntos de validación

## User Stories

### Operario de Cargue
- Como operario de cargue, quiero iniciar el proceso de cargue desde una lista de vehículos listos, para controlar el tiempo y volumen del cargue
- Como operario de cargue, quiero que el sistema capture automáticamente el volumen del medidor de flujo, para evitar errores manuales
- Como operario de cargue, quiero tomar foto del display del medidor como evidencia, para tener respaldo documental

### Operario de Báscula  
- Como operario de báscula, quiero que el sistema capture automáticamente el peso bruto y calcule el neto, para agilizar el proceso
- Como operario de báscula, quiero recibir alertas automáticas cuando hay discrepancias entre peso y volumen, para validar inconsistencias

### Auxiliar de Laboratorio
- Como auxiliar de laboratorio, quiero acceder al inventario de sellos asignados al despacho, para instalar los sellos correctos
- Como auxiliar de laboratorio, quiero usar OCR para verificar automáticamente los números de sellos instalados, para evitar errores de transcripción
- Como auxiliar de laboratorio, quiero completar la inspección de calidad desde el mismo sistema, para centralizar la información

### Analista de Laboratorio
- Como analista de laboratorio, quiero adjuntar el certificado de análisis al paquete documental, para completar la documentación requerida

### Facturación/Logística
- Como usuario de facturación, quiero generar automáticamente el paquete documental consolidado, para agilizar el proceso de despacho
- Como usuario de logística, quiero integración con SAP para obtener datos finales de remisión y factura, para asegurar consistencia

### Guarda de Seguridad (Salida)
- Como guarda de seguridad, quiero validar visualmente los sellos contra las fotos del sistema, para asegurar integridad del despacho
- Como guarda de seguridad, quiero cambiar el estado de los sellos a "validado en salida", para completar la trazabilidad

### Analista Logístico
- Como analista logístico, quiero cerrar definitivamente el despacho cuando se confirme la entrega, para mantener el registro histórico completo

## Functional Requirements

### Fase 3: Cargue y Control

**FR-1**: El sistema debe mostrar una lista de vehículos en estado "Pesado (Tara) / Listo para Cargar" para el operario de cargue
**FR-2**: El sistema debe permitir iniciar/finalizar el proceso de cargue con cronómetro automático
**FR-3**: El sistema debe integrar con el medidor de flujo para capturar volumen automáticamente
**FR-4**: El sistema debe permitir tomar foto del display del medidor como evidencia
**FR-5**: El sistema debe cambiar el estado a "Cargado / Pendiente de Pesaje Bruto" al finalizar cargue

**FR-6**: El sistema debe capturar peso bruto automáticamente desde la báscula
**FR-7**: El sistema debe calcular peso neto (Bruto - Tara) automáticamente
**FR-8**: El sistema debe comparar peso neto vs volumen del medidor con tolerancia configurable (+/- 0.5%)
**FR-9**: El sistema debe generar alerta y retener despacho si hay discrepancia fuera de tolerancia
**FR-10**: El sistema debe notificar al Líder de Proceso en caso de discrepancia

### Fase 4: Sellado y Documentación

**FR-11**: El sistema debe integrarse completamente con el submódulo de sellos existente
**FR-12**: El sistema debe mostrar sellos asignados al despacho en estado "Asignado"
**FR-13**: El sistema debe permitir tomar foto de cada sello instalado
**FR-14**: El sistema debe usar OCR para leer automáticamente el número de sello de la foto
**FR-15**: El sistema debe comparar número leído vs asignado y validar coincidencia
**FR-16**: El sistema debe cambiar estado de sellos a "Instalado y Verificado" tras validación exitosa
**FR-17**: El sistema debe permitir adjuntar Certificado de Análisis en PDF
**FR-18**: El sistema debe integrar con SAP para obtener datos finales de remisión/factura
**FR-19**: El sistema debe generar Paquete Documental Digital consolidado

### Fase 5: Salida y Cierre

**FR-20**: El sistema debe permitir búsqueda por QR o placa en portería de salida
**FR-21**: El sistema debe mostrar resumen de verificación con fotos de sellos instalados
**FR-22**: El sistema debe permitir validación visual y cambio de estado a "Validado en Salida"
**FR-23**: El sistema debe cambiar estado del despacho a "En Tránsito" tras validación
**FR-24**: El sistema debe permitir cierre definitivo del despacho como "Entregado/Cerrado"
**FR-25**: El sistema debe mantener registro histórico inmutable para auditorías

### Integración y Trazabilidad

**FR-26**: El sistema debe mostrar estado en tiempo real en la vista centralizada
**FR-27**: El sistema debe sincronizar automáticamente con el sistema de sellos
**FR-28**: El sistema debe generar reportes de integración entre módulos
**FR-29**: El sistema debe mantener log completo de cambios de estado
**FR-30**: El sistema debe permitir notificaciones automáticas entre roles

## Non-Goals (Out of Scope)

1. **Integración directa con SAP**: Se usará OCR para capturar datos, no integración API directa
2. **Modificación del submódulo de sellos**: Solo integración, no cambios estructurales 
3. **Nuevos roles de usuario**: Se trabajará con los roles existentes
4. **Mobile app nativa**: Solo interfaz web responsive
5. **Integración con sistemas de terceros**: Solo OCR para captura de datos
6. **Facturación automática**: Solo consolidación documental, no generación de facturas

## Design Considerations

- **Reutilizar templates existentes**: Aprovechar los 7 templates ya implementados y crear los faltantes siguiendo el mismo patrón
- **Mantener consistencia visual**: Usar los estilos CSS existentes del proyecto (Bootstrap 5)
- **Integración con sellos**: Usar las tablas y modelos existentes del submódulo de sellos sin modificaciones
- **OCR service**: Aprovechar el servicio OCR + LangChain ya implementado
- **Base de datos**: Extender las tablas existentes, no crear nuevas estructuras
- **QR codes**: Mantener el sistema de QR existente para trazabilidad

## Technical Considerations

- **Modelos existentes**: Aprovechar RegistroEntradaGraneles, PrimerPesajeGranel, InspeccionVehiculo ya implementados
- **Rutas faltantes**: Crear nuevas rutas en graneles_bp para las fases 3-5
- **Integración de sellos**: Usar los métodos ya definidos en InspeccionVehiculo para integración
- **OCR**: Ampliar el uso del ocr_service existente para validación de sellos
- **Estados del flujo**: Extender los estados existentes en estado_registro
- **Dependencias**: No agregar nuevas librerías, usar las existentes (OCR, QR, requests)

## Success Metrics

1. **Completitud del flujo**: 100% de los 12 pasos del proceso implementados y funcionales
2. **Integración con sellos**: 95% de validaciones OCR de sellos exitosas
3. **Trazabilidad**: Visibilidad completa del estado en tiempo real
4. **Tiempo de proceso**: Reducción del 40% en tiempo total de despacho vs proceso manual
5. **Consistencia de datos**: 99% de concordancia entre peso/volumen dentro de tolerancia
6. **Documentación**: 100% de paquetes documentales generados automáticamente

## Open Questions

1. **Tolerancia de discrepancia**: ¿El +/- 0.5% entre peso y volumen es adecuado o necesita ajuste?
2. **Notificaciones**: ¿Se requiere integración con sistemas de notificaciones externos (email, SMS)?
3. **Roles de aprobación**: ¿Los Líderes de Proceso y Jefes de Calidad ya tienen acceso al sistema?
4. **Backup de datos**: ¿Se requiere sincronización con sistemas externos para respaldo?
5. **Medidor de flujo**: ¿Se tiene acceso directo a la API del medidor o solo OCR de pantalla?
6. **Estados intermedios**: ¿Se necesitan estados adicionales para control más granular del proceso?