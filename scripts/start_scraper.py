#!/usr/bin/env python3
"""
Script principal para iniciar el scraper integrado de Wallapop
Orquesta todos los componentes del sistema de automatización
"""
import asyncio
import signal
import sys
import os
import logging
from pathlib import Path
from datetime import datetime
import json
from typing import Optional

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper.scraper_integration import ScraperIntegration
from scraper.session_manager import AuthMethod
from scraper.error_handler import error_handler, AlertManager, ErrorSeverity
from scraper.config import scraper_config


class ScraperOrchestrator:
    """Orquestador principal del scraper"""
    
    def __init__(self):
        self.integration: Optional[ScraperIntegration] = None
        self.is_running = False
        self.shutdown_requested = False
        
        # Configurar logging
        self.setup_logging()
        
        # Configurar alertas
        self.setup_alerts()
        
        # Configurar handlers de señales
        self.setup_signal_handlers()
        
        self.logger = logging.getLogger("scraper_orchestrator")
    
    def setup_logging(self):
        """Configura el sistema de logging"""
        # Crear directorio de logs
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configurar logging principal
        logging.basicConfig(
            level=getattr(logging, scraper_config.LOG_LEVEL.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / scraper_config.LOG_FILE),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Configurar loggers específicos
        playwright_logger = logging.getLogger("playwright")
        playwright_logger.setLevel(logging.WARNING)  # Reducir verbosidad de Playwright
    
    def setup_alerts(self):
        """Configura el sistema de alertas"""
        alert_config = {}
        
        # Configurar Slack si está disponible
        if scraper_config.SLACK_WEBHOOK_URL:
            alert_config["slack_webhook_url"] = scraper_config.SLACK_WEBHOOK_URL
        
        # Configurar email si está disponible
        if scraper_config.EMAIL_ALERTS:
            alert_config["email_config"] = {
                "smtp_host": scraper_config.SMTP_HOST,
                "smtp_port": scraper_config.SMTP_PORT,
                "from_address": scraper_config.EMAIL_FROM,
                "to_address": scraper_config.EMAIL_TO
            }
        
        if alert_config:
            alert_manager = AlertManager(**alert_config)
            error_handler.alert_manager = alert_manager
    
    def setup_signal_handlers(self):
        """Configura handlers para señales del sistema"""
        def signal_handler(signum, frame):
            signal_name = signal.Signals(signum).name
            self.logger.info(f"Received signal {signal_name}, initiating graceful shutdown...")
            self.shutdown_requested = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self) -> bool:
        """Inicia el orquestador del scraper"""
        self.logger.info("🚀 Starting Wallapop Scraper Orchestrator")
        
        try:
            # Verificar configuración
            await self._verify_configuration()
            
            # Crear integración
            auth_method = self._determine_auth_method()
            self.integration = ScraperIntegration(auth_method)
            
            # Inicializar sistema
            success = await self.integration.start()
            
            if not success:
                raise Exception("Failed to start scraper integration")
            
            self.is_running = True
            self.logger.info("✅ Scraper system started successfully")
            
            # Enviar alerta de inicio
            if error_handler.alert_manager:
                await error_handler.alert_manager.send_alert(
                    title="Scraper Started",
                    message="Wallapop scraper system started successfully",
                    severity=ErrorSeverity.LOW,
                    context={"start_time": datetime.now().isoformat()}
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start scraper system: {e}")
            
            if error_handler.alert_manager:
                await error_handler.alert_manager.send_alert(
                    title="Scraper Startup Failed",
                    message=f"Failed to start scraper system: {str(e)}",
                    severity=ErrorSeverity.CRITICAL,
                    context={"error": str(e)}
                )
            
            return False
    
    async def run(self):
        """Ejecuta el bucle principal del orquestador"""
        self.logger.info("🔄 Starting main orchestrator loop")
        
        # Estadísticas
        last_stats_time = datetime.now()
        stats_interval = 3600  # 1 hora
        
        while self.is_running and not self.shutdown_requested:
            try:
                # Verificar salud del sistema
                await self._monitor_system_health()
                
                # Generar estadísticas periódicas
                current_time = datetime.now()
                if (current_time - last_stats_time).total_seconds() >= stats_interval:
                    await self._generate_stats_report()
                    last_stats_time = current_time
                
                # Verificar si necesitamos detener
                if self.shutdown_requested:
                    break
                
                # Dormir antes de próxima verificación
                await asyncio.sleep(60)  # Verificar cada minuto
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                error_handler.record_error(e, {"context": "main_loop"}, ErrorSeverity.HIGH)
                await asyncio.sleep(300)  # Esperar 5 minutos en caso de error
        
        self.logger.info("🛑 Main loop ending, initiating shutdown")
        await self._shutdown()
    
    async def _verify_configuration(self):
        """Verifica la configuración del sistema"""
        self.logger.info("🔍 Verifying system configuration")
        
        # Verificar horario activo
        if not scraper_config.is_within_active_hours():
            self.logger.warning("⚠️  Starting outside active hours")
        
        # Verificar límites
        if scraper_config.MAX_CONCURRENT_CONVERSATIONS > 10:
            self.logger.warning("⚠️  High concurrent conversation limit may trigger detection")
        
        if scraper_config.MIN_DELAY < 30:
            self.logger.warning("⚠️  Low minimum delay may trigger detection")
        
        # Verificar directorio de screenshots
        if scraper_config.SCREENSHOT_ON_ERROR:
            screenshot_dir = Path(scraper_config.SCREENSHOT_DIR)
            screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("✅ Configuration verified")
    
    def _determine_auth_method(self) -> AuthMethod:
        """Determina el método de autenticación a usar"""
        # Verificar si hay cookies guardadas
        cookies_file = Path("wallapop_cookies.json")
        
        if cookies_file.exists():
            self.logger.info("🍪 Found existing cookies, using cookie authentication")
            return AuthMethod.COOKIES
        
        # Verificar si hay credenciales
        credentials_file = Path("credentials.enc")
        
        if credentials_file.exists():
            self.logger.info("🔑 Found stored credentials, using credential authentication")
            return AuthMethod.CREDENTIALS
        
        self.logger.info("🔄 No existing authentication found, using auto method")
        return AuthMethod.AUTO
    
    async def _monitor_system_health(self):
        """Monitorea la salud del sistema"""
        try:
            if not self.integration:
                return
            
            # Health check del scraper
            if self.integration.scraper:
                health = await self.integration.scraper.health_check()
                
                if not health.get("healthy", False):
                    self.logger.warning(f"⚠️  System health check failed: {health}")
                    
                    # Intentar recuperación automática
                    await self._attempt_recovery()
            
            # Verificar estadísticas de errores
            error_stats = error_handler.get_error_stats()
            recent_errors = error_stats.get("recent_errors_24h", 0)
            
            if recent_errors > 50:  # Más de 50 errores en 24h
                self.logger.warning(f"⚠️  High error rate detected: {recent_errors} errors in 24h")
                
                if error_handler.alert_manager:
                    await error_handler.alert_manager.send_alert(
                        title="High Error Rate",
                        message=f"Detected {recent_errors} errors in the last 24 hours",
                        severity=ErrorSeverity.HIGH,
                        context=error_stats
                    )
            
        except Exception as e:
            self.logger.error(f"Error monitoring system health: {e}")
    
    async def _attempt_recovery(self):
        """Intenta recuperación automática del sistema"""
        self.logger.info("🔧 Attempting automatic system recovery")
        
        try:
            if self.integration and self.integration.scraper:
                # Intentar refrescar sesión
                session_info = await self.integration.scraper.session_manager.refresh_session(
                    self.integration.scraper.context
                )
                
                if session_info:
                    self.logger.info("✅ Session refreshed successfully")
                else:
                    self.logger.warning("⚠️  Session refresh failed, may need re-authentication")
            
        except Exception as e:
            self.logger.error(f"❌ Recovery attempt failed: {e}")
            error_handler.record_error(e, {"context": "recovery_attempt"}, ErrorSeverity.HIGH)
    
    async def _generate_stats_report(self):
        """Genera reporte de estadísticas"""
        self.logger.info("📊 Generating hourly stats report")
        
        try:
            stats = {}
            
            # Estadísticas del integrador
            if self.integration:
                stats["integration"] = self.integration.get_status()
            
            # Estadísticas del scraper
            if self.integration and self.integration.scraper:
                stats["scraper"] = self.integration.scraper.get_status()
            
            # Estadísticas de errores
            stats["errors"] = error_handler.get_error_stats()
            
            # Health check
            if self.integration and self.integration.scraper:
                stats["health"] = await self.integration.scraper.health_check()
            
            # Guardar estadísticas
            stats_dir = Path("stats")
            stats_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stats_file = stats_dir / f"hourly_stats_{timestamp}.json"
            
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            
            # Log resumen
            self.logger.info("📈 Hourly stats summary:")
            if "integration" in stats:
                integration_stats = stats["integration"]
                self.logger.info(f"  - Active conversations: {integration_stats.get('active_conversations', 0)}")
                self.logger.info(f"  - Messages processed: {integration_stats.get('processed_messages', 0)}")
            
            if "errors" in stats:
                error_stats = stats["errors"]
                self.logger.info(f"  - Total errors: {error_stats.get('total_errors', 0)}")
                self.logger.info(f"  - Recent errors (24h): {error_stats.get('recent_errors_24h', 0)}")
            
        except Exception as e:
            self.logger.error(f"Error generating stats report: {e}")
    
    async def _shutdown(self):
        """Ejecuta shutdown limpio del sistema"""
        self.logger.info("🛑 Executing system shutdown")
        
        try:
            # Detener integración
            if self.integration:
                await self.integration.stop()
            
            # Enviar alerta de shutdown
            if error_handler.alert_manager:
                await error_handler.alert_manager.send_alert(
                    title="Scraper Shutdown",
                    message="Wallapop scraper system shutdown completed",
                    severity=ErrorSeverity.LOW,
                    context={"shutdown_time": datetime.now().isoformat()}
                )
            
            self.is_running = False
            self.logger.info("✅ System shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during shutdown: {e}")


async def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Wallapop Scraper - Sistema de automatización")
    parser.add_argument("--config", help="Archivo de configuración personalizado")
    parser.add_argument("--auth-method", choices=["cookies", "credentials", "auto"], 
                        default="auto", help="Método de autenticación")
    parser.add_argument("--dry-run", action="store_true", 
                        help="Ejecutar en modo simulación (no envía mensajes)")
    parser.add_argument("--verbose", "-v", action="store_true", 
                        help="Logging verbose")
    
    args = parser.parse_args()
    
    # Configurar nivel de logging si es verbose
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Configurar dry run si está activado
    if args.dry_run:
        os.environ["WALLAPOP_DRY_RUN"] = "true"
        print("🧪 DRY RUN MODE - No messages will be sent")
    
    print("🤖 WALLAPOP SCRAPER - Automated Sales Assistant")
    print("=" * 50)
    print()
    print("Features:")
    print("✓ Intelligent conversation management")
    print("✓ Advanced anti-detection measures") 
    print("✓ Robust error handling with auto-recovery")
    print("✓ 24/7 continuous operation capability")
    print("✓ Real-time fraud detection")
    print("✓ Human-like response timing")
    print()
    
    orchestrator = ScraperOrchestrator()
    
    try:
        # Iniciar sistema
        success = await orchestrator.start()
        
        if not success:
            print("❌ Failed to start scraper system")
            return 1
        
        print("✅ System started successfully!")
        print("📱 Monitoring Wallapop conversations...")
        print("📊 Stats will be logged hourly")
        print()
        print("Press Ctrl+C to stop gracefully")
        print("-" * 50)
        
        # Ejecutar bucle principal
        await orchestrator.run()
        
        print("\n✅ Scraper stopped successfully")
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Shutdown requested by user")
        if orchestrator.is_running:
            await orchestrator._shutdown()
        return 0
        
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        logging.exception("Critical error in main")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())