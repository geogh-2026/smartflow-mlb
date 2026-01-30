# Documentación de Workflows n8n Existentes - TiquetesApp

**Fecha**: Enero 2025  
**Objetivo**: Documentar todos los workflows de n8n identificados para su migración a LangChain

---

## Resumen Ejecutivo

El sistema TiquetesApp utiliza **15 workflows de n8n diferentes** distribuidos en **2 plataformas**:
- **Make.com** (hook.us2.make.com): 10 webhooks
- **Railway App** (primary-production-6eccf.up.railway.app): 5 webhooks

Estos workflows automatizan **6 procesos críticos** del negocio mediante procesamiento de imágenes y datos.

---

## Workflows Identificados por Categoría

### 1. 📄 **Procesamiento de Tiquetes (OCR de Entrada)**

#### PROCESS_WEBHOOK_URL
- **URL**: `https://hook.us2.make.com/asrfb3kv3cw4o4nd43wylyasfx5yq55f`
- **Función**: Extrae datos de tiquetes mediante OCR
- **Input**: Imagen del tiquete (multipart/form-data)
- **Output**: JSON con datos extraídos (código, nombre, racimos, transportador, etc.)
- **Usado en**: `app/blueprints/entrada/routes.py:process_tiquete_image()`
- **Criticidad**: ⭐⭐⭐ ALTA - Proceso principal de entrada

#### REVALIDATION_WEBHOOK_URL  
- **URL**: `https://hook.us2.make.com/bok045bvtwpj89ig58nhrmx1x09yh56u`
- **Función**: Revalida y procesa datos de tiquetes editados
- **Input**: JSON con datos corregidos del usuario
- **Output**: JSON con datos validados y procesados
- **Usado en**: `app/blueprints/entrada/routes.py:update_data()`
- **Criticidad**: ⭐⭐⭐ ALTA - Validación de datos críticos

---

### 2. 🚗 **Reconocimiento de Placas**

#### PLACA_WEBHOOK_URL
- **URL**: `https://primary-production-6eccf.up.railway.app/webhook/4109b3f4-db19-440e-b153-59b685ba914d`
- **Función**: Reconoce texto de placas vehiculares
- **Input**: Imagen binaria (image/jpeg, image/png, etc.)
- **Output**: Texto de la placa detectada
- **Usado en**: 
  - `app/utils/image_processing.py:process_plate_image()`
  - `app/blueprints/pesaje/routes.py:verificar_placa_pesaje()`
  - `app/blueprints/entrada/routes.py`
  - `app/blueprints/api/routes.py:verificar_placa()`
- **Criticidad**: ⭐⭐ MEDIA - Verificación de vehículos

---

### 3. ⚖️ **Procesamiento de Pesaje**

#### PESAJE_WEBHOOK_URL
- **URL**: `https://primary-production-6eccf.up.railway.app/webhook/aa5b7caf-ee3b-40b9-8778-6f1ab8cda6fc`
- **Función**: Procesa imágenes de básculas para extraer peso
- **Input**: Imagen de báscula + código_proveedor
- **Output**: Peso extraído + guía SAP (formato: "Guia de transporte SAP: NUMERO")
- **Usado en**: 
  - `app/blueprints/pesaje/routes.py:procesar_pesaje_directo()`
  - `app/blueprints/pesaje/routes.py:procesar_pesaje_tara_directo()`
- **Criticidad**: ⭐⭐⭐ ALTA - Proceso crítico de pesaje

#### REGISTRO_PESO_WEBHOOK_URL
- **URL**: `https://hook.us2.make.com/agxyjbyswl2cg1bor1wdrlfcgrll0y15`
- **Función**: Registra pesos en sistema externo
- **Input**: JSON con datos de peso
- **Output**: Confirmación de registro
- **Usado en**: Archivos legacy (archive/)
- **Criticidad**: ⭐ BAJA - Proceso legacy

#### REGISTRO_PESO_NETO_WEBHOOK_URL
- **URL**: `https://primary-production-6eccf.up.railway.app/webhook-test/fef5b25d-3313-46d1-9f38-1e13f1319020`
- **Función**: Procesa peso neto y consulta SAP
- **Input**: FormData con código_proveedor, peso_bruto, guia_transporte_sap, imagen
- **Output**: Datos SAP parseados (guía tránsito, peso SAP, etc.)
- **Usado en**: `templates/pesaje/pesaje_neto.html`
- **Criticidad**: ⭐⭐ MEDIA - Integración SAP

---

