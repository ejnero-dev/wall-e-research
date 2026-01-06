#!/usr/bin/env python3
"""
Database management utility script
Provides commands for common database operations
"""
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.config import DatabaseConfig
from src.database.db_manager import DatabaseManager


def setup_database(args):
    """Initialize database tables"""
    config = DatabaseConfig()
    db_manager = DatabaseManager(config.get_database_url(), echo=args.verbose)

    print("Creating database tables...")
    db_manager.create_tables()
    print("✅ Database tables created successfully!")


def drop_database(args):
    """Drop all database tables"""
    if not args.force:
        confirm = input("⚠️  This will DELETE ALL DATA! Are you sure? (yes/no): ")
        if confirm.lower() != "yes":
            print("Cancelled.")
            return

    config = DatabaseConfig()
    db_manager = DatabaseManager(config.get_database_url(), echo=args.verbose)

    print("Dropping database tables...")
    db_manager.drop_tables()
    print("✅ Database tables dropped!")


def show_stats(args):
    """Show database statistics"""
    config = DatabaseConfig()
    db_manager = DatabaseManager(config.get_database_url(), echo=args.verbose)

    # Get today's stats
    today_stats = db_manager.get_daily_stats()

    # Get yesterday's stats for comparison
    yesterday = datetime.utcnow().date() - timedelta(days=1)
    yesterday_stats = db_manager.get_daily_stats(yesterday)

    print("📊 Database Statistics")
    print("=" * 50)
    print(f"📅 Date: {today_stats['date']}")
    print(
        f"💬 Conversations created: {today_stats['conversations_created']} (yesterday: {yesterday_stats['conversations_created']})"
    )
    print(
        f"📝 Messages sent: {today_stats['messages_sent']} (yesterday: {yesterday_stats['messages_sent']})"
    )
    print(
        f"👥 Active buyers: {today_stats['active_buyers']} (yesterday: {yesterday_stats['active_buyers']})"
    )
    print(
        f"✅ Completed sales: {today_stats['completed_sales']} (yesterday: {yesterday_stats['completed_sales']})"
    )

    # Get overall stats
    with db_manager.get_session() as session:
        from src.database.models import Product, Buyer, Conversation, Message

        total_products = session.query(Product).count()
        total_buyers = session.query(Buyer).count()
        total_conversations = session.query(Conversation).count()
        total_messages = session.query(Message).count()

        print("\n📈 Overall Statistics")
        print("=" * 50)
        print(f"🛍️  Total products: {total_products}")
        print(f"👥 Total buyers: {total_buyers}")
        print(f"💬 Total conversations: {total_conversations}")
        print(f"📝 Total messages: {total_messages}")


def cleanup_sessions(args):
    """Clean up old bot sessions"""
    config = DatabaseConfig()
    db_manager = DatabaseManager(config.get_database_url(), echo=args.verbose)

    days = args.days or 7
    print(f"Cleaning up bot sessions older than {days} days...")

    db_manager.cleanup_old_sessions(days)
    print("✅ Old sessions cleaned up!")


def test_connections(args):
    """Test database and Redis connections"""
    config = DatabaseConfig()

    print("🔍 Testing connections...")
    results = config.validate_connection()

    if results["database"]:
        print("✅ PostgreSQL connection: OK")
    else:
        print("❌ PostgreSQL connection: FAILED")

    if results["redis"]:
        print("✅ Redis connection: OK")
    else:
        print("❌ Redis connection: FAILED")

    if all(results.values()):
        print("\n🎉 All connections successful!")
    else:
        print("\n⚠️  Some connections failed. Check your configuration.")


def export_data(args):
    """Export data to JSON"""
    import json
    from src.database.models import Product, Buyer, Conversation, Message

    config = DatabaseConfig()
    db_manager = DatabaseManager(config.get_database_url(), echo=args.verbose)

    output_file = (
        args.output
        or f"wallapop_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    data = {
        "exported_at": datetime.utcnow().isoformat(),
        "products": [],
        "buyers": [],
        "conversations": [],
        "messages": [],
    }

    with db_manager.get_session() as session:
        # Export products
        for product in session.query(Product).all():
            data["products"].append(
                {
                    "id": product.id,
                    "wallapop_id": product.wallapop_id,
                    "title": product.title,
                    "price": product.price,
                    "status": product.status.value,
                    "created_at": product.created_at.isoformat(),
                }
            )

        # Export buyers (limited info for privacy)
        for buyer in session.query(Buyer).all():
            data["buyers"].append(
                {
                    "id": buyer.id,
                    "username": buyer.username,
                    "is_verified": buyer.is_verified,
                    "is_blocked": buyer.is_blocked,
                    "total_conversations": buyer.total_conversations,
                    "created_at": buyer.created_at.isoformat(),
                }
            )

        # Export conversations
        for conv in session.query(Conversation).all():
            data["conversations"].append(
                {
                    "id": conv.id,
                    "product_id": conv.product_id,
                    "buyer_id": conv.buyer_id,
                    "status": conv.status.value,
                    "message_count": conv.message_count,
                    "created_at": conv.created_at.isoformat(),
                }
            )

        # Export messages (last 1000 for size)
        for msg in (
            session.query(Message).order_by(Message.created_at.desc()).limit(1000)
        ):
            data["messages"].append(
                {
                    "id": msg.id,
                    "conversation_id": msg.conversation_id,
                    "message_type": msg.message_type.value,
                    "intent": msg.intent,
                    "sentiment": msg.sentiment,
                    "created_at": msg.created_at.isoformat(),
                }
            )

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Data exported to: {output_file}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Wallapop Bot Database Manager")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Initialize database tables")
    setup_parser.set_defaults(func=setup_database)

    # Drop command
    drop_parser = subparsers.add_parser("drop", help="Drop all database tables")
    drop_parser.add_argument("--force", action="store_true", help="Skip confirmation")
    drop_parser.set_defaults(func=drop_database)

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show database statistics")
    stats_parser.set_defaults(func=show_stats)

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old bot sessions")
    cleanup_parser.add_argument("--days", type=int, help="Days to keep (default: 7)")
    cleanup_parser.set_defaults(func=cleanup_sessions)

    # Test command
    test_parser = subparsers.add_parser(
        "test", help="Test database and Redis connections"
    )
    test_parser.set_defaults(func=test_connections)

    # Export command
    export_parser = subparsers.add_parser("export", help="Export data to JSON")
    export_parser.add_argument("-o", "--output", help="Output filename")
    export_parser.set_defaults(func=export_data)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        args.func(args)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
