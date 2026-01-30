#!/usr/bin/env python3
"""
Script de configuración para OCR local con LangChain
====================================================

Este script configura automáticamente el entorno para usar OCR local
con LangChain en lugar de webhooks externos.

Funcionalidades:
- Instala dependencias necesarias
- Configura variables de entorno
- Verifica que todo funcione correctamente
- Proporciona instrucciones de configuración manual

Uso:
    python setup_ocr_langchain.py
"""

import os
import sys
import subprocess
import platform
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class OCRLangChainSetup:
    def __init__(self):
        self.is_windows = platform.system() == 'Windows'
        self.is_mac = platform.system() == 'Darwin'
        self.is_linux = platform.system() == 'Linux'
        
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / 'venv'
        self.requirements_file = self.project_root / 'requirements_ocr.txt'
        
        self.success_steps = []
        self.failed_steps = []

    def print_header(self):
        """Imprime el header del setup."""
        print("=" * 70)
        print("🚀 CONFIGURACIÓN OCR LOCAL + LANGCHAIN")
        print("=" * 70)
        print(f"Sistema operativo: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version}")
        print(f"Directorio del proyecto: {self.project_root}")
        print("-" * 70)

    def check_python_version(self):
        """Verifica que la versión de Python sea compatible."""
        try:
            version = sys.version_info
            if version.major < 3 or (version.major == 3 and version.minor < 8):
                logger.error("❌ Se requiere Python 3.8 o superior")
                return False
            logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} es compatible")
            self.success_steps.append("Versión de Python verificada")
            return True
        except Exception as e:
            logger.error(f"❌ Error verificando versión de Python: {e}")
            self.failed_steps.append("Verificación de Python")
            return False

    def install_system_dependencies(self):
        """Instala dependencias del sistema según el OS."""
        logger.info("📦 Instalando dependencias del sistema...")
        
        try:
            if self.is_mac:
                # macOS con Homebrew
                logger.info("Instalando Tesseract en macOS con Homebrew...")
                subprocess.run(["brew", "install", "tesseract"], check=True)
                subprocess.run(["brew", "install", "tesseract-lang"], check=True)
                
            elif self.is_linux:
                # Ubuntu/Debian
                logger.info("Instalando Tesseract en Linux...")
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-y", "tesseract-ocr"], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-y", "tesseract-ocr-spa"], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-y", "libtesseract-dev"], check=True)
                
            elif self.is_windows:
                logger.warning("⚠️ En Windows, instale Tesseract manualmente desde:")
                logger.warning("https://github.com/UB-Mannheim/tesseract/wiki")
                logger.warning("Luego agregue la ruta de Tesseract al PATH del sistema")
                
            self.success_steps.append("Dependencias del sistema")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error instalando dependencias del sistema: {e}")
            self.failed_steps.append("Dependencias del sistema")
            return False
        except FileNotFoundError:
            logger.warning("⚠️ Gestor de paquetes no encontrado. Instale manualmente:")
            if self.is_mac:
                logger.warning("- Instale Homebrew: https://brew.sh/")
            elif self.is_linux:
                logger.warning("- Use su gestor de paquetes para instalar tesseract-ocr")
            self.failed_steps.append("Dependencias del sistema (gestor no encontrado)")
            return False

    def install_python_dependencies(self):
        """Instala las dependencias de Python."""
        logger.info("🐍 Instalando dependencias de Python...")
        
        try:
            if not self.requirements_file.exists():
                logger.error(f"❌ No se encontró {self.requirements_file}")
                self.failed_steps.append("requirements_ocr.txt no encontrado")
                return False
            
            # Instalar dependencias
            cmd = [sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Dependencias de Python instaladas correctamente")
                self.success_steps.append("Dependencias de Python")
                return True
            else:
                logger.error(f"❌ Error instalando dependencias: {result.stderr}")
                self.failed_steps.append("Dependencias de Python")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error instalando dependencias de Python: {e}")
            self.failed_steps.append("Dependencias de Python")
            return False

    def setup_environment_variables(self):
        """Configura las variables de entorno necesarias."""
        logger.info("🔧 Configurando variables de entorno...")
        
        env_file = self.project_root / '.env'
        env_content = []
        
        # Leer archivo .env existente si existe
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.readlines()
        
        # Variables que necesitamos configurar
        required_vars = {
            'OPENAI_API_KEY': 'tu_openai_api_key_aqui',
            # 'ANTHROPIC_API_KEY': 'tu_anthropic_api_key_aqui',  # Opcional
            # 'OLLAMA_BASE_URL': 'http://localhost:11434',      # Para modelos locales
        }
        
        updated = False
        for var_name, default_value in required_vars.items():
            # Verificar si la variable ya existe
            var_exists = any(line.strip().startswith(f"{var_name}=") for line in env_content)
            
            if not var_exists:
                env_content.append(f"{var_name}={default_value}\n")
                updated = True
                logger.info(f"➕ Agregada variable: {var_name}")
        
        # Escribir archivo .env actualizado
        if updated:
            with open(env_file, 'w') as f:
                f.writelines(env_content)
            logger.info(f"✅ Archivo .env actualizado: {env_file}")
        else:
            logger.info("✅ Variables de entorno ya configuradas")
        
        self.success_steps.append("Variables de entorno")
        return True

    def test_ocr_libraries(self):
        """Prueba que las librerías de OCR funcionen."""
        logger.info("🧪 Probando librerías de OCR...")
        
        ocr_available = []
        
        # Probar EasyOCR
        try:
            import easyocr
            reader = easyocr.Reader(['es', 'en'], gpu=False)
            ocr_available.append("EasyOCR")
            logger.info("✅ EasyOCR disponible")
        except Exception as e:
            logger.warning(f"⚠️ EasyOCR no disponible: {e}")
        
        # Probar Tesseract
        try:
            import pytesseract
            from PIL import Image
            # Crear imagen de prueba
            test_image = Image.new('RGB', (200, 50), color='white')
            pytesseract.image_to_string(test_image)
            ocr_available.append("Tesseract")
            logger.info("✅ Tesseract disponible")
        except Exception as e:
            logger.warning(f"⚠️ Tesseract no disponible: {e}")
        
        if ocr_available:
            logger.info(f"✅ Motores OCR disponibles: {', '.join(ocr_available)}")
            self.success_steps.append(f"OCR ({', '.join(ocr_available)})")
            return True
        else:
            logger.error("❌ No hay motores de OCR disponibles")
            self.failed_steps.append("Motores OCR")
            return False

    def test_langchain(self):
        """Prueba que LangChain esté disponible."""
        logger.info("🔗 Probando LangChain...")
        
        try:
            from langchain.prompts import PromptTemplate
            from langchain.chains import LLMChain
            
            # Verificar si hay una API key configurada
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key and openai_key != 'tu_openai_api_key_aqui':
                try:
                    from langchain.chat_models import ChatOpenAI
                    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.1)
                    logger.info("✅ LangChain con OpenAI configurado")
                except Exception as e:
                    logger.warning(f"⚠️ Error configurando OpenAI: {e}")
            else:
                logger.warning("⚠️ OPENAI_API_KEY no configurada")
            
            logger.info("✅ LangChain disponible")
            self.success_steps.append("LangChain")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error con LangChain: {e}")
            self.failed_steps.append("LangChain")
            return False

    def run_setup(self):
        """Ejecuta todo el proceso de configuración."""
        self.print_header()
        
        steps = [
            ("Verificar Python", self.check_python_version),
            ("Instalar dependencias del sistema", self.install_system_dependencies),
            ("Instalar dependencias Python", self.install_python_dependencies),
            ("Configurar variables de entorno", self.setup_environment_variables),
            ("Probar librerías OCR", self.test_ocr_libraries),
            ("Probar LangChain", self.test_langchain),
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n🔄 {step_name}...")
            try:
                step_func()
            except Exception as e:
                logger.error(f"❌ Error en {step_name}: {e}")
                self.failed_steps.append(step_name)
        
        # Resumen final
        self.print_summary()

    def print_summary(self):
        """Imprime el resumen de la configuración."""
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE CONFIGURACIÓN")
        print("=" * 70)
        
        if self.success_steps:
            print("✅ PASOS EXITOSOS:")
            for step in self.success_steps:
                print(f"   ✓ {step}")
        
        if self.failed_steps:
            print("\n❌ PASOS FALLIDOS:")
            for step in self.failed_steps:
                print(f"   ✗ {step}")
        
        print("\n" + "=" * 70)
        print("📝 INSTRUCCIONES ADICIONALES")
        print("=" * 70)
        
        if not self.failed_steps:
            print("🎉 ¡Configuración completada exitosamente!")
        else:
            print("⚠️ Configuración parcial. Revise los pasos fallidos.")
        
        print("\n1. Configure su API key de OpenAI:")
        print("   - Edite el archivo .env")
        print("   - Reemplace 'tu_openai_api_key_aqui' con su API key real")
        
        print("\n2. Para usar el OCR local:")
        print("   - EasyOCR: Recomendado, no requiere configuración adicional")
        print("   - Tesseract: Requiere instalación del sistema")
        
        print("\n3. Ejecute la migración de base de datos:")
        print("   python scripts/add_vencimiento_fields.py")
        
        print("\n4. Reinicie su aplicación Flask")
        
        print("\n5. Los webhooks seguirán funcionando como fallback")
        
        if self.failed_steps:
            print(f"\n❗ Total de errores: {len(self.failed_steps)}")
            return False
        else:
            print(f"\n🎯 Todo configurado correctamente!")
            return True

def main():
    """Función principal."""
    setup = OCRLangChainSetup()
    success = setup.run_setup()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 