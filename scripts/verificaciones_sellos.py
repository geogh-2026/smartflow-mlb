#!/usr/bin/env python3
"""
Script de verificaciones programadas para el sistema de sellos.
Ejecuta verificaciones automáticas y envía notificaciones cuando sea necesario.

Uso:
    python scripts/verificaciones_sellos.py

Este script debe ejecutarse periódicamente (ej: cada hora) mediante cron o similar.
"""

import sys
import os
import logging
from datetime import datetime

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/verificaciones_sellos.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Función principal del script de verificaciones."""
    try:
        logger.info("=== INICIANDO VERIFICACIONES PROGRAMADAS DE SELLOS ===")
        
        # Importar después de configurar el path
        from app import create_app
        from app.utils.sellos_notification_service import ejecutar_verificaciones_programadas
        
        # Crear aplicación Flask
        app = create_app()
        
        with app.app_context():
            logger.info("Ejecutando verificaciones programadas...")
            
            # Ejecutar todas las verificaciones
            resultados = ejecutar_verificaciones_programadas()
            
            # Registrar resultados
            logger.info("Resultados de verificaciones:")
            for verificacion, resultado in resultados.items():
                if isinstance(resultado, list):
                    logger.info(f"  - {verificacion}: {len(resultado)} elementos encontrados")
                    if resultado:
                        logger.info(f"    Detalles: {resultado}")
                else:
                    logger.info(f"  - {verificacion}: {resultado}")
            
            # Estadísticas adicionales
            total_verificaciones = len(resultados)
            verificaciones_con_resultados = len([r for r in resultados.values() if r])
            
            logger.info(f"Resumen: {total_verificaciones} verificaciones ejecutadas, "
                       f"{verificaciones_con_resultados} con resultados")
            
            logger.info("=== VERIFICACIONES COMPLETADAS EXITOSAMENTE ===")
            
            return 0
            
    except ImportError as e:
        logger.error(f"Error de importación: {e}")
        logger.error("Asegúrese de que el entorno virtual esté activado y las dependencias instaladas")
        return 1
        
    except Exception as e:
        logger.error(f"Error ejecutando verificaciones: {e}")
        logger.exception("Detalles del error:")
        return 1

def verificar_configuracion():
    """Verificar que la configuración esté correcta."""
    try:
        from app import create_app
        from app.utils.sellos_notification_service import sello_notification_service
        
        app = create_app()
        
        with app.app_context():
            # Verificar que el servicio esté disponible
            if not sello_notification_service:
                logger.error("Servicio de notificaciones no disponible")
                return False
            
            # Verificar configuración básica
            config = sello_notification_service.configuracion
            logger.info(f"Configuración cargada: {len(config)} parámetros")
            
            # Verificar canales activos
            canales = sello_notification_service.canales_activos
            logger.info(f"Canales activos: {[c.value for c in canales]}")
            
            return True
            
    except Exception as e:
        logger.error(f"Error verificando configuración: {e}")
        return False

def mostrar_ayuda():
    """Mostrar información de ayuda."""
    print("""
Script de Verificaciones Programadas - Sistema de Sellos

DESCRIPCIÓN:
    Este script ejecuta verificaciones automáticas del sistema de sellos
    y envía notificaciones cuando detecta situaciones que requieren atención.

VERIFICACIONES INCLUIDAS:
    - Inventario bajo: Detecta tipos de sello con stock insuficiente
    - Instalaciones retrasadas: Identifica instalaciones que han tomado demasiado tiempo
    - Alertas de seguridad: Procesa alertas pendientes del sistema

USO:
    python scripts/verificaciones_sellos.py [opciones]

OPCIONES:
    --help, -h          Mostrar esta ayuda
    --check-config      Verificar configuración sin ejecutar verificaciones
    --verbose, -v       Mostrar información detallada

CONFIGURACIÓN CRON:
    Para ejecutar cada hora:
    0 * * * * cd /ruta/al/proyecto && python scripts/verificaciones_sellos.py

    Para ejecutar cada 30 minutos:
    */30 * * * * cd /ruta/al/proyecto && python scripts/verificaciones_sellos.py

LOGS:
    Los logs se escriben en: logs/verificaciones_sellos.log

EJEMPLOS:
    # Ejecución normal
    python scripts/verificaciones_sellos.py
    
    # Verificar configuración
    python scripts/verificaciones_sellos.py --check-config
    
    # Ejecución con detalles
    python scripts/verificaciones_sellos.py --verbose
""")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Verificaciones programadas del sistema de sellos')
    parser.add_argument('--check-config', action='store_true', 
                       help='Verificar configuración sin ejecutar verificaciones')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Mostrar información detallada')
    parser.add_argument('--help-extended', action='store_true',
                       help='Mostrar ayuda extendida')
    
    args = parser.parse_args()
    
    if args.help_extended:
        mostrar_ayuda()
        sys.exit(0)
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Modo verbose activado")
    
    if args.check_config:
        logger.info("Verificando configuración...")
        if verificar_configuracion():
            logger.info("✓ Configuración válida")
            sys.exit(0)
        else:
            logger.error("✗ Error en la configuración")
            sys.exit(1)
    
    # Ejecutar verificaciones
    exit_code = main()
    sys.exit(exit_code) 