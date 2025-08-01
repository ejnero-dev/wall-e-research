# 🤝 Sistema de Gestión de Conversaciones

## 📋 Índice
1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Motor de Intenciones](#motor-de-intenciones)
3. [Flujos de Conversación](#flujos-de-conversación)
4. [Sistema Anti-Fraude](#sistema-anti-fraude)
5. [Plantillas de Respuestas](#plantillas-de-respuestas)
6. [Métricas y KPIs](#métricas-y-kpis)

## 🏗️ Arquitectura del Sistema

### Pipeline de Procesamiento de Mensajes
```
Mensaje Entrante (Wallapop)
         ↓
[Rate Limiter] → Evitar detección
         ↓
[Clasificador de Intención] → NLP/Regex
         ↓
[Analizador de Contexto] → Estado conversación
         ↓
[Detector Anti-Fraude] → Seguridad
         ↓
[Generador de Respuesta] → Templates + IA
         ↓
[Sistema de Delay] → 30-120 segundos
         ↓
Respuesta Enviada
```

### Estados de Conversación
- **INICIAL**: Primer contacto del comprador
- **EXPLORANDO**: Haciendo preguntas sobre el producto
- **NEGOCIANDO**: Discutiendo precio o condiciones
- **COMPROMETIDO**: Intención clara de compra
- **COORDINANDO**: Acordando entrega/envío
- **FINALIZADO**: Venta completada o cancelada
- **ABANDONADO**: Sin actividad >48h

## 🧠 Motor de Intenciones

### Categorías de Intención
```python
INTENCIONES = {
    "SALUDO": ["hola", "buenas", "hey", "buenos días"],
    "PRECIO": ["precio", "cuánto", "€", "euros", "cuesta"],
    "NEGOCIACION": ["menos", "rebaja", "descuento", "última oferta"],
    "DISPONIBILIDAD": ["disponible", "vendido", "reservado", "queda"],
    "ESTADO_PRODUCTO": ["estado", "funciona", "roto", "nuevo", "usado"],
    "UBICACION": ["dónde", "zona", "dirección", "cerca de"],
    "ENVIO": ["envío", "enviar", "correos", "mensajería"],
    "COMPRA_DIRECTA": ["lo quiero", "me lo llevo", "lo compro", "trato"],
    "INFORMACION": ["info", "detalles", "características", "medidas"],
    "PAGO": ["pago", "bizum", "efectivo", "transferencia"]
}
```

### Priorización de Compradores
1. **🔴 Alta Prioridad**
   - Mensajes con intención directa de compra
   - Preguntas sobre forma de pago
   - Solicitud de ubicación para recogida

2. **🟡 Media Prioridad**
   - Preguntas específicas del producto
   - Negociación razonable de precio
   - Consultas sobre envío

3. **🟢 Baja Prioridad**
   - Ofertas muy bajas (<50% del precio)
   - Preguntas genéricas
   - Propuestas de intercambio

## 🔄 Flujos de Conversación

### Flujo Estándar de Venta Exitosa
```yaml
1_SALUDO:
  comprador: "Hola, está disponible?"
  bot: "¡Hola! Sí, está disponible 😊 ¿Te interesa?"

2_CONFIRMACION_INTERES:
  comprador: "Sí, en qué estado está?"
  bot: "[Estado del producto]. Lo tengo desde [tiempo] y funciona perfectamente"

3_NEGOCIACION:
  comprador: "Lo dejarías en X€?"
  bot: 
    si_razonable: "Te lo podría dejar en [precio_acordado] si te lo llevas hoy/mañana"
    si_muy_bajo: "Es un precio muy ajustado ya. Mi última oferta sería [precio_minimo]"

4_ACUERDO:
  comprador: "Vale, me lo quedo"
  bot: "¡Perfecto! ¿Cuándo podrías recogerlo?"

5_COORDINACION:
  comprador: "Mañana por la tarde"
  bot: "Genial, te propongo [lugar_publico] sobre las [hora]. ¿Te viene bien?"

6_CIERRE:
  comprador: "Sí, perfecto"
  bot: "¡Estupendo! Te mando ubicación exacta por privado. Mi teléfono es [numero] por si necesitas algo"
```

## 🛡️ Sistema Anti-Fraude

### Patrones de Estafa Comunes
1. **Envío sin Ver Producto**
   - "Te hago transferencia y me lo envías"
   - "Mi transportista lo recoge"
   
2. **Enlaces Sospechosos**
   - URLs acortadas
   - Dominios extraños
   - Petición de datos personales

3. **Métodos de Pago Raros**
   - "Pago por PayPal de familiares"
   - "Cheque del extranjero"
   - "Western Union"

### Respuestas a Intentos de Estafa
```python
respuestas_seguridad = {
    "envio_sin_ver": "Solo hago entregas en mano, lo siento",
    "enlace_externo": "Prefiero gestionar todo por Wallapop",
    "pago_adelantado": "El pago se hace en el momento de la entrega",
    "datos_personales": "No comparto datos personales hasta acordar la venta"
}
```

## 📝 Plantillas de Respuestas

### Por Categoría
Las plantillas completas están en `/src/templates/responses.json`

### Variables Dinámicas
- `{producto}` - Nombre del producto
- `{precio}` - Precio actual
- `{precio_rebajado}` - Precio con descuento
- `{zona}` - Zona de entrega
- `{estado}` - Estado del producto

## 📊 Métricas y KPIs

### Métricas de Conversación
- **Tiempo Primera Respuesta**: < 2 minutos
- **Tasa de Respuesta**: > 95%
- **Conversión a Venta**: > 25%
- **Satisfacción Usuario**: Sin reportes/bloqueos

### Dashboard Métricas
- Total conversaciones activas
- Conversiones por día/semana
- Tiempo medio de venta
- Productos más demandados
- Patrones de horarios

## 🔧 Configuración Recomendada

### Delays Entre Mensajes
```json
{
  "primer_mensaje": "30-60 segundos",
  "respuestas_rapidas": "45-90 segundos",
  "respuestas_complejas": "60-120 segundos",
  "horario_activo": "09:00-22:00"
}
```

### Límites de Seguridad
- Máximo 5 conversaciones simultáneas por producto
- Máximo 20 mensajes por conversación
- Pausa de 5 minutos cada 10 conversaciones
