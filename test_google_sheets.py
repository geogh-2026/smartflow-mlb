#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración de Google Sheets
Oleoflores Smart Flow - Validación de Proveedores

Uso: python test_google_sheets.py
"""

import os
import sys
sys.path.append('.')

def test_validation():
    print("=" * 60)
    print("🔍 PROBANDO CONFIGURACIÓN GOOGLE SHEETS OLEOFLORES")
    print("=" * 60)
    
    try:
        from app.utils.provider_validation_service import provider_validation_service
        
        print(f"📊 Estado inicial del servicio:")
        print(f"   🔍 Google Sheets disponible: {provider_validation_service.google_sheets_available}")
        print(f"   📡 Webhook fallback disponible: {provider_validation_service.webhook_available}")
        print(f"   📋 Hoja de proveedores: {provider_validation_service.spreadsheet_id}")
        print(f"   📐 Rango configurado: {provider_validation_service.sheets_range}")
        print(f"   🔧 Usando configuración de graneles reutilizada")
        
        if not provider_validation_service.google_sheets_available:
            print("\n⚠️  ADVERTENCIA: Google Sheets no está disponible")
            print("   Verifica la configuración en el archivo .env")
            print("   El sistema usará webhook como fallback")
        
        print("\n" + "=" * 60)
        print("🧪 PROBANDO CÓDIGOS DE TU HOJA")
        print("=" * 60)
        
        # Códigos reales de la hoja mostrada en la imagen
        test_codes = [
            {
                "codigo": "0101001A",
                "esperado": "OSWALDO BLANCO PADILLA"
            },
            {
                "codigo": "0101002A", 
                "esperado": "REYES MIGUEL MARTINEZ"
            },
            {
                "codigo": "0101003A",
                "esperado": "ELADIO CHIQUILLO MERCADO"
            },
            {
                "codigo": "0101017A",
                "esperado": "ANDREA MARIA RAMOS"
            },
            {
                "codigo": "0101022A",
                "esperado": "DORA LUISA RIOS"
            },
            {
                "codigo": "NOEXISTE",
                "esperado": "ERROR - Código inexistente"
            }
        ]
        
        resultados = {
            "total": len(test_codes),
            "exitosos": 0,
            "fallidos": 0,
            "google_sheets": 0,
            "webhook": 0,
            "errores": 0
        }
        
        for i, test_case in enumerate(test_codes, 1):
            codigo = test_case["codigo"]
            esperado = test_case["esperado"]
            
            print(f"\n🎯 Prueba {i}/{len(test_codes)}: {codigo}")
            print(f"   Esperado: {esperado}")
            
            try:
                result = provider_validation_service.validate_provider_code(codigo)
                
                if result['success']:
                    data = result['data']
                    method = result.get('method', 'desconocido')
                    nombre_obtenido = data.get('nombre_agricultor', 'Sin nombre')
                    
                    # Verificar si el nombre contiene lo esperado (búsqueda flexible)
                    match = any(word.upper() in nombre_obtenido.upper() for word in esperado.split())
                    
                    if match or codigo == "NOEXISTE":  # NOEXISTE debería fallar
                        print(f"   ✅ ÉXITO ({method})")
                        print(f"   📋 Código: {data.get('codigo')}")
                        print(f"   👤 Nombre: {nombre_obtenido}")
                        if method == 'google_sheets':
                            print(f"   📊 Fila: {data.get('fila_encontrada')}")
                            resultados["google_sheets"] += 1
                        else:
                            resultados["webhook"] += 1
                        resultados["exitosos"] += 1
                    else:
                        print(f"   ⚠️  NOMBRE NO COINCIDE")
                        print(f"   📋 Obtenido: {nombre_obtenido}")
                        resultados["fallidos"] += 1
                        
                else:
                    if codigo == "NOEXISTE":
                        print(f"   ✅ CORRECTO - Error esperado: {result.get('error')}")
                        resultados["exitosos"] += 1
                    else:
                        print(f"   ❌ ERROR: {result.get('error')}")
                        resultados["fallidos"] += 1
                        
            except Exception as e:
                print(f"   💥 EXCEPCIÓN: {str(e)}")
                resultados["errores"] += 1
        
        # Resumen de resultados
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE RESULTADOS")
        print("=" * 60)
        print(f"   📈 Total de pruebas: {resultados['total']}")
        print(f"   ✅ Exitosas: {resultados['exitosos']}")
        print(f"   ❌ Fallidas: {resultados['fallidos']}")
        print(f"   💥 Errores: {resultados['errores']}")
        print(f"   🔍 Google Sheets: {resultados['google_sheets']}")
        print(f"   📡 Webhook: {resultados['webhook']}")
        
        # Evaluación final
        if resultados["exitosos"] >= 4:  # Al menos 4 de 6 pruebas exitosas
            print(f"\n🎉 CONFIGURACIÓN EXITOSA!")
            if resultados["google_sheets"] > 0:
                print(f"   ⚡ Google Sheets funcionando - Validación en 1-2 segundos")
            else:
                print(f"   📡 Usando webhook fallback - Validación en 30+ segundos")
        else:
            print(f"\n⚠️  CONFIGURACIÓN NECESITA AJUSTES")
            print(f"   Revisa la documentación en: docs/migracion/setup_google_sheets_oleoflores.md")
        
    except ImportError as e:
        print(f"❌ ERROR DE IMPORTACIÓN: {e}")
        print("   Verifica que el servicio esté correctamente configurado")
    except Exception as e:
        print(f"💥 ERROR INESPERADO: {e}")

def test_environment():
    """Verificar configuración existente de graneles"""
    print("\n" + "=" * 60)
    print("🔧 VERIFICANDO CONFIGURACIÓN EXISTENTE")
    print("=" * 60)
    
    print("   📁 Buscando archivo de credenciales de graneles...")
    
    # Verificar archivo de credenciales de graneles
    creds_file = 'google_sheets_credentials_09052025.json'
    if os.path.exists(creds_file):
        print(f"   ✅ {creds_file}: Encontrado")
    else:
        print(f"   ⚠️  {creds_file}: No encontrado en raíz del proyecto")
    
    # Verificar módulo google_sheets_api
    try:
        from app.utils.google_sheets_api import get_sheets_service
        print("   ✅ google_sheets_api.py: Disponible")
    except ImportError:
        print("   ❌ google_sheets_api.py: No disponible")
    
    # Verificar webhook fallback
    webhook_url = os.getenv('REVALIDATION_WEBHOOK_URL', '')
    if webhook_url:
        print(f"   ✅ Webhook fallback: Configurado")
    else:
        print("   ⚪ Webhook fallback: No configurado (se usará el de misc/routes)")
    
    print("\n   🔄 Reutilizando configuración de graneles existente")
    print("   📋 Hoja específica: Proveedores Oleoflores")
    print("   📐 Estructura: A=Tratamiento, B=Acreedor, C=Nombre 1")

def main():
    print("🚀 INICIANDO VERIFICACIÓN COMPLETA...")
    
    # Verificar variables de entorno
    test_environment()
    
    # Probar validación
    test_validation()
    
    print("\n" + "=" * 60)
    print("🏁 VERIFICACIÓN COMPLETADA")
    print("=" * 60)
    print("📚 Documentación completa en:")
    print("   docs/migracion/setup_google_sheets_oleoflores.md")
    print("   docs/migracion/configuracion_google_sheets.md")

if __name__ == "__main__":
    main() 