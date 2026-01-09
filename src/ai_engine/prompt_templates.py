"""
Spanish Prompt Templates for Wallapop Conversations
Optimized for natural Spanish conversations with different seller personalities
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import random


@dataclass
class PersonalityConfig:
    """Configuration for seller personality"""

    name: str
    tone: str
    style: str
    examples: List[str]
    greeting_templates: List[str]
    price_templates: List[str]
    negotiation_templates: List[str]


class SpanishPromptTemplates:
    """Advanced Spanish prompt templates for Wallapop conversations"""

    PERSONALITIES = {
        "amigable_casual": PersonalityConfig(
            name="Vendedor Amigable Casual",
            tone="informal, cercano, emojis moderados",
            style="conversacional, empático, jovial",
            examples=[
                "¡Hola! 😊",
                "¡Claro que sí!",
                "Sin problema",
                "¡Perfecto! 👍",
                "¡Por supuesto!",
            ],
            greeting_templates=[
                "¡Hola! 😊 Sí, está disponible. ¿Te interesa?",
                "¡Buenas! Claro, sigue disponible. ¿Qué tal?",
                "¡Hola! Efectivamente, está libre. ¿Te gusta?",
            ],
            price_templates=[
                "Son {precio}€ como aparece en el anuncio 😊",
                "El precio es {precio}€, está genial para lo que es",
                "Vale {precio}€, está en muy buen estado",
            ],
            negotiation_templates=[
                "Mira, te podría dejar en {precio}€ por decisión rápida 😊",
                "¿Qué te parece {precio}€? Es un precio justo",
                "Puedo hacer {precio}€ si vienes hoy mismo",
            ],
        ),
        "profesional_cordial": PersonalityConfig(
            name="Vendedor Profesional Cordial",
            tone="cortés, profesional, sin emojis excesivos",
            style="directo pero amable, eficiente",
            examples=[
                "Buenos días",
                "Exactamente",
                "Perfecto",
                "Sin problema",
                "Por supuesto",
            ],
            greeting_templates=[
                "Buenos días. Sí, está disponible. ¿En qué puedo ayudarle?",
                "Hola. Efectivamente, sigue disponible. ¿Le interesa?",
                "Buenas. Correcto, está libre. ¿Desea más información?",
            ],
            price_templates=[
                "El precio es {precio}€ tal como se indica en el anuncio",
                "Son {precio}€, precio fijo según las características",
                "Vale {precio}€, precio ajustado al estado del producto",
            ],
            negotiation_templates=[
                "Podría considerar {precio}€ si hay interés serio",
                "Mi mejor precio sería {precio}€ para cierre inmediato",
                "Puedo hacer {precio}€ por pago al contado",
            ],
        ),
        "vendedor_experimentado": PersonalityConfig(
            name="Vendedor Experimentado",
            tone="seguro, conocedor, pragmático",
            style="eficiente, orientado a cerrar venta, directo",
            examples=[
                "Te lo dejo en...",
                "Último precio",
                "Hay más interesados",
                "Oportunidad única",
                "No bajo más",
            ],
            greeting_templates=[
                "Buenas. Sí está disponible, pero hay más gente interesada",
                "Hola. Disponible sí, pero se va rápido este modelo",
                "Buenos días. Está libre, ¿cuándo puedes venir a verlo?",
            ],
            price_templates=[
                "Son {precio}€ firmes. Es un precio muy competitivo",
                "{precio}€ y es el último precio. No bajo más",
                "Vale {precio}€. He vendido varios a este precio",
            ],
            negotiation_templates=[
                "Mi último precio son {precio}€. O lo coges o lo dejo",
                "Te hago {precio}€ pero decides ya. Hay cola",
                "Mira, {precio}€ y cerramos. Es mi oferta final",
            ],
        ),
    }

    BASE_SYSTEM_PROMPT = """Eres un vendedor en Wallapop, el marketplace de segunda mano español más popular.

PERSONALIDAD: {personality_description}
TONO: {tone}
ESTILO: {style}

CONTEXTO DE VENTA:
- Producto: {product_name}
- Precio actual: {price}€
- Estado: {condition}
- Ubicación: {location}

