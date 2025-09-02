# 🤖 Wall-E Research Dashboard

Dashboard integrado desarrollado con **React 18 + TypeScript** conectado al backend **FastAPI** de Wall-E Research para automatización inteligente de Wallapop.

## 🚀 Inicio Rápido

### Método 1: Script Automático (Recomendado)
```bash
# Ejecutar el dashboard completo
./start_dashboard.sh
```

### Método 2: Manual
```bash
# Terminal 1 - Backend API
python -m uvicorn src.api.dashboard_server:app --reload --port 8000

# Terminal 2 - Frontend UI  
cd frontend && npm run dev
```

## 🌐 URLs del Sistema

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend Dashboard** | http://localhost:3000 | Interfaz principal del usuario |
| **Backend API** | http://localhost:8000 | API REST endpoints |
| **API Documentation** | http://localhost:8000/docs | Swagger/OpenAPI docs |
| **WebSocket Live** | ws://localhost:8000/api/dashboard/ws/live | Datos en tiempo real |
| **Health Check** | http://localhost:8000/api/dashboard/health | Estado del sistema |

## ✨ Características Implementadas

### 🎯 **Componentes Principales**

#### **1. QuickStats - Métricas en Tiempo Real**
- Anuncios activos con contador dinámico
- Mensajes por hora desde backend
- Ingresos del mes con datos reales
- Tasa de éxito de scrapers
- **Actualización:** Cada 5 segundos via React Query + WebSocket

#### **2. ActiveListings - Gestión de Productos**
- Lista productos desde `/api/dashboard/products`
- Estados: activo, pausado, vendido, expirado
- Vistas y mensajes en tiempo real
- Badges de estado con colores temáticos
- **Funcional:** Conectado a backend research

#### **3. AutomatedResponses - Respuestas Inteligentes**
- Switch maestro para activar/desactivar
- Configuración desde `/api/dashboard/config/current`
- Templates de respuesta con contadores de uso
- Indicadores visuales de estado activo/inactivo
- **Integración:** Hot-reload configuration

#### **4. AutoDetectionPanel - Detección Automática**
- Control start/stop del sistema de auto-detección
- Productos detectados en tiempo real
- Estadísticas de escaneo y éxito
- Escaneo manual con un click
- **Conectado:** `/api/dashboard/auto-detection/*`

### 🔧 **Sistema de Navegación Profesional**
- **Sidebar colapsable** con badges dinámicos
- **Breadcrumbs contextuales** para orientación
- **Connection status** en tiempo real
- **Responsive design** mobile-first
- **Keyboard shortcuts** (Ctrl+B para toggle sidebar)

### 🌐 **WebSocket en Tiempo Real**
```typescript
// Tipos de mensajes soportados:
- 'metrics_update'     // Actualizar métricas cada 5s
- 'new_log'           // Nuevas entradas de log
- 'scraper_update'    // Estados de scrapers
- 'product_added'     // Productos detectados automáticamente
- 'config_update'     // Cambios de configuración
- 'heartbeat'         // Keep-alive connection
```

### 🎨 **Optimizaciones UX/UI**
- **Loading skeletons** que coinciden con el contenido final
- **Error boundaries** con fallbacks informativos
- **Toast notifications** para feedback inmediato
- **Micro-interacciones** sutiles y profesionales
- **Accessibility WCAG 2.1** compliance

## 📊 **APIs Integradas**

### Endpoints Principales:
```javascript
// Métricas del sistema
GET /api/dashboard/metrics/summary
GET /api/dashboard/scraper/status
GET /api/dashboard/ai-engine/stats

// Gestión de productos
GET /api/dashboard/products
POST /api/dashboard/products
PUT /api/dashboard/products/{id}
DELETE /api/dashboard/products/{id}
GET /api/dashboard/products/stats

// Auto-detección
GET /api/dashboard/auto-detection/status
POST /api/dashboard/auto-detection/start
POST /api/dashboard/auto-detection/stop
POST /api/dashboard/auto-detection/scan

// Configuración
GET /api/dashboard/config/current
POST /api/dashboard/config/update

// Logs y monitoreo
GET /api/dashboard/logs/recent
GET /api/dashboard/health
```

