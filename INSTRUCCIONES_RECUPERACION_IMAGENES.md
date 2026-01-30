# 🖼️ RECUPERACIÓN DE IMÁGENES DEL SERVIDOR DE PRODUCCIÓN

## 📋 **PASO A PASO COMPLETO**

### **🔧 PASO 1: Acceder al servidor de PythonAnywhere**

```bash
# Conectar al servidor
ssh tu_usuario@ssh.pythonanywhere.com

# O usar la consola web de PythonAnywhere
```

### **🔍 PASO 2: Localizar directorio de imágenes**

```bash
# Buscar directorios con imágenes
find /home/tu_usuario -name "*.jpg" -o -name "*.png" | head -20

# Directorios típicos a revisar:
ls -la /home/tu_usuario/mysite/static/
ls -la /home/tu_usuario/mysite/static/uploads/
ls -la /home/tu_usuario/mysite/static/fotos_pesaje_neto/
ls -la /home/tu_usuario/mysite/static/clasificaciones/
```

### **📦 PASO 3: Comprimir imágenes**

```bash
# Ir al directorio de tu aplicación
cd /home/tu_usuario/mysite

# Crear archivo comprimido con todas las imágenes
tar -czf imagenes_produccion_backup.tar.gz \
    static/uploads/ \
    static/fotos_pesaje_neto/ \
    static/clasificaciones/ \
    static/images/ \
    --exclude="*.log" \
    --exclude="*.tmp"

# Verificar el tamaño del archivo
ls -lh imagenes_produccion_backup.tar.gz
```

### **⬇️ PASO 4: Descargar al sistema local**

#### **Opción A: SCP (recomendado)**
```bash
# Desde tu Mac/local, ejecutar:
scp tu_usuario@ssh.pythonanywhere.com:/home/tu_usuario/mysite/imagenes_produccion_backup.tar.gz ./
```

#### **Opción B: Panel web de PythonAnywhere**
1. Ve a **Files** en tu panel de PythonAnywhere
2. Busca `imagenes_produccion_backup.tar.gz`
3. Click derecho → **Download**

#### **Opción C: Dropbox/Google Drive**
```bash
# En el servidor, mover a carpeta compartida
cp imagenes_produccion_backup.tar.gz /home/tu_usuario/Dropbox/
```

### **📂 PASO 5: Extraer imágenes localmente**

```bash
# En tu directorio del proyecto
cd /Users/enriquepabon/Library/CloudStorage/GoogleDrive-epabon@oleoflores.com/My\ Drive/Proyectos\ automatizaciones/Proyecto\ automatización\ registro\ MLB/oleoflores-smart-flow/

# Crear directorio para imágenes de producción
mkdir -p production_images

# Extraer archivo
tar -xzf imagenes_produccion_backup.tar.gz -C production_images/

# Verificar contenido
find production_images/ -name "*.jpg" -o -name "*.png" | wc -l
```

### **🚀 PASO 6: Ejecutar script de recuperación**

```bash
# Ejecutar script con configuración predeterminada
python3 migrations/recover_production_images.py

# O con rutas personalizadas
python3 migrations/recover_production_images.py \
    --production-path production_images/ \
    --db-path instance/oleoflores_dev.db \
    --static-path app/static/
```

### **📊 PASO 7: Revisar resultados**

```bash
# Ver reporte generado
cat production_image_recovery_report_*.txt

# Verificar imágenes copiadas
ls -la app/static/uploads/ | grep tiquete | wc -l
ls -la app/static/fotos_pesaje_neto/ | wc -l
ls -la app/static/clasificaciones/ | wc -l
```

---

## 🔧 **OPCIONES AVANZADAS**

### **Si las imágenes tienen estructura diferente:**

```bash
# Explorar estructura de archivos
find production_images/ -type f -name "*.jpg" | head -20
find production_images/ -type f -name "*.png" | head -20

# Ver patrones de nombres
ls production_images/static/uploads/ | head -20
```

### **Si hay muchas imágenes (>1000):**

```bash
# Ejecutar con logging detallado
python3 migrations/recover_production_images.py --production-path production_images/ 2>&1 | tee recovery.log

# Verificar progreso
tail -f recovery.log
```

### **Para probar con una muestra pequeña:**

```bash
# Crear directorio de prueba
mkdir production_images_test
cp -r production_images/static/uploads/* production_images_test/ | head -50

# Ejecutar prueba
python3 migrations/recover_production_images.py --production-path production_images_test/
```

---

## 📋 **CHECKLIST DE VERIFICACIÓN**

- [ ] ✅ Acceso al servidor de PythonAnywhere
- [ ] 📁 Localizado directorio de imágenes
- [ ] 📦 Creado archivo comprimido
- [ ] ⬇️ Descargado archivo localmente
- [ ] 📂 Extraído en `production_images/`
- [ ] 🚀 Ejecutado script de recuperación
- [ ] 📊 Revisado reporte de resultados
- [ ] 🖼️ Verificado imágenes en aplicación

---

## 🆘 **SOLUCIÓN DE PROBLEMAS**

### **Problema: "No se encontraron imágenes"**
```bash
# Verificar estructura
find production_images/ -name "*.jpg" -o -name "*.png" | head -10
```

### **Problema: "Pocos códigos de guía reconocidos"**
```bash
# Ver nombres de archivos para ajustar patrones
ls production_images/static/uploads/ | head -20
```

### **Problema: "Base de datos bloqueada"**
```bash
# Detener aplicación Flask
pkill -f "python.*run.py"

# Ejecutar script nuevamente
python3 migrations/recover_production_images.py
```

---

## 📞 **¿NECESITAS AYUDA?**

1. **Comparte ejemplos** de nombres de archivos del servidor
2. **Indica la estructura** de directorios encontrada
3. **Menciona errores específicos** que encuentres

**El script está diseñado para ser robusto y manejar múltiples formatos automáticamente.** 