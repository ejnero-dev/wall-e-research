# 🚀 Guía de Continuidad: Fase 1 - Scraper Prioritario

**Para Claude Code en próximas conversaciones**

---

## 📋 **CONTEXTO OBLIGATORIO PARA NUEVA CONVERSACIÓN**

Al abrir una nueva conversación de Claude Code, **COPIAR Y PEGAR** exactamente este texto:

```markdown
Hola Claude Code. Estoy continuando el desarrollo del bot de automatización de Wallapop.

ESTADO ACTUAL:
- ✅ Fase 0 completada: Setup y MVP básico
- Motor de conversaciones consolidado y funcionando
- Base de datos PostgreSQL + Redis configurada  
- Tests unitarios e integración implementados
- CI/CD pipeline con GitHub Actions operativo
- Happy Path demo funcionando correctamente

PRÓXIMO OBJETIVO:
Implementar la Fase 1 del plan: "Scraper Prioritario"
- 1 semana completa dedicada al scraper de Wallapop
- Prioridad absoluta según recomendaciones de Gemini
- Usar agente web-scraper-security especializado

INSTRUCCIONES INMEDIATAS:
1. Lee el archivo docs/fase1-continuidad.md para información detallada
2. EJECUTA el setup de Git OBLIGATORIO antes de cualquier desarrollo
3. Procede con la Fase 1 siguiendo la guía completa
```

---

## 🎯 **ESTADO ACTUAL DEL PROYECTO**

### ✅ **Fase 0 Completada - Resumen**

**Archivos Clave Creados/Modificados:**
- `src/conversation_engine/engine.py` - Motor consolidado y optimizado
- `src/database/` - Arquitectura completa de BD con PostgreSQL + Redis
- `tests/` - Suite completa de tests unitarios e integración
- `scripts/happy_path_demo.py` - Demo ejecutable del funcionamiento
- `.github/workflows/ci.yml` - Pipeline CI/CD profesional
- `docker-compose.yml` - Infraestructura de desarrollo
- `IMPLEMENTATION_PLAN_V2.md` - Plan completo actualizado

**Funcionalidades Operativas:**
- 🤖 Motor de conversaciones con detección de fraude
- 🗄️ Base de datos optimizada con migraciones
- 🧪 Testing continuo con 80%+ coverage
- 🔄 CI/CD con GitHub Actions
- 📊 Demo interactivo funcional

### 📁 **Archivos de Referencia Críticos**

1. **IMPLEMENTATION_PLAN_V2.md** - Plan maestro con todas las fases
2. **docs/conclusiones-gemini.md** - Recomendaciones críticas de Gemini
3. **CLAUDE.md** - Guía técnica para Claude Code
4. **src/conversation_engine/engine.py** - Motor principal consolidado
5. **src/database/models.py** - Modelos de datos
6. **tests/conftest.py** - Fixtures compartidas para testing

---

## 🔧 **SETUP GIT (CRÍTICO - HACER PRIMERO)**

**⚠️ OBLIGATORIO ANTES DE CUALQUIER DESARROLLO:**

El proyecto necesita Git para CI/CD, backup y versionado. Ejecutar estos comandos:

```bash
# 1. Inicializar Git (si no está ya)
git init

# 2. Configuración básica (cambiar por tus datos)
git config user.name "Tu Nombre"
git config user.email "tu@email.com"

# 3. Agregar archivos existentes
git add .

# 4. Primer commit con todo lo de Fase 0
git commit -m "🎉 Initial commit: Fase 0 completa

- Motor de conversaciones consolidado
- Base de datos PostgreSQL + Redis configurada
- Tests unitarios e integración implementados  
- CI/CD pipeline con GitHub Actions
- Happy Path demo funcional
- Documentación completa

✅ Listo para Fase 1: Scraper Prioritario

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# 5. Crear repo en GitHub (nombre temporal OK)
# - Ir a github.com/new
# - Nombre sugerido: "marketplace-automation-bot" 
# - Descripción: "Wallapop marketplace automation bot"
# - Público o privado según preferencia
# - NO inicializar con README (ya tenemos archivos)

# 6. Conectar con GitHub (cambiar URL por la real)
git remote add origin https://github.com/TU_CUENTA/TU_REPO.git
git branch -M main  
git push -u origin main

# 7. Crear branch para Fase 1
git checkout -b feature/fase1-scraper-prioritario

# 8. Verificar que CI/CD funciona
# - Ir a GitHub Actions tab
# - Debería aparecer el workflow ejecutándose
```

