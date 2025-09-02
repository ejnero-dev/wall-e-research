#!/bin/bash

# Script para iniciar el dashboard completo Wall-E Research
# Backend API + Frontend UI

echo "🤖 Iniciando Wall-E Research Dashboard..."
echo "========================================="

# Verificar dependencias
echo "📋 Verificando dependencias..."

# Verificar Python y dependencias del backend
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt no encontrado"
    exit 1
fi

# Verificar Node.js y dependencias del frontend
if ! command -v npm &> /dev/null; then
    echo "❌ npm no está instalado"
    exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Dependencias del frontend no instaladas. Ejecutando npm install..."
    cd frontend && npm install && cd ..
fi

echo "✅ Dependencias verificadas"

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo servicios..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend detenido"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend detenido"
    fi
    echo "👋 Dashboard detenido"
    exit 0
}

# Configurar trap para cleanup
trap cleanup SIGINT SIGTERM

# Iniciar Backend API
echo ""
echo "🚀 Iniciando Backend API (puerto 8000)..."
uv run python -m uvicorn src.api.dashboard_server:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Esperar a que el backend se inicie
echo "⏳ Esperando a que el backend se inicie..."
sleep 3

# Verificar que el backend está corriendo
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "⚠️  Backend tardando en iniciarse, continuando..."
fi

# Iniciar Frontend UI
echo ""
echo "🎨 Iniciando Frontend UI (puerto 8080)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Dashboard iniciado exitosamente!"
echo ""
echo "🌐 URLs disponibles:"
echo "   • Frontend UI:  http://localhost:8080"
echo "   • Backend API:  http://localhost:8000"
echo "   • API Docs:     http://localhost:8000/docs"
echo "   • Health Check: http://localhost:8000/api/dashboard/health"
echo ""
echo "📊 Funcionalidades disponibles:"
echo "   • Métricas en tiempo real (WebSocket)"
echo "   • Gestión de productos Wallapop"
echo "   • Auto-detección de productos"
echo "   • Respuestas automáticas configurables"
echo "   • Monitoreo de scrapers"
echo ""
echo "🛑 Presiona Ctrl+C para detener el dashboard"
echo ""

# Esperar indefinidamente (los procesos siguen en background)
wait $FRONTEND_PID