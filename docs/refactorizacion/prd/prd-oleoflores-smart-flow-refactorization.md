# Product Requirements Document (PRD) - Oleoflores Smart Flow

## Introducción/Overview

**Proyecto**: Refactorización de TiquetesApp hacia "Oleoflores Smart Flow"

**Problema a Resolver**: El proyecto actual TiquetesApp presenta una estructura desordenada con templates duplicados entre la raíz (`templates/`) y la aplicación (`app/templates/`), generando problemas de mantenimiento, confusión en el desarrollo y dificultades para implementar nuevas funcionalidades. Adicionalmente, existe la necesidad de migrar workflows de n8n hacia un sistema LangChain más integrado.

**Objetivo**: Crear un nuevo repositorio "Oleoflores Smart Flow" con una estructura limpia, moderna y escalable que consolide todas las funcionalidades existentes, elimine duplicaciones, implemente componentes reutilizables y migre completamente hacia LangChain para el procesamiento de datos.

## Goals

1. **Consolidar Estructura de Templates**: Eliminar la duplicación de templates y establecer una ubicación única en `app/templates/` con una estructura modular y organizada.

2. **Modernizar Arquitectura**: Implementar un sistema de componentes reutilizables, layouts estandarizados y macros Jinja2 para reducir código duplicado.

3. **Migrar Workflows a LangChain**: Reemplazar completamente los workflows de n8n con implementaciones LangChain similares a las ya existentes en el módulo de graneles.

4. **Mejorar Experiencia de Usuario**: Modernizar la interfaz manteniendo o mejorando la funcionalidad actual con un diseño más coherente y profesional.

5. **Establecer Base Escalable**: Crear una estructura que permita fácil adición de nuevos módulos y funcionalidades sin generar desorden.

## User Stories

### Como Desarrollador
- **US-D1**: Como desarrollador, quiero una estructura de templates unificada para no confundirme sobre dónde colocar o buscar archivos.
- **US-D2**: Como desarrollador, quiero componentes reutilizables para no duplicar código HTML/CSS entre diferentes módulos.
- **US-D3**: Como desarrollador, quiero documentación clara de la arquitectura para entender rápidamente cómo añadir nuevas funcionalidades.
- **US-D4**: Como desarrollador, quiero un sistema de workflows unificado en LangChain para no depender de herramientas externas como n8n.

### Como Usuario Final
- **US-U1**: Como usuario, quiero que todas las pantallas tengan un diseño consistente para una mejor experiencia de uso.
- **US-U2**: Como usuario, quiero que el sistema responda igual de rápido o más rápido que la versión actual.
- **US-U3**: Como usuario, quiero que todas las funcionalidades actuales sigan disponibles en la nueva versión.
- **US-U4**: Como usuario, quiero una interfaz más moderna y fácil de usar.

### Como Administrador del Sistema
- **US-A1**: Como administrador, quiero un sistema más fácil de mantener y actualizar.
- **US-A2**: Como administrador, quiero logs y monitoreo mejorados para troubleshooting.
- **US-A3**: Como administrador, quiero un proceso de deployment más simple y confiable.

## Functional Requirements

### FR-1: Arquitectura de Templates
1.1. **DEBE** consolidar todos los templates en `app/templates/` únicamente
1.2. **DEBE** organizar templates por módulo: `entrada/`, `pesaje/`, `clasificacion/`, `graneles/`, `pesaje_neto/`, `salida/`
1.3. **DEBE** implementar un directorio `components/` con macros reutilizables para formularios, tablas, modals, etc.
1.4. **DEBE** implementar un directorio `layouts/` con plantillas base específicas (formularios, listas, documentos, resultados)
1.5. **DEBE** mantener un único `base.html` como plantilla raíz

### FR-2: Componentes Reutilizables
2.1. **DEBE** crear macros para elementos de formulario (inputs, selects, buttons, file uploads)
2.2. **DEBE** crear macros para tablas de datos con filtros, paginación y ordenamiento
2.3. **DEBE** crear macros para tarjetas de estadísticas y métricas
2.4. **DEBE** crear macros para modals de confirmación y alertas
2.5. **DEBE** crear macros para navegación y breadcrumbs

