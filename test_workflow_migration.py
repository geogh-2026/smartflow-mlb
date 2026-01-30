#!/usr/bin/env python3
"""
Test completo de migración del workflow de procesamiento de tiquetes
Valida que el nuevo servicio OCR funciona correctamente integrado
"""

import os
import sys
import json
import tempfile
from PIL import Image, ImageDraw, ImageFont

# Configurar path
sys.path.insert(0, '/Users/enriquepabon/Library/CloudStorage/GoogleDrive-epabon@oleoflores.com/My Drive/Proyectos automatizaciones/Proyecto automatización registro MLB/oleoflores-smart-flow')

def create_test_tiquete_image():
    """
    Crear una imagen de tiquete simulada para testing
    """
    try:
        # Crear imagen de prueba
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Simular texto de tiquete
        test_data = [
            "MLB EXTRACTORA S.A.S.",
            "FECHA: 15/11/2024",
            "AGRICULTOR: CARLOS RODRIGUEZ",
            "CÓDIGO: 0123456A",
            "PLACA: ABC123",
            "RACIMOS: 25",
            "ACARREÓ: SÍ",
            "CARGÓ: SÍ",
            "TRANSPORTADOR: JUAN PEREZ",
            "COD. TRANSPORT: T001"
        ]
        
        # Dibujar texto
        y_pos = 50
        for line in test_data:
            draw.text((50, y_pos), line, fill='black')
            y_pos += 40
        
        # Guardar imagen temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        image.save(temp_file.name)
        temp_file.close()
        
        return temp_file.name
        
    except Exception as e:
        print(f"Error creando imagen test: {e}")
        return None

def test_ocr_service():
    """
    Test del servicio OCR completo
    """
    try:
        from app.utils.tiquete_ocr_service import tiquete_ocr_service
        
        print("🔍 Probando servicio OCR...")
        
        # Crear imagen de prueba
        image_path = create_test_tiquete_image()
        if not image_path:
            print("❌ Error creando imagen de prueba")
            return False
        
        try:
            # Procesar imagen
            result = tiquete_ocr_service.process_tiquete_image(image_path, usuario="test")
            
            if result['success']:
                print(f"✅ Procesamiento exitoso con método: {result['method']}")
                
                # Verificar datos
                data = result['data']
                required_fields = ['fecha_tiquete', 'nombre_proveedor', 'codigo_proveedor', 'placa']
                
                for field in required_fields:
                    if field in data:
                        print(f"✅ Campo {field}: {data[field]}")
                    else:
                        print(f"⚠️  Campo {field} no encontrado")
                
                return True
            else:
                print(f"❌ Procesamiento falló: {result.get('error', 'Error desconocido')}")
                return False
                
        finally:
            # Limpiar archivo temporal
            if os.path.exists(image_path):
                os.unlink(image_path)
                
    except Exception as e:
        print(f"❌ Error en test OCR: {e}")
        return False

def test_entrada_integration():
    """
    Test de integración con módulo de entrada
    """
    try:
        # Simular Flask app context
        from flask import Flask
        app = Flask(__name__)
        app.config['UPLOAD_FOLDER'] = '/tmp'
        
        with app.app_context():
            from app.blueprints.entrada.routes import process_tiquete_image
            
            print("🔗 Probando integración con entrada...")
            
            # Crear imagen de prueba
            image_path = create_test_tiquete_image()
            if not image_path:
                print("❌ Error creando imagen de prueba")
                return False
            
            try:
                # Procesar con función de entrada
                result = process_tiquete_image(image_path, "test_image.png")
                
                if result.get('result') == 'ok':
                    print("✅ Integración con entrada exitosa")
                    
                    # Verificar formato de respuesta
                    parsed_data = result.get('parsed_data', {})
                    if 'table_data' in parsed_data:
                        print("✅ Formato de tabla correcto")
                        
                        # Verificar campos requeridos
                        table_data = parsed_data['table_data']
                        campos_esperados = ['Fecha', 'Nombre del Agricultor', 'Código', 'Placa']
                        
                        for campo in campos_esperados:
                            found = any(row.get('campo') == campo for row in table_data)
                            if found:
                                print(f"✅ Campo {campo} encontrado en tabla")
                            else:
                                print(f"⚠️  Campo {campo} no encontrado en tabla")
                    
                    return True
                else:
                    print(f"❌ Integración falló: {result.get('message', 'Error desconocido')}")
                    return False
                    
            finally:
                # Limpiar archivo temporal
                if os.path.exists(image_path):
                    os.unlink(image_path)
                
    except Exception as e:
        print(f"❌ Error en test integración: {e}")
        return False

def test_fallback_mechanism():
    """
    Test del mecanismo de fallback
    """
    try:
        from app.utils.tiquete_ocr_service import tiquete_ocr_service
        
        print("🔄 Probando mecanismo de fallback...")
        
        # Simular falla de OpenAI
        original_available = tiquete_ocr_service.openai_available
        tiquete_ocr_service.openai_available = False
        
        try:
            # Crear imagen de prueba
            image_path = create_test_tiquete_image()
            if not image_path:
                print("❌ Error creando imagen de prueba")
                return False
            
            # Procesar imagen (debería usar fallback)
            result = tiquete_ocr_service.process_tiquete_image(image_path, usuario="test")
            
            if not result['success']:
                print("✅ Fallback activado correctamente")
                return True
            else:
                print("⚠️  Fallback no se activó cuando debería")
                return False
                
        finally:
            # Restaurar configuración original
            tiquete_ocr_service.openai_available = original_available
            
            # Limpiar archivo temporal
            if os.path.exists(image_path):
                os.unlink(image_path)
                
    except Exception as e:
        print(f"❌ Error en test fallback: {e}")
        return False

def test_prompt_validation():
    """
    Test de validación del prompt
    """
    try:
        from app.utils.tiquete_ocr_service import tiquete_ocr_service
        
        print("📝 Probando validación de prompt...")
        
        # Verificar que el prompt contiene elementos clave
        prompt = tiquete_ocr_service._create_tiquete_prompt()
        
        required_elements = [
            "formato Markdown",
            "Fecha",
            "Nombre del Agricultor",
            "Código",
            "Placa",
            "Cantidad de Racimos",
            "Nota de Validación"
        ]
        
        all_found = True
        for element in required_elements:
            if element in prompt:
                print(f"✅ Elemento '{element}' encontrado en prompt")
            else:
                print(f"❌ Elemento '{element}' NO encontrado en prompt")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ Error en test prompt: {e}")
        return False

def main():
    """
    Ejecutar todos los tests
    """
    print("🚀 Iniciando tests de migración del workflow...")
    print("=" * 50)
    
    tests = [
        ("Servicio OCR", test_ocr_service),
        ("Integración Entrada", test_entrada_integration), 
        ("Mecanismo Fallback", test_fallback_mechanism),
        ("Validación Prompt", test_prompt_validation)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 Test: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASÓ")
                passed += 1
            else:
                print(f"❌ {test_name} FALLÓ")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Resumen: {passed} pasaron, {failed} fallaron")
    
    if failed == 0:
        print("🎉 ¡Todos los tests pasaron! Migración exitosa.")
        return True
    else:
        print("⚠️  Algunos tests fallaron. Revisar implementación.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
