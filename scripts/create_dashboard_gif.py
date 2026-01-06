#!/usr/bin/env python3
"""
🎬 Script para crear un GIF animado profesional del Dashboard de Wall-E
Autor: Emilio Neva
Fecha: Enero 2025

Este script automatiza la captura de un GIF que muestra las características
más impactantes del dashboard para LinkedIn.
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print(
    """
╔════════════════════════════════════════════════════════════════════════════╗
║                    🎬 CREADOR DE GIF PARA LINKEDIN                         ║
║                         Dashboard Wall-E                                   ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
)

print(
    """
📋 PLAN DE CAPTURA DEL GIF (30-45 segundos totales):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ESCENA 1: Vista General (5s)
├── Mostrar dashboard completo
├── Hover sobre el título para context
└── Transición suave

ESCENA 2: Métricas en Tiempo Real (8s)
├── Enfocar en QuickStats
├── Mostrar actualización en tiempo real (WebSocket)
├── Hover sobre cada métrica
└── Resaltar las barras de progreso animadas

ESCENA 3: Gestión de Productos (8s)
├── Scroll a Active Listings
├── Hover sobre productos
├── Click en menú de acciones (dropdown)
├── Mostrar estado (Activo/Pausado)
└── Cambiar estado de un producto

ESCENA 4: Panel de Automatización (7s)
├── Enfocar AutoDetection Panel
├── Activar detección automática
├── Mostrar cambio de estado
└── Visualizar feedback visual

ESCENA 5: Respuestas Automatizadas (7s)
├── Scroll a Automated Responses
├── Toggle activación de respuestas
├── Mostrar configuración de personalidad
└── Preview de respuesta generada

ESCENA 6: Navegación y Responsive (5s)
├── Abrir/cerrar sidebar
├── Navegar a página de Analytics
├── Mostrar diseño responsive
└── Volver a dashboard principal

ESCENA 7: Notificaciones WebSocket (5s)
├── Simular mensaje entrante
├── Mostrar notificación toast
├── Actualización de métricas
└── Badge de contador en sidebar
"""
)

print(
    """
🎯 CARACTERÍSTICAS A DESTACAR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Actualización en tiempo real (WebSocket)
✅ Dashboard profesional con shadcn/ui
✅ Métricas visuales con animaciones
✅ Gestión CRUD de productos
✅ Control de automatización
✅ Diseño responsive y moderno
✅ Notificaciones en tiempo real
✅ Navegación fluida con sidebar
"""
)

print(
    """
🛠️ HERRAMIENTAS RECOMENDADAS PARA CAPTURA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPCIÓN 1: OBS Studio (Recomendada)
├── Grabar en MP4 a 60fps
├── Resolución: 1920x1080 o 1280x720
├── Convertir a GIF con FFmpeg
└── Comando: ffmpeg -i dashboard.mp4 -vf "fps=15,scale=800:-1:flags=lanczos" -c:v gif dashboard.gif

OPCIÓN 2: Peek (Linux)
├── Captura directa a GIF
├── Ajustar área de captura
├── FPS: 15-20 para tamaño óptimo
└── Formato: GIF o WebM

OPCIÓN 3: ScreenToGif (Windows)
├── Grabar y editar frame por frame
├── Optimización automática
├── Exportar con compresión
└── Tamaño máximo: 5-10MB

OPCIÓN 4: Kap (Mac)
├── Captura con preview en tiempo real
├── Exportar a GIF optimizado
├── Ajustes de calidad y FPS
└── Plugins para optimización
"""
)

