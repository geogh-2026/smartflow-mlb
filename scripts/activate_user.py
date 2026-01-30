#!/usr/bin/env python
"""
Script para activar usuarios en Oleoflores Smart Flow
"""

import sys
import os

# Agregar el directorio padre al path para importar la app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import User, db
from config.config import DevelopmentConfig

def list_users():
    """Lista todos los usuarios con su estado"""
    
    app = create_app(DevelopmentConfig)
    
    with app.app_context():
        try:
            users = User.query.all()
            
            if not users:
                print("📋 No hay usuarios registrados")
                return []
            
            print("📋 Usuarios registrados:")
            print("-" * 60)
            for user in users:
                status = "✅ ACTIVO" if user.is_active else "⚠️  INACTIVO"
                print(f"ID: {user.id} | Usuario: {user.username:<15} | Email: {user.email:<25} | {status}")
            print("-" * 60)
            
            return users
            
        except Exception as e:
            print(f"❌ Error al listar usuarios: {e}")
            return []

def activate_user_by_id(user_id):
    """Activa un usuario por su ID"""
    
    app = create_app(DevelopmentConfig)
    
    with app.app_context():
        try:
            user = User.query.get(user_id)
            
            if not user:
                print(f"❌ Usuario con ID {user_id} no encontrado")
                return False
            
            if user.is_active:
                print(f"ℹ️  El usuario '{user.username}' ya está activo")
                return True
            
            user.is_active = 1
            db.session.commit()
            
            print(f"✅ Usuario '{user.username}' activado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al activar usuario: {e}")
            db.session.rollback()
            return False

def activate_user_by_username(username):
    """Activa un usuario por su nombre de usuario"""
    
    app = create_app(DevelopmentConfig)
    
    with app.app_context():
        try:
            user = User.query.filter_by(username=username).first()
            
            if not user:
                print(f"❌ Usuario '{username}' no encontrado")
                return False
            
            if user.is_active:
                print(f"ℹ️  El usuario '{username}' ya está activo")
                return True
            
            user.is_active = 1
            db.session.commit()
            
            print(f"✅ Usuario '{username}' activado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al activar usuario: {e}")
            db.session.rollback()
            return False

def activate_all_users():
    """Activa todos los usuarios inactivos"""
    
    app = create_app(DevelopmentConfig)
    
    with app.app_context():
        try:
            inactive_users = User.query.filter_by(is_active=0).all()
            
            if not inactive_users:
                print("ℹ️  No hay usuarios inactivos para activar")
                return True
            
            for user in inactive_users:
                user.is_active = 1
                print(f"✅ Activando usuario: {user.username}")
            
            db.session.commit()
            
            print(f"🎉 {len(inactive_users)} usuario(s) activado(s) exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al activar usuarios: {e}")
            db.session.rollback()
            return False

def main():
    """Función principal"""
    
    print("🔐 Activador de Usuarios - Oleoflores Smart Flow")
    print("=" * 50)
    
    # Listar usuarios actuales
    users = list_users()
    
    if not users:
        print("No hay usuarios para activar")
        return
    
    print("\n📝 Opciones:")
    print("1. Activar usuario por ID")
    print("2. Activar usuario por nombre")
    print("3. Activar TODOS los usuarios inactivos")
    print("4. Solo mostrar lista (no activar)")
    
    try:
        choice = input("\n🔢 Selecciona una opción (1-4): ").strip()
        
        if choice == "1":
            user_id = input("📝 Ingresa el ID del usuario: ").strip()
            try:
                user_id = int(user_id)
                activate_user_by_id(user_id)
            except ValueError:
                print("❌ ID debe ser un número")
                
        elif choice == "2":
            username = input("📝 Ingresa el nombre de usuario: ").strip()
            activate_user_by_username(username)
            
        elif choice == "3":
            confirm = input("⚠️  ¿Activar TODOS los usuarios inactivos? (s/N): ").strip().lower()
            if confirm in ['s', 'si', 'sí', 'y', 'yes']:
                activate_all_users()
            else:
                print("❌ Operación cancelada")
                
        elif choice == "4":
            print("ℹ️  Solo mostrando lista")
            
        else:
            print("❌ Opción no válida")
            
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main() 