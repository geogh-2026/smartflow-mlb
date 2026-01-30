#!/usr/bin/env python3
"""
Script para recuperar y asociar imágenes de tiquetes con las guías migradas.
Escanea los directorios de imágenes y actualiza las referencias en la base de datos.
"""

import sqlite3
import os
import re
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TiqueteImageRecovery:
    def __init__(self, db_path="instance/oleoflores_dev.db"):
        self.db_path = db_path
        self.static_path = Path("app/static")
        self.uploads_path = self.static_path / "uploads"
        self.fotos_pesaje_path = self.static_path / "fotos_pesaje_neto"
        
        # Contadores
        self.images_found = 0
        self.images_associated = 0
        self.db_updates = 0
        
    def scan_images(self):
        """Escanear todos los directorios de imágenes y catalogar las encontradas"""
        logger.info("🔍 Escaneando imágenes de tiquetes...")
        
        images_catalog = {
            'uploads': [],
            'fotos_pesaje_neto': [],
            'other': []
        }
        
        # Escanear directorio uploads
        if self.uploads_path.exists():
            for file_path in self.uploads_path.glob("tiquete_*"):
                if file_path.is_file() and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    images_catalog['uploads'].append({
                        'path': file_path,
                        'relative_path': f"uploads/{file_path.name}",
                        'filename': file_path.name,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                    })
                    self.images_found += 1
        
        # Escanear directorio fotos_pesaje_neto
        if self.fotos_pesaje_path.exists():
            for file_path in self.fotos_pesaje_path.glob("*"):
                if file_path.is_file() and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    images_catalog['fotos_pesaje_neto'].append({
                        'path': file_path,
                        'relative_path': f"fotos_pesaje_neto/{file_path.name}",
                        'filename': file_path.name,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                    })
                    self.images_found += 1
        
        logger.info(f"📊 Imágenes encontradas:")
        logger.info(f"   - Uploads: {len(images_catalog['uploads'])}")
        logger.info(f"   - Fotos pesaje neto: {len(images_catalog['fotos_pesaje_neto'])}")
        logger.info(f"   - Total: {self.images_found}")
        
        return images_catalog
    
    def extract_codigo_guia_from_filename(self, filename):
        """Intentar extraer código de guía del nombre del archivo"""
        logger.debug(f"🔍 Procesando archivo: {filename}")
        
        patterns = [
            # Formato completo con timestamp: 0105007A_20250711080143_2025-07-11_19-53-51.png
            r'(\d{7}[A-Z]_\d{14})',        # Captura: 0105007A_20250711080143
            # Formato con guión bajo adicional: 0150294A_20250711_155400
            r'(\d{7}[A-Z]_\d{8}_\d{6})',   # Captura: 0150294A_20250711_155400
            # Formato bascula: tiquete_bascula_0150076A.png
            r'bascula_(\d{7}[A-Z])',       # Captura: 0150076A
            # Formato genérico: cualquier código de guía
            r'(\d{7}[A-Z])',               # Captura: 0150294A
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                codigo_encontrado = match.group(1)
                logger.debug(f"✅ Patrón {i+1} coincidió: {codigo_encontrado}")
                return codigo_encontrado
        
        logger.debug(f"❌ No se encontró código de guía en: {filename}")
        return None
    
    def find_matching_guia(self, codigo_extraido, guias_en_db):
        """Buscar coincidencia entre código extraído y códigos en BD"""
        logger.debug(f"🔍 Buscando coincidencia para: {codigo_extraido}")
        
        # 1. Verificar coincidencia exacta
        if codigo_extraido in guias_en_db:
            logger.debug(f"✅ Coincidencia exacta encontrada: {codigo_extraido}")
            return codigo_extraido
        
        # 2. Si el código extraído contiene timestamp, buscar solo el código base
        if '_' in codigo_extraido:
            codigo_base = codigo_extraido.split('_')[0]  # 0105007A de 0105007A_20250711080143
            
            # Buscar guías que empiecen con este código base
            coincidencias = [guia for guia in guias_en_db if guia.startswith(codigo_base + '_')]
            if coincidencias:
                # Si tenemos el timestamp completo, buscar coincidencia exacta
                timestamp_completo = codigo_extraido.replace('_', '_', 1)  # Mantener formato
                for guia in coincidencias:
                    if guia == timestamp_completo:
                        logger.debug(f"✅ Coincidencia con timestamp encontrada: {guia}")
                        return guia
                
                # Si no hay coincidencia exacta con timestamp, tomar la primera
                primera_coincidencia = coincidencias[0]
                logger.debug(f"✅ Usando primera coincidencia: {primera_coincidencia}")
                return primera_coincidencia
        
        # 3. Si solo tenemos el código base (ej: 0150076A), buscar cualquier coincidencia
        else:
            coincidencias = [guia for guia in guias_en_db if guia.startswith(codigo_extraido + '_')]
            if coincidencias:
                primera_coincidencia = coincidencias[0]
                logger.debug(f"✅ Coincidencia por código base: {primera_coincidencia}")
                return primera_coincidencia
        
        logger.debug(f"❌ No se encontró coincidencia para: {codigo_extraido}")
        return None
    
    def associate_images_with_guides(self, images_catalog):
        """Asociar imágenes encontradas con códigos de guía en la base de datos"""
        logger.info("🔗 Asociando imágenes con guías...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Obtener todas las guías de la base de datos
            cursor.execute("SELECT codigo_guia FROM entry_records")
            guias_en_db = {row[0] for row in cursor.fetchall()}
            logger.info(f"📋 Guías en BD: {len(guias_en_db)}")
            
            associations = []
            
            # Procesar imágenes de uploads
            for img_info in images_catalog['uploads']:
                codigo_guia = self.extract_codigo_guia_from_filename(img_info['filename'])
                if codigo_guia:
                    # Verificar si el código existe exactamente o buscar coincidencias parciales
                    codigo_encontrado = self.find_matching_guia(codigo_guia, guias_en_db)
                    if codigo_encontrado:
                        associations.append({
                            'codigo_guia': codigo_encontrado,
                            'image_path': img_info['relative_path'],
                            'image_type': 'tiquete_upload',
                            'filename': img_info['filename'],
                            'size': img_info['size'],
                            'modified': img_info['modified']
                        })
                        self.images_associated += 1
                        logger.debug(f"✅ Asociado: {codigo_encontrado} -> {img_info['filename']}")
            
            # Procesar imágenes de fotos_pesaje_neto
            for img_info in images_catalog['fotos_pesaje_neto']:
                codigo_guia = self.extract_codigo_guia_from_filename(img_info['filename'])
                if codigo_guia:
                    # Verificar si el código existe exactamente o buscar coincidencias parciales
                    codigo_encontrado = self.find_matching_guia(codigo_guia, guias_en_db)
                    if codigo_encontrado:
                        associations.append({
                            'codigo_guia': codigo_encontrado,
                            'image_path': img_info['relative_path'],
                            'image_type': 'tiquete_pesaje_neto',
                            'filename': img_info['filename'],
                            'size': img_info['size'],
                            'modified': img_info['modified']
                        })
                        self.images_associated += 1
                        logger.debug(f"✅ Asociado: {codigo_encontrado} -> {img_info['filename']}")
            
            logger.info(f"🎯 Asociaciones encontradas: {len(associations)}")
            return associations
            
        finally:
            conn.close()
    
    def update_database_with_images(self, associations):
        """Actualizar la base de datos con las rutas de imágenes encontradas"""
        logger.info("💾 Actualizando base de datos con rutas de imágenes...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for assoc in associations:
                codigo_guia = assoc['codigo_guia']
                image_path = assoc['image_path']
                image_type = assoc['image_type']
                
                # Actualizar entry_records con la imagen principal
                # Si es una imagen de pesaje_neto (mejor calidad), siempre actualizar
                if image_type == 'tiquete_pesaje_neto':
                    cursor.execute("""
                        UPDATE entry_records 
                        SET image_filename = ? 
                        WHERE codigo_guia = ?
                    """, (image_path, codigo_guia))
                else:
                    # Para uploads, solo actualizar si no hay imagen o es genérica
                    cursor.execute("""
                        UPDATE entry_records 
                        SET image_filename = ? 
                        WHERE codigo_guia = ? AND (image_filename IS NULL OR image_filename = 'camera_capture.jpg')
                    """, (image_path, codigo_guia))
                
                if cursor.rowcount > 0:
                    self.db_updates += 1
                    logger.debug(f"📝 Actualizado entry_record: {codigo_guia} -> {image_path}")
                
                # Si es una imagen de pesaje neto, también actualizar pesajes_neto
                if image_type == 'tiquete_pesaje_neto':
                    cursor.execute("""
                        UPDATE pesajes_neto 
                        SET imagen_soporte_sap = ? 
                        WHERE codigo_guia = ? AND (imagen_soporte_sap IS NULL OR imagen_soporte_sap = '')
                    """, (image_path, codigo_guia))
                    
                    if cursor.rowcount > 0:
                        logger.debug(f"📝 Actualizado pesaje_neto: {codigo_guia} -> {image_path}")
                
                # También actualizar pesajes_bruto si corresponde
                if image_type == 'tiquete_upload':
                    cursor.execute("""
                        UPDATE pesajes_bruto 
                        SET imagen_pesaje = ? 
                        WHERE codigo_guia = ? AND (imagen_pesaje IS NULL OR imagen_pesaje = '')
                    """, (image_path, codigo_guia))
                    
                    if cursor.rowcount > 0:
                        logger.debug(f"📝 Actualizado pesaje_bruto: {codigo_guia} -> {image_path}")
            
            conn.commit()
            logger.info(f"✅ Base de datos actualizada: {self.db_updates} registros")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error actualizando BD: {e}")
            raise e
        finally:
            conn.close()
    
    def generate_report(self, associations):
        """Generar reporte detallado de la recuperación"""
        logger.info("📋 Generando reporte de recuperación...")
        
        report = {
            'summary': {
                'images_found': self.images_found,
                'images_associated': self.images_associated,
                'db_updates': self.db_updates,
                'success_rate': (self.images_associated / self.images_found * 100) if self.images_found > 0 else 0
            },
            'associations': associations
        }
        
        # Guardar reporte en archivo
        report_file = f"image_recovery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("REPORTE DE RECUPERACIÓN DE IMÁGENES DE TIQUETES\n")
            f.write("=" * 60 + "\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("RESUMEN:\n")
            f.write(f"- Imágenes encontradas: {report['summary']['images_found']}\n")
            f.write(f"- Imágenes asociadas: {report['summary']['images_associated']}\n")
            f.write(f"- Registros actualizados en BD: {report['summary']['db_updates']}\n")
            f.write(f"- Tasa de éxito: {report['summary']['success_rate']:.1f}%\n\n")
            
            f.write("ASOCIACIONES REALIZADAS:\n")
            f.write("-" * 40 + "\n")
            for assoc in associations:
                f.write(f"Código: {assoc['codigo_guia']}\n")
                f.write(f"Imagen: {assoc['image_path']}\n")
                f.write(f"Tipo: {assoc['image_type']}\n")
                f.write(f"Tamaño: {assoc['size']:,} bytes\n")
                f.write(f"Modificado: {assoc['modified']}\n")
                f.write("-" * 40 + "\n")
        
        logger.info(f"📄 Reporte guardado en: {report_file}")
        return report
    
    def run_recovery(self):
        """Ejecutar el proceso completo de recuperación de imágenes"""
        logger.info("🚀 INICIANDO RECUPERACIÓN DE IMÁGENES DE TIQUETES")
        logger.info("=" * 60)
        
        try:
            # 1. Escanear imágenes
            images_catalog = self.scan_images()
            
            # 2. Asociar con guías
            associations = self.associate_images_with_guides(images_catalog)
            
            # 3. Actualizar base de datos
            if associations:
                self.update_database_with_images(associations)
            else:
                logger.warning("⚠️  No se encontraron asociaciones para actualizar")
            
            # 4. Generar reporte
            report = self.generate_report(associations)
            
            logger.info("=" * 60)
            logger.info("🎉 RECUPERACIÓN COMPLETADA")
            logger.info(f"✅ {self.images_associated} imágenes asociadas exitosamente")
            logger.info(f"💾 {self.db_updates} registros actualizados en la base de datos")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error durante la recuperación: {e}")
            raise e

def main():
    recovery = TiqueteImageRecovery()
    report = recovery.run_recovery()
    
    print("\n" + "="*60)
    print("🎯 RESUMEN FINAL:")
    print(f"📸 Imágenes encontradas: {report['summary']['images_found']}")
    print(f"🔗 Imágenes asociadas: {report['summary']['images_associated']}")
    print(f"💾 Registros actualizados: {report['summary']['db_updates']}")
    print(f"📊 Tasa de éxito: {report['summary']['success_rate']:.1f}%")
    print("="*60)

if __name__ == "__main__":
    main() 