#!/usr/bin/env python3
"""
Script de inicialización del proyecto Wallapop Automation Bot
Ejecutar después de la instalación para configurar el entorno
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def print_header(text):
    """Imprime un header formateado"""
    print("\n" + "="*50)
    print(f"  {text}")
    print("="*50 + "\n")

def check_python_version():
    """Verifica la versión de Python"""
    print("Verificando versión de Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python {version.major}.{version.minor} detectado")
        print("   Se requiere Python 3.11 o superior")
        return False
    print(f"✅ Python {version.major}.{version.minor} - OK")
    return True

def create_directories():
    """Crea directorios necesarios"""
    print("\nCreando directorios...")
    directories = [
        "logs",
        "data",
        "data/products",
        "data/conversations", 
        "backups",
        "backups/database",
        "backups/conversations",
        "debug",
        "debug/screenshots",
        "credentials"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Creado: {directory}")

def check_dependencies():
    """Verifica dependencias del sistema"""
    print("\nVerificando dependencias del sistema...")
    
    dependencies = {
        "PostgreSQL": "psql --version",
        "Redis": "redis-cli --version",
        "Git": "git --version"
    }
    
    for name, command in dependencies.items():
        try:
            subprocess.run(command.split(), capture_output=True, check=True)
            print(f"✅ {name} - Instalado")
        except:
            print(f"❌ {name} - No encontrado")
            print(f"   Instalar con: sudo apt install {name.lower()}")

def create_env_file():
    """Crea archivo .env de ejemplo"""
    print("\nCreando archivo .env...")
    
    env_content = """# Configuración de entorno para Wallapop Bot

# Base de datos
DATABASE_URL=postgresql://wallapop_user:password@localhost:5432/wallapop_bot

# Redis
REDIS_URL=redis://localhost:6379/0

# Seguridad
SECRET_KEY=cambiar-esta-clave-secreta-en-produccion

# Wallapop
WALLAPOP_SESSION_COOKIE=

# Desarrollo
DEBUG=True
LOG_LEVEL=INFO

# Timezone
TZ=Europe/Madrid
"""
    
    if not Path(".env").exists():
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Archivo .env creado")
        print("   ⚠️  Recuerda configurar las variables de entorno")
    else:
        print("⚠️  Archivo .env ya existe")

def create_test_config():
    """Crea configuración de prueba"""
    print("\nCreando configuración de prueba...")
    
    if not Path("config/config.yaml").exists():
        subprocess.run(["cp", "config/config.example.yaml", "config/config.yaml"])
        print("✅ Configuración creada desde ejemplo")
        print("   ⚠️  Editar config/config.yaml con tus datos")
    else:
        print("⚠️  Configuración ya existe")

def install_spacy_model():
    """Instala modelo de spaCy para español"""
    print("\nInstalando modelo de spaCy...")
    try:
        subprocess.run([sys.executable, "-m", "spacy", "download", "es_core_news_sm"], check=True)
        print("✅ Modelo de spaCy instalado")
    except:
        print("❌ Error instalando modelo de spaCy")
        print("   Ejecutar manualmente: python -m spacy download es_core_news_sm")

def create_sample_cookies():
    """Crea archivo de cookies de ejemplo"""
    print("\nCreando archivo de cookies de ejemplo...")
    
    sample_cookies = {
        "_wallapop_session": "TU_SESSION_COOKIE_AQUI",
        "user_id": "TU_USER_ID",
        "auth_token": "TU_AUTH_TOKEN"
    }
    
    if not Path("credentials/cookies.json").exists():
        with open("credentials/cookies.json", "w") as f:
            json.dump(sample_cookies, f, indent=2)
        print("✅ Archivo de cookies de ejemplo creado")
        print("   ⚠️  Actualizar con cookies reales de Wallapop")
    else:
        print("⚠️  Archivo de cookies ya existe")

def check_playwright():
    """Verifica instalación de Playwright"""
    print("\nVerificando Playwright...")
    try:
        import playwright
        print("✅ Playwright instalado")
        
        # Instalar navegadores si no están
        subprocess.run(["playwright", "install", "chromium"], check=True)
        print("✅ Navegador Chromium instalado")
    except:
        print("❌ Playwright no instalado correctamente")
        print("   Ejecutar: pip install playwright && playwright install chromium")

def main():
    """Función principal"""
    print_header("INICIALIZACIÓN DEL PROYECTO WALLAPOP BOT")
    
    # Verificaciones
    if not check_python_version():
        sys.exit(1)
    
    # Crear estructura
    create_directories()
    
    # Verificar dependencias
    check_dependencies()
    
    # Crear archivos de configuración
    create_env_file()
    create_test_config()
    create_sample_cookies()
    
    # Instalar componentes
    install_spacy_model()
    check_playwright()
    
    print_header("INICIALIZACIÓN COMPLETADA")
    print("Próximos pasos:")
    print("1. Configurar PostgreSQL y crear base de datos")
    print("2. Editar config/config.yaml con tu configuración")
    print("3. Obtener cookies de Wallapop y actualizar credentials/cookies.json")
    print("4. Ejecutar: python src/bot/wallapop_bot.py")
    print("\n¡Buena suerte! 🚀")

if __name__ == "__main__":
    main()
