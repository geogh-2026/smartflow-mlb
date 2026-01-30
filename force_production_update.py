#!/usr/bin/env python3
"""
Script para forzar la actualización en producción
Verifica el estado del código y proporciona comandos para actualizar
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(cmd, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n🔧 {description}")
    print(f"Comando: {cmd}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"Exit Code: {result.returncode}")
        if result.stdout:
            print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Error:\n{result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error ejecutando comando: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 SCRIPT DE ACTUALIZACIÓN FORZADA PARA PRODUCCIÓN")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar estado del repositorio local
    print("\n📋 VERIFICANDO ESTADO LOCAL...")
    run_command("git status", "Estado del repositorio local")
    run_command("git log --oneline -5", "Últimos 5 commits")
    
    # Verificar que estamos en la rama main
    run_command("git branch", "Rama actual")
    
    # Verificar el último commit
    run_command("git show --name-only HEAD", "Archivos modificados en el último commit")
    
    # Verificar el contenido específico del archivo problemático
    print("\n🔍 VERIFICANDO CONTENIDO DEL ARCHIVO PROBLEMÁTICO...")
    
    file_path = "app/blueprints/misc/routes.py"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Buscar las líneas críticas
        for i, line in enumerate(lines[2170:2175], start=2171):
            print(f"Línea {i}: {line.rstrip()}")
    else:
        print(f"❌ Archivo no encontrado: {file_path}")
    
    print("\n" + "=" * 60)
    print("📝 COMANDOS PARA EJECUTAR EN PRODUCCIÓN:")
    print("=" * 60)
    
    commands = [
        "cd /home/enriquepabon/oleoflores-smart-flow",
        "git fetch origin",
        "git reset --hard origin/main",
        "git pull origin main",
        "# Reiniciar la aplicación (método depende del servidor)",
        "# Para PythonAnywhere: 'Reload' en el dashboard web",
        "# Para systemd: sudo systemctl restart oleoflores-smart-flow",
        "# Para uWSGI: touch /path/to/wsgi.py o kill -HUP <pid>"
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"{i}. {cmd}")
    
    print("\n" + "=" * 60)
    print("🔄 VERIFICACIÓN POST-ACTUALIZACIÓN:")
    print("=" * 60)
    
    verification_steps = [
        "1. Verificar que el archivo routes.py contiene las funciones safe_int y safe_float",
        "2. Comprobar que la línea 2172 contiene 'def safe_int(value, default=0):'",
        "3. Acceder al dashboard y verificar que no hay errores en los logs",
        "4. Confirmar que los KPIs se muestran correctamente"
    ]
    
    for step in verification_steps:
        print(step)
    
    print(f"\n✅ Script completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