**💡 CAMBIOS DE NOMBRE POSTERIORES (Muy Fácil):**

Los nombres son completamente flexibles. Para cambiar después:

```bash
# 1. Cambiar nombre del repo en GitHub
# - Ir a Settings > Repository name > Rename

# 2. Actualizar remote local
git remote set-url origin https://github.com/NUEVA_CUENTA/NUEVO_NOMBRE.git

# 3. Transferir a otra cuenta (si necesario)
# - GitHub Settings > Transfer ownership

# 4. Renombrar directorio local
mv project-wall-e nuevo-nombre-del-proyecto

# 5. Actualizar badges en README.md
# Buscar/reemplazar referencias al nombre anterior
```

**Nombres Temporales Sugeridos (cambiar después sin problema):**
- Repo: `marketplace-automation-bot` 
- Descripción: `Marketplace automation bot for conversation management`
- Branch principal: `main` (estándar actual)

## 🚨 **VERIFICACIONES OBLIGATORIAS DESPUÉS DEL SETUP GIT**

**EJECUTAR ESTOS COMANDOS EN ORDEN:**

```bash
# 1. Verificar que los tests pasan
pytest tests/ -v --tb=short

# 2. Ejecutar demo del Happy Path
python scripts/happy_path_demo.py

# 3. Verificar base de datos
python scripts/quick_start.py --check

# 4. Verificar estructura del proyecto
ls -la src/ && ls -la tests/ && ls -la config/

# 5. Verificar que el motor de conversaciones funciona
python -c "from src.conversation_engine.engine import ConversationEngine; print('✅ Motor importado correctamente')"
```

**Resultados Esperados:**
- ✅ Todos los tests pasan (0 failed)
- ✅ Demo ejecuta sin errores y muestra conversaciones
- ✅ Base de datos se conecta correctamente
- ✅ Estructura de archivos completa
- ✅ Imports funcionan sin errores

❌ **Si algo falla**, DETENER y revisar la configuración antes de proceder.

---

## 🎯 **FASE 1: SCRAPER PRIORITARIO - PLAN DETALLADO**

### **🚨 ADVERTENCIAS CRÍTICAS DE GEMINI**

> "El scraper es el **CAMINO CRÍTICO** y más frágil. Wallapop puede cambiar su diseño en cualquier momento. Esta fase presenta **MAYOR INCERTIDUMBRE** y riesgo de retrasos."

**Principios Obligatorios:**
1. **Una semana completa** dedicada SOLO al scraper
2. **Diseñar para el fracaso** - asumir que se romperá
3. **Alertas automáticas** cuando falle
4. **Manejo robusto de errores** en cada función
5. **Testing exhaustivo** antes de integración

### **📋 Sprint 1A: Scraper Robusto (MÁXIMA PRIORIDAD)**

**Agente Especializado:** `web-scraper-security`

