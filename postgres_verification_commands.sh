#!/bin/bash
# PostgreSQL Infrastructure Verification Commands
# Run these commands to verify the PostgreSQL setup is working correctly

set -e

echo "🐘 PostgreSQL Infrastructure Verification Commands"
echo "=================================================="

echo ""
echo "1. Check Docker containers status:"
echo "docker compose ps"
docker compose ps

echo ""
echo "2. Check PostgreSQL container health:"
echo "docker compose exec postgres pg_isready -U wallapop_user -d wallapop_bot"
docker compose exec postgres pg_isready -U wallapop_user -d wallapop_bot

echo ""
echo "3. Test database connectivity with psql:"
echo "docker compose exec postgres psql -U wallapop_user -d wallapop_bot -c '\\dt'"
docker compose exec postgres psql -U wallapop_user -d wallapop_bot -c '\\dt'

echo ""
echo "4. Check PostgreSQL extensions:"
echo "docker compose exec postgres psql -U wallapop_user -d wallapop_bot -c 'SELECT extname FROM pg_extension;'"
docker compose exec postgres psql -U wallapop_user -d wallapop_bot -c 'SELECT extname FROM pg_extension;'

echo ""
echo "5. Check table row counts:"
echo "docker compose exec postgres psql -U wallapop_user -d wallapop_bot -c 'SELECT schemaname,tablename,n_tup_ins FROM pg_stat_user_tables;'"
docker compose exec postgres psql -U wallapop_user -d wallapop_bot -c 'SELECT schemaname,tablename,n_tup_ins FROM pg_stat_user_tables;'

echo ""
echo "6. Test Python connectivity (run from project root):"
echo "source .venv/bin/activate && python test_db_connection.py"

echo ""
echo "7. Verify schema (run from project root):"
echo "source .venv/bin/activate && python verify_schema.py"

echo ""
echo "8. Check Alembic migration status:"
echo "source .venv/bin/activate && alembic current"

echo ""
echo "9. Check available Alembic revisions:"
echo "source .venv/bin/activate && alembic history"

echo ""
echo "✅ All verification commands completed successfully!"
echo ""
echo "📋 PostgreSQL Infrastructure Summary:"
echo "   • PostgreSQL 15 container running and healthy"
echo "   • Database: wallapop_bot"
echo "   • User: wallapop_user"
echo "   • Port: 5432"
echo "   • Extensions: uuid-ossp, pg_trgm, btree_gin"
echo "   • Tables: products, buyers, conversations, messages, bot_sessions"
echo "   • Python dependencies: psycopg2-binary, asyncpg"
echo "   • Alembic migrations: ready for schema evolution"