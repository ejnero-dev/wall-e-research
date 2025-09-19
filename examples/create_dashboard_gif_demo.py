#!/usr/bin/env python3
"""
🎬 Automatización completa para crear GIF del Dashboard Wall-E
Este script navega automáticamente por el dashboard mientras capturas con tu herramienta favorita
"""

from playwright.sync_api import sync_playwright
import time
import sys
from pathlib import Path

# Colores para output
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_scene(scene_name, description=""):
    """Imprime información de la escena actual"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{YELLOW}🎬 ESCENA: {scene_name}{RESET}")
    if description:
        print(f"{GREEN}{description}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def smooth_hover(page, selector, duration=0.5):
    """Realiza un hover suave sobre un elemento"""
    element = page.locator(selector).first
    if element.is_visible():
        element.hover()
        time.sleep(duration)
        return True
    return False

def create_dashboard_demo():
    """
    Automatiza completamente la navegación del dashboard para crear un GIF profesional.
    Duración total: ~45 segundos
    """
    
    print(f"""
{BOLD}{BLUE}╔════════════════════════════════════════════════════════════════╗
║         🎬 DEMO AUTOMATIZADA DEL DASHBOARD WALL-E              ║
╚════════════════════════════════════════════════════════════════╝{RESET}
    """)
    
    print(f"{YELLOW}📋 Instrucciones:{RESET}")
    print("1. Inicia tu herramienta de captura AHORA")
    print("2. Configura área de captura en la ventana del navegador")
    print("3. Presiona Enter cuando estés listo para empezar")
    print(f"{RED}4. La demo durará aproximadamente 45 segundos{RESET}\n")
    
    input(f"{GREEN}Presiona Enter para iniciar...{RESET}")
    
    with sync_playwright() as p:
        # Configuración del navegador
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--window-size=1280,800',
                '--window-position=100,50'
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            device_scale_factor=1.5,  # Mayor calidad
            color_scheme='light',  # Forzar tema claro
        )
        
        page = context.new_page()
        
        # Simular usuario real
        page.set_default_timeout(30000)
        
        print(f"{YELLOW}⏳ Cargando dashboard...{RESET}")
        
        # ============ ESCENA 1: CARGA INICIAL ============
        print_scene("1/7 - CARGA INICIAL", "Mostrando el dashboard completo")
        
        page.goto("http://localhost:8080")
        page.wait_for_load_state("networkidle")
        time.sleep(3)  # Pausa para apreciar la vista general
        
        # Smooth scroll para mostrar todo
        page.evaluate("window.scrollTo({top: 200, behavior: 'smooth'})")
        time.sleep(1)
        page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        time.sleep(2)
        
        # ============ ESCENA 2: MÉTRICAS EN TIEMPO REAL ============
        print_scene("2/7 - MÉTRICAS EN TIEMPO REAL", "WebSocket actualizando datos en vivo")
        
        # Hover sobre cada métrica con tooltip
        metrics_cards = page.locator(".grid > .card").all()[:4]
        for i, card in enumerate(metrics_cards):
            print(f"  📊 Mostrando métrica {i+1}/4...")
            card.hover()
            time.sleep(1.5)  # Tiempo para que se vea el hover effect y tooltip
        
        # Mostrar actualización en tiempo real
        print("  🔄 Esperando actualización WebSocket...")
        time.sleep(3)
        
        # ============ ESCENA 3: GESTIÓN DE PRODUCTOS ============
        print_scene("3/7 - GESTIÓN DE PRODUCTOS", "CRUD completo de productos")
        
        # Scroll suave a productos
        page.locator("text=Anuncios Activos").scroll_into_view_if_needed()
        time.sleep(1)
        
        # Hover sobre productos para mostrar interactividad
        print("  📦 Mostrando productos activos...")
        product_cards = page.locator(".group.relative").all()[:3]
        
        for i, product in enumerate(product_cards):
            if product.is_visible():
                print(f"  🛍️ Producto {i+1}: hover effect...")
                product.hover()
                time.sleep(1)
                
                # En el segundo producto, abrir menú
                if i == 1:
                    more_button = product.locator("button").filter(has_text="").last
                    if more_button.is_visible():
                        print("  📝 Abriendo menú de acciones...")
                        more_button.click()
                        time.sleep(2)  # Mostrar opciones del menú
                        
                        # Hover sobre opciones
                        menu_items = page.locator("[role='menuitem']").all()[:3]
                        for item in menu_items:
                            item.hover()
                            time.sleep(0.5)
                        
                        # Cerrar menú
                        page.keyboard.press("Escape")
                        time.sleep(1)
        
        # Botón de agregar producto
        add_button = page.locator("button:has-text('Agregar')")
        if add_button.is_visible():
            print("  ➕ Mostrando botón de agregar...")
            add_button.hover()
            time.sleep(1)
        
        # ============ ESCENA 4: PANEL DE AUTOMATIZACIÓN ============
        print_scene("4/7 - AUTOMATIZACIÓN INTELIGENTE", "Control de detección automática")
        
        # Scroll al panel
        page.locator("text=Automatización Inteligente").scroll_into_view_if_needed()
        time.sleep(1)
        
        # Interactuar con controles
        auto_panel = page.locator("text=Auto-detección").first
        if auto_panel.is_visible():
            print("  🤖 Panel de auto-detección...")
            auto_panel.hover()
            time.sleep(1)
        
        # Toggle detección
        detect_button = page.locator("button:has-text('Iniciar')").or_(
            page.locator("button:has-text('Detener')")
        ).first
        
        if detect_button.is_visible():
            print("  🔄 Activando detección automática...")
            detect_button.click()
            time.sleep(2)  # Mostrar cambio de estado
            
            # Click de nuevo para mostrar toggle
            detect_button.click()
            time.sleep(1.5)
        
        # ============ ESCENA 5: RESPUESTAS AUTOMATIZADAS ============
        print_scene("5/7 - RESPUESTAS AUTOMATIZADAS", "Configuración de IA conversacional")
        
        # Buscar panel de respuestas
        responses_section = page.locator("text=Respuestas Automatizadas").first
        if responses_section.is_visible():
            responses_section.scroll_into_view_if_needed()
            time.sleep(1)
            
            print("  💬 Configuración de respuestas...")
            
            # Toggle de activación
            toggle_switch = page.locator("button[role='switch']").first
            if toggle_switch.is_visible():
                print("  🔀 Toggle de activación...")
                toggle_switch.click()
                time.sleep(1.5)
                toggle_switch.click()  # Volver al estado original
                time.sleep(1)
        
        # ============ ESCENA 6: NAVEGACIÓN Y RESPONSIVE ============
        print_scene("6/7 - NAVEGACIÓN DEL SISTEMA", "Sidebar y páginas")
        
        # Abrir/cerrar sidebar
        sidebar_toggle = page.locator("button[data-sidebar='trigger']").or_(
            page.locator("button:has-text('☰')").or_(
                page.locator("button[aria-label*='sidebar']")
            )
        ).first
        
        if sidebar_toggle.is_visible():
            print("  📱 Toggle sidebar...")
            sidebar_toggle.click()
            time.sleep(1.5)
            sidebar_toggle.click()
            time.sleep(1)
        
        # Navegar a Analytics
        analytics_link = page.locator("a:has-text('Analytics')").or_(
            page.locator("a:has-text('Análisis')")
        ).first
        
        if analytics_link.is_visible():
            print("  📈 Navegando a Analytics...")
            analytics_link.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            # Volver al dashboard
            dashboard_link = page.locator("a:has-text('Dashboard')").or_(
                page.locator("a:has-text('Panel')")
            ).first
            
            if dashboard_link.is_visible():
                print("  🏠 Volviendo al Dashboard...")
                dashboard_link.click()
                time.sleep(2)
        
        # ============ ESCENA 7: FINAL - VISTA GENERAL ============
        print_scene("7/7 - VISTA FINAL", "Mostrando el sistema completo")
        
        # Scroll final suave
        print("  📸 Vista panorámica final...")
        page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        time.sleep(1)
        
        # Pequeño scroll para mostrar todo
        for scroll_pos in [0, 300, 600, 300, 0]:
            page.evaluate(f"window.scrollTo({{top: {scroll_pos}, behavior: 'smooth'}})")
            time.sleep(1)
        
        # Hover final sobre el título
        title = page.locator("h2:has-text('Vista General')")
        if title.is_visible():
            title.hover()
            time.sleep(2)
        
        print(f"""
{GREEN}{'='*60}
✅ DEMO COMPLETADA EXITOSAMENTE
{'='*60}{RESET}