print(
    """
📝 SCRIPT DE AUTOMATIZACIÓN CON PLAYWRIGHT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
)

# Crear script de Playwright para automatización
playwright_script = '''
from playwright.sync_api import sync_playwright
import time

def create_demo_gif():
    """Automatiza la navegación del dashboard para crear el GIF"""
    
    with sync_playwright() as p:
        # Configurar navegador
        browser = p.chromium.launch(
            headless=False,  # Visible para captura
            args=['--start-maximized']
        )
        
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            device_scale_factor=2,  # Alta calidad
        )
        
        page = context.new_page()
        
        print("🎬 Iniciando demo del dashboard...")
        
        # 1. Cargar dashboard
        page.goto("http://localhost:8080")
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        # 2. Hover sobre métricas
        print("📊 Mostrando métricas en tiempo real...")
        metrics = page.locator(".grid > .card").all()
        for metric in metrics[:4]:
            metric.hover()
            time.sleep(0.5)
        
        # 3. Interactuar con productos
        print("📦 Gestionando productos...")
        page.locator("text=Anuncios Activos").scroll_into_view_if_needed()
        time.sleep(1)
        
        # Hover sobre productos
        products = page.locator("[role='button']").filter(has_text="€").all()
        for product in products[:2]:
            product.hover()
            time.sleep(0.5)
        
        # Abrir menú de acciones
        if page.locator(".group button").nth(0).is_visible():
            page.locator(".group button").nth(0).click()
            time.sleep(1)
            page.keyboard.press("Escape")
        
        # 4. Panel de automatización
        print("🤖 Configurando automatización...")
        page.locator("text=Automatización Inteligente").scroll_into_view_if_needed()
        time.sleep(1)
        
        # Toggle detección automática
        auto_detect = page.locator("button:has-text('Iniciar Detección')")
        if auto_detect.is_visible():
            auto_detect.click()
            time.sleep(2)
        
        # 5. Sidebar navigation
        print("🧭 Navegación por el sistema...")
        page.locator("button[aria-label='Toggle Sidebar']").click()
        time.sleep(1)
        page.locator("button[aria-label='Toggle Sidebar']").click()
        time.sleep(1)
        
        # 6. Navegar a Analytics
        page.locator("a:has-text('Analytics')").click()
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Volver al dashboard
        page.locator("a:has-text('Dashboard')").click()
        time.sleep(2)
        
        print("✅ Demo completada!")
        
        # Mantener abierto para captura manual
        input("Presiona Enter para cerrar el navegador...")
        
        browser.close()

if __name__ == "__main__":
    create_demo_gif()
'''

print("💾 Guardando script de automatización...")
automation_script_path = project_root / "examples" / "create_dashboard_demo.py"
automation_script_path.write_text(playwright_script)
print(f"✅ Script guardado en: {automation_script_path}")

print(
    """
🎨 OPTIMIZACIÓN DEL GIF FINAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. TAMAÑO Y CALIDAD:
   - Resolución: 800x450 o 960x540 (16:9)
   - FPS: 15-20 para balance calidad/tamaño
   - Duración: 30-45 segundos máximo
   - Tamaño final: 5-10MB ideal para LinkedIn

2. COMANDO FFMPEG PARA OPTIMIZACIÓN:
   ```bash
   # Versión alta calidad (10-15MB)
   ffmpeg -i dashboard_raw.mp4 -vf "fps=20,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 dashboard_hq.gif
   
   # Versión optimizada (5-8MB)
   ffmpeg -i dashboard_raw.mp4 -vf "fps=15,scale=800:-1:flags=lanczos" -c:v gif -f gif dashboard_optimized.gif
   
   # Versión ultra-comprimida (2-5MB)
   ffmpeg -i dashboard_raw.mp4 -vf "fps=10,scale=640:-1:flags=lanczos" -c:v gif dashboard_compressed.gif
   ```

3. HERRAMIENTA ONLINE (Alternativa):
   - ezgif.com para optimización adicional
   - Puede reducir 30-50% el tamaño
   - Mantiene buena calidad visual
"""
)

print(
    """
📱 CONTENIDO SUGERIDO PARA EL POST:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"El desarrollo de software debe resolver problemas reales de personas reales.

Wall-E: Mi sistema de automatización inteligente con IA conversacional 🤖

Lo que ven aquí es el dashboard en tiempo real:
• Métricas actualizándose via WebSocket
• Gestión completa de productos
• Control de IA conversacional
• Detección de fraude automática

Stack: React 18 + TypeScript + FastAPI + Python + PostgreSQL

Código completo en GitHub [link]

#FullStack #React #Python #RealTimeData #OpenSource"
"""
)

print(
    """
⚡ COMANDOS RÁPIDOS:
━━━━━━━━━━━━━━━━━━

1. Iniciar el dashboard:
   cd frontend && npm run dev
   
2. Iniciar el backend (en otra terminal):
   cd .. && uv run python -m uvicorn src.api.dashboard_server:app --reload

3. Ejecutar script de demo:
   python examples/create_dashboard_demo.py

4. Capturar con Peek (Linux):
   peek

5. Optimizar GIF:
   ffmpeg -i input.mp4 -vf "fps=15,scale=800:-1" output.gif
"""
)

print(
    """
✨ TIPS FINALES:
━━━━━━━━━━━━━━━

1. PREPARACIÓN:
   - Limpia las notificaciones del sistema
   - Usa modo incógnito para evitar extensiones
   - Ajusta el zoom del navegador a 100%
   - Cierra aplicaciones innecesarias
   
2. DATOS DE PRUEBA:
   - Asegúrate de tener productos activos
   - Genera algunas métricas de ejemplo
   - Ten mensajes no leídos para mostrar badges

3. CAPTURA:
   - Movimientos suaves del mouse
   - Pausas de 1-2s entre acciones
   - Evita movimientos bruscos
   - Captura en horario con buena luz

4. POST-PRODUCCIÓN:
   - Recorta espacios muertos
   - Añade loop infinito
   - Verifica que se vea bien en móvil
   - Prueba en LinkedIn antes de publicar

¡Mucho éxito con tu GIF! 🚀
"""
)

# Crear directorio para outputs
output_dir = project_root / "outputs" / "gifs"
output_dir.mkdir(parents=True, exist_ok=True)
print(f"\n📁 Directorio para GIFs creado: {output_dir}")

print("\n" + "=" * 80)
print("🎬 Script completado. ¡Listo para crear tu GIF profesional!")
print("=" * 80)
