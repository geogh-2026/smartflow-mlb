# ✅ Checklist de Despliegue a Producción

## Oleoflores Smart Flow - Lista de Verificación PythonAnywhere

Usa esta lista para asegurar que todos los pasos estén completados antes del despliegue.

---

## 🎯 Pre-Despliegue (Local)

### Configuración del Proyecto
- [ ] **Archivo wsgi.py creado** - Punto de entrada WSGI para PythonAnywhere
- [ ] **USERNAME actualizado en wsgi.py** - Cambiar `YOURUSERNAME` por tu usuario real
- [ ] **Template .env creado** - `env_template_production.txt` disponible
- [ ] **Requirements específicos** - `requirements_pythonanywhere.txt` creado
- [ ] **Configuración PythonAnywhere** - Clase `PythonAnywhereConfig` implementada

### Verificaciones de Código
- [ ] **Script de verificación ejecutado** - `python check_pythonanywhere_config.py`
- [ ] **Todas las dependencias probadas** - Sin errores de importación
- [ ] **Aplicación Flask funcional** - Se puede crear sin errores
- [ ] **Variables de entorno configuradas** - Al menos FLASK_SECRET_KEY

### Documentación
- [ ] **Guía de despliegue disponible** - `deploy_pythonanywhere.md` creada
- [ ] **Este checklist completado** - Todas las tareas verificadas

---

## 🌐 Configuración PythonAnywhere

### Cuenta y Plan
- [ ] **Cuenta PythonAnywhere activa** - Con plan que soporte web apps
- [ ] **Dominio disponible** - `tuusuario.pythonanywhere.com`
- [ ] **Límites de plan verificados** - CPU, storage, etc.

### Subida de Código
- [ ] **Código subido a PythonAnywhere** - Vía Git o Files tab
- [ ] **Estructura de directorios correcta** - Todos los archivos en su lugar
- [ ] **Permisos de archivos configurados** - Lectura/escritura donde sea necesario

---

## 🐍 Entorno Python

### Virtual Environment
- [ ] **Virtualenv creado** - `mkvirtualenv oleoflores-venv`
- [ ] **Python 3.10 seleccionado** - Versión correcta
- [ ] **Virtualenv activado** - `workon oleoflores-venv`

### Dependencias
- [ ] **Requirements instalados** - `pip install -r requirements_pythonanywhere.txt`
- [ ] **OpenCV funcional** - opencv-python-headless instalado
- [ ] **EasyOCR funcional** - Sin errores de GPU
- [ ] **LangChain disponible** - Versiones compatibles
- [ ] **Flask y extensiones** - Todas las dependencias core

---

## ⚙️ Variables de Entorno

### Archivo .env
- [ ] **Archivo .env creado** - En directorio raíz del proyecto
- [ ] **FLASK_SECRET_KEY generada** - Clave de 32+ caracteres
- [ ] **FLASK_ENV=production** - Configurado para producción
- [ ] **FLASK_DEBUG=False** - Debug desactivado

### APIs Externas
- [ ] **OPENAI_API_KEY configurada** - Para funcionalidad OCR inteligente
- [ ] **ROBOFLOW_API_KEY configurada** - Para clasificación automática
- [ ] **API Keys válidas** - Probadas y funcionales

### Configuración Regional
- [ ] **TIMEZONE configurada** - America/Bogota
- [ ] **OCR_LANGUAGES configurada** - es,en
- [ ] **OCR_GPU=false** - Para servidores sin GPU

---

## 🌐 Configuración Web App

### Configuración Básica
- [ ] **Web app creada** - Desde dashboard PythonAnywhere
- [ ] **Manual configuration seleccionada** - No usar template automático
- [ ] **Python 3.10 seleccionado** - Versión correcta

### Rutas y Archivos
- [ ] **Source code configurado** - `/home/tuusuario/oleoflores-smart-flow`
- [ ] **Working directory configurado** - Misma ruta que source code
- [ ] **WSGI file configurado** - Apunta a nuestro wsgi.py personalizado
- [ ] **Virtualenv configurado** - Ruta al virtualenv creado

