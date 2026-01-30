#!/bin/bash

# Script para iniciar la aplicación Flask con las variables de entorno correctas

echo "🚀 Iniciando Oleoflores Smart Flow..."

# Limpiar variables de entorno conflictivas
unset OPENAI_API_KEY
unset OCR_ENGINE

# Configurar certificados SSL
export SSL_CERT_FILE=$(python -c "import certifi; print(certifi.where())")
export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE

# Cargar variables del archivo .env
if [ -f .env ]; then
    echo "📋 Cargando variables de entorno desde .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Verificar que la API key esté configurada
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Advertencia: OPENAI_API_KEY no está configurada"
else
    echo "✅ OPENAI_API_KEY configurada"
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Iniciar la aplicación
echo "🌐 Iniciando servidor Flask..."
python run.py 