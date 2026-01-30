# Documento de Requisitos de Producto (PRD): Submódulo de Sellos - Graneles

**Producto:** Oleoflores Smart Flow - Módulo de Graneles  
**Feature:** Submódulo de Gestión y Trazabilidad de Sellos de Seguridad  
**Fecha:** 15 de enero de 2025  
**Versión:** 1.0 MVP  
**Stakeholders:** Gerencia Agroindustrial, Jefe de Calidad, Jefe de Logística, Auditores  

---

## 1. Introducción y Resumen Ejecutivo

Este PRD define los requisitos para el desarrollo del **Submódulo de Sellos**, una funcionalidad crítica dentro del módulo de Graneles de Oleoflores Smart Flow. El objetivo es digitalizar completamente el ciclo de vida de los sellos de seguridad utilizados en carrotanques, eliminando los controles manuales actuales y estableciendo un sistema de trazabilidad unitaria robusto y auditable.

### Problema Principal
El proceso actual presenta **múltiples riesgos críticos de igual importancia**:
- Falta de trazabilidad completa desde recepción hasta validación
- Errores sistemáticos en conteo y registro manual
- Ausencia de segregación de funciones y controles de autorización
- Pérdida y desaparición de sellos sin justificación documentada

### Solución Propuesta
Sistema digital integrado que implementa control unitario de sellos con validación por IA, flujos de aprobación automatizados y trazabilidad completa en tiempo real.

---

## 2. Objetivos y Metas Cuantificables

### Objetivo Primario
Mitigar completamente los riesgos operativos y financieros asociados a la gestión de sellos, eliminando todos los hallazgos de auditoría identificados.

### Metas Específicas
1. **Trazabilidad 100%**: Seguimiento completo de cada sello desde ingreso hasta validación final
2. **Eliminación de papel**: 0% uso de formatos manuales F-GL-088 y F-GC-240
3. **Discrepancias cero**: 0% diferencias entre inventario físico y sistema
4. **Control de excepciones**: 100% de solicitudes adicionales y anulaciones justificadas y aprobadas

---

## 3. Usuarios y Roles del Sistema

| Rol | Responsabilidades Principales | Permisos Específicos |
|-----|------------------------------|---------------------|
| **Auxiliar de Laboratorio** | Gestión de inventario: ingreso, despacho, recepción devoluciones | Solo CRUD inventario, no puede aprobar excepciones |
| **Inspector** | Solicitud, instalación y registro fotográfico de sellos | Solo instalación y registro, requiere aprobación para extras |
| **Guarda Móvil** | Transporte y validación final en portería | Solo validación final, no puede modificar estados anteriores |
| **Jefe de Calidad/Lab** | Supervisión, aprobaciones y acceso a reportes | Todos los permisos, aprobación de excepciones |
| **Auditor** | Consulta de registros históricos y reportes de trazabilidad | Solo lectura, acceso completo a auditoría |

---

## 4. Arquitectura Técnica y Integración

### Integración con OCR Existente
- **Motor Principal**: Utilizar `app/utils/ocr_service.py` existente con GPT-4o Vision
- **Fallback**: Sistema OCR local (EasyOCR/Tesseract) ya implementado
- **Validación**: Reconocimiento automático de números de serie en fotos de sellos instalados

### Flujo de Aprobaciones
- **Modalidad**: Aprobación diferida con posibilidad de despacho bajo responsabilidad
- **Proceso**: Inspector puede proceder con justificación, Jefe de Calidad aprueba posteriormente
- **Alertas**: Notificaciones automáticas para aprobaciones pendientes

---

## 5. Requisitos Funcionales - MVP (Versión 1.0)

### 5.1 Flujo Básico Principal: Recepción → Despacho → Instalación → Validación

#### **RF-001: Recepción de Inventario**
**Como** Auxiliar de Laboratorio  
**Quiero** registrar lotes de sellos escaneando serial inicial y final  
**Para que** el sistema genere automáticamente 100 registros individuales con estado "En Almacén Laboratorio"

**Criterios de Aceptación:**
- Escaneo de rango de seriales (ej: 02128201 a 02128300)
- Generación automática de 100 registros individuales
- Estado inicial: "En Almacén Laboratorio"
- Validación de formato de seriales según prefijos configurados

#### **RF-002: Solicitud de Sellos**
**Como** Inspector  
**Quiero** seleccionar un vehículo y que el sistema sugiera la cantidad estándar de sellos  
**Para que** pueda solicitar la cantidad correcta con justificación de extras si es necesario

**Criterios de Aceptación:**
- Selección de vehículo por placa
- Sugerencia automática basada en maestro de vehículos
- Campo obligatorio de justificación para sellos adicionales
- Posibilidad de proceder bajo responsabilidad (aprobación diferida)

#### **RF-002A: Bandeja de Solicitudes**
**Como** Auxiliar de Laboratorio / Jefe de Calidad  
**Quiero** visualizar una lista unificada de solicitudes de sellos con filtros por estado, placa, fecha y solicitante  
**Para que** pueda revisar, priorizar y ejecutar el despacho sin depender de canales externos

