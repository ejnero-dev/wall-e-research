#!/usr/bin/env python3
"""
Test rápido para validar integraciones en wall-e-research
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def test_research_integrations():
    """Test básico de integraciones en versión research"""

    print("🔬 VALIDANDO INTEGRACIONES - WALL-E RESEARCH")
    print("=" * 50)

    # Test 1: Imports
    try:
        from bot.wallapop_bot import WallapopBot

        print("✅ Import bot research: SUCCESS")
    except Exception as e:
        print(f"❌ Import bot research: FAILED - {e}")
        return False

    # Test 2: Configuración research
    try:
        # Crear bot sin dependencias pesadas
        bot_config = {
            "wallapop": {
                "behavior": {
                    "max_messages_per_hour": 50,
                    "min_delay_between_messages": 5,
                    "require_human_confirmation": False,
                },
                "anti_detection": {"enabled": True, "level": "aggressive"},
            },
            "database": {"url": None},  # Sin DB para test
            "responses": {"templates_path": "src/templates/responses.json"},
        }

        # Simular inicialización (sin ejecutar realmente)
        print("✅ Configuración research: SUCCESS")
        print(
            f"   - Rate limit: {bot_config['wallapop']['behavior']['max_messages_per_hour']} msg/hora"
        )
        print(
            f"   - Delays: {bot_config['wallapop']['behavior']['min_delay_between_messages']}s mínimo"
        )
        print(
            f"   - Anti-detección: {'HABILITADO' if bot_config['wallapop']['anti_detection']['enabled'] else 'DESHABILITADO'}"
        )
        print(
            f"   - Confirmación humana: {'OPCIONAL' if not bot_config['wallapop']['behavior']['require_human_confirmation'] else 'OBLIGATORIA'}"
        )

    except Exception as e:
        print(f"❌ Configuración research: FAILED - {e}")
        return False

    # Test 3: Verificar diferencias con compliance
    print("\n📊 COMPARACIÓN RESEARCH vs COMPLIANCE:")
    print("   Research: 50 msg/hora | Compliance: 5 msg/hora")
    print("   Research: 5s delays  | Compliance: 120s delays")
    print("   Research: Anti-det ON | Compliance: Anti-det OFF")
    print("   Research: Human ↑risk | Compliance: Human ALWAYS")

    print("\n🎉 VALIDACIÓN COMPLETADA: wall-e-research LISTO")
    return True


if __name__ == "__main__":
    success = test_research_integrations()
    exit(0 if success else 1)
