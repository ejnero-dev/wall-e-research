# 🚀 Guía de Instalación - Wallapop Automation Bot

## 📋 Requisitos Previos

### Sistema Operativo
- Ubuntu 20.04+ / Debian 10+ (recomendado)
- Windows 10/11 con WSL2
- macOS 11+

### Software Necesario
- Python 3.11 o superior
- PostgreSQL 14+
- Redis 6+
- Git
- Docker y Docker Compose (opcional pero recomendado)

## 🛠️ Instalación Paso a Paso

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/wallapop-automation-project.git
cd wallapop-automation-project
```

### 2. Crear Entorno Virtual
```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias Python
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Instalar y Configurar PostgreSQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Crear usuario y base de datos
sudo -u postgres psql
CREATE USER wallapop_user WITH PASSWORD 'tu_password_seguro';
CREATE DATABASE wallapop_bot OWNER wallapop_user;
GRANT ALL PRIVILEGES ON DATABASE wallapop_bot TO wallapop_user;
\q
```

### 5. Instalar y Configurar Redis
```bash
# Ubuntu/Debian
sudo apt install redis-server

# Verificar que está funcionando
redis-cli ping
# Debería responder: PONG
```

### 6. Instalar Playwright (para automatización web)
```bash
# Instalar Playwright
pip install playwright

# Instalar navegadores
playwright install chromium
playwright install-deps
```

### 7. Configurar spaCy para NLP
```bash
# Descargar modelo en español
python -m spacy download es_core_news_sm

# Para un modelo más grande y preciso (opcional)
python -m spacy download es_core_news_md
```

### 8. Configurar Ollama para IA Local (Opcional)
```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar modelo
ollama pull llama2:7b
# o para un modelo más pequeño
ollama pull mistral:7b

# Verificar
ollama list
```

### 9. Configurar el Bot
```bash
# Copiar configuración de ejemplo
cp config/config.example.yaml config/config.yaml

# Editar configuración
nano config/config.yaml
```

Configuración mínima necesaria:
```yaml
database:
  host: "localhost"
  port: 5432
  name: "wallapop_bot"
  user: "wallapop_user"
  password: "tu_password_seguro"

redis:
  host: "localhost"
  port: 6379

wallapop:
  auth_method: "cookies"  # Necesitarás las cookies de tu sesión
```

### 10. Obtener Cookies de Wallapop
1. Inicia sesión en Wallapop desde tu navegador
2. Abre las herramientas de desarrollador (F12)
3. Ve a la pestaña "Application" o "Storage"
4. Busca las cookies de wallapop.com
5. Copia las cookies necesarias a un archivo `cookies.json`

### 11. Inicializar la Base de Datos
```bash
# Ejecutar migraciones
python scripts/init_database.py
```

### 12. Verificar la Instalación
```bash
# Test de componentes
python scripts/test_installation.py
```

## 🐳 Instalación con Docker (Alternativa)

### 1. Construir y Ejecutar con Docker Compose
```bash
# Construir imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 2. Archivo docker-compose.yml
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: wallapop_user
      POSTGRES_PASSWORD: secure_password
      POSTGRES_DB: wallapop_bot
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  bot:
    build: .
    depends_on:
      - postgres
      - redis
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
      - ./data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped

volumes:
  postgres_data:
```

## 🔧 Configuración Adicional

### Prometheus y Grafana (Monitoreo)
```bash
# Prometheus
docker run -d -p 9090:9090 \
  -v $(pwd)/config/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Grafana
docker run -d -p 3000:3000 grafana/grafana
```

### Configurar Backups Automáticos
```bash
# Añadir a crontab
crontab -e

# Backup diario a las 3 AM
0 3 * * * /path/to/project/scripts/backup.sh
```

## 🚦 Primeros Pasos

### 1. Ejecutar el Bot
```bash
# Modo normal
python src/bot/wallapop_bot.py

# Modo debug
python src/bot/wallapop_bot.py --debug

# Con logs detallados
python src/bot/wallapop_bot.py --log-level DEBUG
```

### 2. Verificar Dashboard
Abre http://localhost:8000 en tu navegador

### 3. Monitorear Logs
```bash
# Logs en tiempo real
tail -f logs/wallapop_bot.log

# Logs de errores
tail -f logs/errors.log
```

## ❗ Solución de Problemas

### Error: "No module named 'spacy'"
```bash
pip install spacy
python -m spacy download es_core_news_sm
```

### Error: "PostgreSQL connection refused"
```bash
# Verificar que PostgreSQL está ejecutándose
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### Error: "Redis connection refused"
```bash
# Verificar Redis
sudo systemctl status redis
sudo systemctl start redis-server
```

### Error: "Playwright browser not found"
```bash
playwright install chromium
playwright install-deps
```

## 📚 Recursos Adicionales

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Guía de Playwright](https://playwright.dev/python/)
- [spaCy en Español](https://spacy.io/models/es)
- [Ollama Docs](https://github.com/jmorganca/ollama)

## 🤝 Soporte

Si encuentras problemas durante la instalación:
1. Revisa los logs en `/logs/installation.log`
2. Abre un issue en el repositorio
3. Contacta en el canal de soporte

---

¡Felicidades! Tu bot de Wallapop está listo para usar. 🎉