### 4. 🍇 **Clasificación de Racimos (IA/ML)**

#### CLASIFICACION_WEBHOOK_URL (Make.com)
- **URL**: `https://hook.us2.make.com/clasificacion_webhook_url`
- **Función**: Clasificación básica (parece placeholder)
- **Usado en**: Variables legacy
- **Criticidad**: ⭐ BAJA - Parece no estar en uso activo

#### REGISTRO_CLASIFICACION_WEBHOOK_URL
- **URL**: `https://hook.us2.make.com/ydtogfd3mln2ixbcuam0xrd2m9odfgna`
- **Función**: Registra resultados de clasificación en sistema externo
- **Input**: JSON con datos de clasificación
- **Output**: Confirmación de registro
- **Usado en**: Variables legacy
- **Criticidad**: ⭐ BAJA - Proceso legacy

#### ⚠️ **NOTA CRÍTICA - Sistema Roboflow**
El verdadero sistema de clasificación automática de racimos utiliza **Roboflow API directamente**, NO webhooks n8n:
- **Implementado en**: `app/blueprints/clasificacion/helpers.py:process_images_with_roboflow()`
- **Función**: Detecta y clasifica racimos por categorías (verde, sobremaduro, daño corona, pedúnculo largo, podrido)
- **Tecnología**: API REST de Roboflow + modelos pre-entrenados
- **Estado**: ✅ **YA FUNCIONA INDEPENDIENTE DE n8n**

---

### 5. ✅ **Validación SAP**

#### Webhook Validación SAP (Graneles)
- **URL**: `https://primary-production-6eccf.up.railway.app/webhook/782f58fe-6037-4c23-87a2-bf402faf9766`
- **Función**: Valida pesos contra sistema SAP
- **Input**: Imagen + datos de pesaje
- **Output**: Peso tara, guía transporte, notas
- **Usado en**: `app/blueprints/graneles/routes.py:validar_foto_pesaje()`
- **Criticidad**: ⭐⭐ MEDIA - Validación específica graneles

#### Webhook Validación Diaria SAP
- **URL**: `https://primary-production-6eccf.up.railway.app/webhook/13eb6b6c-e04d-41b1-9537-f6740e08c2c5`
- **Función**: Validación diaria de pesos vs SAP
- **Input**: Foto + peso_neto_total
- **Output**: "EXITOSO!" o "NO EXITOSO!" + mensaje
- **Usado en**: `app/blueprints/pesaje/routes.py:validar_pesos()`
- **Criticidad**: ⭐⭐ MEDIA - Control de calidad diario

---

### 6. 📋 **Registro y Notificaciones**

#### REGISTER_WEBHOOK_URL
- **URL**: `https://hook.us2.make.com/f63o7rmsuixytjfqxq3gjljnscqhiedl`
- **Función**: Registra entradas completas en sistema central
- **Input**: JSON completo con datos de entrada
- **Output**: Confirmación de registro
- **Usado en**: `app/blueprints/entrada/routes.py:register()`
- **Criticidad**: ⭐⭐⭐ ALTA - Registro principal

#### ADMIN_NOTIFICATION_WEBHOOK_URL
- **URL**: `https://hook.us2.make.com/wpeskbay7k21c3jnthu86lyo081r76fe`
- **Función**: Notificaciones administrativas
- **Input**: Datos de notificación
- **Output**: Confirmación de envío
- **Usado en**: Variables definidas pero uso no identificado
- **Criticidad**: ⭐ BAJA - Notificaciones

#### AUTORIZACION_WEBHOOK_URL
- **URL**: `https://hook.us2.make.com/py29fwgfrehp9il45832acotytu8xr5s`
- **Función**: Procesa códigos de autorización
- **Input**: JSON con código de autorización
- **Output**: Validación de autorización
- **Usado en**: `app/blueprints/pesaje/routes.py` (archivos legacy)
- **Criticidad**: ⭐ BAJA - Proceso legacy

---

### 7. 📄 **Documentos de Vencimiento (OCR)**

#### OCR Documentos Webhook (Graneles)
- **URL**: `https://hook.us2.make.com/a2yotw5cls6qxom2iacvyaoh2b9uk9ip`
- **Función**: Extrae fechas de vencimiento de documentos (ARL, SOAT, Tecnomecánica, Licencia)
- **Input**: Imagen + tipo_documento + usuario
- **Output**: JSON con fecha_vencimiento extraída
- **Usado en**: `app/utils/ocr_service.py:_process_with_webhook()` (como fallback)
- **Criticidad**: ⭐ BAJA - **YA MIGRADO A LANGCHAIN**

