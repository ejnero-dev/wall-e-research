# 🛠️ Development Setup Guide

## 📦 Package Management with uv

Este proyecto utiliza **uv** como gestor de paquetes por su velocidad superior (10-100x más rápido que pip).

### Instalación de uv (si no está instalado)

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# O con pip
pip install uv
```

### Configuración del Entorno Virtual

```bash
# 1. Crear entorno virtual con uv
uv venv

# 2. Activar el entorno
# Linux/macOS:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

# 3. Instalar dependencias
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt

# 4. Instalar modelos de spaCy
uv pip install spacy
python -m spacy download es_core_news_sm

# 5. Instalar navegadores de Playwright
playwright install chromium
```

### Comandos Frecuentes con uv

```bash
# Instalar un paquete
uv pip install <package>

# Instalar desde requirements
uv pip install -r requirements.txt

# Actualizar un paquete
uv pip install --upgrade <package>

# Listar paquetes instalados
uv pip list

# Crear requirements.txt actualizado
uv pip freeze > requirements.txt
```

### Verificación del Entorno

```bash
# Verificar que el entorno está activo
which python
# Debería mostrar: /home/emilio/project-wall-e/.venv/bin/python

# Verificar instalación
python -c "import spacy; print('✅ spaCy instalado')"
python -c "import playwright; print('✅ Playwright instalado')"
python -c "import sqlalchemy; print('✅ SQLAlchemy instalado')"
```

## 🔧 Configuración de Base de Datos

```bash
# 1. Iniciar servicios con Docker
docker-compose up -d

# 2. Verificar que están corriendo
docker-compose ps

# 3. Inicializar base de datos
python scripts/init_database.py
```

## 🚀 Comandos de Desarrollo

### Tests
```bash
# Ejecutar todos los tests
pytest tests/ -v

# Tests con coverage
pytest tests/ --cov=src --cov-report=html

# Tests específicos
pytest tests/unit/test_conversation_engine.py -v
```

### Linting y Formato
```bash
# Formatear código
black src/ tests/

# Verificar estilo
flake8 src/ tests/

# Type checking
mypy src/
```

### Ejecución del Bot
```bash
# Modo desarrollo con logs
python src/bot/wallapop_bot.py --debug

# Demo del Happy Path
python scripts/happy_path_demo.py

# Verificar sistema
python scripts/quick_start.py --check
```

## 📝 Notas Importantes

1. **SIEMPRE** activar el entorno virtual antes de trabajar:
   ```bash
   source .venv/bin/activate
   ```

2. **NUNCA** commitear el directorio `.venv/`:
   - Ya está en `.gitignore`
   - Cada desarrollador crea su propio entorno

3. **Actualizar requirements.txt** al agregar dependencias:
   ```bash
   uv pip freeze > requirements.txt
   ```

4. **Variables de entorno** en `.env`:
   ```bash
   cp .env.example .env
   # Editar con tus credenciales
   ```

## 🐛 Troubleshooting

### Error: "uv: command not found"
```bash
# Reinstalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# Agregar al PATH si es necesario
export PATH="$HOME/.cargo/bin:$PATH"
```

### Error: "No module named 'spacy'"
```bash
# Verificar entorno activo
which python
# Reinstalar dependencias
uv pip install -r requirements.txt
```

### Error con Playwright
```bash
# Reinstalar navegadores
playwright install chromium
# O todos los navegadores
playwright install
```

### Base de datos no conecta
```bash
# Verificar Docker
docker-compose ps
# Reiniciar servicios
docker-compose down
docker-compose up -d
# Verificar logs
docker-compose logs postgres
```

---

*Última actualización: Fase 1 - Scraper Prioritario*