**Prompt Completo para el Agente:**
```markdown
Necesito implementar un scraper robusto y seguro para Wallapop como parte de un bot de automatización de ventas.

CONTEXTO DEL PROYECTO:
- Bot de automatización para gestionar conversaciones de venta en Wallapop  
- Motor de conversaciones YA implementado en src/conversation_engine/engine.py
- Base de datos PostgreSQL configurada con modelos en src/database/models.py
- Suite de tests operativa en tests/
- Enfoque MVP pero con calidad profesional

REQUERIMIENTOS TÉCNICOS ESPECÍFICOS:
1. Sistema de autenticación multi-método:
   - Login con cookies persistentes  
   - Credenciales como fallback
   - Rotación automática de sesiones
   - Detección de sesión expirada

2. Anti-detección avanzado:
   - Delays humanizados (30-120 segundos)
   - Rotación de User-Agent
   - Headers realistas de navegador
   - Patrón de navegación humano
   - Proxies opcionales

3. Manejo robusto de errores:
   - Retry con backoff exponencial
   - Circuit breaker pattern
   - Alertas automáticas por Slack/email
   - Logs detallados para debugging
   - Fallback a modo manual

4. Detección de cambios en UI:
   - Selectores CSS flexibles
   - Múltiples estrategias de localización
   - Validación de elementos críticos
   - Sistema de alerta inmediata

5. Rate limiting inteligente:
   - Cumplimiento estricto con ToS
   - Pausa automática ante detección
   - Límites configurables por tipo de acción
   - Monitoreo de velocidad de requests

FUNCIONALIDADES REQUERIDAS:
- ✅ Login automático y mantener sesión
- ✅ Leer mensajes nuevos de conversaciones  
- ✅ Enviar respuestas a compradores
- ✅ Obtener detalles completos de productos
- ✅ Gestión de múltiples conversaciones simultáneas
- ✅ Navegación por la interfaz de usuario
- ✅ Manejo de notificaciones y alerts

INTEGRACIÓN CON SISTEMA EXISTENTE:
- Usar ConversationEngine de src/conversation_engine/engine.py
- Integrar con modelos de src/database/models.py  
- Logging compatible con configuración existente
- Tests en tests/integration/test_scraper.py

ARQUITECTURA OBJETIVO:
src/scraper/
├── wallapop_scraper.py      # Scraper principal
├── session_manager.py       # Gestión de sesiones y auth  
├── anti_detection.py        # Medidas anti-detección
├── error_handler.py         # Manejo centralizado de errores
├── config.py               # Configuración del scraper  
└── utils.py                # Utilidades compartidas

CASOS DE USO CRÍTICOS:
1. Login exitoso y mantener sesión por 24h+
2. Leer 50+ mensajes nuevos sin fallos
3. Responder automáticamente con delays realistas
4. Recuperación automática ante errores temporales
5. Detección inmediata de cambios en UI
6. Funcionamiento continuo por 24h sin intervención

CRITERIOS DE ÉXITO:
- Funciona 24h continuas sin fallos
- Velocidad realista (no más de 1 acción/30seg)
- Zero detecciones por Wallapop
- 100% de mensajes procesados correctamente
- Alertas funcionando ante cualquier error

Por favor implementa todo el sistema completo siguiendo estas especificaciones exactas.
```

### **📋 Sprint 1B: Testing Exhaustivo**

**Agente:** `test-automation-specialist`

**Objetivos:**
- Tests de integración con Wallapop real (modo dev)
- Tests de resiliencia ante fallos de red
- Tests de recuperación ante cambios de UI
- Mocks completos para CI/CD
- Benchmarks de rendimiento

### **📋 Sprint 1C: Auditoría de Seguridad**

**Agente:** `security-compliance-auditor`

**Objetivos:**
- Verificación completa del cumplimiento ToS
- Análisis de rate limiting
- Review de logs y privacidad
- Documentación de límites operativos

---

## 📊 **MÉTRICAS DE ÉXITO - FASE 1**

### **Criterios Obligatorios para Completar Fase 1:**

✅ **Funcionalidad Básica:**
- [ ] Login automático funciona 100% de las veces
- [ ] Lee mensajes nuevos sin errores
- [ ] Envía respuestas correctamente  
- [ ] Maneja múltiples conversaciones

✅ **Robustez:**
- [ ] 24 horas de funcionamiento continuo SIN fallos
- [ ] Recuperación automática ante errores temporales
- [ ] Alertas funcionando correctamente
- [ ] Logs detallados y útiles

✅ **Seguridad:**
- [ ] Cumplimiento verificado con ToS de Wallapop
- [ ] Rate limiting apropiado (max 1 acción/30seg)
- [ ] Sin detección por sistemas anti-bot
- [ ] Datos sensibles protegidos

✅ **Testing:**
- [ ] Tests unitarios 100% passing
- [ ] Tests de integración funcionando
- [ ] Coverage >90% en código del scraper
- [ ] Tests de recuperación ante fallos

✅ **Integración:**
- [ ] Funciona con ConversationEngine existente
- [ ] Usa base de datos correctamente
- [ ] Logs integrados con sistema
- [ ] Configuración externalizada

---

## ⚠️ **RIESGOS CRÍTICOS Y MITIGACIONES**

### **🚨 Riesgo Alto: Cambios en Wallapop**
- **Señales**: Selectores CSS no funcionan, elementos no encontrados
- **Mitigación**: Múltiples estrategias de selección, alertas inmediatas
- **Plan B**: Sistema de alerta para actualización manual urgente