#### ⚠️ **NOTA CRÍTICA - OCR ya migrado**
El procesamiento de documentos **YA ESTÁ MIGRADO A LANGCHAIN**:
- **Implementado en**: `app/utils/ocr_service.py:OCRDocumentService`
- **Tecnología**: EasyOCR/Tesseract + LangChain + GPT-4o-mini
- **Estado**: ✅ **FUNCIONA INDEPENDIENTE DE n8n** (webhook solo como fallback)

---

## Análisis de Dependencias Críticas

### 🚨 **Workflows CRÍTICOS que requieren migración prioritaria**:

1. **PROCESS_WEBHOOK_URL** (Procesamiento tiquetes) - ⭐⭐⭐ CRÍTICO
2. **REVALIDATION_WEBHOOK_URL** (Validación datos) - ⭐⭐⭐ CRÍTICO  
3. **PESAJE_WEBHOOK_URL** (Extracción peso básculas) - ⭐⭐⭐ CRÍTICO
4. **REGISTER_WEBHOOK_URL** (Registro central) - ⭐⭐⭐ CRÍTICO
5. **PLACA_WEBHOOK_URL** (Reconocimiento placas) - ⭐⭐ MEDIO

### ✅ **Sistemas YA independientes de n8n**:

1. **Clasificación de racimos** - Usa Roboflow API directamente
2. **OCR documentos vencimiento** - Migrado a LangChain + GPT-4o-mini
3. **Módulo graneles** - Implementa patrón LangChain completo

---

## Patrón de Migración Identificado

### 🎯 **Patrón LangChain Existente** (Módulo Graneles):
```python
# 1. OCR Local (EasyOCR/Tesseract)
text = self._extract_text_from_image(image_path)

# 2. LangChain + LLM para análisis inteligente
prompt = self._create_document_prompt(document_type)
chain = LLMChain(llm=self.llm, prompt=prompt)
response = chain.run(text=extracted_text)

# 3. Webhook fallback si falla
if not local_success:
    webhook_result = self._process_with_webhook(image_path, document_type)
```

### 📋 **Plan de Migración por Prioridad**:

1. **FASE 1**: Migrar procesamiento de tiquetes (PROCESS_WEBHOOK_URL)
2. **FASE 2**: Migrar reconocimiento de placas (PLACA_WEBHOOK_URL)  
3. **FASE 3**: Migrar extracción de pesos (PESAJE_WEBHOOK_URL)
4. **FASE 4**: Migrar validaciones SAP
5. **FASE 5**: Migrar registro y notificaciones

---

## Estimación de Complejidad

| Workflow | Complejidad | Esfuerzo | Patrón |
|----------|-------------|----------|---------|
| Procesamiento tiquetes | ⭐⭐⭐ Alta | 2-3 semanas | OCR + LangChain |
| Reconocimiento placas | ⭐⭐ Media | 1-2 semanas | OCR especializado |
| Extracción pesos | ⭐⭐⭐ Alta | 2-3 semanas | OCR numérico + validación |
| Validaciones SAP | ⭐⭐ Media | 1-2 semanas | API calls + LangChain |
| Registro/Notificaciones | ⭐ Baja | 1 semana | API REST simple |

**Total estimado**: 7-11 semanas de desarrollo

---

## Tecnologías Requeridas para Migración

### Core LangChain Stack:
- **LangChain**: Framework principal
- **OpenAI GPT-4o-mini**: LLM principal (ya configurado)
- **EasyOCR/Tesseract**: OCR local (ya implementado)

### Librerías Adicionales:
- **PIL/Pillow**: Procesamiento de imágenes
- **OpenCV**: Preprocesamiento avanzado de imágenes
- **pytesseract**: OCR alternativo
- **requests**: API calls para fallbacks

### APIs Externas (mantener como fallback):
- **Roboflow**: Clasificación racimos (mantener)
- **Webhooks n8n**: Fallback durante transición

---

## Próximos Pasos

1. ✅ **Documentación completada** - Este documento
2. 🔄 **Sub-tarea 1.3**: Mapear rutas y controladores por módulo
3. 🔄 **Sub-tarea 1.4**: Identificar dependencias entre módulos
4. 🔄 **Análisis completo** del proyecto actual
5. 🚀 **Inicio de migración** por fases según prioridad

---

**Documento generado**: Enero 2025  
**Próxima revisión**: Al completar Sub-tarea 1.2 