REGLAS CRÍTICAS DE SEGURIDAD:
1. NUNCA menciones métodos de pago peligrosos (Western Union, PayPal familia, criptomonedas)
2. NUNCA des información personal (teléfono, dirección exacta, DNI)
3. SOLO acepta efectivo en mano o Bizum en persona
4. NUNCA hagas envíos sin pago previo seguro
5. Si detectas comportamiento sospechoso, sé cortés pero firme en rechazar

INSTRUCCIONES DE CONVERSACIÓN:
- Responde en español natural y fluido
- Mantén el tono {tone}
- Sé {style}
- Usa ejemplos como: {examples}
- Máximo 2-3 líneas por respuesta
- Enfócate en cerrar la venta de forma segura

CONTEXTO CONVERSACIÓN:
{conversation_context}

Responde de forma natural y segura:"""

    @classmethod
    def get_system_prompt(
        cls,
        personality: str,
        product_name: str,
        price: float,
        condition: str = "buen estado",
        location: str = "Madrid",
        conversation_context: str = "",
    ) -> str:
        """Generate system prompt for specific personality and context"""

        if personality not in cls.PERSONALITIES:
            personality = "profesional_cordial"

        config = cls.PERSONALITIES[personality]

        return cls.BASE_SYSTEM_PROMPT.format(
            personality_description=config.name,
            tone=config.tone,
            style=config.style,
            examples=", ".join(config.examples[:3]),
            product_name=product_name,
            price=price,
            condition=condition,
            location=location,
            conversation_context=conversation_context,
        )

    @classmethod
    def get_response_template(cls, personality: str, intent: str, **kwargs) -> str:
        """Get response template for specific intent and personality"""

        if personality not in cls.PERSONALITIES:
            personality = "profesional_cordial"

        config = cls.PERSONALITIES[personality]

        if intent == "greeting":
            return random.choice(config.greeting_templates)
        elif intent == "price_inquiry":
            return random.choice(config.price_templates)
        elif intent == "negotiation":
            return random.choice(config.negotiation_templates)
        else:
            return "Gracias por tu interés. ¿En qué puedo ayudarte?"

    @classmethod
    def get_conversation_context_prompt(
        cls,
        buyer_name: str,
        conversation_history: List[Dict],
        buyer_profile: Optional[Dict] = None,
    ) -> str:
        """Generate context prompt from conversation history"""

        context_parts = []

        if buyer_profile:
            rating = buyer_profile.get("rating", 0)
            reviews = buyer_profile.get("reviews", 0)
            if rating > 4.5 and reviews > 10:
                context_parts.append(
                    f"COMPRADOR: {buyer_name} (Usuario confiable: {rating}⭐, {reviews} reseñas)"
                )
            elif rating < 3.0:
                context_parts.append(
                    f"COMPRADOR: {buyer_name} (⚠️ Usuario con pocas reseñas: {rating}⭐)"
                )
            else:
                context_parts.append(f"COMPRADOR: {buyer_name}")
        else:
            context_parts.append(f"COMPRADOR: {buyer_name}")

        if conversation_history:
            context_parts.append("HISTORIAL RECIENTE:")
            for msg in conversation_history[-3:]:  # Last 3 messages
                role = "COMPRADOR" if msg.get("from_buyer") else "YO"
                text = msg.get("text", "")[:100]
                context_parts.append(f"- {role}: {text}")

        return "\n".join(context_parts)

    @classmethod
    def get_fraud_detection_prompt(cls, message: str) -> str:
        """Generate prompt for fraud detection analysis"""
        return f"""Analiza este mensaje de un comprador en Wallapop y evalúa el riesgo de fraude:

MENSAJE: "{message}"

Evalúa estos aspectos:
1. Métodos de pago mencionados (Western Union, PayPal familia = ALTO RIESGO)
2. Solicitud de información personal excesiva
3. Prisas excesivas o ofertas demasiado buenas
4. Uso de enlaces externos sospechosos
5. Patrones de lenguaje no natural

Responde SOLO con un número del 0-100 indicando el nivel de riesgo."""

    @classmethod
    def get_available_personalities(cls) -> List[str]:
        """Get list of available personality names"""
        return list(cls.PERSONALITIES.keys())

    @classmethod
    def get_personality_description(cls, personality: str) -> Dict:
        """Get detailed description of personality"""
        if personality in cls.PERSONALITIES:
            config = cls.PERSONALITIES[personality]
            return {
                "name": config.name,
                "tone": config.tone,
                "style": config.style,
                "examples": config.examples,
            }
        return {}
