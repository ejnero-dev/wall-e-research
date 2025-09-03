# 🛡️ Guía de Seguridad: Cómo Evitar Estafas en Wallapop

## 📋 Índice
1. [Estafas Más Comunes](#estafas-más-comunes)
2. [Señales de Alerta](#señales-de-alerta)
3. [Buenas Prácticas para Vendedores](#buenas-prácticas-para-vendedores)
4. [Sistema Anti-Fraude para el Bot](#sistema-anti-fraude-para-el-bot)
5. [Casos Reales y Ejemplos](#casos-reales-y-ejemplos)
6. [Recomendaciones de la Comunidad](#recomendaciones-de-la-comunidad)

## 🚨 Estafas Más Comunes

### 1. **El Timo del Envío Falso**
- **Modus Operandi**: El estafador se hace pasar por una empresa de transporte
- **Señal**: Piden datos bancarios por WhatsApp para "formalizar el envío"
- **Defensa**: NUNCA dar datos bancarios fuera de la plataforma

### 2. **Phishing de Wallapop**
- **Modus Operandi**: Emails falsos haciéndose pasar por Wallapop
- **Señal**: Enlaces externos para "verificar cuenta" o "confirmar pago"
- **Defensa**: Wallapop NUNCA pide contraseñas por email

### 3. **La Estafa del Bizum Cancelado**
- **Modus Operandi**: Envían un Bizum programado que luego cancelan
- **Señal**: "Ya te he enviado el dinero" + comprobante falso
- **Defensa**: Verificar SIEMPRE que el dinero está en tu cuenta

### 4. **PayPal "Amigos y Familia"**
- **Modus Operandi**: Pagan por PayPal sin protección al comprador
- **Señal**: "Te ahorro la comisión si lo hacemos por amigos"
- **Defensa**: NUNCA aceptar pagos sin protección

### 5. **El Intercambio de Productos**
- **Modus Operandi**: Compran producto, reclaman que llegó otro diferente
- **Señal**: Compradores sin valoraciones que compran productos caros
- **Defensa**: Grabar TODO el proceso de empaquetado

### 6. **La Estafa Nigeriana 2.0**
- **Modus Operandi**: "Compro para mi hijo en el extranjero"
- **Señal**: Transferencias internacionales, inglés raro, urgencia
- **Defensa**: NO enviar nunca al extranjero sin cobrar antes

### 7. **El Timo del DNI**
- **Modus Operandi**: Piden foto del DNI para "verificar identidad"
- **Señal**: Cualquier petición de documentos personales
- **Defensa**: NUNCA enviar DNI ni documentos personales

## 🔍 Señales de Alerta (Red Flags)

### Perfil del Estafador Típico:
```yaml
ALTA PROBABILIDAD DE ESTAFA:
- ❌ Cuenta nueva (0 valoraciones, 0 compras, 0 ventas)
- ❌ Quiere sacar la conversación de Wallapop inmediatamente
- ❌ Urgencia extrema ("lo necesito YA")
- ❌ No regatean ni preguntan sobre el producto
- ❌ Español extraño o uso de traductores
- ❌ Ubicación muy lejana o extranjero
- ❌ Métodos de pago raros o complicados
- ❌ Enlaces externos en los mensajes
- ❌ Piden datos personales (DNI, teléfono, email)
```

### Frases Típicas de Estafadores:
- "Mi transportista pasará a recogerlo"
- "Te pago por adelantado + gastos de envío"
- "Es para mi hijo/sobrino en [país extranjero]"
- "Necesito tu email para completar el pago"
- "El banco me pide que ingreses X€ para desbloquear"
- "Te mando comprobante del pago"
- "Haz clic en este enlace para confirmar"

## 💡 Buenas Prácticas para Vendedores

### 1. **Configuración del Perfil**
- ✅ Verificar email y teléfono en Wallapop
- ✅ NO usar fotos personales reconocibles
- ✅ Descripción clara pero sin datos personales
- ✅ Mantener buenas valoraciones

### 2. **Gestión de Anuncios**
- ✅ Fotos claras y detalladas del producto
- ✅ Descripción honesta incluyendo defectos
- ✅ Precio justo (ni muy alto ni sospechosamente bajo)
- ✅ Especificar "NO REGATEO" si es el caso

### 3. **Durante la Conversación**
- ✅ Mantener TODA la comunicación en Wallapop
- ✅ Ser amable pero firme
- ✅ No ceder a presiones o urgencias
- ✅ Verificar valoraciones del comprador

### 4. **Para Envíos**
- ✅ Preferir Wallapop Envíos (aunque tenga comisión)
- ✅ Si envío ordinario: cobrar ANTES de enviar
- ✅ Grabar proceso de empaquetado
- ✅ Guardar comprobantes de envío
- ✅ Foto del paquete cerrado con dirección visible

### 5. **Para Entregas en Mano**
- ✅ Quedar SIEMPRE en lugares públicos
- ✅ Horario diurno preferiblemente
- ✅ Llevar acompañante si es posible
- ✅ Comprobar billetes (rotulador detector)
- ✅ NO aceptar cheques ni pagarés

## 🤖 Sistema Anti-Fraude para el Bot

### Detección Automática de Patrones Sospechosos
```python
PATRONES_FRAUDE = {
    "urls_sospechosas": [
        r"bit\.ly", r"tinyurl", r"goo\.gl",
        r"wallapop\.com(?!$)", # URLs falsas de Wallapop
        r"[a-z]+\.[a-z]+/[a-zA-Z0-9]{5,}" # URLs acortadas
    ],
    
    "palabras_clave_estafa": [
        "western union", "moneygram", "paypal familia",
        "transportista", "mi hijo", "en el extranjero",
        "desbloquear cuenta", "verificar tarjeta",
        "ingresa", "adelantado", "urgente hoy"
    ],
    
    "solicitudes_peligrosas": [
        "email", "whatsapp", "telegram",
        "dni", "documento", "tarjeta",
        "número de cuenta", "contraseña"
    ]
}
```

### Scoring de Riesgo
```python
def calcular_riesgo_estafa(conversacion, usuario):
    score = 0
    
    # Usuario nuevo sin valoraciones
    if usuario.valoraciones == 0:
        score += 30
    
    # Ubicación lejana
    if usuario.distancia > 500:  # km
        score += 20
    
    # No hace preguntas sobre el producto
    if not conversacion.tiene_preguntas_producto:
        score += 25
    
    # Urgencia extrema
    if conversacion.contiene(["urgente", "ahora mismo", "ya"]):
        score += 15
    
    # Quiere salir de la plataforma
    if conversacion.contiene(["whatsapp", "email", "teléfono"]):
        score += 40
    
    return score  # >70 = Alto riesgo
```

### Respuestas Automáticas Anti-Fraude
```python
respuestas_seguridad = {
    "solicitud_whatsapp": 
        "Prefiero mantener toda la comunicación por Wallapop 😊",
    
    "pago_adelantado": 
        "El pago se realiza en el momento de la entrega",
    
    "envio_extranjero": 
        "Lo siento, solo hago envíos nacionales",
    
    "datos_personales": 
        "No comparto datos personales, todo por la app",
    
    "enlace_externo": 
        "No puedo acceder a enlaces externos, hablemos por aquí",
    
    "transportista_propio": 
        "Solo uso los métodos de envío de Wallapop"
}
```

## 📱 Casos Reales y Ejemplos

### Caso 1: La Estafa del Comprobante Falso
```
🔴 Estafador: "Ya te he hecho el Bizum, mira"
[Envía captura falsa]
🔴 Estafador: "Puedes enviar ya?"

✅ Respuesta Correcta: "Esperaré a que llegue a mi cuenta, 
luego envío sin problema 😊"
```

### Caso 2: El Comprador Internacional
```
🔴 Estafador: "Hello, I want buy for my son in UK"
🔴 Estafador: "I pay you 50€ extra for shipping"

✅ Respuesta: "Sorry, only national shipping"
[BLOQUEAR]
```

### Caso 3: Presión por Urgencia
```
🔴 Estafador: "Necesito que me lo envíes HOY"
🔴 Estafador: "Es un regalo urgente, pago extra"

✅ Respuesta: "Puedo enviarlo mañana una vez reciba el pago"
```

## 📚 Recomendaciones de la Comunidad

### De Vendedores Experimentados:
1. **"Graba TODO el proceso de empaquetado"**
   - Especialmente para electrónica
   - Mostrar números de serie
   - Sellar con cinta en cámara

2. **"Nunca envíes sin cobrar"**
   - Aunque tengan 100 valoraciones positivas
   - Aunque parezcan de confianza
   - Sin excepciones

3. **"En persona: billetes de 50€ máximo"**
   - Más fáciles de verificar
   - Menos pérdida si son falsos
   - Llevar cambio preparado

4. **"Perfil sin foto = Sospechoso"**
   - Los estafadores no personalizan
   - Cuentas creadas rápidamente
   - Sin descripción personal

### Experiencias que Debes Conocer:
- Wallapop tiende a dar la razón al comprador en disputas
- El sistema de valoraciones puede ser manipulado
- Las transferencias pueden ser canceladas (hasta 48h)
- Los envíos contra reembolso NO son seguros
- Algunos bancos no colaboran con denuncias

## 🚀 Implementación en el Bot

### Flujo de Seguridad
```
1. ANÁLISIS INICIAL
   ├── Verificar perfil del usuario
   ├── Calcular score de riesgo
   └── Activar modo defensivo si score > 70

2. DURANTE CONVERSACIÓN
   ├── Detectar patrones de fraude
   ├── No ceder a presiones
   └── Mantener todo en la plataforma

3. CIERRE DE VENTA
   ├── Solo métodos seguros
   ├── Confirmación de pago real
   └── Documentar todo

4. POST-VENTA
   ├── Guardar evidencias
   ├── Seguimiento del envío
   └── Gestión de incidencias
```

## ⚠️ Qué Hacer Si Te Intentan Estafar

1. **NO BORRAR NADA** - Guarda toda la conversación
2. **Reportar en Wallapop** - Usa el botón de denuncia
3. **Bloquear al usuario** - Evita más contacto
4. **Si perdiste dinero** - Denuncia en Policía Nacional
5. **Comparte la experiencia** - Avisa a otros usuarios

## 🎯 Conclusión

La clave está en:
- 🛡️ Mantener TODO dentro de Wallapop
- 🚫 No ceder a presiones ni urgencias  
- 👀 Verificar siempre perfiles y pagos
- 📸 Documentar todos los procesos
- 🤝 Usar sentido común

Recuerda: Es mejor perder una venta que perder el producto Y el dinero.
