# Configuración de Google Sheets para Validación de Proveedores

## 🎯 Descripción

Este documento explica cómo configurar la validación directa con Google Sheets para reemplazar el workflow lento de n8n con una búsqueda instantánea en la hoja de cálculo.

## ✅ Beneficios

- **⚡ Velocidad**: Validación en 1-2 segundos vs 30+ segundos con n8n
- **🔍 Búsqueda directa**: Sin intermediarios, acceso directo a los datos
- **🛡️ Fallback robusto**: Si Google Sheets falla, usa automáticamente el webhook de n8n
- **📊 Flexibilidad**: Funciona con cualquier estructura de hoja de cálculo

## 🚀 Configuración Paso a Paso

### 1. Configurar Service Account de Google

1. **Ir a Google Cloud Console**: https://console.cloud.google.com/
2. **Crear o seleccionar proyecto**
3. **Habilitar Google Sheets API**:
   - Ir a "APIs y servicios" → "Biblioteca"
   - Buscar "Google Sheets API"
   - Hacer clic en "Habilitar"

4. **Crear Service Account**:
   - Ir a "APIs y servicios" → "Credenciales"
   - Hacer clic en "Crear credenciales" → "Cuenta de servicio"
   - Nombre: `oleoflores-sheets-reader`
   - Descripción: `Servicio para leer datos de proveedores`

5. **Generar credenciales JSON**:
   - Hacer clic en la cuenta de servicio creada
   - Ir a "Claves" → "Agregar clave" → "Crear nueva clave"
   - Seleccionar "JSON"
   - Descargar el archivo JSON

### 2. Compartir la Hoja de Cálculo

1. **Abrir tu hoja de proveedores en Google Sheets**
2. **Hacer clic en "Compartir"**
3. **Agregar el email del Service Account**:
   - Email: `oleoflores-sheets-reader@tu-proyecto.iam.gserviceaccount.com`
   - Permisos: "Lector" (solo lectura)

### 3. Configurar Variables de Entorno

Agregar al archivo `.env`:

```bash
# ===========================================
# GOOGLE SHEETS VALIDATION SERVICE
# ===========================================

# ID de la hoja de cálculo (desde la URL)
# https://docs.google.com/spreadsheets/d/1ABC123DEF456/edit
# ID: 1ABC123DEF456
GOOGLE_SPREADSHEET_ID=1ABC123DEF456

# Rango de datos en la hoja
GOOGLE_SHEETS_RANGE=Hoja1!A:Z

# Método 1: Archivo de credenciales (desarrollo)
GOOGLE_CREDENTIALS_PATH=path/to/credentials.json

# Método 2: JSON como variable (producción)
# GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}

# Webhook fallback (mantener el actual)
REVALIDATION_WEBHOOK_URL=https://primary-production-6eccf.up.railway.app/webhook/e42ff176-7d0a-4be2-b721-ac3f92795b01
```

### 4. Instalar Dependencias

```bash
pip install google-api-python-client google-auth
```

## 📋 Estructura Requerida de la Hoja

El sistema es **flexible** y detecta automáticamente las columnas. Funciona con cualquiera de estos nombres:

### Columna de Código (requerida)
- `codigo`, `código`, `code`, `id`

### Columna de Nombre (requerida)  
- `nombre`, `name`, `proveedor`, `agricultor`

### Ejemplo de estructura válida:

| codigo | nombre | telefono | direccion |
|--------|--------|----------|-----------|
| 0150076A | Inversiones Salas | 123456789 | Calle 123 |
| 0105007A | Ricardo Flores | 987654321 | Carrera 456 |

O también:

| ID | Agricultor | Email | Observaciones |
|----|------------|-------|---------------|
| 0150076A | Juan Pérez | juan@email.com | Activo |
| 0105007A | María González | maria@email.com | Nuevo |

## 🔄 Flujo de Validación

1. **Usuario edita datos en review** → Envía formulario
2. **Sistema intenta Google Sheets** → Búsqueda directa (1-2 segundos)
3. **Si encuentra el código** → Retorna nombre y validación exitosa
4. **Si Google Sheets falla** → Automáticamente usa webhook n8n
5. **Si webhook falla** → Usa datos editados por usuario

## 🔍 Logs del Sistema

El sistema genera logs detallados para debugging:

```
🔍 Validación Google Sheets disponible: True
📡 Webhook fallback disponible: True
🎯 Validando código de proveedor: 0150076A
🔍 Buscando código '0150076A' en Google Sheets...
✅ Código encontrado en fila 2
✅ Validación exitosa con google_sheets
```

## ⚠️ Troubleshooting

### Error: "Google Sheets no disponible"
- Verificar que `GOOGLE_SPREADSHEET_ID` esté configurado
- Verificar que las credenciales JSON sean válidas
- Verificar que las bibliotecas estén instaladas

### Error: "Código no encontrado"  
- Verificar que el código existe en la hoja
- Verificar que la columna de código tenga un nombre reconocible
- Revisar el rango configurado en `GOOGLE_SHEETS_RANGE`

### Error: "Permission denied"
- Verificar que el Service Account tenga acceso a la hoja
- Verificar que el email del Service Account esté en los permisos

### El sistema usa webhook en lugar de Google Sheets
- Verificar logs del sistema
- Verificar conexión a internet
- Verificar que las credenciales no hayan expirado

## 🧪 Probar la Configuración

Puedes probar la configuración manualmente:

```python
from app.utils.provider_validation_service import provider_validation_service

# Probar validación
result = provider_validation_service.validate_provider_code("0150076A")
print(result)

# Salida esperada:
# {
#   'success': True,
#   'data': {'codigo': '0150076A', 'nombre_agricultor': 'Nombre del proveedor'},
#   'method': 'google_sheets',
#   'mensaje': 'Código 0150076A validado exitosamente'
# }
```

## 📈 Monitoreo y Métricas

El sistema reporta el método usado en cada validación:

- `google_sheets` - Validación directa (rápida)
- `webhook_fallback` - Usó webhook n8n (lenta)

Esto permite monitorear la efectividad de cada método.

---

## 🎉 Resultado Final

Una vez configurado correctamente:

- **Validación instantánea** en 1-2 segundos
- **Búsqueda directa** en tu hoja de proveedores
- **Fallback automático** al webhook si hay problemas
- **Sin cambios** en la interfaz de usuario
- **100% compatible** con el flujo existente 