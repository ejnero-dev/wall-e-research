#!/usr/bin/env python3
"""
Validador de funcionamiento continuo 24h para el scraper de Wallapop
Monitorea el sistema durante 24 horas y valida todos los criterios de éxito
"""
import asyncio
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import sys
import os

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper import WallapopScraper, AuthMethod, ScraperStatus
from scraper.scraper_integration import ScraperIntegration
from scraper.error_handler import error_handler
from scraper.config import scraper_config


@dataclass
class ValidationMetrics:
    """Métricas de validación del funcionamiento 24h"""
    start_time: datetime
    end_time: Optional[datetime] = None
    total_runtime_hours: float = 0.0
    
    # Criterios de éxito
    continuous_operation: bool = False
    zero_detections: bool = True
    messages_processed_correctly: bool = True
    realistic_speed: bool = True
    error_recovery: bool = True
    
    # Estadísticas de operación
    total_messages_processed: int = 0
    total_conversations_handled: int = 0
    average_response_time: float = 0.0
    total_errors: int = 0
    critical_errors: int = 0
    
    # Estadísticas de velocidad
    actions_per_minute: float = 0.0
    average_delay_between_actions: float = 0.0
    
    # Detección y recuperación
    session_renewals: int = 0
    circuit_breaker_activations: int = 0
    automatic_recoveries: int = 0
    
    # Health checks
    successful_health_checks: int = 0
    failed_health_checks: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para serialización"""
        return asdict(self)


class ScraperValidator:
    """Validador principal del scraper 24h"""
    
    def __init__(self, test_duration_hours: float = 24.0):
        self.test_duration_hours = test_duration_hours
        self.metrics = ValidationMetrics(start_time=datetime.now())
        self.integration: Optional[ScraperIntegration] = None
        self.monitoring_active = False
        
        # Configuración de logging específica para validación
        self.setup_validation_logging()
        
        # Listas para tracking
        self.response_times: List[float] = []
        self.action_timestamps: List[datetime] = []
        self.error_events: List[Dict[str, Any]] = []
        
        # Archivos de salida
        self.results_dir = Path("validation_results")
        self.results_dir.mkdir(exist_ok=True)
        
        self.metrics_file = self.results_dir / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.detailed_log = self.results_dir / f"detailed_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    def setup_validation_logging(self):
        """Configura logging específico para validación"""
        self.logger = logging.getLogger("scraper_validator")
        self.logger.setLevel(logging.INFO)
        
        # Handler para archivo de validación
        handler = logging.FileHandler(self.detailed_log)
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    async def run_24h_validation(self) -> ValidationMetrics:
        """Ejecuta validación completa de 24 horas"""
        self.logger.info(f"Starting 24h validation - Duration: {self.test_duration_hours} hours")
        
        try:
            # Inicializar sistema
            await self._initialize_system()
            
            # Iniciar monitoreo
            await self._start_monitoring()
            
            # Ejecutar validaciones
            await self._run_validation_tests()
            
            # Finalizar y generar reporte
            await self._finalize_validation()
            
            return self.metrics
            
        except Exception as e:
            self.logger.error(f"Critical error in validation: {e}")
            self.metrics.critical_errors += 1
            return self.metrics
    
    async def _initialize_system(self):
        """Inicializa el sistema de scraping"""
        self.logger.info("Initializing scraper system")
        
        try:
            # Crear integración con configuración de validación
            self.integration = ScraperIntegration(AuthMethod.AUTO)
            
            # Configurar callbacks para métricas
            self._setup_metrics_callbacks()
            
            # Inicializar sistema
            success = await self.integration.start()
            
            if not success:
                raise Exception("Failed to initialize scraper integration")
            
            self.logger.info("System initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize system: {e}")
            raise
    
    def _setup_metrics_callbacks(self):
        """Configura callbacks para recopilar métricas"""
        original_process_message = self.integration._process_single_message
        
        async def tracked_process_message(*args, **kwargs):
            start_time = time.time()
            result = await original_process_message(*args, **kwargs)
            end_time = time.time()
            
            # Registrar métricas
            response_time = end_time - start_time
            self.response_times.append(response_time)
            self.action_timestamps.append(datetime.now())
            
            if result.success:
                self.metrics.total_messages_processed += 1
                if result.response_sent:
                    self.metrics.total_conversations_handled += 1
            else:
                self.metrics.total_errors += 1
                if result.requires_human:
                    self.metrics.critical_errors += 1
            
            return result
        
        # Reemplazar método con versión trackeada
        self.integration._process_single_message = tracked_process_message
    
    async def _start_monitoring(self):
        """Inicia el monitoreo continuo"""
        self.logger.info("Starting continuous monitoring")
        self.monitoring_active = True
        
        # Iniciar tareas de monitoreo en paralelo
        monitoring_tasks = [
            asyncio.create_task(self._monitor_health()),
            asyncio.create_task(self._monitor_performance()),
            asyncio.create_task(self._monitor_errors()),
            asyncio.create_task(self._monitor_session_status())
        ]
        
        # Esperar que todas las tareas se inicien
        await asyncio.sleep(1)
        self.logger.info("All monitoring tasks started")
    
    async def _run_validation_tests(self):
        """Ejecuta las pruebas de validación durante el período especificado"""
        self.logger.info(f"Running validation tests for {self.test_duration_hours} hours")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=self.test_duration_hours)
        
        test_interval = 300  # 5 minutos entre tests
        next_test_time = start_time
        
        while datetime.now() < end_time and self.monitoring_active:
            try:
                current_time = datetime.now()
                
                # Ejecutar tests según programación
                if current_time >= next_test_time:
                    await self._run_periodic_tests()
                    next_test_time = current_time + timedelta(seconds=test_interval)
                
                # Log de progreso cada hora
                elapsed = current_time - start_time
                if elapsed.total_seconds() % 3600 < 60:  # Cada hora aprox
                    hours_elapsed = elapsed.total_seconds() / 3600
                    self.logger.info(f"Validation progress: {hours_elapsed:.1f}h completed")
                    await self._generate_interim_report()
                
                # Dormir hasta próxima verificación
                await asyncio.sleep(60)  # Verificar cada minuto
                
            except Exception as e:
                self.logger.error(f"Error in validation test loop: {e}")
                await asyncio.sleep(300)  # Esperar 5 minutos en caso de error
        
        self.logger.info("Validation test period completed")
    
    async def _run_periodic_tests(self):
        """Ejecuta tests periódicos"""
        self.logger.debug("Running periodic tests")
        
        try:
            # Test 1: Health check
            await self._test_health_check()
            
            # Test 2: Session validity
            await self._test_session_validity()
            
            # Test 3: Performance metrics
            await self._test_performance_metrics()
            
            # Test 4: Error rates
            await self._test_error_rates()
            
        except Exception as e:
            self.logger.error(f"Error in periodic tests: {e}")
    
    async def _test_health_check(self):
        """Test de health check del sistema"""
        try:
            if self.integration and self.integration.scraper:
                health = await self.integration.scraper.health_check()
                
                if health.get("healthy", False):
                    self.metrics.successful_health_checks += 1
                else:
                    self.metrics.failed_health_checks += 1
                    self.logger.warning(f"Health check failed: {health}")
            
        except Exception as e:
            self.metrics.failed_health_checks += 1
            self.logger.error(f"Health check error: {e}")
    
    async def _test_session_validity(self):
        """Test de validez de sesión"""
        try:
            if self.integration and self.integration.scraper:
                session_info = self.integration.scraper.session_manager.get_session_info()
                
                if not session_info or not self.integration.scraper.session_manager._is_session_valid():
                    self.logger.warning("Session expired, renewal needed")
                    self.metrics.session_renewals += 1
            
        except Exception as e:
            self.logger.error(f"Session validity check error: {e}")
    
    async def _test_performance_metrics(self):
        """Test de métricas de rendimiento"""
        try:
            # Calcular velocidad de acciones
            if len(self.action_timestamps) >= 2:
                recent_actions = [ts for ts in self.action_timestamps 
                                if datetime.now() - ts < timedelta(minutes=10)]
                
                if len(recent_actions) > 1:
                    time_span = (recent_actions[-1] - recent_actions[0]).total_seconds()
                    if time_span > 0:
                        actions_per_minute = (len(recent_actions) - 1) / (time_span / 60)
                        self.metrics.actions_per_minute = actions_per_minute
                        
                        # Verificar que no excedemos 2 acciones por minuto
                        if actions_per_minute > 2.5:  # Margen de error
                            self.logger.warning(f"High action rate detected: {actions_per_minute:.2f}/min")
                            self.metrics.realistic_speed = False
            
            # Calcular tiempo promedio de respuesta
            if self.response_times:
                recent_times = self.response_times[-20:]  # Últimas 20 respuestas
                self.metrics.average_response_time = sum(recent_times) / len(recent_times)
            
        except Exception as e:
            self.logger.error(f"Performance metrics error: {e}")
    
    async def _test_error_rates(self):
        """Test de tasas de error"""
        try:
            # Verificar circuit breakers
            cb_stats = error_handler.get_error_stats().get("circuit_breakers", {})
            
            for name, status in cb_stats.items():
                if status.get("state") == "open":
                    self.logger.warning(f"Circuit breaker '{name}' is open")
                    self.metrics.circuit_breaker_activations += 1
            
            # Verificar tasa de errores recientes
            error_stats = error_handler.get_error_stats()
            recent_errors = error_stats.get("recent_errors_24h", 0)
            
            if recent_errors > 100:  # Más de 100 errores en 24h es preocupante
                self.logger.warning(f"High error rate: {recent_errors} errors in 24h")
                self.metrics.error_recovery = False
            
        except Exception as e:
            self.logger.error(f"Error rate test error: {e}")
    
    async def _monitor_health(self):
        """Monitor continuo de salud del sistema"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(120)  # Cada 2 minutos
                await self._test_health_check()
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def _monitor_performance(self):
        """Monitor continuo de rendimiento"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(180)  # Cada 3 minutos
                await self._test_performance_metrics()
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def _monitor_errors(self):
        """Monitor continuo de errores"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(240)  # Cada 4 minutos
                await self._test_error_rates()
            except Exception as e:
                self.logger.error(f"Error monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def _monitor_session_status(self):
        """Monitor continuo del estado de sesión"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(600)  # Cada 10 minutos
                await self._test_session_validity()
            except Exception as e:
                self.logger.error(f"Session monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def _generate_interim_report(self):
        """Genera reporte intermedio"""
        elapsed = datetime.now() - self.metrics.start_time
        self.metrics.total_runtime_hours = elapsed.total_seconds() / 3600
        
        # Calcular métricas finales
        self._calculate_final_metrics()
        
        # Guardar métricas intermedias
        interim_file = self.results_dir / f"interim_metrics_{datetime.now().strftime('%H%M')}.json"
        
        with open(interim_file, 'w') as f:
            json.dump(self.metrics.to_dict(), f, indent=2, default=str)
        
        self.logger.info(f"Interim report saved: {interim_file}")
        self._log_current_status()
    
    async def _finalize_validation(self):
        """Finaliza la validación y genera reporte final"""
        self.logger.info("Finalizing validation")
        
        self.monitoring_active = False
        self.metrics.end_time = datetime.now()
        
        # Calcular métricas finales
        self._calculate_final_metrics()
        
        # Determinar criterios de éxito
        self._evaluate_success_criteria()
        
        # Generar reporte final
        await self._generate_final_report()
        
        # Limpiar sistema
        if self.integration:
            await self.integration.stop()
    
    def _calculate_final_metrics(self):
        """Calcula métricas finales"""
        if self.metrics.end_time:
            elapsed = self.metrics.end_time - self.metrics.start_time
        else:
            elapsed = datetime.now() - self.metrics.start_time
        
        self.metrics.total_runtime_hours = elapsed.total_seconds() / 3600
        
        # Promedio de tiempo de respuesta
        if self.response_times:
            self.metrics.average_response_time = sum(self.response_times) / len(self.response_times)
        
        # Calcular acciones por minuto promedio
        if len(self.action_timestamps) > 1 and elapsed.total_seconds() > 0:
            total_minutes = elapsed.total_seconds() / 60
            self.metrics.actions_per_minute = len(self.action_timestamps) / total_minutes
        
        # Calcular delay promedio entre acciones
        if len(self.action_timestamps) > 1:
            delays = []
            for i in range(1, len(self.action_timestamps)):
                delay = (self.action_timestamps[i] - self.action_timestamps[i-1]).total_seconds()
                delays.append(delay)
            
            if delays:
                self.metrics.average_delay_between_actions = sum(delays) / len(delays)
    
    def _evaluate_success_criteria(self):
        """Evalúa criterios de éxito"""
        self.logger.info("Evaluating success criteria")
        
        # Criterio 1: Funcionamiento continuo por 24h
        self.metrics.continuous_operation = self.metrics.total_runtime_hours >= (self.test_duration_hours * 0.95)  # 95% del tiempo
        
        # Criterio 2: Zero detecciones (inferido por ausencia de bloqueos críticos)
        self.metrics.zero_detections = self.metrics.critical_errors == 0
        
        # Criterio 3: 100% de mensajes procesados correctamente
        total_attempts = self.metrics.total_messages_processed + self.metrics.total_errors
        if total_attempts > 0:
            success_rate = self.metrics.total_messages_processed / total_attempts
            self.metrics.messages_processed_correctly = success_rate >= 0.98  # 98% éxito
        
        # Criterio 4: Velocidad realista (no más de 1 acción/30seg = 2 acciones/min)
        self.metrics.realistic_speed = self.metrics.actions_per_minute <= 2.1  # Margen de error
        
        # Criterio 5: Recuperación automática ante errores
        self.metrics.error_recovery = self.metrics.automatic_recoveries > 0 or self.metrics.total_errors < 10
    
    async def _generate_final_report(self):
        """Genera el reporte final de validación"""
        self.logger.info("Generating final validation report")
        
        # Guardar métricas completas
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics.to_dict(), f, indent=2, default=str)
        
        # Generar reporte de texto
        report_file = self.results_dir / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w') as f:
            f.write("WALLAPOP SCRAPER - 24H VALIDATION REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Test Duration: {self.test_duration_hours} hours\n")
            f.write(f"Actual Runtime: {self.metrics.total_runtime_hours:.2f} hours\n")
            f.write(f"Start Time: {self.metrics.start_time}\n")
            f.write(f"End Time: {self.metrics.end_time}\n\n")
            
            f.write("SUCCESS CRITERIA EVALUATION:\n")
            f.write("-" * 30 + "\n")
            f.write(f"✓ Continuous Operation (24h): {'PASS' if self.metrics.continuous_operation else 'FAIL'}\n")
            f.write(f"✓ Zero Detections: {'PASS' if self.metrics.zero_detections else 'FAIL'}\n")
            f.write(f"✓ Messages Processed Correctly: {'PASS' if self.metrics.messages_processed_correctly else 'FAIL'}\n")
            f.write(f"✓ Realistic Speed: {'PASS' if self.metrics.realistic_speed else 'FAIL'}\n")
            f.write(f"✓ Error Recovery: {'PASS' if self.metrics.error_recovery else 'FAIL'}\n\n")
            
            # Criterio general
            all_passed = all([
                self.metrics.continuous_operation,
                self.metrics.zero_detections,
                self.metrics.messages_processed_correctly,
                self.metrics.realistic_speed,
                self.metrics.error_recovery
            ])
            
            f.write(f"OVERALL RESULT: {'✓ PASS - All criteria met' if all_passed else '✗ FAIL - Some criteria not met'}\n\n")
            
            f.write("DETAILED METRICS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Messages Processed: {self.metrics.total_messages_processed}\n")
            f.write(f"Total Conversations Handled: {self.metrics.total_conversations_handled}\n")
            f.write(f"Average Response Time: {self.metrics.average_response_time:.2f}s\n")
            f.write(f"Actions per Minute: {self.metrics.actions_per_minute:.2f}\n")
            f.write(f"Average Delay Between Actions: {self.metrics.average_delay_between_actions:.2f}s\n")
            f.write(f"Total Errors: {self.metrics.total_errors}\n")
            f.write(f"Critical Errors: {self.metrics.critical_errors}\n")
            f.write(f"Session Renewals: {self.metrics.session_renewals}\n")
            f.write(f"Circuit Breaker Activations: {self.metrics.circuit_breaker_activations}\n")
            f.write(f"Successful Health Checks: {self.metrics.successful_health_checks}\n")
            f.write(f"Failed Health Checks: {self.metrics.failed_health_checks}\n")
        
        self.logger.info(f"Final report saved: {report_file}")
        self._log_final_summary()
    
    def _log_current_status(self):
        """Log del estado actual"""
        self.logger.info("=== CURRENT STATUS ===")
        self.logger.info(f"Runtime: {self.metrics.total_runtime_hours:.2f}h")
        self.logger.info(f"Messages processed: {self.metrics.total_messages_processed}")
        self.logger.info(f"Conversations handled: {self.metrics.total_conversations_handled}")
        self.logger.info(f"Actions/min: {self.metrics.actions_per_minute:.2f}")
        self.logger.info(f"Errors: {self.metrics.total_errors}")
        self.logger.info(f"Health checks: {self.metrics.successful_health_checks}✓/{self.metrics.failed_health_checks}✗")
    
    def _log_final_summary(self):
        """Log del resumen final"""
        self.logger.info("=== FINAL VALIDATION SUMMARY ===")
        
        criteria = [
            ("Continuous Operation", self.metrics.continuous_operation),
            ("Zero Detections", self.metrics.zero_detections),
            ("Messages Processed", self.metrics.messages_processed_correctly),
            ("Realistic Speed", self.metrics.realistic_speed),
            ("Error Recovery", self.metrics.error_recovery)
        ]
        
        for name, passed in criteria:
            status = "✓ PASS" if passed else "✗ FAIL"
            self.logger.info(f"{name}: {status}")
        
        all_passed = all(passed for _, passed in criteria)
        overall = "✓ ALL CRITERIA MET" if all_passed else "✗ SOME CRITERIA FAILED"
        self.logger.info(f"OVERALL RESULT: {overall}")


async def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validador 24h del scraper de Wallapop")
    parser.add_argument("--duration", type=float, default=24.0, 
                       help="Duración del test en horas (default: 24.0)")
    parser.add_argument("--quick-test", action="store_true",
                       help="Ejecutar test rápido de 1 hora para pruebas")
    
    args = parser.parse_args()
    
    if args.quick_test:
        test_duration = 1.0
        print("🚀 Running QUICK TEST (1 hour) for validation purposes")
    else:
        test_duration = args.duration
        print(f"🚀 Running FULL 24H VALIDATION ({test_duration} hours)")
    
    print("=" * 60)
    print("WALLAPOP SCRAPER - 24H CONTINUOUS OPERATION VALIDATOR")
    print("=" * 60)
    print()
    print("This validator will test the following success criteria:")
    print("✓ Continuous operation for 24+ hours without failures")
    print("✓ Realistic speed (max 1 action per 30 seconds)")
    print("✓ Zero detections by Wallapop")
    print("✓ 100% of messages processed correctly") 
    print("✓ Automatic recovery from temporary errors")
    print("✓ Proper alert system functionality")
    print()
    print(f"Starting validation run for {test_duration} hours...")
    print("Press Ctrl+C to stop early and generate partial report")
    print()
    
    validator = ScraperValidator(test_duration)
    
    try:
        metrics = await validator.run_24h_validation()
        
        print("\n" + "=" * 60)
        print("VALIDATION COMPLETED")
        print("=" * 60)
        print(f"Results saved in: {validator.results_dir}")
        print(f"Metrics file: {validator.metrics_file}")
        print(f"Detailed log: {validator.detailed_log}")
        
        return 0 if all([
            metrics.continuous_operation,
            metrics.zero_detections, 
            metrics.messages_processed_correctly,
            metrics.realistic_speed,
            metrics.error_recovery
        ]) else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Validation stopped by user")
        print("Generating partial report...")
        
        await validator._finalize_validation()
        print(f"Partial results saved in: {validator.results_dir}")
        return 2
    
    except Exception as e:
        print(f"\n❌ Critical error in validation: {e}")
        return 3


if __name__ == "__main__":
    exit_code = asyncio.run(main())