## 🏗️ **Arquitectura Técnica**

### Frontend Stack:
```
React 18.3.1          # Framework principal
TypeScript 5.8.3      # Type safety
Vite 5.4.19           # Build tool optimizado
shadcn-ui             # Component library
Tailwind CSS 3.4.17  # Utility-first styling
React Query 5.83.0   # Estado servidor + caché
React Router 6.30.1   # Navegación SPA
```

### Estructura de Archivos:
```
frontend/
├── src/
│   ├── components/
│   │   ├── QuickStats.tsx           # Métricas tiempo real
│   │   ├── ActiveListings.tsx       # Lista productos
│   │   ├── AutomatedResponses.tsx   # Config respuestas
│   │   ├── AutoDetectionPanel.tsx   # Panel auto-detección
│   │   ├── AppSidebar.tsx          # Navegación lateral
│   │   ├── AppBreadcrumb.tsx       # Breadcrumbs
│   │   └── ui/                     # shadcn-ui components
│   ├── hooks/
│   │   ├── useAPI.ts               # React Query hooks
│   │   ├── useWebSocket.ts         # WebSocket real-time
│   │   └── use-toast.ts           # Notifications
│   ├── services/
│   │   └── api.ts                  # API client + types
│   └── pages/
│       └── Index.tsx               # Layout principal
```

## 🔒 **Seguridad y Rendimiento**

### Características de Seguridad:
- **Error boundaries** para prevenir crashes
- **Input sanitization** en formularios
- **CORS configurado** para localhost development
- **API error handling** con fallbacks

### Optimizaciones de Rendimiento:
- **React Query caching** con stale times optimizados
- **Memoization** de componentes costosos
- **Lazy loading** de rutas y componentes
- **Bundle splitting** automático con Vite
- **WebSocket reconnection** automática con backoff

## 🎯 **Datos Mock vs Reales**

| Componente | Estado | Datos Fuente |
|------------|--------|--------------|
| **QuickStats** | ✅ Real | Backend metrics API |
| **ActiveListings** | ✅ Real | Backend products API |
| **AutomatedResponses** | ✅ Real | Backend config API |
| **AutoDetectionPanel** | ✅ Real | Backend auto-detection API |
| **WebSocket Updates** | ✅ Real | Live WebSocket feed |
| **Sidebar Badges** | ✅ Real | Computed from APIs |

## 🚨 **Troubleshooting**

### Problema: WebSocket no conecta
```bash
# Verificar que backend está corriendo
curl http://localhost:8000/api/dashboard/health

# Verificar WebSocket endpoint
wscat -c ws://localhost:8000/api/dashboard/ws/live
```

### Problema: APIs devuelven error 500
```bash
# Verificar logs del backend
tail -f logs/wallapop_bot.log

# Verificar Redis (si está configurado)
redis-cli ping
```

### Problema: Frontend no carga
```bash
# Limpiar caché y reinstalar
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## 📈 **Próximas Mejoras**

- [ ] **Páginas adicionales:** Productos, Mensajes, Analytics, Settings
- [ ] **Charts avanzados:** Recharts integration para métricas visuales
- [ ] **Notificaciones push:** Sistema completo de alertas
- [ ] **Themes:** Soporte para dark/light mode
- [ ] **Internationalization:** Soporte multi-idioma
- [ ] **Performance monitoring:** Integración con Sentry o similar

## 🤝 **Integración Desarrollada Por**

✅ **Fase 1:** Estructura y APIs (Completada)  
✅ **Fase 2:** WebSocket tiempo real (Completada)  
✅ **Fase 3:** Auto-detection UI (Completada)  
✅ **Fase 4:** UX optimization (Completada)  

**Resultado:** Dashboard production-ready integrado con backend Wall-E Research, métricas en tiempo real, gestión completa de productos y sistema de auto-detección funcional.

---

*Dashboard integrado exitosamente usando Claude Code con agentes especializados: `ux-dashboard-creator`, React Query, shadcn-ui y WebSocket real-time.*