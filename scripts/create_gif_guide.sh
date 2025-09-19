#!/bin/bash
# 🎬 Script de comandos para crear GIF del Dashboard Wall-E
# Compatible con Linux, Windows (WSL) y Mac

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         🎬 GUÍA RÁPIDA PARA CREAR GIF - WALL-E                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Detectar sistema operativo
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "linux" ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="Mac"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="Windows"
else
    OS="Unknown"
fi

echo "🖥️  Sistema detectado: $OS"
echo ""

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "📋 PASOS RÁPIDOS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "1️⃣  INICIAR EL DASHBOARD:"
echo "   Terminal 1:"
echo "   cd frontend && npm run dev"
echo ""
echo "   Terminal 2:"
echo "   cd .. && uv run python -m uvicorn src.api.dashboard_server:app --reload"
echo ""

echo "2️⃣  EJECUTAR DEMO AUTOMATIZADA:"
echo "   python examples/create_dashboard_gif_demo.py"
echo ""

echo "3️⃣  HERRAMIENTAS DE CAPTURA RECOMENDADAS:"
echo ""

if [[ "$OS" == "Linux" ]]; then
    echo "   🐧 LINUX - Opciones disponibles:"
    echo ""
    
    if command_exists peek; then
        echo "   ✅ Peek está instalado"
        echo "      Comando: peek"
    else
        echo "   📦 Peek (recomendado):"
        echo "      sudo apt install peek         # Ubuntu/Debian"
        echo "      sudo dnf install peek          # Fedora"
        echo "      sudo pacman -S peek            # Arch"
    fi
    echo ""
    
    if command_exists kazam; then
        echo "   ✅ Kazam está instalado"
        echo "      Comando: kazam"
    else
        echo "   📦 Kazam:"
        echo "      sudo apt install kazam"
    fi
    echo ""
    
    echo "   📦 SimpleScreenRecorder + FFmpeg:"
    echo "      sudo apt install simplescreenrecorder ffmpeg"
    echo ""
    
elif [[ "$OS" == "Mac" ]]; then
    echo "   🍎 MAC - Opciones disponibles:"
    echo ""
    
    echo "   📦 Kap (recomendado):"
    echo "      brew install --cask kap"
    echo "      O descargar de: https://getkap.co"
    echo ""
    
    echo "   📦 Gifski:"
    echo "      brew install gifski"
    echo ""
    
    echo "   📦 GIPHY Capture:"
    echo "      Descargar de App Store"
    echo ""
    
elif [[ "$OS" == "Windows" ]]; then
    echo "   🪟 WINDOWS - Opciones disponibles:"
    echo ""
    
    echo "   📦 ScreenToGif (recomendado):"
    echo "      winget install ScreenToGif"
    echo "      O descargar de: https://www.screentogif.com"
    echo ""
    
    echo "   📦 ShareX:"
    echo "      winget install ShareX.ShareX"
    echo ""
    
    echo "   📦 LICEcap:"
    echo "      Descargar de: https://www.cockos.com/licecap/"
    echo ""
fi

echo "4️⃣  OPTIMIZACIÓN CON FFMPEG:"
echo ""

if command_exists ffmpeg; then
    echo "   ✅ FFmpeg está instalado"
else
    echo "   ⚠️  FFmpeg no detectado. Instalar con:"
    if [[ "$OS" == "Linux" ]]; then
        echo "      sudo apt install ffmpeg       # Ubuntu/Debian"
        echo "      sudo dnf install ffmpeg       # Fedora"
    elif [[ "$OS" == "Mac" ]]; then
        echo "      brew install ffmpeg"
    elif [[ "$OS" == "Windows" ]]; then
        echo "      winget install ffmpeg"
    fi
fi

echo ""
echo "   📊 Comandos de optimización:"
echo ""
echo "   # Alta calidad (10-15MB) - Mejor para portfolios"
echo "   ffmpeg -i input.mp4 -vf \"fps=20,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse\" -loop 0 output_hq.gif"
echo ""
echo "   # Calidad media (5-8MB) - Ideal para LinkedIn"
echo "   ffmpeg -i input.mp4 -vf \"fps=15,scale=800:-1:flags=lanczos\" -loop 0 output_medium.gif"
echo ""
echo "   # Comprimido (2-5MB) - Para límites estrictos"
echo "   ffmpeg -i input.mp4 -vf \"fps=10,scale=640:-1:flags=lanczos\" -loop 0 output_small.gif"
echo ""

echo "5️⃣  VERIFICACIÓN FINAL:"
echo ""
echo "   📏 Tamaño ideal LinkedIn: 5-10MB"
echo "   ⏱️  Duración óptima: 30-45 segundos"
echo "   🖼️  Resolución recomendada: 800x450 o 960x540"
echo "   🔄 FPS sugerido: 15-20"
echo ""

# Crear directorio para outputs si no existe
mkdir -p outputs/gifs

echo "📁 Los GIFs se guardarán en: $(pwd)/outputs/gifs/"
echo ""

echo "🚀 COMANDO RÁPIDO TODO-EN-UNO:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "# Copiar y pegar en terminal:"
echo ""
echo "cd frontend && npm run dev &"
echo "sleep 3"
echo "cd .. && uv run python -m uvicorn src.api.dashboard_server:app --reload &"
echo "sleep 5"
echo "python examples/create_dashboard_gif_demo.py"
echo ""

# Función para crear un GIF de prueba rápido (si tienen las herramientas)
create_test_gif() {
    echo "🧪 Creando GIF de prueba..."
    
    # Aquí podrías agregar comandos específicos según el OS
    if [[ "$OS" == "Linux" ]] && command_exists peek; then
        echo "Abriendo Peek para captura..."
        peek &
    elif [[ "$OS" == "Mac" ]] && command_exists kap; then
        echo "Abriendo Kap para captura..."
        open -a Kap
    elif [[ "$OS" == "Windows" ]]; then
        echo "Por favor, abre ScreenToGif manualmente"
    fi
}

echo "💡 TIPS FINALES:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "• Cierra otras aplicaciones para mejorar rendimiento"
echo "• Usa modo incógnito en el navegador"
echo "• Ajusta zoom del navegador a 100%"
echo "• Graba en resolución nativa, luego escala"
echo "• Movimientos suaves del mouse"
echo "• Pausas de 1-2s entre acciones"
echo ""

echo "✨ ¡Listo para crear tu GIF profesional!"
echo ""
echo "¿Iniciar herramienta de captura? (s/n): "
read -r response

if [[ "$response" == "s" ]] || [[ "$response" == "S" ]]; then
    create_test_gif
fi

echo ""
echo "📌 Script completado. ¡Buena suerte con tu post de LinkedIn!"