### **🚨 Riesgo Alto: Detección y Bloqueo**  
- **Señales**: Captchas, bloqueos IP, mensajes de error
- **Mitigación**: Delays conservadores, comportamiento humano
- **Plan B**: Rotación de proxies, pausa automática

### **🚨 Riesgo Medio: Rate Limiting Agresivo**
- **Señales**: Errores 429, timeouts frecuentes
- **Mitigación**: Rate limiting más conservador
- **Plan B**: Escalado con múltiples cuentas

---

## 🔧 **HERRAMIENTAS Y COMANDOS ÚTILES**

### **Durante Desarrollo:**
```bash
# Ejecutar tests del scraper
pytest tests/integration/test_scraper.py -v -s

# Debug del scraper con logs
python -m src.scraper.wallapop_scraper --debug

# Verificar conectividad
python scripts/test_scraper_connection.py

# Monitorear logs en tiempo real
tail -f logs/scraper.log
```

### **Para Debugging:**
```bash
# Inspeccionar elementos de Wallapop
python scripts/inspect_wallapop_elements.py

# Test de selectores CSS
python scripts/test_css_selectors.py

# Verificar headers y cookies
python scripts/debug_session.py
```

---

## 📝 **TEMPLATE DE PROGRESO**

**Copiar y usar en la nueva conversación:**

```python
TodoWrite([
    {"id": "1", "content": "Verificar estado actual y pre-requisitos", "status": "pending", "priority": "high"},
    {"id": "2", "content": "Implementar scraper básico con web-scraper-security", "status": "pending", "priority": "high"},
    {"id": "3", "content": "Sistema de autenticación robusto", "status": "pending", "priority": "high"},
    {"id": "4", "content": "Anti-detección y delays humanizados", "status": "pending", "priority": "high"},
    {"id": "5", "content": "Manejo robusto de errores y alertas", "status": "pending", "priority": "high"},
    {"id": "6", "content": "Tests exhaustivos del scraper", "status": "pending", "priority": "high"},
    {"id": "7", "content": "Integración con motor de conversaciones", "status": "pending", "priority": "high"},
    {"id": "8", "content": "Auditoría de seguridad y compliance", "status": "pending", "priority": "medium"},
    {"id": "9", "content": "24h de testing continuo", "status": "pending", "priority": "medium"}
])
```

---

## 🎯 **FLUJO DE TRABAJO SUGERIDO**

### **Día 1: Setup y Fundamentos**
1. Verificar pre-requisitos
2. Invocar `web-scraper-security` con prompt completo
3. Implementar login básico
4. Tests iniciales de conectividad

### **Día 2-3: Funcionalidad Core**
1. Lectura de mensajes
2. Envío de respuestas  
3. Gestión de múltiples conversaciones
4. Anti-detección básico

### **Día 4-5: Robustez**
1. Manejo exhaustivo de errores
2. Sistema de alertas
3. Recovery automático
4. Testing de estrés

### **Día 6-7: Integración y Testing**
1. Integración con ConversationEngine
2. Tests end-to-end
3. Auditoría de seguridad
4. 24h de testing continuo

---

## 📞 **SALIDA DE LA FASE 1**

Al finalizar exitosamente, deberías tener:
- 🤖 Scraper completamente funcional y robusto
- ✅ Integración perfecta con sistema existente
- 🛡️ Seguridad y compliance verificados
- 📊 24h+ de funcionamiento estable
- 📝 Documentación completa de uso y mantenimiento

**Criterio de éxito final:** El scraper debe poder funcionar **autónomamente por 24 horas** procesando conversaciones reales sin intervención humana.

---

## 🚀 **INSTRUCCIONES PARA CLAUDE CODE**

1. **Lee este documento COMPLETO** antes de proceder
2. **Ejecuta las verificaciones** obligatorias
3. **Usa los prompts exactos** proporcionados para los agentes
4. **Sigue el flujo de trabajo** sugerido día a día
5. **Monitorea los riesgos** críticos constantemente
6. **Actualiza el progreso** con TodoWrite regularmente

**Recuerda:** Esta fase es **CRÍTICA** para el éxito del proyecto. La calidad y robustez del scraper determinará el éxito de todo el sistema.

---

*Documento creado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Siguiente actualización: Al completar Fase 1*