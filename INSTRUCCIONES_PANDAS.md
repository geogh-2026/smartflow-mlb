# 📋 Instrucciones para Habilitar el Módulo de Presupuesto

## 🔧 Problema Actual

El módulo de presupuesto está temporalmente deshabilitado porque requiere la librería `pandas` que no está instalada.

## 🚀 Solución

### Paso 1: Instalar pandas
```bash
pip install pandas
```

### Paso 2: Habilitar el blueprint de presupuesto

En el archivo `app/__init__.py`, descomenta las siguientes líneas:

**Línea ~126:**
```python
# Cambiar de:
# from app.blueprints.presupuesto import bp as presupuesto_bp  # Comentado temporalmente - requiere pandas

# A:
from app.blueprints.presupuesto import bp as presupuesto_bp
```

**Línea ~140:**
```python
# Cambiar de:
# app.register_blueprint(presupuesto_bp)  # Comentado temporalmente - requiere pandas

# A:
app.register_blueprint(presupuesto_bp)  # Ya tiene el prefix en el blueprint
```

### Paso 3: Habilitar el formulario en dashboard.html

En el archivo `app/templates/dashboard.html`, línea ~736:

```html
<!-- Cambiar de: -->
<!-- <form id="uploadBudgetForm" method="POST" action="{{ url_for('presupuesto.upload_budget') }}" enctype="multipart/form-data"> -->
<form id="uploadBudgetForm" method="POST" action="#" enctype="multipart/form-data"> <!-- Temporalmente deshabilitado - requiere pandas -->

<!-- A: -->
<form id="uploadBudgetForm" method="POST" action="{{ url_for('presupuesto.upload_budget') }}" enctype="multipart/form-data">
```

### Paso 4: Reiniciar la aplicación
```bash
python run.py
```

## ✅ Estado Actual

- ✅ **Sistema de Sellos**: Completamente funcional
- ✅ **Todas las demás funcionalidades**: Operativas
- ⏳ **Módulo de Presupuesto**: Deshabilitado temporalmente

## 🎯 Alternativa

Si no necesitas el módulo de presupuesto inmediatamente, puedes continuar usando el sistema normalmente. El sistema de sellos y todas las demás funcionalidades están completamente operativas.

---

**Nota**: Este archivo se puede eliminar una vez que pandas esté instalado y el módulo de presupuesto esté habilitado. 