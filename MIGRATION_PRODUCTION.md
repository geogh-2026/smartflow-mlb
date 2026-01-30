# Migración de Producción: tipo_insumo

## Problema
```
ERROR: table enturnamientos_graneles has no column named tipo_insumo
```

## Solución

### Opción 1: Script Automático
Ejecutar en el servidor de producción:
```bash
python3 fix_production_migration.py
```

### Opción 2: SQL Manual
Conectarse a la base de datos y ejecutar:

```sql
-- Crear backup primero
.backup backup_antes_migracion.db

-- Agregar columna
ALTER TABLE enturnamientos_graneles 
ADD COLUMN tipo_insumo TEXT DEFAULT 'Granel';

-- Actualizar registros existentes
UPDATE enturnamientos_graneles 
SET tipo_insumo = 'Granel' 
WHERE tipo_insumo IS NULL;

-- Verificar
PRAGMA table_info(enturnamientos_graneles);
SELECT COUNT(*) FROM enturnamientos_graneles WHERE tipo_insumo = 'Granel';
```

### Opción 3: Desde consola Python
```python
import sqlite3
conn = sqlite3.connect('ruta/a/tu/base_de_datos.db')
cursor = conn.cursor()

# Agregar columna
cursor.execute("ALTER TABLE enturnamientos_graneles ADD COLUMN tipo_insumo TEXT DEFAULT 'Granel'")

# Actualizar registros
cursor.execute("UPDATE enturnamientos_graneles SET tipo_insumo = 'Granel' WHERE tipo_insumo IS NULL")

conn.commit()
conn.close()
print("✅ Migración completada")
```

## Verificación
Después de aplicar la migración, verificar que no hay más errores:
1. Reiniciar la aplicación
2. Probar crear un enturnamiento
3. Verificar logs de error

## Rutas Posibles de BD en Producción
- `/home/enriquepabon/mysite/instance/oleoflores_prod.db`
- `/home/enriquepabon/mysite/tiquetes.db`
- `instance/oleoflores_prod.db`
- `tiquetes.db`

## Rollback (si es necesario)
Si algo sale mal, restaurar desde el backup:
```bash
cp backup_antes_migracion.db tu_base_de_datos.db
```
