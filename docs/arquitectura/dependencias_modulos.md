# Análisis de Dependencias entre Módulos - TiquetesApp

**Fecha**: Enero 2025  
**Objetivo**: Documentar todas las dependencias entre módulos y funcionalidades para facilitar la migración a Oleoflores Smart Flow

---

## Resumen Ejecutivo

El análisis identificó **6 tipos principales de dependencias** entre los 13 módulos activos del sistema:
1. **Dependencias de flujo de datos** - Secuencia entrada → pesaje → clasificación → pesaje_neto → salida
2. **Dependencias de base de datos** - 5 tablas relacionadas por `codigo_guia`
3. **Dependencias de sesión** - Estado compartido via Flask session
4. **Dependencias de utilidades** - Servicios transversales compartidos
5. **Dependencias de configuración** - Paths, variables y configuraciones centralizadas
6. **Dependencias de assets** - CSS, JS y recursos estáticos compartidos

**Criticidad**: El 80% de las dependencias son CRÍTICAS para el funcionamiento del sistema.

---

## 1. Dependencias de Flujo de Datos (CRÍTICAS)

### 1.1 Flujo Principal del Proceso
**Secuencia obligatoria**: entrada → pesaje → clasificación → pesaje_neto → salida

| Desde | Hacia | Dato Transferido | Método | Criticidad |
|-------|-------|------------------|---------|------------|
| `entrada` | `pesaje` | `codigo_guia`, `codigo_proveedor`, `nombre_proveedor` | Sesión + BD | ⭐⭐⭐ CRÍTICA |
| `pesaje` | `clasificacion` | `peso_bruto`, `codigo_guia_transporte_sap` | BD + Sesión | ⭐⭐⭐ CRÍTICA |
| `clasificacion` | `pesaje_neto` | `timestamp_clasificacion_utc` | BD | ⭐⭐⭐ CRÍTICA |
| `pesaje_neto` | `salida` | `peso_neto`, `peso_producto` | BD | ⭐⭐⭐ CRÍTICA |

### 1.2 Validaciones de Estado
Cada módulo valida que el anterior esté completado:
```python
# Ejemplo en clasificacion/views.py líneas 118-127
tiene_peso_bruto = datos_guia.get('peso_bruto') is not None
if not tiene_peso_bruto:
    return redirect(url_for('pesaje.pesaje_inicial', codigo=codigo_guia))
```

### 1.3 Key Transferido: `codigo_guia`
**Formato**: `{codigo_proveedor}_{timestamp}_{secuencia}`  
**Función**: Clave primaria lógica que conecta todos los módulos  
**Generación**: `app/utils/common.py:CommonUtils.generar_codigo_guia()`

---

## 2. Dependencias de Base de Datos (CRÍTICAS)

### 2.1 Esquema de Relaciones
```sql
-- Consulta principal que conecta todos los módulos (app/utils/common.py líneas 188-215)
SELECT 
    e.*, 
    pb.peso_bruto, pb.timestamp_pesaje_utc, pb.tipo_pesaje, pb.codigo_guia_transporte_sap, 
    c.timestamp_clasificacion_utc, c.clasificacion_manual_json, c.clasificacion_automatica_json,
    pn.peso_tara, pn.peso_neto, pn.peso_producto, pn.timestamp_pesaje_neto_utc,
    s.timestamp_salida_utc, s.comentarios_salida
FROM entry_records e
LEFT JOIN pesajes_bruto pb ON e.codigo_guia = pb.codigo_guia
LEFT JOIN clasificaciones c ON e.codigo_guia = c.codigo_guia
LEFT JOIN pesajes_neto pn ON e.codigo_guia = pn.codigo_guia
LEFT JOIN salidas s ON e.codigo_guia = s.codigo_guia
WHERE e.codigo_guia = ?
```

### 2.2 Tablas y Dependencias

| Tabla | Módulo Propietario | Módulos Dependientes | Campos Clave |
|-------|-------------------|---------------------|--------------|
| `entry_records` | entrada | pesaje, clasificacion, pesaje_neto, salida | `codigo_guia`, `codigo_proveedor`, `nombre_proveedor` |
| `pesajes_bruto` | pesaje | clasificacion, pesaje_neto | `peso_bruto`, `codigo_guia_transporte_sap` |
| `clasificaciones` | clasificacion | pesaje_neto | `timestamp_clasificacion_utc`, `clasificacion_consolidada` |
| `pesajes_neto` | pesaje_neto | salida | `peso_neto`, `peso_producto` |
| `salidas` | salida | ninguno | `timestamp_salida_utc` |