**Criterios de Aceptación:**
- Listado con: placa, fecha/hora, solicitante, cantidad solicitada, cantidad sugerida (maestro), estado de la solicitud
- Enlace directo al resumen de inspección de calidad asociado (detalle en Graneles)
- Acciones contextuales según estado: Revisar → Despachar → Ver Instalación → Ver Validación
- Estados de solicitud visibles: "Solicitada", "Revisada (sin discrepancia)", "Despachada/En Inst." , "Instalada", "Validada" y "Anulada"
- Paginación y orden por más reciente

#### **RF-003: Despacho de Sellos**
**Como** Auxiliar de Laboratorio  
**Quiero** recibir notificación de solicitud y escanear sellos para despacho  
**Para que** el sistema actualice estados a "En Proceso de Instalación"

**Criterios de Aceptación:**
- Notificación automática de solicitudes pendientes
- Escaneo individual de sellos a despachar
- Validación de cantidad vs solicitud
- Cambio automático de estado a "En Proceso de Instalación"
- Asociación con Inspector y vehículo específico

Adicionalmente:
- Asociación explícita al `RegistroEntradaGraneles` (guía) correspondiente
- Registro de `MovimientoSello` por cada serial despachado

#### **RF-004: Instalación con Validación IA**
**Como** Inspector  
**Quiero** fotografiar cada sello instalado para validación automática por IA  
**Para que** el sistema confirme la instalación correcta y actualice el estado

**Criterios de Aceptación:**
- Interfaz móvil para captura de fotos
- Integración con `ocr_service.py` existente para reconocimiento de seriales
- Validación automática contra sellos asignados
- Estado actualizado a "Instalado"
- Almacenamiento permanente de evidencia fotográfica

Adicionalmente:
- OCR debe permitir confirmación manual como fallback si el reconocimiento es ambiguo
- Consolidación de evidencia por serial (múltiples fotos por sello si es necesario)

#### **RF-005: Validación Final en Portería**
**Como** Guarda Móvil  
**Quiero** fotografiar sellos en portería para validación final  
**Para que** el sistema confirme y complete el ciclo de vida del sello

**Criterios de Aceptación:**
- Segunda validación fotográfica independiente
- Confirmación de estado "Instalado" previo
- Cambio final a estado "Validado y Despachado"
- Registro de fecha/hora/usuario de validación final

Adicionalmente:
- Alertar si algún sello asignado no alcanza estado "Validado" al cierre del proceso
- Registrar evidencia fotográfica final y `MovimientoSello` correspondiente

### 5.2 Configuración y Maestros Básicos

#### **RF-006: Maestro de Vehículos**
**Como** Jefe de Calidad  
**Quiero** registrar vehículos con cantidad estándar de sellos  
**Para que** el sistema pueda sugerir automáticamente y alertar sobre desviaciones

#### **RF-007: Control de Usuarios y Roles**
**Como** Jefe de Calidad  
**Quiero** asignar roles específicos con permisos diferenciados  
**Para que** se garantice la segregación de funciones

### 5.3 Gestión Básica de Excepciones

#### **RF-008: Devolución de Sellos Sobrantes**
**Como** Inspector  
**Quiero** registrar sellos no utilizados como devolución  
**Para que** el Auxiliar de Laboratorio pueda confirmar recepción y retornarlos al inventario

#### **RF-009: Anulación de Sellos Defectuosos**
**Como** Inspector  
**Quiero** marcar sellos dañados como anulados con motivo y evidencia  
**Para que** quede registro documentado de la anulación

---

### 5.4 Estados del Ciclo de Vida y Bandejas

#### Estados de Solicitud de Sellos
- Solicitud: `Solicitada` → `Revisada` (sin discrepancia) → `Despachada/En Instalación` → `Instalada` → `Validada` → `Cerrada`
- Excepciones: `Anulada` (con motivo), `Requiere Aprobación` (extras, aprobación diferida)

#### Estados de Sello (unitario)
- `En Almacén Laboratorio` → `En Proceso de Instalación` → `Instalado` → `Validado y Despachado`
- Excepciones: `Devuelto a Almacén`, `Anulado` (defectuoso) con motivo y evidencia

#### Bandejas y Navegación
- Bandeja de Solicitudes (Auxiliar/Jefe): filtros por estado, placa, fecha, solicitante; enlaces a detalle de solicitud y a resumen de inspección de calidad
- Mis Solicitudes (Inspector): historial de solicitudes creadas desde inspección de calidad
- Monitoreo (Dashboard): conteos por estado, alertas de solicitudes en espera > N minutos

### 5.5 Integración con Graneles (Inspección de Calidad)
- La creación de `SolicitudSello` se dispara automáticamente al guardar la Inspección de Calidad (`graneles`), con cantidad sugerida desde `MaestroVehiculo` y justificación para extras
- Cada solicitud queda vinculada a: `placa`, `registro_entrada_granel_id` (guía) y usuario solicitante
- La bandeja de solicitudes ofrece enlace al detalle de la inspección de calidad (`graneles.detalle_inspeccion_calidad`)
- El despacho registra la asociación de seriales de sellos a la guía correspondiente y genera `MovimientoSello`

---

