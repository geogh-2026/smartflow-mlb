# 📁 Estructura Detallada del Proyecto

## Oleoflores Smart Flow - Organización de Archivos

```
oleoflores-smart-flow/
│
├── 📁 app/                                 # Aplicación Flask principal
│   ├── 📄 __init__.py                     # Factory de la aplicación
│   │
│   ├── 📁 blueprints/                     # Módulos de funcionalidad (Blueprints)
│   │   ├── 📁 entrada/                    # Gestión de entradas
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 routes.py              # Rutas del módulo entrada
│   │   │   └── 📄 forms.py               # Formularios WTF
│   │   │
│   │   ├── 📁 pesaje/                     # Sistema de pesaje
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 routes.py              # Rutas del módulo pesaje
│   │   │   └── 📄 forms.py               # Formularios WTF
│   │   │
│   │   ├── 📁 clasificacion/             # Clasificación con IA
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 routes.py              # Rutas del módulo clasificación
│   │   │   └── 📄 forms.py               # Formularios WTF
│   │   │
│   │   ├── 📁 graneles/                   # Manejo de graneles
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 routes.py              # Rutas del módulo graneles
│   │   │   └── 📄 forms.py               # Formularios WTF
│   │   │
│   │   ├── 📁 pesaje_neto/              # Pesaje neto específico
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 routes.py              # Rutas del módulo pesaje neto
│   │   │
│   │   ├── 📁 salida/                     # Gestión de salidas
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 routes.py              # Rutas del módulo salida
│   │   │
│   │   ├── 📁 auth/                       # Autenticación y autorización
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 routes.py              # Login, registro, logout
│   │   │   └── 📄 forms.py               # Formularios de auth
│   │   │
│   │   ├── 📁 admin/                      # Panel de administración
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 routes.py              # Gestión de usuarios, config
│   │   │
│   │   ├── 📁 api/                        # API REST
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 routes.py              # Endpoints API
│   │   │
│   │   ├── 📁 misc/                       # Rutas misceláneas
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 routes.py              # Home, about, contact
│   │   │
│   │   └── 📁 utils/                      # Utilidades para blueprints
│   │       ├── 📄 __init__.py
│   │       └── 📄 routes.py              # Endpoints de utilidades
│   │
│   ├── 📁 static/                         # Archivos estáticos
│   │   ├── 📁 css/                       # Hojas de estilo
│   │   │   ├── 📄 bootstrap.min.css
│   │   │   ├── 📄 custom.css             # Estilos personalizados
│   │   │   └── 📄 themes/                # Temas adicionales
│   │   │
│   │   ├── 📁 js/                        # JavaScript
│   │   │   ├── 📄 bootstrap.min.js
│   │   │   ├── 📄 jquery.min.js
│   │   │   ├── 📄 app.js                 # JavaScript principal
│   │   │   └── 📁 modules/               # JS por módulo
│   │   │       ├── 📄 entrada.js
│   │   │       ├── 📄 pesaje.js
│   │   │       └── 📄 clasificacion.js
│   │   │
│   │   ├── 📁 images/                    # Imágenes
│   │   │   ├── 📄 logo.png
│   │   │   ├── 📄 favicon.ico
│   │   │   └── 📁 uploads/               # Imágenes subidas
│   │   │
│   │   ├── 📁 fonts/                     # Fuentes
│   │   └── 📁 vendor/                    # Librerías externas
│   │
│   ├── 📁 templates/                      # Templates Jinja2
│   │   ├── 📄 base.html                  # Template base
│   │   ├── 📄 navbar.html                # Barra de navegación
│   │   ├── 📄 footer.html                # Pie de página
│   │   ├── 📄 home.html                  # Página principal
│   │   │
│   │   ├── 📁 auth/                      # Templates de autenticación
│   │   │   ├── 📄 login.html
│   │   │   ├── 📄 register.html
│   │   │   └── 📄 profile.html
│   │   │
│   │   ├── 📁 entrada/                   # Templates de entrada
│   │   │   ├── 📄 entrada_form.html
│   │   │   ├── 📄 entrada_lista.html
│   │   │   └── 📄 entrada_detalle.html
│   │   │
│   │   ├── 📁 pesaje/                    # Templates de pesaje
│   │   │   ├── 📄 pesaje_form.html
│   │   │   ├── 📄 pesaje_lista.html
│   │   │   └── 📄 pesaje_detalle.html
│   │   │
│   │   ├── 📁 clasificacion/            # Templates de clasificación
│   │   │   ├── 📄 clasificacion_form.html
│   │   │   ├── 📄 clasificacion_lista.html
│   │   │   └── 📄 clasificacion_detalle.html
│   │   │
│   │   ├── 📁 graneles/                  # Templates de graneles
│   │   │   ├── 📄 graneles_form.html
│   │   │   └── 📄 graneles_lista.html
│   │   │
│   │   ├── 📁 admin/                     # Templates de admin
│   │   │   ├── 📄 dashboard.html
│   │   │   ├── 📄 usuarios.html
│   │   │   └── 📄 configuracion.html
│   │   │
│   │   ├── 📁 errors/                    # Templates de errores
│   │   │   ├── 📄 404.html
│   │   │   ├── 📄 500.html
│   │   │   ├── 📄 403.html
│   │   │   └── 📄 413.html
│   │   │
│   │   └── 📁 components/                # Componentes reutilizables
│   │       ├── 📄 form_field.html
│   │       ├── 📄 pagination.html
│   │       └── 📄 alerts.html
│   │
│   └── 📁 utils/                         # Utilidades y servicios
│       ├── 📄 __init__.py
│       ├── 📄 common.py                  # Utilidades comunes
│       ├── 📄 auth_utils.py              # Utilidades de autenticación
│       ├── 📄 logger.py                  # Sistema de logging
│       ├── 📄 image_processing.py        # Procesamiento de imágenes
│       ├── 📄 ocr_service.py            # Servicio OCR
│       ├── 📄 ai_integration.py         # Integración con IA
│       ├── 📄 langchain_processor.py    # Procesador LangChain
│       ├── 📄 roboflow_client.py        # Cliente Roboflow
│       ├── 📄 email_service.py          # Servicio de email
│       ├── 📄 pdf_generator.py          # Generación de PDFs
│       ├── 📄 excel_processor.py        # Procesamiento Excel
│       ├── 📄 qr_generator.py           # Generación QR
│       └── 📄 validators.py             # Validadores personalizados
│
├── 📁 config/                            # Configuraciones
│   ├── 📄 __init__.py
│   ├── 📄 config.py                     # Configuraciones principales
│   └── 📄 logging.conf                  # Configuración de logging
│
├── 📁 migrations/                        # Scripts de base de datos
│   ├── 📄 __init__.py
│   ├── 📄 init_db.py                    # Inicialización BD
│   ├── 📄 create_tables.py              # Creación de tablas
│   ├── 📄 seed_data.py                  # Datos iniciales
│   └── 📁 versions/                     # Versiones de migración
│
├── 📁 tests/                            # Tests automatizados
│   ├── 📄 __init__.py
│   ├── 📄 conftest.py                   # Configuración pytest
│   ├── 📄 test_basic.py                 # Tests básicos
│   ├── 📄 README.md                     # Documentación tests
│   │
│   ├── 📁 unit/                         # Tests unitarios
│   │   ├── 📁 blueprints/              # Tests de blueprints
│   │   │   ├── 📄 test_auth.py
│   │   │   ├── 📄 test_entrada.py
│   │   │   ├── 📄 test_pesaje.py
│   │   │   └── 📄 test_clasificacion.py
│   │   │
│   │   └── 📁 utils/                    # Tests de utilidades
│   │       ├── 📄 test_logger.py
│   │       ├── 📄 test_common.py
│   │       └── 📄 test_ai_integration.py
│   │
│   ├── 📁 integration/                  # Tests de integración
│   │   ├── 📁 workflows/               # Tests de flujos
│   │   └── 📁 modules/                 # Tests entre módulos
│   │
│   └── 📁 fixtures/                     # Datos de prueba
│       ├── 📄 sample_data.json
│       └── 📄 test_images/
│
├── 📁 docs/                             # Documentación
│   ├── 📄 ESTRUCTURA_PROYECTO.md        # Este archivo
│   ├── 📄 API_DOCUMENTATION.md          # Documentación API
│   ├── 📄 DEPLOYMENT.md                 # Guía de despliegue
│   ├── 📄 CONTRIBUTING.md               # Guía de contribución
│   ├── 📄 CHANGELOG.md                  # Registro de cambios
│   ├── 📄 hallazgos_consolidados.md     # Análisis técnico
│   ├── 📄 dependencias_modulos.md       # Documentación dependencias
│   ├── 📄 esquema_base_datos.md         # Esquema de BD
│   ├── 📄 mapeo_rutas_controladores.md  # Mapeo de rutas
│   ├── 📄 assets_estaticos_estructura.md # Assets estáticos
│   ├── 📄 workflows_n8n_documentacion.md # Workflows N8N
│   └── 📄 OCR_LANGCHAIN_SETUP.md        # Setup OCR y LangChain
│
├── 📁 instance/                         # Datos de instancia
│   ├── 📄 oleoflores_dev.db            # BD desarrollo
│   └── 📁 uploads/                      # Archivos subidos
│
├── 📁 logs/                             # Logs del sistema
│   ├── 📄 app.log                       # Log principal
│   ├── 📄 errors.log                    # Log de errores
│   └── 📄 debug.log                     # Log de debug
│
├── 📁 generated/                        # Archivos generados
│   ├── 📁 pdfs/                        # PDFs generados
│   ├── 📁 qr_codes/                    # Códigos QR
│   ├── 📁 excel/                       # Archivos Excel
│   └── 📁 temp/                        # Archivos temporales
│
├── 📁 .pytest_cache/                   # Cache de pytest
├── 📁 __pycache__/                     # Cache Python
├── 📁 .git/                            # Control de versiones
│
├── 📄 .env                             # Variables de entorno (no versionado)
├── 📄 .env.example                     # Ejemplo de variables
├── 📄 .gitignore                       # Archivos ignorados por Git
├── 📄 requirements.txt                 # Dependencias Python
├── 📄 pytest.ini                      # Configuración pytest
├── 📄 run.py                           # Punto de entrada principal
├── 📄 README.md                        # Documentación principal
├── 📄 LICENSE                          # Licencia del proyecto
└── 📄 CHANGELOG.md                     # Registro de cambios
```

