# 🚀 Guía de Despliegue en PythonAnywhere

## Oleoflores Smart Flow - Despliegue a Producción

Esta guía te llevará paso a paso para desplegar la aplicación **Oleoflores Smart Flow** en PythonAnywhere.

---

## 📋 Prerrequisitos

### 1. Cuenta de PythonAnywhere
- Cuenta activa en [PythonAnywhere](https://www.pythonanywhere.com)
- Plan recomendado: **Hacker** o superior (para aplicaciones web)

### 2. Credenciales Necesarias
- **FLASK_SECRET_KEY**: Clave secreta única para la aplicación
- **OPENAI_API_KEY**: Clave API de OpenAI (para OCR inteligente)
- **ROBOFLOW_API_KEY**: Clave API de Roboflow (para clasificación automática)

---

## 🔧 Paso 1: Preparación Local

### 1.1 Generar Clave Secreta
En tu terminal local, ejecuta:
```bash
python -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"
```
Guarda esta clave, la necesitarás más tarde.

### 1.2 Actualizar wsgi.py
Edita el archivo `wsgi.py` y cambia:
```python
PYTHONANYWHERE_USERNAME = 'YOURUSERNAME'  # Cambia por tu usuario real
```

---

## 📤 Paso 2: Subir Código a PythonAnywhere

### 2.1 Opción A: Usando Git (Recomendado)
En una consola Bash de PythonAnywhere:
```bash
cd ~
git clone https://github.com/tu-usuario/oleoflores-smart-flow.git
cd oleoflores-smart-flow
```

### 2.2 Opción B: Usando Files Tab
1. Ve a la pestaña **Files** en PythonAnywhere
2. Sube todos los archivos del proyecto a `/home/tuusuario/oleoflores-smart-flow/`

---

## 🐍 Paso 3: Configurar Entorno Virtual

### 3.1 Crear Virtual Environment
En una consola Bash:
```bash
cd ~/oleoflores-smart-flow
mkvirtualenv --python=/usr/bin/python3.10 oleoflores-venv
```

### 3.2 Activar e Instalar Dependencias
```bash
workon oleoflores-venv
pip install -r requirements_pythonanywhere.txt
```

### 3.3 Resolver Posibles Errores

**Si OpenCV falla:**
```bash
pip install opencv-python-headless --no-cache-dir --force-reinstall
```

**Si EasyOCR tiene problemas:**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install easyocr --no-deps
```

---

## ⚙️ Paso 4: Configurar Variables de Entorno

### 4.1 Crear archivo .env
En el directorio del proyecto (`~/oleoflores-smart-flow/`):
```bash
nano .env
```

### 4.2 Contenido del archivo .env
```bash
# CONFIGURACIÓN BÁSICA
FLASK_SECRET_KEY=tu-clave-secreta-generada-anteriormente
FLASK_ENV=production
FLASK_DEBUG=False

# APIs DE IA
OPENAI_API_KEY=sk-tu-clave-openai-aqui
ROBOFLOW_API_KEY=tu-clave-roboflow-aqui
ROBOFLOW_WORKSPACE=tu-workspace-roboflow
ROBOFLOW_PROJECT=clasificacion-racimos
ROBOFLOW_VERSION=1

# CONFIGURACIÓN DE OCR
OCR_ENGINE=easyocr
OCR_LANGUAGES=es,en
OCR_GPU=false

# BASE DE DATOS
DATABASE_URL=sqlite:///instance/oleoflores_prod.db
TIQUETES_DB_PATH=instance/oleoflores_prod.db

# CONFIGURACIÓN REGIONAL
TIMEZONE=America/Bogota

# SEGURIDAD
VERIFY_SSL=true
```

---

## 🌐 Paso 5: Configurar Web App

### 5.1 Crear Web App
1. Ve a la pestaña **Web** en tu dashboard
2. Haz clic en **"Add a new web app"**
3. Selecciona tu dominio: `tuusuario.pythonanywhere.com`
4. Elige **"Manual configuration"**
5. Selecciona **Python 3.10**

### 5.2 Configurar Archivos

**Source code:**
```
/home/tuusuario/oleoflores-smart-flow
```

**Working directory:**
```
/home/tuusuario/oleoflores-smart-flow
```

**WSGI configuration file:**
Edita el archivo WSGI generado y reemplaza todo el contenido con:
```python
# Importar nuestro archivo wsgi.py personalizado
import sys
import os

# Ruta al proyecto
project_home = '/home/tuusuario/oleoflores-smart-flow'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Importar la aplicación desde nuestro wsgi.py
from wsgi import application
```

**Virtualenv:**
```
/home/tuusuario/.virtualenvs/oleoflores-venv
```

### 5.3 Configurar Archivos Estáticos

Agregar mapping de archivos estáticos:

**URL:** `/static/`  
**Directory:** `/home/tuusuario/oleoflores-smart-flow/app/static/`

---

## 📁 Paso 6: Configurar Permisos y Directorios

### 6.1 Crear Directorios Necesarios
```bash
cd ~/oleoflores-smart-flow
mkdir -p instance logs
mkdir -p app/static/uploads app/static/generated
mkdir -p app/static/generated/pdfs app/static/generated/qr
mkdir -p app/static/generated/guias app/static/generated/excels
mkdir -p app/static/temp
```

### 6.2 Configurar Permisos
```bash
chmod 755 instance logs
chmod 755 app/static/uploads
chmod 755 app/static/generated -R
chmod 755 app/static/temp
```

---

## 🚀 Paso 7: Inicializar Base de Datos

### 7.1 Ejecutar Inicialización
En una consola Python:
```bash
cd ~/oleoflores-smart-flow
workon oleoflores-venv
python -c "
from app import create_app
from config.config import PythonAnywhereConfig
app = create_app(PythonAnywhereConfig)
with app.app_context():
    print('Base de datos inicializada correctamente')
"
```

---

## ✅ Paso 8: Probar y Lanzar

### 8.1 Recargar Web App
1. Ve a la pestaña **Web**
2. Haz clic en **"Reload tuusuario.pythonanywhere.com"**

### 8.2 Verificar Funcionamiento
1. Visita `https://tuusuario.pythonanywhere.com`
2. Deberías ver la página principal de Oleoflores Smart Flow

### 8.3 Verificar Logs
```bash
tail -f ~/oleoflores-smart-flow/logs/oleoflores.log
```

---

## 🔧 Paso 9: Configuración Adicional (Opcional)

### 9.1 Dominio Personalizado
Si tienes un dominio propio:
1. Ve a **Web** → **"Set up a custom domain"**
2. Sigue las instrucciones para configurar DNS

### 9.2 HTTPS/SSL
- PythonAnywhere incluye HTTPS automáticamente
- No se requiere configuración adicional

### 9.3 Backup de Base de Datos
```bash
# Crear script de backup
nano ~/backup_db.sh
```

Contenido del script:
```bash
#!/bin/bash
cd ~/oleoflores-smart-flow
cp instance/oleoflores_prod.db backups/oleoflores_prod_$(date +%Y%m%d_%H%M%S).db
```

---

## 🚨 Solución de Problemas Comunes

### Error 1: "No module named 'app'"
**Solución:** Verificar que el working directory y source code estén correctamente configurados.

### Error 2: "ImportError: cannot import name 'PythonAnywhereConfig'"
**Solución:** Asegurar que `config/config.py` contenga la clase `PythonAnywhereConfig`.

### Error 3: Archivos estáticos no cargan
**Solución:** Verificar configuración de Static files mapping.

### Error 4: Base de datos bloqueada
**Solución:** 
```bash
rm instance/oleoflores_prod.db
# Volver a inicializar la base de datos
```

### Error 5: OCR no funciona
**Solución:**
```bash
workon oleoflores-venv
pip install easyocr --force-reinstall --no-cache-dir
```

---

## 📊 Monitoreo y Mantenimiento

### Logs de Aplicación
```bash
tail -f ~/oleoflores-smart-flow/logs/oleoflores.log
```

### Logs de Error del Servidor
```bash
tail -f /var/log/tuusuario.pythonanywhere.com.error.log
```

### Reiniciar Aplicación
- Desde Web tab: **"Reload tuusuario.pythonanywhere.com"**
- O desde consola: `touch /var/www/tuusuario_pythonanywhere_com_wsgi.py`

---

## 🎉 ¡Listo!

Tu aplicación **Oleoflores Smart Flow** ya está ejecutándose en producción en PythonAnywhere.

**URL de acceso:** `https://tuusuario.pythonanywhere.com`

### Próximos Pasos Recomendados:
1. Configurar monitoreo de logs
2. Realizar backup regular de la base de datos
3. Configurar dominio personalizado si es necesario
4. Optimizar rendimiento según uso real

---

## 📞 Soporte

Si encuentras problemas durante el despliegue:

1. **Revisar logs:** Siempre el primer paso
2. **Consola PythonAnywhere:** Para debug interactivo
3. **PythonAnywhere Help:** Documentación oficial
4. **Contactar soporte:** Si es problema de la plataforma

¡Tu aplicación ya está lista para producción! 🚀 