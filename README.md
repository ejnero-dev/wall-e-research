# 🤖 Wallapop Automation Project

[![CI/CD Pipeline](https://github.com/USERNAME/REPOSITORY/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/USERNAME/REPOSITORY/actions)
[![Coverage](https://codecov.io/gh/USERNAME/REPOSITORY/branch/main/graph/badge.svg)](https://codecov.io/gh/USERNAME/REPOSITORY)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## 📋 Descripción
Sistema de automatización para gestionar ventas en Wallapop, centrado principalmente en la gestión inteligente de conversaciones con compradores potenciales.

## 🎯 Objetivos Principales
- Automatizar respuestas a compradores
- Detectar intenciones de compra
- Priorizar conversaciones importantes
- Maximizar conversiones de venta
- Evitar estafas y fraudes

## 🛠️ Stack Tecnológico (100% Open Source & Self-Hosted)

### Backend
- **Python 3.11+** - Lenguaje principal
- **FastAPI** - Framework web asíncrono
- **PostgreSQL** - Base de datos principal
- **Redis** - Cache y gestión de sesiones
- **Celery** - Cola de tareas asíncronas

### Automatización & Scraping
- **Playwright** - Automatización del navegador
- **BeautifulSoup4** - Parsing HTML
- **Selenium** (alternativa) - Si Playwright falla

### NLP & IA (Self-Hosted)
- **spaCy** - Procesamiento de lenguaje natural
- **Rasa Open Source** - Motor conversacional
- **Ollama** - LLMs locales (Llama2, Mistral)
- **Chroma** - Base de datos vectorial

### Frontend
- **React** - Interface de usuario
- **Tailwind CSS** - Estilos
- **Chart.js** - Gráficos y métricas
- **Socket.io** - Comunicación en tiempo real

### Infraestructura
- **Docker & Docker Compose** - Contenedorización
- **Nginx** - Proxy reverso
- **Prometheus + Grafana** - Monitoreo
- **MinIO** - Almacenamiento de objetos (S3 compatible)

## 📁 Estructura del Proyecto
```
wallapop-automation-project/
├── docs/                    # Documentación
├── src/                     # Código fuente
│   ├── bot/                # Lógica del bot
│   ├── conversation_engine/ # Motor de conversaciones
│   ├── price_analyzer/     # 🆕 Análisis de precios
│   └── templates/          # Plantillas de respuestas
├── config/                 # Configuraciones
├── docker/                 # Archivos Docker
├── tests/                  # Tests unitarios
└── scripts/               # Scripts de utilidad
```

## 🚀 Instalación
Documentación completa en `/docs/installation.md`

### 🔧 Desarrollo
```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt -r requirements-dev.txt

# Instalar pre-commit hooks
pre-commit install

# Ejecutar tests
pytest

# Ejecutar tests con coverage
pytest --cov=src --cov-report=html

# Formatear código
black src/ tests/

# Linting
flake8 src/ tests/

# Chequeos de seguridad
bandit -r src/
```

## 🔄 CI/CD Pipeline
El proyecto incluye un pipeline completo de CI/CD con GitHub Actions que incluye:

- **Calidad de código**: Black, Flake8, MyPy
- **Tests**: Pytest con cobertura en múltiples versiones de Python (3.11, 3.12)
- **Seguridad**: Bandit para análisis de vulnerabilidades, Safety para dependencias
- **Servicios**: PostgreSQL y Redis para tests de integración
- **Artefactos**: Reportes de cobertura, seguridad y dependencias
- **Cache**: Optimización de dependencias para builds más rápidos

El pipeline se ejecuta automáticamente en:
- Push a main/master
- Pull requests a main/master

## 📊 Características Principales
- Gestión inteligente de conversaciones
- Detección de intenciones de compra
- Sistema anti-fraude
- 🆕 **Análisis de precios competitivos** (Wallapop, Amazon, eBay)
- 🆕 **Sugerencias de precio óptimo** según estrategia de venta
- Dashboard de métricas
- Multi-cuenta (futuro)

## ⚖️ Consideraciones Legales
Este proyecto está diseñado para cumplir con los ToS de Wallapop y las leyes de protección de datos.

## 📚 Documentación
- [Instalación](./docs/installation.md)
- [Sistema de Conversaciones](./docs/conversation-system.md)
- [Guía Anti-Fraude](./docs/anti-fraud-guide.md)
- [🆕 Sistema de Análisis de Precios](./docs/price-analysis-system.md)
- [API Reference](./docs/api-reference.md)