### FR-3: Migración de Workflows
3.1. **DEBE** identificar todos los workflows de n8n actualmente en uso
3.2. **DEBE** implementar equivalentes en LangChain basados en el patrón del módulo graneles
3.3. **DEBE** migrar procesamiento OCR de imágenes de tiquetes a LangChain
3.4. **DEBE** migrar reconocimiento de placas a LangChain
3.5. **DEBE** migrar clasificación automática de racimos a LangChain
3.6. **DEBE** mantener compatibilidad con webhooks existentes durante la transición

### FR-4: Organización de Código
4.1. **DEBE** mantener la estructura de blueprints actual pero con mejor organización
4.2. **DEBE** centralizar utilidades comunes en `app/utils/`
4.3. **DEBE** implementar un sistema de configuración centralizado
4.4. **DEBE** separar claramente lógica de negocio de presentación
4.5. **DEBE** implementar manejo de errores consistente en todos los módulos

### FR-5: Base de Datos y Migración
5.1. **DEBE** mantener compatibilidad con la estructura de BD actual
5.2. **DEBE** permitir migración de datos del sistema anterior
5.3. **DEBE** implementar scripts de migración automática
5.4. **DEBE** mantener integridad de datos durante la migración

### FR-6: Funcionalidades Existentes
6.1. **DEBE** preservar todos los flujos de trabajo actuales: entrada, pesaje, clasificación, pesaje neto, salida
6.2. **DEBE** mantener generación de PDFs y documentos
6.3. **DEBE** preservar sistema de códigos QR
6.4. **DEBE** mantener búsquedas y filtros
6.5. **DEBE** preservar sistema de usuarios y permisos si existe

## Non-Goals (Out of Scope)

1. **Cambios en la lógica de negocio**: El comportamiento funcional debe mantenerse idéntico
2. **Nuevas funcionalidades**: Esta refactorización se enfoca en organización, no en nuevas features
3. **Cambios en la base de datos**: La estructura de BD debe mantenerse compatible
4. **Migración de datos históricos**: Los datos históricos se migrarán pero sin modificación
5. **Cambios en APIs externas**: Las integraciones existentes deben mantenerse
6. **Deployment en producción**: El enfoque es crear el nuevo repositorio, no hacer deployment

## Design Considerations

### Estructura de Directorios Propuesta
```
oleoflores-smart-flow/
├── app/
│   ├── __init__.py
│   ├── blueprints/
│   │   ├── entrada/
│   │   ├── pesaje/
│   │   ├── clasificacion/
│   │   ├── graneles/
│   │   ├── pesaje_neto/
│   │   ├── salida/
│   │   ├── admin/
│   │   └── api/
│   ├── templates/
│   │   ├── base.html
│   │   ├── layouts/
│   │   │   ├── form_layout.html
│   │   │   ├── list_layout.html
│   │   │   ├── document_layout.html
│   │   │   └── results_layout.html
│   │   ├── components/
│   │   │   ├── forms/
│   │   │   ├── tables/
│   │   │   ├── cards/
│   │   │   └── navigation/
│   │   ├── entrada/
│   │   ├── pesaje/
│   │   ├── clasificacion/
│   │   ├── graneles/
│   │   ├── pesaje_neto/
│   │   └── salida/
│   ├── static/
│   ├── utils/
│   │   ├── langchain_processors/
│   │   ├── common.py
│   │   └── validation.py
│   └── models/
├── static/ (archivo de compatibilidad, debe vaciarse gradualmente)
├── config/
├── migrations/
├── tests/
├── docs/
├── requirements.txt
└── run.py
```

### Patrones de Diseño
- **Template Inheritance**: Jerarquía clara base.html → layouts → páginas específicas
- **Component-Based**: Macros reutilizables para elementos comunes
- **Configuration-Driven**: Archivos de configuración para mapeos y constantes
- **Separation of Concerns**: Clara separación entre lógica, presentación y datos

## Technical Considerations

### Tecnologías y Dependencias
- **Backend**: Flask con blueprints
- **Frontend**: Bootstrap 5, Font Awesome, JavaScript vanilla
- **Templating**: Jinja2 con macros y herencia
- **AI/ML**: LangChain para reemplazar n8n workflows
- **Database**: SQLite (mantener compatibilidad)
- **File Processing**: Pillow para imágenes, reportlab/weasyprint para PDFs

