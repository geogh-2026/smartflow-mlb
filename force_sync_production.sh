#!/bin/bash

echo "============================================================"
echo "🚀 SCRIPT DE SINCRONIZACIÓN FORZADA PARA PRODUCCIÓN"
echo "============================================================"
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

echo "📋 COMANDOS PARA EJECUTAR EN EL SERVIDOR DE PRODUCCIÓN:"
echo "============================================================"
echo ""

echo "1. Conectar al servidor:"
echo "   ssh enriquepabon@ssh.pythonanywhere.com"
echo ""

echo "2. Ir al directorio del proyecto:"
echo "   cd /home/enriquepabon/oleoflores-smart-flow"
echo ""

echo "3. Verificar estado actual:"
echo "   git status"
echo "   git log --oneline -3"
echo ""

echo "4. Forzar actualización desde GitHub:"
echo "   git fetch origin"
echo "   git reset --hard origin/main"
echo "   git pull origin main"
echo ""

echo "5. Verificar que la corrección se aplicó:"
echo "   grep -n 'total_racimos_manuales_clasificados = 0' app/blueprints/misc/routes.py"
echo "   # Debería mostrar línea 2208 con la inicialización"
echo ""

echo "6. Verificar el último commit:"
echo "   git log --oneline -1"
echo "   # Debería mostrar: c581350 hotfix: Corregir UnboundLocalError"
echo ""

echo "7. Reiniciar la aplicación:"
echo "   # Ir a: https://www.pythonanywhere.com/user/enriquepabon/webapps/"
echo "   # Hacer clic en el botón 'Reload' de la aplicación"
echo ""

echo "8. Verificar que no hay errores:"
echo "   # Acceder al dashboard y revisar logs en tiempo real"
echo "   # Los logs deberían mostrar datos sin errores UnboundLocalError"
echo ""

echo "============================================================"
echo "🔍 VERIFICACIÓN POST-ACTUALIZACIÓN:"
echo "============================================================"
echo ""

echo "✅ Verificar en el archivo routes.py:"
echo "   - Línea 2208: total_racimos_manuales_clasificados = 0"
echo "   - Líneas 2209-2210: calidad_sumas_manual y calidad_sumas_automatica"
echo "   - Línea 2262: total_racimos_manuales_clasificados += ..."
echo ""

echo "✅ Verificar en los logs:"
echo "   - Sin errores UnboundLocalError"
echo "   - API /api/dashboard/stats responde correctamente"
echo "   - Dashboard muestra KPIs sin errores"
echo ""

echo "============================================================"
echo "📞 CONTACTO DE EMERGENCIA:"
echo "============================================================"
echo ""
echo "Si persisten problemas:"
echo "1. Verificar que el commit c581350 está en el servidor"
echo "2. Comprobar que el archivo routes.py tiene las correcciones"
echo "3. Reiniciar completamente la aplicación web"
echo "4. Revisar logs de error en PythonAnywhere"
echo ""

echo "✅ Script completado: $(date '+%Y-%m-%d %H:%M:%S')"
