#!/usr/bin/env python3
"""
Script avanzado para recuperar imágenes de tiquetes del servidor de producción.
Maneja múltiples formatos de nombres y estructuras de directorios.
"""

import sqlite3
import os
import re
import logging
import shutil
from pathlib import Path
from datetime import datetime
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionImageRecovery:
    def __init__(self, 
                 production_images_path="production_images/", 
                 db_path="instance/oleoflores_dev.db",
                 target_static_path="app/static/"):
        self.production_path = Path(production_images_path)
        self.db_path = db_path
        self.target_static = Path(target_static_path)
        
        # Directorios de destino
        self.target_uploads = self.target_static / "uploads"
        self.target_fotos_pesaje = self.target_static / "fotos_pesaje_neto"
        self.target_fotos_clasificacion = self.target_static / "clasificaciones"
        
        # Crear directorios si no existen
        self.target_uploads.mkdir(exist_ok=True)
        self.target_fotos_pesaje.mkdir(exist_ok=True)
        self.target_fotos_clasificacion.mkdir(exist_ok=True)
        
        # Contadores
        self.images_found = 0
        self.images_processed = 0
        self.images_associated = 0
        self.db_updates = 0
        
        # Patrones de reconocimiento avanzados
        self.codigo_guia_patterns = [
            # Formato completo: 0150294A_20250711155400
            r'(\d{7}[A-Z]_\d{14})',
            # Formato con fecha separada: 0150294A_20250711_155400
            r'(\d{7}[A-Z]_\d{8}_\d{6})',
            # Formato solo código: 0150294A
            r'(\d{7}[A-Z])',
            # Formato con prefijos: tiquete_0150294A, pesaje_0150294A, etc.
            r'(?:tiquete|pesaje|bascula|entrada|clasificacion)_(\d{7}[A-Z])',
            # Formato con GUID/UUID seguido de código
            r'[a-f0-9-]{36}_(\d{7}[A-Z])',
            # Formato inverso: 20250711_0150294A
            r'\d{8}_(\d{7}[A-Z])',
        ]
    
    def scan_production_directory(self):
        """Escanear recursivamente el directorio de producción"""
        logger.info(f"🔍 Escaneando directorio de producción: {self.production_path}")
        
        if not self.production_path.exists():
            logger.error(f"❌ Directorio de producción no encontrado: {self.production_path}")
            return []
        
        image_files = []
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        
        for root, dirs, files in os.walk(self.production_path):
            root_path = Path(root)
            for file in files:
                file_path = root_path / file
                if file_path.suffix.lower() in image_extensions:
                    image_files.append({
                        'path': file_path,
                        'relative_path': file_path.relative_to(self.production_path),
                        'filename': file_path.name,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                        'directory': root_path.name
                    })
                    self.images_found += 1
        
        logger.info(f"📊 Imágenes encontradas: {len(image_files)}")
        return image_files
    
    def extract_codigo_guia_advanced(self, filename, directory_name=""):
        """Extraer código de guía usando patrones avanzados"""
        # Combinar filename y directory para más contexto
        search_text = f"{directory_name}_{filename}"
        
        logger.debug(f"🔍 Analizando: {search_text}")
        
        for i, pattern in enumerate(self.codigo_guia_patterns):
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                codigo = match.group(1)
                logger.debug(f"✅ Patrón {i+1} encontrado: {codigo}")
                return codigo
        
        logger.debug(f"❌ No se encontró código en: {search_text}")
        return None
    
    def get_guias_from_database(self):
        """Obtener todas las guías de la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT codigo_guia FROM entry_records")
            guias = {row[0] for row in cursor.fetchall()}
            logger.info(f"📋 Guías en BD: {len(guias)}")
            return guias
        finally:
            conn.close()
    
    def find_best_match(self, codigo_extraido, guias_en_db):
        """Encontrar la mejor coincidencia para un código extraído"""
        if not codigo_extraido:
            return None
        
        # 1. Coincidencia exacta
        if codigo_extraido in guias_en_db:
            return codigo_extraido
        
        # 2. Si el código tiene timestamp, buscar por código base
        if '_' in codigo_extraido:
            codigo_base = codigo_extraido.split('_')[0]
            coincidencias = [g for g in guias_en_db if g.startswith(codigo_base + '_')]
            
            # Buscar coincidencia exacta con el timestamp
            if codigo_extraido in coincidencias:
                return codigo_extraido
                
            # Si no, devolver la primera coincidencia
            if coincidencias:
                return coincidencias[0]
        
        # 3. Buscar por código base solamente
        else:
            coincidencias = [g for g in guias_en_db if g.startswith(codigo_extraido + '_')]
            if coincidencias:
                return coincidencias[0]
        
        return None
    
    def categorize_image(self, image_info, codigo_guia):
        """Categorizar imagen según su tipo y directorio"""
        filename = image_info['filename'].lower()
        directory = image_info['directory'].lower()
        
        # Determinar tipo de imagen y directorio destino
        if 'pesaje' in filename or 'pesaje' in directory or 'bascula' in filename:
            if 'neto' in filename or 'neto' in directory:
                return 'pesaje_neto', self.target_fotos_pesaje
            else:
                return 'pesaje_bruto', self.target_uploads
        elif 'clasificacion' in filename or 'clasificacion' in directory:
            return 'clasificacion', self.target_fotos_clasificacion
        elif 'entrada' in filename or 'entrada' in directory:
            return 'entrada', self.target_uploads
        else:
            # Por defecto, imágenes generales van a uploads
            return 'general', self.target_uploads
    
    def copy_and_rename_image(self, image_info, codigo_guia, image_type):
        """Copiar imagen al directorio correcto con nombre estandarizado"""
        source_path = image_info['path']
        
        # Generar nombre de archivo estandarizado
        timestamp = image_info['modified'].strftime('%Y%m%d_%H%M%S')
        extension = source_path.suffix
        
        if image_type == 'pesaje_neto':
            new_filename = f"{codigo_guia}_pesaje_neto_{timestamp}{extension}"
            target_dir = self.target_fotos_pesaje
        elif image_type == 'clasificacion':
            new_filename = f"{codigo_guia}_clasificacion_{timestamp}{extension}"
            target_dir = self.target_fotos_clasificacion
        else:
            new_filename = f"tiquete_{codigo_guia}_{timestamp}{extension}"
            target_dir = self.target_uploads
        
        target_path = target_dir / new_filename
        
        # Evitar sobrescribir archivos existentes
        counter = 1
        while target_path.exists():
            name_part = target_path.stem
            ext_part = target_path.suffix
            target_path = target_dir / f"{name_part}_{counter}{ext_part}"
            counter += 1
        
        try:
            shutil.copy2(source_path, target_path)
            logger.debug(f"📋 Copiado: {source_path.name} → {target_path.name}")
            return target_path.relative_to(self.target_static)
        except Exception as e:
            logger.error(f"❌ Error copiando {source_path}: {e}")
            return None
    
    def update_database_references(self, associations):
        """Actualizar referencias de imágenes en la base de datos"""
        logger.info("💾 Actualizando referencias en la base de datos...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for assoc in associations:
                codigo_guia = assoc['codigo_guia']
                image_path = str(assoc['image_path'])
                image_type = assoc['image_type']
                
                # Actualizar entry_records
                if image_type in ['entrada', 'general']:
                    cursor.execute("""
                        UPDATE entry_records 
                        SET image_filename = ? 
                        WHERE codigo_guia = ?
                    """, (image_path, codigo_guia))
                
                # Actualizar pesajes_neto
                if image_type == 'pesaje_neto':
                    cursor.execute("""
                        UPDATE pesajes_neto 
                        SET imagen_soporte_sap = ? 
                        WHERE codigo_guia = ?
                    """, (image_path, codigo_guia))
                
                # Actualizar pesajes_bruto
                if image_type == 'pesaje_bruto':
                    cursor.execute("""
                        UPDATE pesajes_bruto 
                        SET imagen_pesaje = ? 
                        WHERE codigo_guia = ?
                    """, (image_path, codigo_guia))
                
                # Actualizar clasificaciones si existe la tabla
                if image_type == 'clasificacion':
                    try:
                        cursor.execute("""
                            UPDATE clasificaciones 
                            SET foto_soporte_manual = ? 
                            WHERE codigo_guia = ?
                        """, (image_path, codigo_guia))
                    except sqlite3.OperationalError:
                        # Tabla clasificaciones no existe o no tiene esa columna
                        pass
                
                if cursor.rowcount > 0:
                    self.db_updates += 1
                    logger.debug(f"📝 Actualizado {image_type}: {codigo_guia} → {image_path}")
            
            conn.commit()
            logger.info(f"✅ Base de datos actualizada: {self.db_updates} registros")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error actualizando BD: {e}")
            raise e
        finally:
            conn.close()
    
    def generate_detailed_report(self, associations):
        """Generar reporte detallado de la recuperación"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"production_image_recovery_report_{timestamp}.json"
        
        report_data = {
            'summary': {
                'timestamp': timestamp,
                'images_found': self.images_found,
                'images_processed': self.images_processed,
                'images_associated': self.images_associated,
                'db_updates': self.db_updates,
                'success_rate': (self.images_associated / self.images_found * 100) if self.images_found > 0 else 0
            },
            'associations': [
                {
                    'codigo_guia': assoc['codigo_guia'],
                    'original_filename': assoc['original_filename'],
                    'new_image_path': str(assoc['image_path']),
                    'image_type': assoc['image_type'],
                    'size_bytes': assoc['size'],
                    'modified_date': assoc['modified'].isoformat()
                }
                for assoc in associations
            ]
        }
        
        # Guardar reporte JSON
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # Generar reporte de texto legible
        text_report = f"production_image_recovery_report_{timestamp}.txt"
        with open(text_report, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("REPORTE DE RECUPERACIÓN DE IMÁGENES DE PRODUCCIÓN\n")
            f.write("=" * 70 + "\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("RESUMEN:\n")
            f.write(f"- Imágenes encontradas: {self.images_found}\n")
            f.write(f"- Imágenes procesadas: {self.images_processed}\n")
            f.write(f"- Imágenes asociadas: {self.images_associated}\n")
            f.write(f"- Registros BD actualizados: {self.db_updates}\n")
            f.write(f"- Tasa de éxito: {report_data['summary']['success_rate']:.1f}%\n\n")
            
            f.write("ASOCIACIONES DETALLADAS:\n")
            f.write("-" * 50 + "\n")
            for assoc in associations:
                f.write(f"Código: {assoc['codigo_guia']}\n")
                f.write(f"Original: {assoc['original_filename']}\n")
                f.write(f"Nueva ruta: {assoc['image_path']}\n")
                f.write(f"Tipo: {assoc['image_type']}\n")
                f.write(f"Tamaño: {assoc['size']:,} bytes\n")
                f.write(f"Modificado: {assoc['modified']}\n")
                f.write("-" * 50 + "\n")
        
        logger.info(f"📄 Reportes guardados: {report_file} y {text_report}")
        return report_data
    
    def run_production_recovery(self):
        """Ejecutar proceso completo de recuperación de imágenes de producción"""
        logger.info("🚀 INICIANDO RECUPERACIÓN DE IMÁGENES DE PRODUCCIÓN")
        logger.info("=" * 70)
        
        try:
            # 1. Escanear imágenes de producción
            image_files = self.scan_production_directory()
            if not image_files:
                logger.warning("⚠️  No se encontraron imágenes en el directorio de producción")
                return
            
            # 2. Obtener guías de la base de datos
            guias_en_db = self.get_guias_from_database()
            
            # 3. Procesar cada imagen
            associations = []
            for image_info in image_files:
                self.images_processed += 1
                
                # Extraer código de guía
                codigo_extraido = self.extract_codigo_guia_advanced(
                    image_info['filename'], 
                    image_info['directory']
                )
                
                if not codigo_extraido:
                    continue
                
                # Encontrar coincidencia en BD
                codigo_guia = self.find_best_match(codigo_extraido, guias_en_db)
                if not codigo_guia:
                    continue
                
                # Categorizar imagen
                image_type, target_dir = self.categorize_image(image_info, codigo_guia)
                
                # Copiar imagen al directorio correcto
                new_image_path = self.copy_and_rename_image(image_info, codigo_guia, image_type)
                if not new_image_path:
                    continue
                
                # Registrar asociación
                associations.append({
                    'codigo_guia': codigo_guia,
                    'original_filename': image_info['filename'],
                    'image_path': new_image_path,
                    'image_type': image_type,
                    'size': image_info['size'],
                    'modified': image_info['modified']
                })
                
                self.images_associated += 1
                logger.debug(f"✅ Asociado: {codigo_guia} ← {image_info['filename']}")
            
            # 4. Actualizar base de datos
            if associations:
                self.update_database_references(associations)
            
            # 5. Generar reporte
            report = self.generate_detailed_report(associations)
            
            logger.info("=" * 70)
            logger.info("🎉 RECUPERACIÓN DE PRODUCCIÓN COMPLETADA")
            logger.info(f"📸 Imágenes encontradas: {self.images_found}")
            logger.info(f"🔗 Imágenes asociadas: {self.images_associated}")
            logger.info(f"💾 Registros actualizados: {self.db_updates}")
            logger.info(f"📊 Tasa de éxito: {report['summary']['success_rate']:.1f}%")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Error durante la recuperación: {e}")
            raise e

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Recuperar imágenes de tiquetes del servidor de producción')
    parser.add_argument('--production-path', default='production_images/', 
                       help='Ruta al directorio de imágenes de producción')
    parser.add_argument('--db-path', default='instance/oleoflores_dev.db',
                       help='Ruta a la base de datos')
    parser.add_argument('--static-path', default='app/static/',
                       help='Ruta al directorio static de destino')
    
    args = parser.parse_args()
    
    recovery = ProductionImageRecovery(
        production_images_path=args.production_path,
        db_path=args.db_path,
        target_static_path=args.static_path
    )
    
    report = recovery.run_production_recovery()
    
    if report:
        print("\n" + "="*70)
        print("🎯 RESUMEN FINAL:")
        print(f"📸 Imágenes encontradas: {report['summary']['images_found']}")
        print(f"🔗 Imágenes asociadas: {report['summary']['images_associated']}")
        print(f"💾 Registros actualizados: {report['summary']['db_updates']}")
        print(f"📊 Tasa de éxito: {report['summary']['success_rate']:.1f}%")
        print("="*70)

if __name__ == "__main__":
    main() 