## 🗂️ Descripción de Directorios Principales

### 📁 **app/**
Contiene toda la lógica de la aplicación Flask organizada en módulos (blueprints).

### 📁 **app/blueprints/**
Cada subdirectorio es un módulo funcional independiente con sus rutas, formularios y lógica específica.

### 📁 **app/static/**
Archivos estáticos servidos directamente por el servidor web (CSS, JS, imágenes).

### 📁 **app/templates/**
Templates Jinja2 organizados por módulo, con templates base compartidos.

### 📁 **app/utils/**
Servicios y utilidades reutilizables en toda la aplicación.

### 📁 **config/**
Configuraciones centralizadas para diferentes entornos (desarrollo, producción, testing).

### 📁 **migrations/**
Scripts para gestión de base de datos y versionado de esquemas.

### 📁 **tests/**
Framework completo de testing con tests unitarios, de integración y fixtures.

### 📁 **docs/**
Documentación técnica completa del proyecto.

### 📁 **instance/**
Datos específicos de la instancia (base de datos, uploads) - no versionados.

### 📁 **logs/**
Logs del sistema con rotación automática.

### 📁 **generated/**
Archivos generados dinámicamente por la aplicación.

## 🔄 Convenciones de Naming

### Archivos Python
- **snake_case** para nombres de archivos y funciones
- **PascalCase** para clases
- **UPPER_CASE** para constantes

### Templates HTML
- **snake_case** con sufijos descriptivos
- Organización por módulo funcional

### Archivos Estáticos
- **kebab-case** para CSS y JS
- Versionado para archivos de librerías

### Base de Datos
- **snake_case** para tablas y columnas
- Prefijos descriptivos para tipos de datos

## 📋 Estándares de Organización

1. **Separación de responsabilidades**: Cada módulo tiene una función específica
2. **Reutilización**: Componentes y utilidades compartidas
3. **Escalabilidad**: Estructura que permite crecimiento
4. **Mantenibilidad**: Código organizado y documentado
5. **Testing**: Cobertura completa con estructura clara

## 🔍 Navegación Rápida

- **Iniciar desarrollo**: `run.py`
- **Configurar entorno**: `config/config.py`
- **Agregar nueva funcionalidad**: `app/blueprints/`
- **Modificar UI**: `app/templates/` y `app/static/`
- **Agregar tests**: `tests/`
- **Consultar documentación**: `docs/`
- **Ver logs**: `logs/` 