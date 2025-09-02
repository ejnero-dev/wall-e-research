#!/bin/bash

# Wall-E Dashboard Setup Script
# Prepares both backend API and frontend for development

set -e  # Exit on error

echo "╔════════════════════════════════════════════╗"
echo "║  Wall-E Dashboard Setup                    ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check current directory
if [[ ! "$PWD" == *"wall-e-research"* ]]; then
    print_error "Please run this script from /home/emilio/wall-e-research/"
    exit 1
fi

echo "📦 Installing Backend Dependencies..."
echo "────────────────────────────────────"

# Install Python dependencies
if command -v pip &> /dev/null; then
    pip install -q -r src/api/requirements.txt
    print_status "Python dependencies installed"
else
    print_error "pip not found. Please install Python and pip."
    exit 1
fi

echo ""
echo "🔧 Checking Services..."
echo "────────────────────────────────────"

# Check if Redis is installed and running
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        print_status "Redis is running"
    else
        print_warning "Redis installed but not running. Starting Redis..."
        redis-server --daemonize yes
        sleep 2
        if redis-cli ping &> /dev/null; then
            print_status "Redis started successfully"
        else
            print_warning "Could not start Redis. Dashboard will use mock data."
        fi
    fi
else
    print_warning "Redis not installed. Dashboard will use mock data."
    echo "  To install: sudo apt-get install redis-server"
fi

echo ""
echo "🚀 Starting Dashboard API..."
echo "────────────────────────────────────"

# Start the API server in background
python src/api/dashboard_server.py &
API_PID=$!

# Wait for server to start
sleep 3

# Check if server is running
if curl -s http://localhost:8000/api/dashboard/health > /dev/null; then
    print_status "Dashboard API running at http://localhost:8000"
    print_status "API Documentation at http://localhost:8000/docs"
else
    print_error "Failed to start Dashboard API"
    exit 1
fi

echo ""
echo "🧪 Running API Tests..."
echo "────────────────────────────────────"

# Run the test suite
python src/api/test_dashboard.py

echo ""
echo "📝 Next Steps for Claude Code:"
echo "────────────────────────────────────"
echo ""
echo "1. Create the frontend project:"
echo "   ${GREEN}cd /home/emilio/${NC}"
echo "   ${GREEN}npx create-next-app@latest wall-e-dashboard --typescript --tailwind --app${NC}"
echo ""
echo "2. The API is running at:"
echo "   - REST API: ${GREEN}http://localhost:8000${NC}"
echo "   - WebSocket: ${GREEN}ws://localhost:8000/api/dashboard/ws/live${NC}"
echo "   - API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo "3. Reference the UI design guide at:"
echo "   ${GREEN}/home/emilio/project-wall-e/docs/dashboard/UI_DESIGN_GUIDE.md${NC}"
echo ""
echo "4. Follow the implementation plan at:"
echo "   ${GREEN}/home/emilio/project-wall-e/docs/dashboard/IMPLEMENTATION_PLAN.md${NC}"
echo ""

# Keep the script running to maintain the API server
echo "────────────────────────────────────"
echo "Press Ctrl+C to stop the Dashboard API"
echo ""

# Wait for user to stop
wait $API_PID
