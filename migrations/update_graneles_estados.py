#!/usr/bin/env python3
"""
Migración para actualizar estados del flujo de graneles
Actualiza los estados existentes a los nuevos nombres especificados por el usuario
"""

import sqlite3
import os
import sys
from datetime import datetime

def get_database_path():
    """Obtener la ruta correcta de la base de datos"""
    # Primero intentar leer desde config
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from config.config import Config
        return Config.TIQUETES_DB_PATH
    except Exception as e:
        print(f"⚠️  No se pudo leer configuración: {e}")
        # Fallback a ubicación esperada
        instance_path = os.path.join(os.path.dirname(__file__), '..', 'instance')
        return os.path.join(instance_path, 'oleoflores_dev.db')

def migrate_estados():
    """Actualizar estados existentes a los nuevos nombres"""
    
    # Mapeo de estados antiguos → nuevos
    mapeo_estados = {
        'porteria': 'registrado',
        'pendiente_guarda': 'inspeccion_seguridad', 
        'inspeccion_parcial': 'inspeccion_calidad',
        'pesado_tara': 'pesado_tara',  # Sin cambio
        'cargando': 'en_cargue',
        'cargado': 'listo_pesaje_neto',
        'pesado_bruto': 'pesado_neto',
        'sellado': 'instalacion_sellos',
        'documentado': 'documentado',  # Temporal - será 'instalacion_sellos' cuando llegue a ese punto
        'completado': 'validacion_salida',
        'retenido_discrepancia': 'retenido_discrepancia'  # Sin cambio
    }
    
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada en: {db_path}")
        return False
    
    print(f"🔄 Actualizando estados en: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar que existe la tabla y la columna
        cursor.execute("PRAGMA table_info(RegistroEntradaGraneles)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'estado_registro' not in columns:
            print("❌ La columna 'estado_registro' no existe en la tabla")
            return False
        
        # Obtener conteo actual de estados
        cursor.execute("SELECT estado_registro, COUNT(*) FROM RegistroEntradaGraneles GROUP BY estado_registro")
        estados_actuales = cursor.fetchall()
        
        print("\n📊 Estados actuales:")
        for estado, count in estados_actuales:
            nuevo_estado = mapeo_estados.get(estado, estado)
            print(f"   {estado} ({count}) → {nuevo_estado}")
        
        # Actualizar cada estado
        total_actualizados = 0
        for estado_antiguo, estado_nuevo in mapeo_estados.items():
            if estado_antiguo != estado_nuevo:  # Solo actualizar si cambió
                cursor.execute("""
                    UPDATE RegistroEntradaGraneles 
                    SET estado_registro = ? 
                    WHERE estado_registro = ?
                """, (estado_nuevo, estado_antiguo))
                
                actualizados = cursor.rowcount
                if actualizados > 0:
                    total_actualizados += actualizados
                    print(f"✅ Actualizados {actualizados} registros: '{estado_antiguo}' → '{estado_nuevo}'")
        
        # Verificar estados finales
        cursor.execute("SELECT estado_registro, COUNT(*) FROM RegistroEntradaGraneles GROUP BY estado_registro")
        estados_finales = cursor.fetchall()
        
        print(f"\n📊 Estados después de migración:")
        for estado, count in estados_finales:
            print(f"   {estado}: {count} registros")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Migración completada exitosamente!")
        print(f"📈 Total registros actualizados: {total_actualizados}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando migración de estados de graneles...")
    print("=" * 60)
    
    if migrate_estados():
        print("\n🎉 ¡Migración completada con éxito!")
        print("Los estados del flujo de graneles han sido actualizados según la nueva especificación:")
        print("1. registrado - Vehículo Registrado")
        print("2. inspeccion_seguridad - Inspección de seguridad (Guarda)")
        print("3. inspeccion_calidad - Inspección de calidad (Inspector)")
        print("4. pesado_tara - Vehículo con pesaje tara (Basculero)")
        print("5. en_cargue - Vehículo en cargue (Operador de carga)")
        print("6. pesado_neto - Vehículo en pesaje neto (Basculero)")
        print("7. instalacion_sellos - Instalación de sellos (Inspector)")
        print("8. validacion_salida - Validación de salida (Guarda)")
    else:
        print("\n💥 La migración falló. Revisa los errores arriba.")
        sys.exit(1)