### 2.3 Capa de Acceso Unificada
**Función central**: `app/utils/common.py:CommonUtils.get_datos_guia()`  
**Usado por**: Todos los módulos principales  
**Patrón**: LEFT JOINs para obtener datos completos de una guía

---

## 3. Dependencias de Sesión Flask (CRÍTICAS)

### 3.1 Datos Compartidos en Sesión

| Campo | Módulos que Escriben | Módulos que Leen | Propósito |
|-------|---------------------|------------------|-----------|
| `codigo_guia` | entrada | pesaje, clasificacion, pesaje_neto | Identificación del proceso |
| `codigo_proveedor` | entrada | pesaje, clasificacion | Identificación del proveedor |
| `nombre_proveedor` | entrada | pesaje, clasificacion | Información del proveedor |
| `peso_bruto` | pesaje | clasificacion, pesaje_neto | Datos de pesaje |
| `codigo_guia_transporte_sap` | pesaje | pesaje_neto | Código SAP |
| `estado_actual` | todos | todos | Control de flujo |

### 3.2 Gestión de Sesión
**Configuración**: `config.py` líneas 27-31
```python
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_SECURE'] = False
```

### 3.3 Patrón de Uso
```python
# Escribir en sesión (entrada/routes.py líneas 147-151)
session['codigo_proveedor'] = datos_guia.get('codigo_proveedor')
session['nombre_proveedor'] = datos_guia.get('nombre_proveedor')
session.modified = True

# Leer de sesión (pesaje/routes.py líneas 75-85)
datos_sesion = {
    'peso_bruto': session.get('peso_bruto'),
    'codigo_proveedor': session.get('codigo_proveedor'),
    'nombre_proveedor': session.get('nombre_proveedor')
}
```

---

## 4. Dependencias de Utilidades Compartidas (CRÍTICAS)

### 4.1 CommonUtils - Servicio Central
**Archivo**: `app/utils/common.py`  
**Usado por**: Todos los módulos  
**Funciones clave**:
- `get_datos_guia()` - Obtener datos completos de una guía
- `standardize_template_data()` - Estandarizar datos para templates
- `get_estado_guia()` - Determinar estado del proceso
- `get_db_connection()` - Conexión a base de datos

### 4.2 Autenticación (Flask-Login)
**Archivo**: `app/utils/auth_utils.py`  
**Decorator**: `@login_required` usado en TODAS las rutas  
**Configuración**: `app/__init__.py` líneas 17-41
```python
login_manager.login_view = 'auth.login'
login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
```

### 4.3 Procesamiento de Imágenes
**Archivo**: `app/utils/image_processing.py`  
**Función**: `process_plate_image()` - Reconocimiento de placas  
**Usado por**: entrada, pesaje, api

### 4.4 Generación de PDFs
**Archivo**: `app/utils/pdf_generator.py`  
**Usado por**: entrada, pesaje, clasificacion, salida

### 4.5 OCR y LangChain (Graneles)
**Archivo**: `app/utils/ocr_service.py`  
**Patrón funcional**: OCR local + LangChain + Webhook fallback  
**Estado**: ✅ Independiente de n8n  
**Usar como referencia**: Para migrar otros workflows

---

## 5. Dependencias de Configuración (CRÍTICAS)

### 5.1 Configuración Centralizada
**Archivo principal**: `config.py`  
**Cargada en**: `app/__init__.py` líneas 144-149

### 5.2 Rutas de Directorios (Todas Absolutas)
```python
# config.py líneas 14-25
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER_PATH, 'uploads')
PDF_FOLDER = os.path.join(STATIC_FOLDER_PATH, 'pdfs')
GUIAS_FOLDER = os.path.join(STATIC_FOLDER_PATH, 'guias')
QR_FOLDER = os.path.join(STATIC_FOLDER_PATH, 'qr')
IMAGES_FOLDER = os.path.join(STATIC_FOLDER_PATH, 'images')
EXCEL_FOLDER = os.path.join(STATIC_FOLDER_PATH, 'excels')
```