{YELLOW}📋 Próximos pasos:{RESET}
1. Detén la grabación en tu herramienta
2. Guarda el archivo como MP4 o GIF
3. Optimiza con FFmpeg si es necesario
4. Sube a LinkedIn con tu post

{BLUE}💡 Comando FFmpeg sugerido:{RESET}
ffmpeg -i input.mp4 -vf "fps=15,scale=800:-1:flags=lanczos" -loop 0 output.gif

{GREEN}¡Éxito con tu publicación! 🚀{RESET}
        """)
        
        input(f"\n{YELLOW}Presiona Enter para cerrar el navegador...{RESET}")
        browser.close()

def main():
    """Punto de entrada principal"""
    try:
        # Verificar que el servidor esté corriendo
        import requests
        try:
            response = requests.get("http://localhost:8080", timeout=2)
        except:
            print(f"{RED}❌ Error: El dashboard no está corriendo en http://localhost:8080{RESET}")
            print(f"{YELLOW}Por favor, inicia el dashboard con:{RESET}")
            print("  cd frontend && npm run dev")
            sys.exit(1)
        
        # Verificar backend
        try:
            response = requests.get("http://localhost:8000/api/dashboard/health", timeout=2)
        except:
            print(f"{YELLOW}⚠️  Advertencia: El backend no está corriendo en http://localhost:8000{RESET}")
            print("Algunas funciones podrían no funcionar correctamente.")
            print("Para iniciar el backend:")
            print("  uv run python -m uvicorn src.api.dashboard_server:app --reload")
            print()
            
            continue_anyway = input(f"{YELLOW}¿Continuar de todos modos? (s/n): {RESET}")
            if continue_anyway.lower() != 's':
                sys.exit(1)
        
        # Ejecutar demo
        create_dashboard_demo()
        
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Demo cancelada por el usuario{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{RED}❌ Error inesperado: {e}{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
