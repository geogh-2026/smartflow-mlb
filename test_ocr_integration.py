#!/usr/bin/env python3
"""
Test rápido de integración del servicio OCR de tiquetes
"""

import sys
import os

# Configurar path
sys.path.insert(0, '/Users/enriquepabon/Library/CloudStorage/GoogleDrive-epabon@oleoflores.com/My Drive/Proyectos automatizaciones/Proyecto automatización registro MLB/oleoflores-smart-flow')

def test_import():
    """Test básico de importación"""
    try:
        from app.utils.tiquete_ocr_service import tiquete_ocr_service
        print("✅ Servicio OCR importado exitosamente")
        
        # Verificar configuración
        print(f"OpenAI disponible: {tiquete_ocr_service.openai_available}")
        print(f"Modelo: {tiquete_ocr_service.model}")
        
        # Test de prompt
        prompt = tiquete_ocr_service._create_tiquete_prompt()
        if "formato Markdown" in prompt:
            print("✅ Prompt configurado correctamente")
        else:
            print("❌ Error en prompt")
            
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_import()
    sys.exit(0 if success else 1)