### 5.3 Variables de Entorno Requeridas
- `FLASK_SECRET_KEY` - Clave secreta para sesiones
- `OPENAI_API_KEY` - Para LangChain (graneles)
- `ROBOFLOW_API_KEY` - Para clasificación automática

### 5.4 Rutas de Base de Datos
```python
# app/__init__.py líneas 162-167
app.config['TIQUETES_DB_PATH'] = os.path.join(base_dir, 'tiquetes.db')
```

---

## 6. Dependencias de Assets Estáticos (MEDIAS)

### 6.1 Template Base Compartido
**Archivo**: `templates/base.html`  
**Estado**: ⚠️ CRÍTICO - `app/templates/base.html` está VACÍO  
**Usado por**: Todos los templates del sistema

### 6.2 CSS y JavaScript Externos
```html
<!-- templates/base.html líneas 7-8 -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
```

### 6.3 Assets Locales
- `static/css/styles.css` - Estilos personalizados
- `static/js/scripts.js` - JavaScript personalizado

### 6.4 Estructura de Static
```
static/
├── css/
├── js/
├── images/
├── uploads/          # Archivos subidos por usuarios
├── pdfs/            # PDFs generados
├── guias/           # Guías HTML
├── qr/              # Códigos QR
└── excels/          # Archivos Excel
```

---

## 7. Módulos Independientes

### 7.1 Graneles (Completamente Independiente)
**Prefijo URL**: `/graneles`  
**Base de datos**: Tablas propias (`RegistroEntradaGraneles`, etc.)  
**Dependencias**: Solo utilidades comunes (auth, assets)  
**LangChain**: ✅ Ya implementado y funcional

### 7.2 Admin (Parcialmente Independiente)
**Prefijo URL**: `/admin`  
**Dependencias**: Solo autenticación y base de datos  
**Función**: Gestión de usuarios, migración de datos

### 7.3 API (Independiente)
**Prefijo URL**: `/api`  
**Función**: Endpoints REST para integraciones  
**Dependencias**: Mínimas (auth, utils)

---

## 8. Análisis de Criticidad para Migración

### 8.1 Dependencias CRÍTICAS (Migrar Primero)
1. **Base de datos y esquema** - Sin esto, nada funciona
2. **CommonUtils** - Usado por todos los módulos
3. **Autenticación** - Requerida en todas las rutas
4. **Templates base** - Estructura de presentación
5. **Configuración** - Rutas y variables esenciales

### 8.2 Dependencias MEDIAS (Migrar Segundo)
1. **Sesión Flask** - Importante pero puede tener fallbacks
2. **Assets estáticos** - Pueden usar CDN temporalmente
3. **Procesamiento de imágenes** - Puede usar webhooks de fallback

### 8.3 Dependencias BAJAS (Migrar Último)
1. **Generación de PDFs** - Funcionalidad complementaria
2. **Excel processing** - Módulos comentados actualmente
3. **Logs y debugging** - Funcionalidad de soporte

---

## 9. Recomendaciones para Migración

### 9.1 Orden de Migración Sugerido
1. **Fase 1**: CommonUtils, autenticación, configuración base
2. **Fase 2**: Base de datos y esquemas
3. **Fase 3**: Módulo entrada (punto de entrada del flujo)
4. **Fase 4**: Módulos pesaje, clasificación, pesaje_neto, salida (en orden)
5. **Fase 5**: Módulos independientes (admin, api, graneles)

### 9.2 Estrategias de Migración
- **Mantener compatibilidad**: Durante la transición, mantener ambos sistemas
- **Migración gradual**: Módulo por módulo, no todo a la vez
- **Testing exhaustivo**: Cada módulo debe probarse antes de migrar el siguiente
- **Documentación**: Actualizar dependencias documentadas después de cada módulo

### 9.3 Riesgos Identificados
1. **Session management**: Flask session debe configurarse idénticamente
2. **Path dependencies**: Rutas absolutas deben mantenerse
3. **Database schema**: Esquema debe ser idéntico
4. **Asset loading**: CDNs externos pueden fallar

---

**Documento generado**: Enero 2025  
**Próxima actualización**: Al completar Sub-tarea 1.5 