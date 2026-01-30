# 🚀 OCR Local con LangChain - Guía Completa

Esta documentación describe cómo usar la nueva funcionalidad de OCR local con LangChain para procesar documentos de vencimiento en lugar de usar webhooks externos.

## 📋 Tabla de Contenidos

- [Visión General](#visión-general)
- [Ventajas del OCR Local](#ventajas-del-ocr-local)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Arquitectura](#arquitectura)
- [Troubleshooting](#troubleshooting)
- [Alternativas](#alternativas)

## 🎯 Visión General

La nueva implementación permite procesar documentos de vencimiento (ARL, SOAT, Tecnomecánica, Licencia) usando:

1. **OCR Local**: EasyOCR o Tesseract para extraer texto de imágenes
2. **LangChain**: Framework para integrar con modelos de lenguaje
3. **LLMs**: GPT-3.5/4, Claude, o modelos locales para análisis inteligente
4. **Fallback**: Los webhooks siguen funcionando como respaldo

### Flujo de Procesamiento

```
Imagen → OCR Local → Texto → LangChain + LLM → Fecha Extraída → Validación → BD
     ↓ (si falla)
   Webhook Fallback → Fecha Extraída → Validación → BD
```

## ✅ Ventajas del OCR Local

| Aspecto | OCR Local + LangChain | Webhooks Make.com |
|---------|----------------------|-------------------|
| **Control** | Total control del proceso | Dependiente de servicio externo |
| **Latencia** | Baja (local/cloud) | Media-Alta (múltiples llamadas) |
| **Costos** | API LLM únicamente | Webhook + API LLM |
| **Confiabilidad** | Alta (menos puntos de falla) | Media (dependiente de Make.com) |
| **Privacidad** | Mejor (procesa localmente) | Menor (datos pasan por Make.com) |
| **Personalización** | Total flexibilidad | Limitado por Make.com |
| **Offline** | Posible con modelos locales | No posible |

## 📋 Requisitos

### Sistema Operativo
- **macOS**: 10.14+ con Homebrew
- **Linux**: Ubuntu 18.04+ o equivalente
- **Windows**: 10+ (requiere instalación manual de Tesseract)

### Software
- **Python**: 3.8+
- **Espacio en disco**: ~2GB para dependencias
- **RAM**: 4GB+ recomendado
- **Internet**: Para descargar modelos y API calls

### APIs (al menos una)
- **OpenAI API Key** (recomendado): GPT-3.5/4
- **Anthropic API Key** (alternativa): Claude
- **Ollama** (local): Para modelos locales

## 🚀 Instalación

### Método 1: Script Automático (Recomendado)

```bash
# 1. Ejecutar script de configuración
python setup_ocr_langchain.py

# 2. Configurar API key
nano .env
# Editar: OPENAI_API_KEY=tu_api_key_real

# 3. Ejecutar migración de BD
python scripts/add_vencimiento_fields.py

# 4. Reiniciar aplicación
```

### Método 2: Instalación Manual

```bash
# 1. Instalar dependencias del sistema
# macOS
brew install tesseract tesseract-lang

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-spa libtesseract-dev

# 2. Instalar dependencias Python
pip install -r requirements_ocr.txt

# 3. Configurar variables de entorno
echo "OPENAI_API_KEY=tu_api_key_aqui" >> .env

# 4. Migrar base de datos
python scripts/add_vencimiento_fields.py
```

## ⚙️ Configuración

### Variables de Entorno

Crear/editar archivo `.env`:

```bash
# LLM Provider (requerido al menos uno)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Alternativos (opcional)
# ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# OLLAMA_BASE_URL=http://localhost:11434

# OCR Configuración (opcional)
# OCR_ENGINE=easyocr  # o 'tesseract'
# OCR_LANGUAGES=es,en
# OCR_GPU=false
```

### Configuración Avanzada

Editar `app/utils/ocr_service.py` para personalizar:

```python
# Cambiar modelo LLM
self.llm = ChatOpenAI(
    model_name="gpt-4",  # Cambiar a gpt-4 para mejor precisión
    temperature=0.1,
)

# Personalizar prompts
def _create_arl_prompt(self):
    template = """Tu prompt personalizado..."""
```

## 🎮 Uso

### Desde la Interfaz Web

1. Ir a **Registro de Graneles**
2. Llenar datos básicos del vehículo
3. En la sección **"Documentos de Vencimiento"**:
   - Hacer clic en el botón **"OCR"** junto al campo deseado
   - Capturar foto del documento
   - Esperar procesamiento automático
   - Verificar fecha extraída

### Desde el Código

```python
from app.utils.ocr_service import ocr_service

# Procesar documento
resultado = ocr_service.process_document(
    image_path="/ruta/al/documento.jpg",
    document_type="soat",  # arl, soat, tecnomecanica, licencia
    user="usuario_actual"
)

if resultado['success']:
    fecha = resultado['fecha_vencimiento']  # "2024-12-31"
    confianza = resultado['confianza']      # 95
    metodo = resultado['metodo']            # "local_ocr_langchain"
else:
    error = resultado['message']
```

## 🏗️ Arquitectura

### Componentes Principales

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask Route   │    │  OCR Service    │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Camera      │ │───▶│ │ /procesar   │ │───▶│ │ process_    │ │
│ │ Capture     │ │    │ │ _documento  │ │    │ │ document()  │ │
│ │ Modal       │ │    │ │ _ocr        │ │    │ │             │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                       ┌─────────────────────────────────┼─────────────────┐
                       │                                 ▼                 │
                       │    ┌─────────────────┐    ┌─────────────────┐     │
                       │    │   EasyOCR       │    │   LangChain     │     │
                       │    │   Tesseract     │───▶│   + GPT/Claude  │     │
                       │    │   (OCR Engine)  │    │   (Analysis)    │     │
                       │    └─────────────────┘    └─────────────────┘     │
                       │                                 │                 │
                       │                                 ▼                 │
                       │                      ┌─────────────────┐          │
                       │                      │   Webhook       │          │
                       │                      │   Fallback      │          │
                       │                      │   (Make.com)    │          │
                       │                      └─────────────────┘          │
                       └───────────────────────────────────────────────────┘
```

### Flujo de Datos

1. **Captura**: Usuario toma foto desde interfaz web
2. **Upload**: Imagen se guarda temporalmente en servidor
3. **OCR**: EasyOCR/Tesseract extrae texto de imagen
4. **LLM**: LangChain + GPT analiza texto y extrae fecha
5. **Validación**: Fecha se valida y formatea
6. **Almacenamiento**: Datos se guardan en base de datos
7. **Fallback**: Si falla, se usa webhook de Make.com

### Base de Datos

Nuevos campos agregados a `RegistroEntradaGraneles`:

```sql
ALTER TABLE RegistroEntradaGraneles ADD COLUMN vencimiento_arl TEXT;
ALTER TABLE RegistroEntradaGraneles ADD COLUMN vencimiento_soat TEXT;
ALTER TABLE RegistroEntradaGraneles ADD COLUMN vencimiento_tecnomecanica TEXT;
ALTER TABLE RegistroEntradaGraneles ADD COLUMN vencimiento_licencia TEXT;
ALTER TABLE RegistroEntradaGraneles ADD COLUMN foto_arl TEXT;
ALTER TABLE RegistroEntradaGraneles ADD COLUMN foto_soat TEXT;
ALTER TABLE RegistroEntradaGraneles ADD COLUMN foto_tecnomecanica TEXT;
ALTER TABLE RegistroEntradaGraneles ADD COLUMN foto_licencia TEXT;
```

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Error: "No OCR engine available"

**Solución**:
```bash
# Verificar instalación
python -c "import easyocr; print('EasyOCR OK')"
python -c "import pytesseract; print('Tesseract OK')"

# Reinstalar si es necesario
pip install easyocr pytesseract
```

#### 2. Error: "OpenAI API key not configured"

**Solución**:
```bash
# Verificar archivo .env
cat .env | grep OPENAI_API_KEY

# Configurar si no existe
echo "OPENAI_API_KEY=tu_api_key_real" >> .env
```

#### 3. Error: "Tesseract not found"

**Solución macOS**:
```bash
brew install tesseract tesseract-lang
```

**Solución Ubuntu**:
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-spa
```

**Solución Windows**:
1. Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Instalar y agregar al PATH
3. Reiniciar terminal/IDE

#### 4. Baja precisión en OCR

**Soluciones**:
- Mejorar calidad de imagen (buena iluminación, imagen clara)
- Usar EasyOCR en lugar de Tesseract: `OCR_ENGINE=easyocr`
- Actualizar prompts en `ocr_service.py`
- Usar GPT-4 en lugar de GPT-3.5

#### 5. Lentitud en procesamiento

**Soluciones**:
- Usar EasyOCR con `gpu=False` para CPU
- Reducir resolución de imágenes capturadas
- Considerar modelos locales con Ollama
- Optimizar prompts para respuestas más concisas

### Logs y Debugging

Activar logs detallados:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Verificar logs en:
```bash
tail -f logs/app.log | grep -i ocr
```

## 🔄 Alternativas y Extensiones

### Modelos LLM Alternativos

#### Anthropic Claude
```python
# En .env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# En ocr_service.py
from langchain.chat_models import ChatAnthropic
self.llm = ChatAnthropic(model="claude-3-sonnet-20240229")
```

#### Ollama (Local)
```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar modelo
ollama pull llama2

# En .env
OLLAMA_BASE_URL=http://localhost:11434

# En ocr_service.py
from langchain.llms import Ollama
self.llm = Ollama(model="llama2")
```

### Motores OCR Alternativos

#### PaddleOCR
```python
# Instalar
pip install paddlepaddle paddleocr

# Usar en ocr_service.py
from paddleocr import PaddleOCR
self.ocr_reader = PaddleOCR(use_angle_cls=True, lang='es')
```

#### Google Cloud Vision
```python
# Instalar
pip install google-cloud-vision

# Configurar y usar
from google.cloud import vision
```

### Mejoras Futuras

1. **Cache de resultados**: Evitar reprocesar mismas imágenes
2. **Procesamiento en lotes**: Múltiples documentos simultáneamente
3. **Modelo fine-tuned**: Entrenar modelo específico para documentos colombianos
4. **Validación cruzada**: Comparar resultados de múltiples motores
5. **Interface mejorada**: Preview en tiempo real, recorte automático

## 📊 Métricas y Monitoreo

### KPIs Importantes

- **Precisión**: % de fechas extraídas correctamente
- **Tiempo de procesamiento**: Segundos por documento
- **Tasa de éxito**: % de documentos procesados exitosamente
- **Costos**: USD por documento procesado

### Implementar Métricas

```python
# En ocr_service.py agregar logging de métricas
import time

start_time = time.time()
# ... procesamiento ...
end_time = time.time()

logger.info(f"OCR_METRICS: tipo={document_type}, tiempo={end_time-start_time:.2f}s, metodo={metodo}, confianza={confianza}")
```

## 📞 Soporte

Si encuentras problemas:

1. **Revisa los logs**: `logs/app.log`
2. **Verifica configuración**: Ejecuta `python setup_ocr_langchain.py`
3. **Consulta troubleshooting**: Esta documentación
4. **Fallback**: Los webhooks siguen funcionando como respaldo

---

¡La implementación de OCR local con LangChain está lista! 🎉 