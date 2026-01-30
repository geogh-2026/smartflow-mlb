"""
Servicio de OCR para procesamiento de documentos de vencimiento.
Implementación con LangChain y OCR local usando Python.
"""

import logging
import re
import json
import os
import base64
import requests
from datetime import datetime
from typing import Dict, Optional, List, Tuple, Union, Any
from PIL import Image
import io
import ssl
import certifi

# Importaciones para OCR
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

# Clases dummy para type hints (siempre disponibles)
class PromptTemplate:
    pass
class ChatOpenAI:
    pass

# Importaciones para LangChain
try:
    from langchain_openai import ChatOpenAI as LangChainChatOpenAI
    from langchain.prompts import PromptTemplate as LangChainPromptTemplate
    from langchain.chains import LLMChain
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
    # Sobrescribir clases dummy con las reales
    PromptTemplate = LangChainPromptTemplate
    ChatOpenAI = LangChainChatOpenAI
except ImportError:
    LANGCHAIN_AVAILABLE = False

logger = logging.getLogger(__name__)

class OCRDocumentService:
    """
    Servicio para procesar documentos mediante OCR local y LangChain para extracción inteligente.
    """
    
    def __init__(self):
        # Configuración del OCR
        self.ocr_reader = None
        self._init_ocr()
        
        # Configuración de LangChain
        self.llm = None
        self._init_langchain()
        
        # Prompts específicos para cada tipo de documento
        self.document_prompts = {
            'arl': self._create_arl_prompt(),
            'soat': self._create_soat_prompt(),
            'tecnomecanica': self._create_tecnomecanica_prompt(),
            'licencia': self._create_licencia_prompt()
        }
        
        # URLs de webhooks como fallback (usando el webhook existente que funciona)
        self.webhook_urls = {
            'arl': 'https://hook.us2.make.com/a2yotw5cls6qxom2iacvyaoh2b9uk9ip',
            'soat': 'https://hook.us2.make.com/a2yotw5cls6qxom2iacvyaoh2b9uk9ip',
            'tecnomecanica': 'https://hook.us2.make.com/a2yotw5cls6qxom2iacvyaoh2b9uk9ip',
            'licencia': 'https://hook.us2.make.com/a2yotw5cls6qxom2iacvyaoh2b9uk9ip'
        }

    def _init_ocr(self):
        """Inicializa el motor de OCR preferido."""
        # Inicializar atributos
        self.ocr_method = None
        
        # Temporalmente deshabilitar EasyOCR para evitar problemas de descarga
        # if EASYOCR_AVAILABLE:
        #     try:
        #         # Configurar SSL antes de inicializar EasyOCR
        #         import ssl
        #         import certifi
        #         ssl._create_default_https_context = ssl._create_unverified_context
        #         
        #         # Configurar variables de entorno para certificados
        #         os.environ['SSL_CERT_FILE'] = certifi.where()
        #         os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        #         
        #         self.ocr_reader = easyocr.Reader(['es', 'en'], gpu=False)
        #         self.ocr_method = 'easyocr'
        #         logger.info("EasyOCR inicializado correctamente")
        #     except Exception as e:
        #         logger.error(f"Error inicializando EasyOCR: {e}")
        #         self.ocr_reader = None
        
        logger.info("EasyOCR temporalmente deshabilitado para debugging")
        
        if not self.ocr_reader and PYTESSERACT_AVAILABLE:
            try:
                # Verificar que Tesseract esté disponible
                pytesseract.get_tesseract_version()
                self.ocr_method = 'tesseract'
                logger.info("Tesseract OCR inicializado correctamente")
            except Exception as e:
                logger.error(f"Error inicializando Tesseract: {e}")
                self.ocr_method = None
        
        if not self.ocr_reader and self.ocr_method != 'tesseract':
            logger.warning("No se pudo inicializar ningún motor de OCR local")
            self.ocr_method = None

    def _init_langchain(self):
        """Inicializa LangChain con el LLM disponible."""
        # Intentar inicializar con OpenAI (preferir GPT-4o-mini para visión)
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            try:
                # Importar OpenAI directamente para capacidades de visión
                import openai
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                logger.info("OpenAI GPT-4o-mini (visión) inicializado correctamente")
                self.vision_available = True
                return
            except Exception as e:
                logger.error(f"Error inicializando OpenAI para visión: {e}")
                self.vision_available = False
        
        # Fallback a LangChain si está disponible
        if LANGCHAIN_AVAILABLE and openai_api_key:
            try:
                self.llm = LangChainChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.1,
                    api_key=openai_api_key
                )
                logger.info("LangChain inicializado con OpenAI GPT-3.5-turbo")
                return
            except Exception as e:
                logger.error(f"Error inicializando LangChain: {e}")
        
        logger.warning("No se pudo inicializar ningún LLM. Configure OPENAI_API_KEY o use webhooks como fallback")
        self.vision_available = False

    def _create_prompt_template(self, template: str) -> PromptTemplate:
        """Helper para crear prompts de manera segura."""
        if LANGCHAIN_AVAILABLE:
            return LangChainPromptTemplate(template=template, input_variables=["text"])
        else:
            return PromptTemplate()  # Dummy fallback

    def _create_arl_prompt(self) -> PromptTemplate:
        """Crea el prompt para extraer fecha de vencimiento de ARL."""
        template = """
Eres un experto en análisis de documentos de ARL (Administradora de Riesgos Laborales).

Analiza el siguiente texto extraído de un documento ARL y extrae la fecha de vencimiento.

TEXTO DEL DOCUMENTO:
{text}

INSTRUCCIONES:
1. Busca términos como: "vence", "vencimiento", "vigencia", "hasta", "válido hasta"
2. Identifica la fecha de vencimiento del ARL
3. La fecha debe estar en formato DD/MM/YYYY, DD-MM-YYYY, o similar
4. Convierte la fecha al formato YYYY-MM-DD

RESPONDE ÚNICAMENTE con un JSON en este formato:
{{
    "fecha_encontrada": "YYYY-MM-DD o null si no se encuentra",
    "confianza": numero del 1 al 100,
    "texto_relevante": "fragmento del texto donde encontraste la fecha"
}}

JSON:"""
        return self._create_prompt_template(template)

    def _create_soat_prompt(self) -> PromptTemplate:
        """Crea el prompt para extraer fecha de vencimiento de SOAT."""
        template = """
Eres un experto en análisis de documentos SOAT (Seguro Obligatorio de Accidentes de Tránsito).

Analiza el siguiente texto extraído de un documento SOAT y extrae la fecha de vencimiento.

TEXTO DEL DOCUMENTO:
{text}

INSTRUCCIONES:
1. Busca términos como: "vence", "vencimiento", "vigencia", "hasta", "válido hasta"
2. Identifica la fecha de vencimiento del SOAT
3. La fecha debe estar en formato DD/MM/YYYY, DD-MM-YYYY, o similar
4. Convierte la fecha al formato YYYY-MM-DD

RESPONDE ÚNICAMENTE con un JSON en este formato:
{{
    "fecha_encontrada": "YYYY-MM-DD o null si no se encuentra",
    "confianza": numero del 1 al 100,
    "texto_relevante": "fragmento del texto donde encontraste la fecha"
}}

JSON:"""
        return self._create_prompt_template(template)

    def _create_tecnomecanica_prompt(self) -> PromptTemplate:
        """Crea el prompt para extraer fecha de vencimiento de Tecnomecánica."""
        template = """
Eres un experto en análisis de documentos de revisión tecnomecánica vehicular.

Analiza el siguiente texto extraído de un certificado de tecnomecánica y extrae la fecha de vencimiento.

TEXTO DEL DOCUMENTO:
{text}

INSTRUCCIONES:
1. Busca términos como: "vence", "vencimiento", "vigencia", "hasta", "válido hasta"
2. Identifica la fecha de vencimiento de la revisión tecnomecánica
3. La fecha debe estar en formato DD/MM/YYYY, DD-MM-YYYY, o similar
4. Convierte la fecha al formato YYYY-MM-DD

RESPONDE ÚNICAMENTE con un JSON en este formato:
{{
    "fecha_encontrada": "YYYY-MM-DD o null si no se encuentra",
    "confianza": numero del 1 al 100,
    "texto_relevante": "fragmento del texto donde encontraste la fecha"
}}

JSON:"""
        return self._create_prompt_template(template)

    def _create_licencia_prompt(self) -> PromptTemplate:
        """Crea el prompt para extraer fecha de vencimiento de Licencia."""
        template = """
Eres un experto en análisis de licencias de conducir.

Analiza el siguiente texto extraído de una licencia de conducir y extrae la fecha de vencimiento.

TEXTO DEL DOCUMENTO:
{text}

INSTRUCCIONES:
1. Busca términos como: "vence", "vencimiento", "vigencia", "hasta", "válido hasta"
2. Identifica la fecha de vencimiento de la licencia
3. La fecha debe estar en formato DD/MM/YYYY, DD-MM-YYYY, o similar
4. Convierte la fecha al formato YYYY-MM-DD

RESPONDE ÚNICAMENTE con un JSON en este formato:
{{
    "fecha_encontrada": "YYYY-MM-DD o null si no se encuentra",
    "confianza": numero del 1 al 100,
    "texto_relevante": "fragmento del texto donde encontraste la fecha"
}}

JSON:"""
        return self._create_prompt_template(template)

    def process_document(self, image_path: str, document_type: str, user: str) -> Dict:
        """
        Procesa un documento y extrae la fecha de vencimiento usando OCR local + LangChain.
        
        Args:
            image_path: Ruta al archivo de imagen
            document_type: Tipo de documento (arl, soat, tecnomecanica, licencia)
            user: Usuario que realiza el procesamiento
            
        Returns:
            Dict con resultado del procesamiento
        """
        try:
            # Validar tipo de documento
            if document_type not in self.document_prompts:
                return {
                    'success': False,
                    'message': f'Tipo de documento "{document_type}" no soportado.'
                }
            
            # Método 1: GPT-4o-mini con visión (PREFERIDO)
            if hasattr(self, 'vision_available') and self.vision_available:
                vision_result = self._process_with_gpt4_vision(image_path, document_type)
                if vision_result['success']:
                    return vision_result
                logger.warning(f"GPT-4o-mini visión falló para {document_type}, intentando OCR local")
            
            # Método 2: OCR local + LangChain
            if self.ocr_method and hasattr(self, 'llm') and self.llm:
                local_result = self._process_with_local_ocr_langchain(image_path, document_type)
                if local_result['success']:
                    return local_result
                logger.warning(f"OCR local + LangChain falló para {document_type}, intentando regex")
            
            # Método 3: OCR local + regex inteligente
            if self.ocr_method:
                regex_result = self._process_with_regex_fallback(image_path, document_type)
                if regex_result['success']:
                    return regex_result
                logger.warning(f"OCR + regex falló para {document_type}, intentando webhook")
            
            # Método 4: Webhook fallback
            webhook_result = self._process_with_webhook(image_path, document_type, user)
            return webhook_result
            
        except Exception as e:
            logger.error(f"Error procesando documento {document_type}: {e}")
            return {
                'success': False,
                'message': f'Error interno procesando el documento: {str(e)}'
            }

    def _process_with_gpt4_vision(self, image_path: str, document_type: str) -> Dict:
        """
        Procesa el documento usando GPT-4o-mini con capacidades de visión.
        Analiza directamente la imagen sin necesidad de OCR previo.
        """
        try:
            # Preparar imagen para GPT-4o-mini
            image_base64, mime_type = self._encode_image_to_base64(image_path)
            
            # Crear prompt específico para análisis de imagen
            prompt = self._create_vision_prompt(document_type)
            
            # Llamar a GPT-4o-mini con visión
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            # Procesar respuesta
            content = response.choices[0].message.content
            logger.info(f"Respuesta completa de GPT-4o-mini: {content}")
            
            # Parsear respuesta JSON
            try:
                # Limpiar respuesta y extraer JSON
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_str = content[json_start:json_end] if json_start != -1 else content
                
                result = json.loads(json_str)
                
                fecha_encontrada = result.get('fecha_encontrada')
                
                if fecha_encontrada and fecha_encontrada != 'null':
                    # Validar formato de fecha específicamente para GPT-4o-mini
                    fecha_validada = self._validate_gpt4_date(fecha_encontrada)
                    
                    if fecha_validada:
                        return {
                            'success': True,
                            'fecha_vencimiento': fecha_validada,
                            'confianza': result.get('confianza', 95),
                            'texto_completo': result.get('texto_visible', ''),
                            'texto_relevante': result.get('contexto', ''),
                            'metodo': 'gpt4_vision',
                            'message': f'Documento {document_type.upper()} procesado exitosamente con GPT-4o-mini visión.',
                            'ruta_imagen': image_path
                        }
                    else:
                        logger.warning(f"GPT-4o-mini fecha no válida: '{fecha_encontrada}' - respuesta completa: {result}")
                        return {
                            'success': False,
                            'message': f'Fecha extraída por GPT-4o-mini no es válida: {fecha_encontrada}'
                        }
                else:
                    logger.warning(f"GPT-4o-mini no encontró fecha - respuesta parseada: {result}")
                    return {
                        'success': False,
                        'message': 'GPT-4o-mini no encontró fecha de vencimiento en la imagen'
                    }
                    
            except json.JSONDecodeError as e:
                logger.error(f"Error parseando respuesta JSON de GPT-4o-mini: {e}\nRespuesta: {content}")
                return {
                    'success': False,
                    'message': 'Error procesando respuesta de GPT-4o-mini'
                }
            
        except Exception as e:
            logger.error(f"Error en GPT-4o-mini visión: {e}")
            return {
                'success': False,
                'message': f'Error en procesamiento con GPT-4o-mini: {str(e)}'
            }

    def _encode_image_to_base64(self, image_path: str) -> tuple[str, str]:
        """
        Convierte una imagen a base64 para enviar a GPT-4o-mini y detecta el formato
        
        Returns:
            tuple: (base64_string, mime_type)
        """
        try:
            # Detectar formato de imagen usando PIL
            from PIL import Image
            import os
            
            # Abrir imagen para detectar formato real
            with Image.open(image_path) as img:
                format_detected = img.format.lower()
                
                # Mapear formatos PIL a tipos MIME soportados por OpenAI
                mime_mapping = {
                    'jpeg': 'image/jpeg',
                    'jpg': 'image/jpeg', 
                    'png': 'image/png',
                    'gif': 'image/gif',
                    'webp': 'image/webp'
                }
                
                mime_type = mime_mapping.get(format_detected, 'image/jpeg')
                logger.info(f"Formato detectado: {format_detected}, MIME type: {mime_type}")
                
                # Si no es un formato soportado, convertir a JPEG
                if format_detected not in mime_mapping:
                    logger.warning(f"Formato {format_detected} no soportado por OpenAI, convirtiendo a JPEG")
                    
                    # Convertir a JPEG y guardar temporalmente
                    temp_path = image_path.replace(os.path.splitext(image_path)[1], '_converted.jpg')
                    
                    # Convertir imagen a RGB si es necesario (para JPEG)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    img.save(temp_path, 'JPEG', quality=95)
                    image_path = temp_path
                    mime_type = 'image/jpeg'
                    logger.info(f"Imagen convertida a JPEG: {temp_path}")
            
            # Leer archivo (original o convertido) y codificar
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                
            return encoded_string, mime_type
            
        except Exception as e:
            logger.error(f"Error codificando imagen a base64: {e}")
            raise

    def _create_vision_prompt(self, document_type: str) -> str:
        """
        Crea prompts específicos para análisis de visión por tipo de documento.
        """
        base_instructions = """
Analiza CUIDADOSAMENTE esta imagen de un documento y extrae la fecha de vencimiento.

INSTRUCCIONES CRÍTICAS:
1. Lee TODO el texto visible en la imagen
2. Busca palabras clave: "VENCIMIENTO", "VENCE", "VIGENCIA", "VÁLIDO HASTA", "EXPIRA", "HASTA"
3. Busca patrones de fecha como: DD-MM-YYYY, DD/MM/YYYY, DD.MM.YYYY
4. IGNORA fechas de expedición, nacimiento, o fechas pasadas
5. Si encuentras múltiples fechas, elige la de vencimiento más reciente
6. Convierte la fecha al formato YYYY-MM-DD

IMPORTANTE: Si ves texto borroso o poco claro, intenta deducir los números basándote en el contexto.

EJEMPLO DE RESPUESTA CORRECTA para "VIGENCIA 13-01-2030":
{
    "fecha_encontrada": "2030-01-13",
    "confianza": 90,
    "contexto": "VIGENCIA 13-01-2030",
    "texto_visible": "Documento con categorías autorizadas y fechas de vigencia"
}

RESPONDE ÚNICAMENTE con un JSON válido en este formato:
{
    "fecha_encontrada": "YYYY-MM-DD o null si absolutamente no encuentras nada",
    "confianza": número del 1 al 100,
    "contexto": "texto exacto donde encontraste la fecha",
    "texto_visible": "descripción del contenido principal del documento"
}
"""
        
        type_specific = {
            'arl': """
DOCUMENTO: ARL (Administradora de Riesgos Laborales)
Busca específicamente la fecha de vencimiento de la afiliación ARL.
Puede aparecer como "Vencimiento ARL", "Vigencia póliza", etc.
""",
            'soat': """
DOCUMENTO: SOAT (Seguro Obligatorio de Accidentes de Tránsito)
Busca específicamente la fecha de vencimiento del SOAT.
Puede aparecer como "Vencimiento SOAT", "Vigencia seguro", etc.
""",
            'tecnomecanica': """
DOCUMENTO: Tecnomecánica (Revisión Tecnomecánica Vehicular)
Busca específicamente la fecha de vencimiento de la revisión tecnomecánica.
Puede aparecer como "Próxima revisión", "Vencimiento", "Vigencia", etc.
""",
            'licencia': """
DOCUMENTO: Licencia de Conducir
Busca específicamente la fecha de vencimiento de la licencia.

PISTAS IMPORTANTES PARA LICENCIAS:
- Busca "VIGENCIA" seguido de una fecha (ej: "VIGENCIA 13-01-2030")
- Busca categorías como "B1", "A2" seguidas de "VIGENCIA" y fecha
- Puede aparecer como "Vencimiento", "Válido hasta", "Expira"
- En licencias colombianas, busca el patrón "DD-MM-YYYY" después de "VIGENCIA"
- Ignora fechas de expedición o nacimiento, solo busca vencimiento
- Si hay múltiples fechas, elige la más reciente en el futuro

FORMATO ESPERADO: Fecha en formato DD-MM-YYYY convertida a YYYY-MM-DD
"""
        }
        
        return base_instructions + type_specific.get(document_type, type_specific['arl'])

    def _process_with_local_ocr_langchain(self, image_path: str, document_type: str) -> Dict:
        """
        Procesa el documento usando OCR local + LangChain.
        """
        try:
            # Paso 1: Extraer texto con OCR
            extracted_text = self._extract_text_from_image(image_path)
            
            if not extracted_text or len(extracted_text.strip()) < 10:
                return {
                    'success': False,
                    'message': 'No se pudo extraer texto suficiente de la imagen'
                }
            
            logger.info(f"Texto extraído ({len(extracted_text)} caracteres): {extracted_text[:200]}...")
            
            # Paso 2: Procesar texto con LangChain
            prompt = self.document_prompts[document_type]
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            response = chain.run(text=extracted_text)
            
            # Paso 3: Parsear respuesta JSON
            try:
                # Limpiar respuesta y extraer JSON
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end] if json_start != -1 else response
                
                result = json.loads(json_str)
                
                fecha_encontrada = result.get('fecha_encontrada')
                
                if fecha_encontrada and fecha_encontrada != 'null':
                    # Validar formato de fecha
                    fecha_validada = self._validate_and_format_date(fecha_encontrada)
                    
                    if fecha_validada:
                        return {
                            'success': True,
                            'fecha_vencimiento': fecha_validada,
                            'confianza': result.get('confianza', 85),
                            'texto_completo': extracted_text,
                            'texto_relevante': result.get('texto_relevante', ''),
                            'metodo': 'local_ocr_langchain',
                            'message': f'Documento {document_type.upper()} procesado exitosamente con OCR local + LangChain.'
                        }
                    else:
                        return {
                            'success': False,
                            'message': f'Fecha extraída no es válida: {fecha_encontrada}'
                        }
                else:
                    return {
                        'success': False,
                        'message': 'No se encontró fecha de vencimiento en el documento'
                    }
                    
            except json.JSONDecodeError as e:
                logger.error(f"Error parseando respuesta JSON: {e}\nRespuesta: {response}")
                return {
                    'success': False,
                    'message': 'Error procesando respuesta del modelo de IA'
                }
            
        except Exception as e:
            logger.error(f"Error en procesamiento local OCR+LangChain: {e}")
            return {
                'success': False,
                'message': f'Error en procesamiento local: {str(e)}'
            }

    def _extract_text_from_image(self, image_path: str) -> str:
        """
        Extrae texto de una imagen usando el motor de OCR disponible.
        """
        try:
            if self.ocr_method == 'easyocr' and self.ocr_reader:
                # Usar EasyOCR
                results = self.ocr_reader.readtext(image_path)
                text = ' '.join([result[1] for result in results])
                return text
                
            elif self.ocr_method == 'tesseract':
                # Usar Tesseract
                image = Image.open(image_path)
                text = pytesseract.image_to_string(image, lang='spa+eng')
                return text
            
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Error extrayendo texto de imagen: {e}")
            return ""

    def _process_with_regex_fallback(self, image_path: str, document_type: str) -> Dict:
        """
        Procesa el documento usando OCR + regex simple como fallback.
        """
        try:
            # Extraer texto con OCR
            extracted_text = self._extract_text_from_image(image_path)
            
            if not extracted_text or len(extracted_text.strip()) < 10:
                return {
                    'success': False,
                    'message': 'No se pudo extraer texto suficiente de la imagen'
                }
            
            logger.info(f"Texto extraído para regex ({len(extracted_text)} caracteres): {extracted_text[:200]}...")
            
            # Buscar fechas con patrones específicos por tipo de documento
            fecha_encontrada = self._extract_date_with_regex(extracted_text, document_type)
            
            if fecha_encontrada:
                fecha_validada = self._validate_and_format_date(fecha_encontrada)
                
                if fecha_validada:
                    return {
                        'success': True,
                        'fecha_vencimiento': fecha_validada,
                        'confianza': 75,  # Confianza media para regex
                        'texto_completo': extracted_text,
                        'texto_relevante': f'Fecha encontrada: {fecha_encontrada}',
                        'metodo': 'regex_fallback',
                        'message': f'Documento {document_type.upper()} procesado con OCR + regex.'
                    }
                else:
                    return {
                        'success': False,
                        'message': f'Fecha extraída no es válida: {fecha_encontrada}'
                    }
            else:
                return {
                    'success': False,
                    'message': 'No se encontró fecha de vencimiento en el texto'
                }
                
        except Exception as e:
            logger.error(f"Error en regex fallback: {e}")
            return {
                'success': False,
                'message': f'Error en procesamiento regex: {str(e)}'
            }

    def _extract_date_with_regex(self, text: str, document_type: str) -> Optional[str]:
        """
        Extrae fechas usando análisis inteligente específico por tipo de documento.
        """
        try:
            logger.info(f"Analizando texto para {document_type}: {text[:200]}...")
            
            # Preprocesar texto para mejor análisis
            text_clean = self._preprocess_text_for_analysis(text)
            
            # Estrategia 1: Buscar con patrones específicos contextualmente
            contextual_date = self._extract_contextual_date(text_clean, document_type)
            if contextual_date:
                logger.info(f"Fecha encontrada con análisis contextual: {contextual_date}")
                return contextual_date
            
            # Estrategia 2: Análisis de múltiples fechas con priorización
            prioritized_date = self._extract_prioritized_date(text_clean, document_type)
            if prioritized_date:
                logger.info(f"Fecha encontrada con análisis priorizado: {prioritized_date}")
                return prioritized_date
            
            # Estrategia 3: Búsqueda genérica de fechas válidas
            generic_date = self._extract_generic_future_date(text_clean)
            if generic_date:
                logger.info(f"Fecha encontrada con análisis genérico: {generic_date}")
                return generic_date
            
            logger.warning(f"No se encontró fecha válida en el texto para {document_type}")
            return None
            
        except Exception as e:
            logger.error(f"Error en extracción inteligente: {e}")
            return None
    
    def _preprocess_text_for_analysis(self, text: str) -> str:
        """
        Preprocesa el texto para análisis más efectivo.
        """
        # Limpiar y normalizar texto
        text_clean = text.lower()
        text_clean = re.sub(r'\s+', ' ', text_clean)  # Normalizar espacios
        text_clean = re.sub(r'[^\w\s\/\-\.\:]', ' ', text_clean)  # Limpiar caracteres especiales
        
        # Normalizar términos comunes
        replacements = {
            'vencimiento': 'vence',
            'vigencia': 'vence',
            'valido hasta': 'vence',
            'válido hasta': 'vence',
            'expira': 'vence',
            'caducidad': 'vence',
            'fecha vence': 'vence',
            'fecha de vencimiento': 'vence',
        }
        
        for old, new in replacements.items():
            text_clean = text_clean.replace(old, new)
        
        return text_clean
    
    def _extract_contextual_date(self, text: str, document_type: str) -> Optional[str]:
        """
        Extrae fechas usando contexto específico del tipo de documento.
        """
        # Patrones más inteligentes por tipo de documento
        context_patterns = {
            'arl': [
                r'(?:arl|riesgo[s]?\s+laboral[es]?).*?venc[e]?\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                r'venc[e]?\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}).*?(?:arl|riesgo)',
                r'(?:poliza|póliza).*?venc[e]?\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
            ],
            'soat': [
                r'(?:soat|seguro.*?obligatorio).*?venc[e]?\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                r'venc[e]?\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}).*?(?:soat|seguro)',
                r'(?:poliza|póliza).*?(?:soat|obligatorio).*?venc[e]?\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
            ],
            'tecnomecanica': [
                r'(?:tecnomecanica|tecnomecánica|revisión).*?venc[e]?\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                r'venc[e]?\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}).*?(?:tecnomecanica|revisión)',
                r'(?:próxima|siguiente)\s+(?:revisión|tecnomecanica).*?(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
            ],
            'licencia': [
                r'(?:licencia|conducir).*?venc[e]?\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                r'venc[e]?\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}).*?(?:licencia|conducir)',
                r'(?:categoria|categoría).*?venc[e]?\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
            ]
        }
        
        patterns = context_patterns.get(document_type, context_patterns['arl'])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                candidate_date = match.group(1)
                if self._validate_and_format_date(candidate_date):
                    return candidate_date
        
        return None
    
    def _extract_prioritized_date(self, text: str, document_type: str) -> Optional[str]:
        """
        Extrae fechas analizando múltiples candidatos y priorizando los más probables.
        """
        # Encontrar todas las fechas posibles
        date_patterns = [
            r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',  # dd/mm/yyyy
            r'(\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})',  # yyyy/mm/dd
            r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2})',  # dd/mm/yy
        ]
        
        all_dates = []
        for pattern in date_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                date_str = match.group(1)
                start_pos = match.start()
                context_before = text[max(0, start_pos-30):start_pos].lower()
                context_after = text[start_pos:start_pos+50].lower()
                
                # Calcular puntuación de prioridad
                priority_score = self._calculate_date_priority(
                    date_str, context_before, context_after, document_type
                )
                
                validated_date = self._validate_and_format_date(date_str)
                if validated_date:
                    all_dates.append((validated_date, priority_score, date_str))
        
        # Ordenar por puntuación y devolver la mejor
        if all_dates:
            all_dates.sort(key=lambda x: x[1], reverse=True)
            best_date = all_dates[0]
            logger.info(f"Mejor fecha seleccionada: {best_date[0]} (puntuación: {best_date[1]})")
            return best_date[0]
        
        return None
    
    def _calculate_date_priority(self, date_str: str, context_before: str, context_after: str, document_type: str) -> int:
        """
        Calcula puntuación de prioridad para una fecha basada en el contexto.
        """
        score = 0
        combined_context = context_before + " " + context_after
        
        # Palabras clave que indican vencimiento
        vencimiento_keywords = ['venc', 'vigencia', 'válido', 'expira', 'caducidad']
        for keyword in vencimiento_keywords:
            if keyword in combined_context:
                score += 50
        
        # Palabras específicas por tipo de documento
        type_keywords = {
            'arl': ['arl', 'riesgo', 'laboral', 'poliza'],
            'soat': ['soat', 'seguro', 'obligatorio', 'vehiculo'],
            'tecnomecanica': ['tecnomecanica', 'revisión', 'mecánica'],
            'licencia': ['licencia', 'conducir', 'categoria']
        }
        
        for keyword in type_keywords.get(document_type, []):
            if keyword in combined_context:
                score += 30
        
        # Penalizar fechas muy pasadas o muy futuras
        try:
            validated_date = self._validate_and_format_date(date_str)
            if validated_date:
                date_obj = datetime.strptime(validated_date, '%Y-%m-%d')
                current_date = datetime.now()
                days_diff = (date_obj - current_date).days
                
                if 0 <= days_diff <= 365*3:  # Fecha futura dentro de 3 años
                    score += 20
                elif days_diff < 0:  # Fecha pasada
                    score -= 100
                elif days_diff > 365*5:  # Muy futura
                    score -= 50
        except:
            pass
        
        return score
    
    def _extract_generic_future_date(self, text: str) -> Optional[str]:
        """
        Extrae la primera fecha futura válida encontrada en el texto.
        """
        date_pattern = r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})'
        matches = re.findall(date_pattern, text)
        
        for date_str in matches:
            validated_date = self._validate_and_format_date(date_str)
            if validated_date:
                # Verificar que sea fecha futura
                try:
                    date_obj = datetime.strptime(validated_date, '%Y-%m-%d')
                    if date_obj > datetime.now():
                        return validated_date
                except:
                    continue
        
        return None

    def _process_with_webhook(self, image_path: str, document_type: str, user: str) -> Dict:
        """
        Procesa el documento usando webhook como fallback.
        """
        
        try:
            webhook_url = self.webhook_urls[document_type]
            
            with open(image_path, 'rb') as image_file:
                files = {'imagen': image_file}
                data = {
                    'tipo_documento': document_type,
                    'usuario': user,
                    'timestamp': datetime.now().isoformat()
                }
                
                response = requests.post(webhook_url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    fecha_extraida = result.get('fecha_vencimiento')
                    fecha_validada = self._validate_and_format_date(fecha_extraida)
                    
                    if fecha_validada:
                        return {
                            'success': True,
                            'fecha_vencimiento': fecha_validada,
                            'confianza': result.get('confianza', 85),
                            'texto_completo': result.get('texto_completo', ''),
                            'metodo': 'webhook_fallback',
                            'message': f'Documento {document_type.upper()} procesado exitosamente por webhook.'
                        }
                    else:
                        return {
                            'success': False,
                            'message': f'Fecha extraída por webhook no es válida: {fecha_extraida}'
                        }
                else:
                    return {
                        'success': False,
                        'message': result.get('message', 'Error en procesamiento webhook')
                    }
            else:
                return {
                    'success': False,
                    'message': f'Error del webhook (código {response.status_code})'
                }
                
        except Exception as e:
            logger.error(f"Error en webhook fallback: {e}")
            return {
                'success': False,
                'message': f'Error en webhook fallback: {str(e)}'
            }

    def _validate_and_format_date(self, date_string: str) -> Optional[str]:
        """
        Valida y formatea una fecha extraída por OCR.
        
        Args:
            date_string: String de fecha extraído
            
        Returns:
            Fecha en formato YYYY-MM-DD o None si no es válida
        """
        if not date_string:
            return None
        
        # Limpiar el string
        date_clean = re.sub(r'[^\d\/\-\.]', ' ', str(date_string)).strip()
        
        # Patrones de fecha comunes
        date_patterns = [
            r'(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})',  # dd/mm/yyyy, dd-mm-yyyy
            r'(\d{4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})',  # yyyy/mm/dd, yyyy-mm-dd
            r'(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2})',  # dd/mm/yy, dd-mm-yy
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_clean)
            if match:
                try:
                    if len(match.group(3)) == 4:  # yyyy format
                        if len(match.group(1)) == 4:  # yyyy/mm/dd
                            year, month, day = match.groups()
                        else:  # dd/mm/yyyy
                            day, month, year = match.groups()
                    else:  # yy format
                        day, month, year_short = match.groups()
                        year_int = int(year_short)
                        if year_int <= 30:
                            year = f"20{year_short}"
                        else:
                            year = f"19{year_short}"
                    
                    # Validar fecha
                    date_obj = datetime(int(year), int(month), int(day))
                    
                    # Verificar que la fecha esté en un rango razonable
                    current_year = datetime.now().year
                    if date_obj.year < current_year - 5 or date_obj.year > current_year + 10:
                        continue
                    
                    return date_obj.strftime('%Y-%m-%d')
                    
                except (ValueError, TypeError):
                    continue
        
        return None

    def _validate_gpt4_date(self, date_string: str) -> Optional[str]:
        """
        Valida fechas que ya vienen formateadas desde GPT-4o-mini.
        
        Args:
            date_string: Fecha en formato YYYY-MM-DD desde GPT-4o-mini
            
        Returns:
            Fecha validada en formato YYYY-MM-DD o None si no es válida
        """
        if not date_string or date_string == 'null':
            return None
        
        # Limpiar string básico (remover espacios)
        date_clean = str(date_string).strip()
        
        # Patrón para YYYY-MM-DD (formato que devuelve GPT-4o-mini)
        pattern = r'^(\d{4})-(\d{1,2})-(\d{1,2})$'
        match = re.match(pattern, date_clean)
        
        if match:
            year, month, day = match.groups()
            try:
                # Validar que la fecha sea real
                date_obj = datetime(int(year), int(month), int(day))
                
                # Verificar que esté en un rango razonable (más amplio para documentos)
                current_year = datetime.now().year
                if date_obj.year < current_year - 10 or date_obj.year > current_year + 20:
                    logger.warning(f"Fecha fuera de rango razonable: {date_clean}")
                    return None
                
                # Verificar que no sea muy antigua (documentos vencidos hace años)
                current_date = datetime.now()
                days_diff = (date_obj - current_date).days
                
                if days_diff < -365:  # Vencido hace más de 1 año
                    logger.warning(f"Fecha muy antigua (vencido hace más de 1 año): {date_clean}")
                    return None
                
                formatted_date = date_obj.strftime('%Y-%m-%d')
                logger.info(f"Fecha GPT-4o-mini validada: {formatted_date}")
                return formatted_date
                
            except (ValueError, TypeError) as e:
                logger.error(f"Error validando fecha GPT-4o-mini '{date_clean}': {e}")
                return None
        
        # Si no coincide con el patrón esperado, intentar otros formatos comunes
        alternative_patterns = [
            r'^(\d{1,2})/(\d{1,2})/(\d{4})$',  # DD/MM/YYYY
            r'^(\d{1,2})-(\d{1,2})-(\d{4})$',  # DD-MM-YYYY
            r'^(\d{4})/(\d{1,2})/(\d{1,2})$',  # YYYY/MM/DD
        ]
        
        for alt_pattern in alternative_patterns:
            match = re.match(alt_pattern, date_clean)
            if match:
                parts = match.groups()
                try:
                    if len(parts[0]) == 4:  # YYYY como primer elemento
                        year, month, day = parts
                    else:  # DD como primer elemento
                        day, month, year = parts
                    
                    date_obj = datetime(int(year), int(month), int(day))
                    
                    # Aplicar mismas validaciones de rango
                    current_year = datetime.now().year
                    if date_obj.year < current_year - 10 or date_obj.year > current_year + 20:
                        continue
                    
                    current_date = datetime.now()
                    days_diff = (date_obj - current_date).days
                    if days_diff < -365:
                        continue
                    
                    formatted_date = date_obj.strftime('%Y-%m-%d')
                    logger.info(f"Fecha GPT-4o-mini validada (formato alternativo): {formatted_date}")
                    return formatted_date
                    
                except (ValueError, TypeError):
                    continue
        
        logger.warning(f"Fecha GPT-4o-mini no reconocida: '{date_clean}'")
        return None

# Instancia global del servicio
ocr_service = OCRDocumentService() 

class OCRPlacaService:
    """
    Servicio especializado para OCR de placas vehiculares con GPT-4 Vision
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ocr_engine = 'easyocr'  # 'easyocr' o 'tesseract'
        
        # Configurar OpenAI GPT-4 Vision (método primario y más rápido)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-4o"  # Usar GPT-4o para visión
        self.openai_client = None
        
        if self.openai_api_key:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                self.logger.info("OpenAI GPT-4o Vision inicializado para placas")
            except Exception as e:
                self.logger.error(f"Error inicializando OpenAI Vision: {e}")
                self.openai_client = None
        
        # OPTIMIZACIÓN MÁXIMA: Control de inicialización de fallbacks
        # Variable de entorno para deshabilitar completamente servicios lentos
        self.enable_fallbacks = os.getenv('ENABLE_OCR_FALLBACKS', 'false').lower() == 'true'
        
        # Inicializar como None para lazy loading
        self.llm = None
        self.ocr_reader = None
        
        if not self.openai_client and self.enable_fallbacks:
            self.logger.warning("OpenAI no disponible, inicializando fallbacks lentos...")
            self._init_fallback_services()
        elif not self.openai_client:
            self.logger.warning("OpenAI no disponible y fallbacks deshabilitados - solo webhook disponible")
        else:
            self.logger.info("OpenAI disponible, saltando inicialización de fallbacks para máxima velocidad")
        
        # Webhook fallback para placas (método final)
        self.webhook_url = "https://primary-production-6eccf.up.railway.app/webhook/4109b3f4-db19-440e-b153-59b685ba914d"
    
    def _init_fallback_services(self):
        """Inicializa servicios de fallback solo cuando son necesarios"""
        
        # Configurar LangChain + OpenAI como método secundario
        try:
            if LANGCHAIN_AVAILABLE:
                from langchain_openai import ChatOpenAI as RealChatOpenAI
                self.llm = RealChatOpenAI(
                    model="gpt-4",
                    temperature=0.1,
                    max_tokens=50
                )
            else:
                # Usar mock class que ya está definida
                self.llm = ChatOpenAI()
                self.logger.warning("LangChain no disponible, usando fallback a webhook")
        except Exception as e:
            self.logger.error(f"Error inicializando LLM: {e}")
            self.llm = None
        
        # Configurar OCR Engine local (método terciario)
        if self.ocr_engine == 'easyocr':
            try:
                import easyocr
                self.ocr_reader = easyocr.Reader(['es', 'en'], gpu=False)
                self.logger.info("EasyOCR inicializado para placas")
            except Exception as e:
                self.logger.error(f"Error inicializando EasyOCR: {e}")
                self.ocr_reader = None
    
    def _encode_image(self, image_path: str) -> tuple[str, str]:
        """
        Codifica imagen a base64 para envío a OpenAI y detecta el formato
        
        Returns:
            tuple: (base64_string, mime_type)
        """
        try:
            # Detectar formato de imagen usando PIL
            from PIL import Image
            import os
            
            # Abrir imagen para detectar formato real
            with Image.open(image_path) as img:
                format_detected = img.format.lower()
                
                # Mapear formatos PIL a tipos MIME soportados por OpenAI
                mime_mapping = {
                    'jpeg': 'image/jpeg',
                    'jpg': 'image/jpeg', 
                    'png': 'image/png',
                    'gif': 'image/gif',
                    'webp': 'image/webp'
                }
                
                mime_type = mime_mapping.get(format_detected, 'image/jpeg')
                self.logger.info(f"Formato detectado: {format_detected}, MIME type: {mime_type}")
                
                # Si no es un formato soportado, convertir a JPEG
                if format_detected not in mime_mapping:
                    self.logger.warning(f"Formato {format_detected} no soportado por OpenAI, convirtiendo a JPEG")
                    
                    # Convertir a JPEG y guardar temporalmente
                    temp_path = image_path.replace(os.path.splitext(image_path)[1], '_converted.jpg')
                    
                    # Convertir imagen a RGB si es necesario (para JPEG)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    img.save(temp_path, 'JPEG', quality=95)
                    image_path = temp_path
                    mime_type = 'image/jpeg'
                    self.logger.info(f"Imagen convertida a JPEG: {temp_path}")
            
            # Leer archivo (original o convertido) y codificar
            with open(image_path, "rb") as image_file:
                base64_string = base64.b64encode(image_file.read()).decode('utf-8')
                
            return base64_string, mime_type
            
        except Exception as e:
            self.logger.error(f"Error codificando imagen: {e}")
            return "", "image/jpeg"

    def _process_with_openai_vision(self, image_path: str, placa_registrada: str = None) -> Dict[str, Any]:
        """
        Procesa imagen usando OpenAI GPT-4 Vision para reconocer placas
        """
        try:
            if not self.openai_client or not self.openai_api_key:
                return {
                    'success': False,
                    'placa': '',
                    'confianza': 0,
                    'metodo': 'openai_vision',
                    'mensaje': 'OpenAI no configurado'
                }

            # Codificar imagen
            base64_image, mime_type = self._encode_image(image_path)
            if not base64_image:
                return {
                    'success': False,
                    'placa': '',
                    'confianza': 0,
                    'metodo': 'openai_vision',
                    'mensaje': 'Error codificando imagen'
                }

            # Crear prompt para reconocimiento de placa
            prompt = """Eres un experto en reconocimiento de placas vehiculares colombianas.

Analiza esta imagen y extrae ÚNICAMENTE el texto de la placa vehicular que veas.

FORMATO ESPERADO: 3 letras seguidas de 3 números (ejemplo: ABC123)

INSTRUCCIONES:
1. Identifica la placa vehicular en la imagen
2. Extrae solo las letras y números de la placa
3. Responde ÚNICAMENTE con el texto de la placa en formato ABC123
4. Si no puedes identificar claramente la placa, responde "NO_DETECTADA"

RESPUESTA:"""

            # Llamar a OpenAI Vision
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=50,
                temperature=0.1
            )

            placa_text = response.choices[0].message.content.strip().upper()
            
            # Validar respuesta
            if placa_text == "NO_DETECTADA":
                return {
                    'success': False,
                    'placa': '',
                    'confianza': 0,
                    'metodo': 'openai_vision',
                    'mensaje': 'OpenAI no pudo detectar placa en la imagen'
                }

            # Validar formato de placa colombiana
            import re
            placa_pattern = r'^[A-Z]{3}[0-9]{3}$'
            
            if re.match(placa_pattern, placa_text):
                return {
                    'success': True,
                    'placa': placa_text,
                    'confianza': 95,
                    'metodo': 'openai_vision',
                    'placa_registrada': placa_registrada,
                    'coincide': placa_text == placa_registrada.upper() if placa_registrada else None
                }
            else:
                # Intentar extraer placa de respuesta más larga
                placa_matches = re.findall(r'[A-Z]{3}[0-9]{3}', placa_text)
                if placa_matches:
                    placa_detectada = placa_matches[0]
                    return {
                        'success': True,
                        'placa': placa_detectada,
                        'confianza': 85,
                        'metodo': 'openai_vision_extracted',
                        'placa_registrada': placa_registrada,
                        'coincide': placa_detectada == placa_registrada.upper() if placa_registrada else None
                    }
                else:
                    return {
                        'success': False,
                        'placa': '',
                        'confianza': 0,
                        'metodo': 'openai_vision',
                        'mensaje': f'Formato de placa inválido: {placa_text}'
                    }

        except Exception as e:
            self.logger.error(f"Error en OpenAI Vision: {e}")
            return {
                'success': False,
                'placa': '',
                'confianza': 0,
                'metodo': 'openai_vision',
                'mensaje': f'Error OpenAI Vision: {str(e)}'
            }

    def _extract_text_from_image(self, image_path: str) -> str:
        """
        Extrae texto de imagen usando OCR local con lazy loading
        """
        try:
            # Lazy loading: Solo inicializar EasyOCR si es necesario y no se ha inicializado
            if self.ocr_engine == 'easyocr' and not self.ocr_reader:
                try:
                    import easyocr
                    self.logger.info("Inicializando EasyOCR bajo demanda...")
                    self.ocr_reader = easyocr.Reader(['es', 'en'], gpu=False)
                    self.logger.info("EasyOCR inicializado bajo demanda para placas")
                except Exception as e:
                    self.logger.error(f"Error inicializando EasyOCR bajo demanda: {e}")
                    self.ocr_reader = None
            
            if self.ocr_engine == 'easyocr' and self.ocr_reader:
                # Usar EasyOCR
                results = self.ocr_reader.readtext(image_path)
                text = ' '.join([item[1] for item in results])
            else:
                # Usar Tesseract como fallback
                from PIL import Image
                import pytesseract
                image = Image.open(image_path)
                text = pytesseract.image_to_string(image, lang='spa+eng')
            
            return text.strip()
        except Exception as e:
            self.logger.error(f"Error en OCR local: {e}")
            return ""
    
    def _create_placa_prompt(self) -> PromptTemplate:
        """
        Crea el prompt específico para OCR de placas vehiculares
        """
        template = """Eres experto en OCR, analizas imagenes de forma excepcional. Con base en la imagen que te adjunto valida lo siguiente:

Placa de Vehiculo, devolver la placa, por lo general 3 letras y 3 números.

Ejemplo respuesta: ABC123

Solo responder en ese formato

Texto extraído de la imagen: {text}"""
        
        return PromptTemplate(
            input_variables=["text"],
            template=template
        )
    
    def _process_with_langchain(self, extracted_text: str) -> Dict[str, Any]:
        """
        Procesa el texto extraído con LangChain + OpenAI para identificar la placa
        """
        try:
            # Verificar si LangChain está realmente disponible
            if not LANGCHAIN_AVAILABLE or self.llm is None:
                return {
                    'success': False,
                    'placa': '',
                    'confianza': 0,
                    'metodo': 'local_ocr_langchain',
                    'mensaje': 'LangChain no disponible'
                }
            
            # Verificar si es la clase mock
            if self.llm.__class__.__name__ == 'ChatOpenAI' and not hasattr(self.llm, 'invoke'):
                return {
                    'success': False,
                    'placa': '',
                    'confianza': 0,
                    'metodo': 'local_ocr_langchain',
                    'mensaje': 'LLM mock class, usando webhook fallback'
                }
            
            # Importar LLMChain solo si está disponible
            from langchain.chains import LLMChain
            prompt = self._create_placa_prompt()
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Ejecutar cadena LangChain
            response = chain.run(text=extracted_text)
            placa_text = response.strip()
            
            # Validar formato de placa (3 letras + 3 números)
            import re
            placa_pattern = r'^[A-Z]{3}[0-9]{3}$'
            
            if re.match(placa_pattern, placa_text):
                return {
                    'success': True,
                    'placa': placa_text,
                    'confianza': 95,  # Alta confianza si pasa validación
                    'metodo': 'local_ocr_langchain'
                }
            else:
                # Intentar extraer placa de texto más largo
                placa_matches = re.findall(r'[A-Z]{3}[0-9]{3}', placa_text.upper())
                if placa_matches:
                    return {
                        'success': True,
                        'placa': placa_matches[0],
                        'confianza': 85,
                        'metodo': 'local_ocr_langchain_extracted'
                    }
                else:
                    return {
                        'success': False,
                        'placa': '',
                        'confianza': 0,
                        'metodo': 'local_ocr_langchain',
                        'mensaje': f'Formato de placa inválido: {placa_text}'
                    }
        
        except Exception as e:
            self.logger.error(f"Error en procesamiento LangChain: {e}")
            return {
                'success': False,
                'placa': '',
                'confianza': 0,
                'metodo': 'local_ocr_langchain',
                'mensaje': f'Error LangChain: {str(e)}'
            }
    
    def _process_with_webhook(self, image_path: str) -> Dict[str, Any]:
        """
        Procesa imagen usando webhook de n8n como fallback
        """
        try:
            with open(image_path, 'rb') as image_file:
                files = {'image': image_file}
                response = requests.post(self.webhook_url, files=files, timeout=30)
            
            if response.status_code == 200:
                placa_text = response.text.strip()
                
                # Validar formato
                import re
                placa_pattern = r'^[A-Z]{3}[0-9]{3}$'
                
                if re.match(placa_pattern, placa_text):
                    return {
                        'success': True,
                        'placa': placa_text,
                        'confianza': 80,
                        'metodo': 'webhook_n8n'
                    }
                else:
                    return {
                        'success': False,
                        'placa': '',
                        'confianza': 0,
                        'metodo': 'webhook_n8n',
                        'mensaje': f'Formato inválido webhook: {placa_text}'
                    }
            else:
                return {
                    'success': False,
                    'placa': '',
                    'confianza': 0,
                    'metodo': 'webhook_n8n',
                    'mensaje': f'Error webhook: {response.status_code}'
                }
        
        except Exception as e:
            self.logger.error(f"Error en webhook fallback: {e}")
            return {
                'success': False,
                'placa': '',
                'confianza': 0,
                'metodo': 'webhook_n8n',
                'mensaje': f'Error webhook: {str(e)}'
            }
    
    def process_placa_image(self, image_path: str, user: str = "sistema", placa_registrada: str = None) -> Dict[str, Any]:
        """
        Procesa imagen de placa vehicular optimizado para velocidad
        
        Args:
            image_path: Ruta a la imagen de la placa
            user: Usuario que ejecuta el procesamiento
            placa_registrada: Placa registrada para comparación (opcional)
        
        Returns:
            Dict con resultado del procesamiento de placa
        """
        try:
            self.logger.info(f"Procesando placa: {image_path} por usuario: {user}")
            if placa_registrada:
                self.logger.info(f"Placa registrada para comparación: {placa_registrada}")
            
            # MÉTODO OPTIMIZADO: OpenAI GPT-4 Vision (Directo y rápido)
            if self.openai_client:
                self.logger.info("🤖 Intentando con OpenAI GPT-4 Vision...")
                result = self._process_with_openai_vision(image_path, placa_registrada)
                
                if result['success']:
                    self.logger.info(f"✅ OpenAI Vision procesó exitosamente: {result['placa']}")
                    return result
                else:
                    self.logger.warning(f"⚠️ OpenAI Vision falló: {result.get('mensaje', 'Sin mensaje')}")
            else:
                self.logger.warning("OpenAI no disponible, usando fallbacks")
            
            # FALLBACKS: Solo si OpenAI no está disponible o falló y están habilitados
            if self.enable_fallbacks:
                # Inicializar servicios de fallback si no se han inicializado
                if not self.llm and not self.ocr_reader:
                    self.logger.info("Inicializando servicios de fallback por primera vez...")
                    self._init_fallback_services()
                
                # MÉTODO 2: OCR Local + LangChain (Secundario)
                if self.ocr_reader or self.llm:
                    extracted_text = self._extract_text_from_image(image_path)
                    
                    if extracted_text:
                        self.logger.info(f"🔍 Texto OCR extraído: {extracted_text}")
                        self.logger.info("🧠 Intentando con LangChain...")
                        
                        result = self._process_with_langchain(extracted_text)
                        
                        if result['success']:
                            # Añadir verificación de placa registrada si se proporcionó
                            if placa_registrada:
                                result['placa_registrada'] = placa_registrada
                                result['coincide'] = result['placa'] == placa_registrada.upper()
                            
                            self.logger.info(f"✅ LangChain procesó exitosamente: {result['placa']}")
                            return result
                        else:
                            self.logger.warning(f"⚠️ LangChain falló: {result.get('mensaje', 'Sin mensaje')}")
                    else:
                        self.logger.warning("⚠️ No se pudo extraer texto con OCR local")
            
            # MÉTODO 3: Webhook Fallback (Final)
            self.logger.info("🔄 Usando webhook fallback para placa...")
            result = self._process_with_webhook(image_path)
            
            if result['success']:
                # Añadir verificación de placa registrada si se proporcionó
                if placa_registrada:
                    result['placa_registrada'] = placa_registrada
                    result['coincide'] = result['placa'] == placa_registrada.upper()
                
                self.logger.info(f"✅ Webhook procesó exitosamente: {result['placa']}")
            else:
                self.logger.error(f"❌ Webhook falló: {result.get('mensaje', 'Sin mensaje')}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"❌ Error general procesando placa: {e}")
            return {
                'success': False,
                'placa': '',
                'confianza': 0,
                'metodo': 'error',
                'mensaje': f'Error general: {str(e)}'
            }

# Instancia global del servicio de placas
ocr_placa_service = OCRPlacaService() 