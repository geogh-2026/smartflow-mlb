# 🔄 Migración de Base de Datos de Producción

Esta guía te ayudará a migrar todos los datos de tu base de datos de producción a la nueva estructura de desarrollo, incluyendo usuarios, contraseñas y todos los datos operativos.

## 📋 Scripts Disponibles

### 1. `migrate_production_to_dev.py` - Script Principal de Migración
- **Función**: Migrar todos los datos de producción a desarrollo
- **Formatos soportados**: SQLite, SQL Dump, JSON, CSV
- **Características**: Backup automático, dry-run, logging detallado

### 2. `validate_migration.py` - Validador Post-Migración  
- **Función**: Verificar que la migración se realizó correctamente
- **Validaciones**: Conteos, integridad referencial, usuarios, datos críticos

## 🚀 Proceso de Migración Paso a Paso

### Paso 1: Preparar el Backup de Producción

```bash
# Si tu backup es un archivo SQLite
cp /ruta/produccion/database.db ./backup_produccion.db

# Si es un SQL dump
# Asegúrate de tener el archivo .sql exportado de producción
```

### Paso 2: Ejecutar Migración en Modo Prueba (Dry-Run)

```bash
# Primero ejecuta en modo dry-run para ver qué se migrará
python migrations/migrate_production_to_dev.py \
    --source backup_produccion.db \
    --dry-run \
    --verbose
```

### Paso 3: Ejecutar Migración Real

```bash
# Si el dry-run se ve correcto, ejecuta la migración real
python migrations/migrate_production_to_dev.py \
    --source backup_produccion.db \
    --verbose
```

### Paso 4: Validar la Migración

```bash
# Validar que todo se migró correctamente
python migrations/validate_migration.py \
    --source backup_produccion.db \
    --target instance/oleoflores_dev.db \
    --verbose
```

## 📊 Datos que se Migran

### ✅ Sistema de Fruta
- **entry_records**: Registros de entrada de fruta
- **pesajes_bruto**: Pesajes brutos de vehículos
- **clasificaciones**: Clasificaciones manuales y automáticas
- **pesajes_neto**: Pesajes netos finales
- **salidas**: Registros de salida
- **fotos_clasificacion**: Fotos de clasificación

### ✅ Usuarios y Autenticación
- **users**: Usuarios con contraseñas hasheadas preservadas
- **Roles**: Admin, Usuario Guarda, Inspector, etc.
- **Permisos**: Configuraciones de acceso

### ✅ Sistema de Graneles
- **RegistroEntradaGraneles**: Registros de graneles
- **PrimerPesajeGranel**: Pesajes iniciales
- **ControlCalidadGranel**: Control de calidad
- **InspeccionVehiculo**: Inspecciones vehiculares

### ✅ Sistema de Sellos
- **tipos_sello**: Tipos de sellos disponibles
- **maestro_vehiculos**: Configuración de vehículos
- **solicitudes_sello**: Solicitudes de sellos
- **sellos**: Sellos individuales y estados
- **movimientos_sello**: Historial de movimientos

### ✅ Datos de Referencia
- **presupuesto_mensual**: Presupuestos mensuales
- **validaciones_diarias_sap**: Validaciones SAP

## 🛡️ Características de Seguridad

### Backup Automático
- Se crea un backup de la DB actual antes de migrar
- Formato: `oleoflores_dev.db.backup_YYYYMMDD_HHMMSS`

### Preservación de Contraseñas
- Las contraseñas hasheadas se mantienen intactas
- Si encuentran contraseñas en texto plano, se hashean automáticamente
- Compatible con sistema de autenticación Flask-Login

### Manejo de Duplicados
- Si un registro ya existe, se actualiza en lugar de fallar
- Se mantiene la integridad de llaves primarias
- Logging detallado de inserciones vs actualizaciones

## 📝 Ejemplos de Uso

### Migración desde SQLite
```bash
python migrations/migrate_production_to_dev.py --source produccion.db
```

### Migración desde SQL Dump
```bash
python migrations/migrate_production_to_dev.py --source backup.sql --format sql
```

### Migración desde JSON Export
```bash
python migrations/migrate_production_to_dev.py --source data_export.json --format json
```

### Migración desde CSVs
```bash
# Directorio con archivos CSV por tabla
python migrations/migrate_production_to_dev.py --source csv_data/ --format csv
```

## 🔍 Interpretación de Logs

### ✅ Éxito
```
✅ users: 5 insertados, 0 actualizados
✅ entry_records: 127 insertados, 3 actualizados
```

### ⚠️ Advertencias
```
⚠️ Tabla backup_logs no mapeada, omitiendo
⚠️ Usuario admin sin email, usando default
```

### ❌ Errores
```
❌ Error insertando en users: UNIQUE constraint failed
❌ Campo requerido 'codigo_guia' faltante en entry_records
```

## 🎯 Validaciones Post-Migración

El script de validación verifica:

1. **Conteos de Registros**: Mismo número de registros entre origen y destino
2. **Integridad de Usuarios**: Usuarios activos, admins, contraseñas válidas
3. **Integridad Referencial**: Relaciones entre tablas correctas
4. **Datos Críticos**: Códigos de guía válidos, campos obligatorios

### Reporte de Validación
```
📊 REPORTE DE VALIDACIÓN DE MIGRACIÓN
=====================================
✅ Validaciones exitosas: 28
❌ Validaciones fallidas: 0
⚠️  Advertencias: 2
📈 Tasa de éxito: 93.3%
🎉 VALIDACIÓN EXITOSA: La migración se completó correctamente
```

## 🚨 Solución de Problemas

### Problema: "Table not found"
**Causa**: La tabla no existe en la DB destino
**Solución**: Ejecutar migraciones de esquema primero
```bash
python migrations/create_tables.py
```

### Problema: "UNIQUE constraint failed"
**Causa**: Registros duplicados en la migración
**Solución**: El script maneja esto automáticamente con UPDATE

### Problema: "Password hash invalid"
**Causa**: Contraseñas en texto plano
**Solución**: Se hashean automáticamente durante la migración

### Problema: "Referential integrity violation"
**Causa**: Registros huérfanos (ej: pesaje sin entry_record)
**Solución**: Revisar orden de migración y datos origen

## 🔧 Personalización

### Mapeo de Tablas Personalizado
Edita `table_mapping` en `migrate_production_to_dev.py`:

```python
self.table_mapping = {
    'tabla_produccion': 'tabla_desarrollo',
    'usuarios_old': 'users',
    # Añadir más mapeos...
}
```

### Transformaciones Personalizadas
Añadir lógica en `transform_user_data()` para campos específicos:

```python
def transform_custom_data(self, data: Dict, table_name: str) -> Dict:
    if table_name == 'mi_tabla':
        # Lógica personalizada aquí
        pass
    return data
```

## 📞 Soporte

Si encuentras problemas durante la migración:

1. **Revisa los logs** detallados generados
2. **Ejecuta en modo dry-run** primero
3. **Valida la estructura** de tu backup
4. **Verifica permisos** de archivos y directorios

Los logs se guardan automáticamente en `migration_YYYYMMDD_HHMMSS.log` 