## 6. Requisitos No Funcionales

| Categoría | Requisito | Criterio de Aceptación |
|-----------|-----------|------------------------|
| **Usabilidad** | Interfaz móvil intuitiva para inspectores y guardas | Tiempo de aprendizaje < 30 minutos |
| **Rendimiento** | Procesamiento OCR rápido | Respuesta IA < 3 segundos |
| **Seguridad** | Control de acceso por roles (RBAC) | 100% acciones auditadas |
| **Disponibilidad** | Operación durante horas de planta | 99% uptime en horario operativo |
| **Integridad** | Estados consistentes de sellos | 0% estados conflictivos |

---

## 7. Flujo del Proceso MVP

```
1. RECEPCIÓN
   Auxiliar Lab escanea lote → Estado: "En Almacén Laboratorio"

2. SOLICITUD  
   Inspector selecciona vehículo → Sistema sugiere cantidad → Solicitud creada

3. DESPACHO
   Auxiliar Lab recibe notificación → Escanea sellos → Estado: "En Proceso de Instalación"

4. INSTALACIÓN
   Inspector instala → Fotografía → IA valida → Estado: "Instalado"

5. VALIDACIÓN FINAL
   Guarda Móvil fotografía en portería → IA confirma → Estado: "Validado y Despachado"

6. EXCEPCIONES (Paralelo)
   - Devoluciones: Vuelta a "En Almacén Laboratorio"
   - Anulaciones: Estado "Anulado" con evidencia
```

---

## 8. Criterios de Éxito y Métricas

### Métricas Cuantitativas
- **Adopción**: 100% despachos procesados vía sistema en 30 días post-implementación
- **Trazabilidad**: 100% sellos con historial completo
- **Discrepancias**: < 0.1% diferencia inventario físico vs digital
- **Tiempo de ciclo**: Reducción 25% tiempo promedio solicitud → validación

### Métricas Cualitativas
- **Auditoría**: 0 hallazgos relacionados con gestión de sellos
- **Satisfacción usuario**: > 4.0/5.0 en evaluación de usabilidad
- **Errores operativos**: Reducción 90% vs proceso manual

---

## 9. Fuera de Alcance - Versión 1.0

### Exclusiones Explícitas
- ❌ Integración automática con SAP para órdenes de compra
- ❌ Módulo de análisis predictivo y detección de patrones de fraude
- ❌ Gestión de sellos para otros procesos fuera de graneles
- ❌ Dashboard avanzado con alertas complejas (se incluirá en v2.0)
- ❌ Módulo de inventario físico automatizado (se incluirá en v2.0)

### Funcionalidades Diferidas a Versión 2.0
- Reportes avanzados de auditoría
- Alertas automáticas de discrepancias
- Integración con sistemas externos (SAP, ERP)
- Análisis de patrones y KPIs avanzados

---

## 10. Plan de Implementación Sugerido

### Fase 1 (Semanas 1-2): Configuración Base
- Implementar maestros de vehículos y usuarios
- Desarrollar sistema de roles y permisos
- Integrar con OCR existente

### Fase 2 (Semanas 3-4): Flujo Principal
- Desarrollar recepción, despacho e instalación
- Implementar validación por IA
- Crear interfaz móvil básica

### Fase 3 (Semanas 5-6): Validación y Excepciones
- Implementar validación final en portería
- Desarrollar gestión de devoluciones y anulaciones
- Testing integral del flujo completo

### Fase 4 (Semana 7): Despliegue y Capacitación
- Despliegue en producción
- Capacitación a usuarios
- Monitoreo y ajustes iniciales

---

## 11. Dependencias y Riesgos

### Dependencias Técnicas
- ✅ Sistema OCR existente (`app/utils/ocr_service.py`) - **Disponible**
- ✅ Base de datos y modelos core - **Disponible**
- ✅ Sistema de autenticación y roles - **Disponible**

### Riesgos Identificados
- **Medio**: Resistencia al cambio por parte de usuarios acostumbrados al proceso manual
- **Bajo**: Problemas de conectividad en zonas de instalación de sellos
- **Bajo**: Calidad de fotos afectando precisión del OCR

### Mitigaciones
- Capacitación intensiva y acompañamiento durante transición
- Modo offline básico para sincronización posterior
- Validación manual como fallback cuando OCR falle

---

## 12. Preguntas Abiertas y Decisiones Pendientes

1. **¿Qué hacer con el inventario actual de sellos no digitalizados?**
   - Propuesta: Migración gradual durante primeras semanas

2. **¿Cómo manejar vehículos nuevos sin cantidad estándar definida?**
   - Propuesta: Flujo de definición inicial obligatorio

3. **¿Nivel de detalle requerido en justificaciones de sellos adicionales?**
   - Propuesta: Campo de texto libre con mínimo 20 caracteres

---

**Aprobaciones Requeridas:**
- [ ] Jefe de Calidad/Laboratorio
- [ ] Gerencia Agroindustrial  
- [ ] Equipo de Desarrollo
- [ ] Usuario Líder (Auxiliar de Laboratorio Senior)

---
*Documento generado el 15 de enero de 2025 - Versión 1.0 MVP* 