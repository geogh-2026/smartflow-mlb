#!/usr/bin/env python3
"""
Test simple para verificar el funcionamiento del OCR de placas actualizado con OpenAI Vision
"""

import os
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_placa_service():
    """Test del servicio de OCR de placas"""
    try:
        # Importar el servicio
        from app.utils.ocr_service import ocr_placa_service
        
        logger.info("🧪 Iniciando test del servicio de OCR de placas...")
        
        # Verificar que el servicio se inicializó correctamente
        logger.info(f"✅ Servicio OCR de placas inicializado")
        logger.info(f"   - OpenAI disponible: {ocr_placa_service.openai_client is not None}")
        logger.info(f"   - LLM disponible: {ocr_placa_service.llm is not None}")
        logger.info(f"   - OCR Reader disponible: {ocr_placa_service.ocr_reader is not None}")
        logger.info(f"   - Webhook URL: {ocr_placa_service.webhook_url}")
        
        # Buscar una imagen de prueba
        test_image_path = "placa_test.jpg"
        
        if os.path.exists(test_image_path):
            logger.info(f"📷 Procesando imagen de prueba: {test_image_path}")
            
            # Test sin placa registrada
            result = ocr_placa_service.process_placa_image(test_image_path, "test_user")
            
            logger.info(f"📊 Resultado del procesamiento:")
            logger.info(f"   - Éxito: {result['success']}")
            logger.info(f"   - Placa detectada: {result.get('placa', 'N/A')}")
            logger.info(f"   - Método: {result.get('metodo', 'N/A')}")
            logger.info(f"   - Confianza: {result.get('confianza', 'N/A')}")
            logger.info(f"   - Mensaje: {result.get('mensaje', 'N/A')}")
            
            if result['success']:
                # Test con placa registrada (simulando verificación)
                placa_test = result['placa']
                logger.info(f"🔍 Probando verificación con placa registrada: {placa_test}")
                
                result2 = ocr_placa_service.process_placa_image(test_image_path, "test_user", placa_test)
                
                logger.info(f"✅ Resultado de verificación:")
                logger.info(f"   - Coincide: {result2.get('coincide', 'N/A')}")
                logger.info(f"   - Placa registrada: {result2.get('placa_registrada', 'N/A')}")
                
        else:
            logger.warning(f"⚠️ No se encontró imagen de prueba en: {test_image_path}")
            logger.info("   Coloque una imagen de placa llamada 'placa_test.jpg' en el directorio raíz para probar")
        
        logger.info("🎉 Test completado")
        
    except Exception as e:
        logger.error(f"❌ Error en el test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    # Configurar variable de entorno si no está configurada
    if not os.getenv('OPENAI_API_KEY'):
        logger.warning("⚠️ OPENAI_API_KEY no está configurada. Solo se probarán métodos fallback.")
    
    test_placa_service() 