### Migración de n8n a LangChain
- Usar el patrón implementado en `app/utils/ocr_service.py` del módulo graneles
- Implementar chains específicos para cada tipo de procesamiento
- Mantener webhooks como fallback durante transición
- Documentar equivalencias entre workflows n8n y chains LangChain

### Performance Considerations
- Optimizar carga de componentes para evitar overhead
- Implementar caching para templates compilados
- Minimizar queries de BD duplicadas
- Optimizar carga de assets estáticos

## Success Metrics

### Métricas Técnicas
1. **Reducción de código duplicado**: Mínimo 40% menos líneas de HTML duplicado
2. **Tiempo de desarrollo**: Nuevas funcionalidades deben implementarse 30% más rápido
3. **Mantenibilidad**: Reducir tiempo de bugfixes en 50%
4. **Test Coverage**: Mínimo 80% de cobertura en tests

### Métricas de Usuario
1. **Performance**: Tiempo de carga de páginas igual o menor al actual
2. **Funcionalidad**: 100% de las funcionalidades actuales deben estar disponibles
3. **Usabilidad**: UI más consistente medida por auditoría de UX
4. **Estabilidad**: Reducir errores de usuario en 25%

### Métricas de Proceso
1. **Deployment**: Proceso de deployment más simple y confiable
2. **Onboarding**: Tiempo de onboarding de nuevos desarrolladores reducido en 50%
3. **Documentation**: Documentación completa y actualizada
4. **Migration**: Migración exitosa de datos sin pérdida

## Open Questions

### Técnicas
1. **¿Mantenemos compatibilidad con URLs existentes?** - Importante para bookmarks de usuarios
2. **¿Implementamos API REST moderna junto con la refactorización?** - Podría beneficiar integraciones futuras
3. **¿Qué nivel de testing automatizado implementamos?** - Definir estrategia de tests

### De Negocio
1. **¿Hay funcionalidades que se usan poco y podrían simplificarse?** - Oportunidad de simplificación
2. **¿Qué mejoras de UX son prioritarias para los usuarios?** - Feedback de usuarios actuales
3. **¿Hay integraciones futuras planeadas que deberíamos considerar?** - Influiría en arquitectura

### De Proceso
1. **¿Cómo validamos que la migración fue exitosa?** - Criterios de aceptación específicos
2. **¿Qué proceso de rollback implementamos si hay problemas?** - Plan de contingencia
3. **¿Cómo gestionamos la transición de usuarios del sistema actual al nuevo?** - Plan de comunicación

## Timeline Estimado

### Fase 1: Preparación (1-2 semanas)
- Análisis detallado del código actual
- Identificación de todos los workflows n8n
- Setup del nuevo repositorio
- Definición de estándares de código

### Fase 2: Fundamentos (2-3 semanas)
- Implementación de estructura base
- Creación de componentes reutilizables
- Setup de sistema de build/deployment
- Implementación de base.html y layouts

### Fase 3: Migración por Módulos (4-6 semanas)
- Migración módulo por módulo
- Implementación de workflows LangChain
- Testing funcional de cada módulo
- Documentación de cada módulo migrado

### Fase 4: Integración y Testing (2-3 semanas)
- Testing de integración completa
- Optimización de performance
- Finalización de documentación
- Preparación para deployment

### Fase 5: Deployment y Migración (1-2 semanas)
- Deployment en ambiente de staging
- Migración de datos
- Testing final con datos reales
- Go-live y monitoreo

**Total Estimado**: 10-16 semanas

## Aprobación y Next Steps

### Criterios de Aprobación
- [ ] Aprobación del stakeholder principal
- [ ] Validación técnica del equipo de desarrollo
- [ ] Confirmación de disponibilidad de recursos
- [ ] Alineación con roadmap de producto

### Próximos Pasos
1. **Aprobación de este PRD** por parte del stakeholder
2. **Generación de task list detallado** usando @generate-tasks.mdc
3. **Setup del nuevo repositorio** "Oleoflores Smart Flow"
4. **Inicio de Fase 1** con análisis detallado del código actual

---

**Documento creado**: {fecha_actual}
**Versión**: 1.0
**Estado**: Draft - Pendiente Aprobación 