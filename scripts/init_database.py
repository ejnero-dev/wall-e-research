#!/usr/bin/env python3
"""
Database initialization script for Wallapop Bot
Run this script to set up the database for the first time
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.config import DatabaseConfig
from src.database.db_manager import DatabaseManager
from src.database.models import ProductStatus, ConversationStatus, MessageType


def main():
    """Initialize the database"""
    print("🚀 Initializing Wallapop Bot Database...")

    # Load configuration
    try:
        config = DatabaseConfig()
        database_url = config.get_database_url()

        print(f"📊 Connecting to database...")
        print(
            f"   URL: {database_url.replace(database_url.split('@')[0].split('://')[-1], '***')}"
        )

    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return 1

    # Test connections
    print("🔍 Testing connections...")
    connections = config.validate_connection()

    if not connections["database"]:
        print("❌ Database connection failed!")
        print("   Make sure PostgreSQL is running and credentials are correct")
        return 1
    else:
        print("✅ Database connection successful")

    if not connections["redis"]:
        print("⚠️  Redis connection failed!")
        print("   Redis is optional for basic functionality")
    else:
        print("✅ Redis connection successful")

    # Initialize database manager
    try:
        db_manager = DatabaseManager(database_url, echo=True)

        # Create tables
        print("📋 Creating database tables...")
        db_manager.create_tables()
        print("✅ Tables created successfully")

        # Create sample data for testing (optional)
        if "--sample-data" in sys.argv:
            print("📝 Creating sample data...")
            create_sample_data(db_manager)
            print("✅ Sample data created")

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    print("\n🎉 Database initialization completed successfully!")
    print("\nNext steps:")
    print("1. Start the bot: python -m src.bot.wallapop_bot")
    print("2. Run tests: pytest tests/")
    print(
        "3. Check database with: docker exec -it wallapop_postgres psql -U wallapop_user -d wallapop_bot"
    )

    return 0


def create_sample_data(db_manager: DatabaseManager):
    """Create sample data for testing"""

    # Create sample product
    product = db_manager.create_product(
        wallapop_id="test_product_001",
        title="iPhone 13 Pro 128GB",
        description="iPhone 13 Pro en perfecto estado, apenas usado. Incluye cargador original.",
        price=650.0,
        currency="EUR",
        status=ProductStatus.AVAILABLE,
        category="Móviles y telefonía",
        condition="like_new",
        location="Madrid, España",
    )
    print(f"   Created product: {product.title}")

    # Create sample buyer
    buyer = db_manager.create_or_update_buyer(
        wallapop_user_id="test_buyer_001",
        username="juan_comprador",
        display_name="Juan Pérez",
        is_verified=True,
    )
    print(f"   Created buyer: {buyer.username}")

    # Create sample conversation
    conversation = db_manager.create_conversation(
        wallapop_chat_id="test_chat_001", product_id=product.id, buyer_id=buyer.id
    )
    print(f"   Created conversation: {conversation.id}")

    # Create sample messages
    db_manager.create_message(
        conversation_id=conversation.id,
        content="¡Hola! Me interesa tu iPhone. ¿Está disponible?",
        message_type=MessageType.USER_MESSAGE,
        buyer_id=buyer.id,
        intent="inquiry",
    )

    db_manager.create_message(
        conversation_id=conversation.id,
        content="¡Hola! Sí, el iPhone está disponible. ¿Tienes alguna pregunta específica?",
        message_type=MessageType.BOT_MESSAGE,
        intent="response",
    )

    print("   Created sample messages")


if __name__ == "__main__":
    sys.exit(main())