### Archivos Estáticos
- [ ] **Static files mapping creado** - URL: `/static/`, Directory: ruta correcta
- [ ] **Permisos de directorio static** - Lectura habilitada
- [ ] **Archivos CSS/JS accesibles** - Verificar carga

---

## 📁 Directorios y Permisos

### Estructura de Directorios
- [ ] **instance/ creado** - Para base de datos SQLite
- [ ] **logs/ creado** - Para archivos de log
- [ ] **app/static/uploads/ creado** - Para archivos subidos
- [ ] **app/static/generated/ creado** - Para archivos generados
- [ ] **app/static/temp/ creado** - Para archivos temporales

### Permisos
- [ ] **instance/ escribible** - chmod 755 aplicado
- [ ] **logs/ escribible** - Para logging
- [ ] **uploads/ escribible** - Para archivos de usuario
- [ ] **generated/ escribible** - Para PDFs, QRs, etc.

---

## 🗄️ Base de Datos

### Configuración
- [ ] **DATABASE_URL configurada** - SQLite para producción
- [ ] **Base de datos inicializada** - Tablas creadas
- [ ] **Permisos de escritura** - En directorio instance/
- [ ] **Backup inicial creado** - Para restauración si es necesario

---

## 🚀 Lanzamiento

### Pruebas Finales
- [ ] **Web app recargada** - Desde dashboard PythonAnywhere
- [ ] **Página principal carga** - Sin errores 500/502
- [ ] **Static files cargan** - CSS, JS, imágenes
- [ ] **Funcionalidad básica probada** - Al menos 1 flujo completo

### Monitoreo
- [ ] **Logs revisados** - Sin errores críticos
- [ ] **Error logs verificados** - `/var/log/tuusuario.pythonanywhere.com.error.log`
- [ ] **Performance inicial OK** - Tiempos de respuesta aceptables

---

## 🔒 Seguridad

### Configuración de Seguridad
- [ ] **HTTPS habilitado** - PythonAnywhere automático
- [ ] **Headers de seguridad** - Implementados via PythonAnywhereConfig
- [ ] **SECRET_KEY segura** - Generada aleatoriamente
- [ ] **Debug desactivado** - No mostrar información sensible

### Variables Sensibles
- [ ] **API Keys no expuestas** - Solo en .env, no en código
- [ ] **Archivo .env no en Git** - Verificar .gitignore
- [ ] **Logs sin información sensible** - Revisar contenido

---

## 📊 Post-Despliegue

### Monitoreo Continuo
- [ ] **Monitoreo de logs configurado** - Revisar regularmente
- [ ] **Backup de base de datos** - Script programado
- [ ] **Alertas de errores** - Email opcional configurado
- [ ] **Performance monitoring** - Tiempos de respuesta

### Documentación
- [ ] **URL de producción documentada** - Compartida con equipo
- [ ] **Credenciales almacenadas seguramente** - Gestor de contraseñas
- [ ] **Proceso de actualizaciones definido** - Para futuras versiones

---

## 🆘 Plan de Contingencia

### Rollback
- [ ] **Backup de código anterior** - Para rollback rápido
- [ ] **Backup de base de datos** - Estado antes del despliegue
- [ ] **Proceso de rollback documentado** - Pasos claros
- [ ] **Contactos de soporte** - PythonAnywhere y equipo técnico

---

## ✅ Firma de Aprobación

**Verificado por:** ___________________ **Fecha:** ___________

**Ambiente:** Producción PythonAnywhere  
**URL:** https://_____.pythonanywhere.com  
**Versión:** Oleoflores Smart Flow v1.0.0  

### Estado Final
- [ ] **TODOS los elementos verificados** ✅
- [ ] **Aplicación funcionando en producción** ✅
- [ ] **Equipo notificado del lanzamiento** ✅
- [ ] **Documentación actualizada** ✅

---

## 📞 Contactos de Emergencia

**Soporte PythonAnywhere:** help@pythonanywhere.com  
**Administrador del Sistema:** _________________  
**Desarrollador Principal:** _________________  

**¡Aplicación lista para producción!** 🎉 