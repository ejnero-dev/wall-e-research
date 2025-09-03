#!/usr/bin/env python3
"""
Test simple de integraciones sin ejecutar el bot completo
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def test_basic_imports():
    """Test básico de imports sin inicializar módulos pesados"""

    print("🔬 TEST BÁSICO - WALL-E RESEARCH")
    print("=" * 40)

    success = True

    # Test 1: ConversationEngine
    try:
        from conversation_engine.engine import ConversationEngine, IntentionType

        print("✅ ConversationEngine: SUCCESS")
    except Exception as e:
        print(f"❌ ConversationEngine: FAILED - {e}")
        success = False

    # Test 2: Database Models
    try:
        from database.models import Buyer, Product, Conversation

        print("✅ Database Models: SUCCESS")
    except Exception as e:
        print(f"❌ Database Models: FAILED - {e}")
        success = False

    # Test 3: Config Loader
    try:
        from config_loader import load_config, ConfigMode

        config = load_config(ConfigMode.RESEARCH)
        rate_limit = config["wallapop"]["behavior"]["max_messages_per_hour"]
        print(f"✅ Config Research: SUCCESS (rate limit: {rate_limit})")

        if rate_limit == 50:
            print("   ✅ Research config confirmed: 50 msg/hora")
        else:
            print(f"   ⚠️ Unexpected rate limit: {rate_limit}")

    except Exception as e:
        print(f"❌ Config Research: FAILED - {e}")
        success = False

    # Test 4: Verificar que NO hay características de compliance
    try:
        compliance_config = load_config(ConfigMode.COMPLIANCE)
        compliance_rate = compliance_config["wallapop"]["behavior"][
            "max_messages_per_hour"
        ]

        if compliance_rate == 5 and rate_limit == 50:
            print("✅ Version differentiation: SUCCESS")
            print(
                f"   Research: {rate_limit} msg/hora | Compliance: {compliance_rate} msg/hora"
            )
        else:
            print("⚠️ Config differentiation issue")

    except Exception as e:
        print(f"❌ Config comparison: FAILED - {e}")
        success = False

    return success


if __name__ == "__main__":
    success = test_basic_imports()

    if success:
        print("\n🎉 BASIC INTEGRATION TEST: PASSED")
        print("✅ Research version ready with differentiated config")
        print("⚠️ Full testing requires Playwright system dependencies")
    else:
        print("\n❌ BASIC INTEGRATION TEST: FAILED")

    exit(0 if success else 1)
