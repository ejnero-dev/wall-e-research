# conversation_engine.py
"""
Motor de Conversaciones Inteligente para Wallapop
Gestiona automáticamente las conversaciones con compradores
"""

import json
import re
import random
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Configurar logging
logger = logging.getLogger(__name__)

# Enums para estados
class ConversationState(Enum):
    INICIAL = "inicial"
    EXPLORANDO = "explorando"
    NEGOCIANDO = "negociando"
    COMPROMETIDO = "comprometido"
    COORDINANDO = "coordinando"
    FINALIZADO = "finalizado"
    ABANDONADO = "abandonado"

class IntentionType(Enum):
    SALUDO = "saludo"
    PRECIO = "precio"
    NEGOCIACION = "negociacion"
    DISPONIBILIDAD = "disponibilidad"
    ESTADO_PRODUCTO = "estado_producto"
    UBICACION = "ubicacion"
    ENVIO = "envio"
    COMPRA_DIRECTA = "compra_directa"
    INFORMACION = "informacion"
    PAGO = "pago"
    FRAUDE = "fraude"

class BuyerPriority(Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"

@dataclass
class Buyer:
    """Información del comprador"""
    id: str
    username: str
    valoraciones: int
    num_compras: int
    distancia_km: float
    ultima_actividad: datetime
    perfil_verificado: bool
    tiene_foto: bool

@dataclass
class Product:
    """Información del producto"""
    id: str
    titulo: str
    precio: float
    precio_minimo: float
    descripcion: str
    estado: str
    categoria: str
    permite_envio: bool
    zona: str
    
class ConversationEngine:
    def __init__(self, templates_path: str = None):
        """Inicializa el motor de conversaciones"""
        if templates_path is None:
            templates_path = Path(__file__).parent.parent / "templates" / "responses.json"
        
        self.templates = self._load_templates(str(templates_path))
        self.conversations = {}
        self.fraud_patterns = self._init_fraud_patterns()
        self.intention_keywords = self._init_intention_keywords()
        logger.info("ConversationEngine initialized successfully")
        
    def _load_templates(self, path: str) -> Dict:
        """Carga las plantillas de respuestas"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Templates file not found at {path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing templates JSON: {e}")
            return {}
    
    def _init_fraud_patterns(self) -> Dict:
        """Inicializa patrones de detección de fraude"""
        return {
            "urls_sospechosas": [
                r"bit\.ly", r"tinyurl", r"goo\.gl",
                r"[a-z]+\.[a-z]+/[a-zA-Z0-9]{5,}"
            ],
            "palabras_fraude": [
                "western union", "moneygram", "paypal familia",
                "transportista", "mi hijo", "extranjero",
                "desbloquear", "verificar tarjeta",
                "adelantado", "urgente hoy"
            ],
            "solicitudes_peligrosas": [
                "whatsapp", "telegram", "email",
                "dni", "documento", "tarjeta",
                "número de cuenta", "contraseña"
            ]
        }
    
    def _init_intention_keywords(self) -> Dict:
        """Inicializa palabras clave para detectar intenciones"""
        return {
            IntentionType.SALUDO: ["hola", "buenas", "hey", "buenos días"],
            IntentionType.PRECIO: ["precio", "cuánto", "€", "euros", "cuesta"],
            IntentionType.NEGOCIACION: ["menos", "rebaja", "descuento", "última oferta"],
            IntentionType.DISPONIBILIDAD: ["disponible", "vendido", "reservado", "queda"],
            IntentionType.ESTADO_PRODUCTO: ["estado", "funciona", "roto", "nuevo", "usado"],
            IntentionType.UBICACION: ["dónde", "zona", "dirección", "cerca de"],
            IntentionType.ENVIO: ["envío", "enviar", "correos", "mensajería"],
            IntentionType.COMPRA_DIRECTA: ["lo quiero", "me lo llevo", "lo compro", "trato"],
            IntentionType.INFORMACION: ["info", "detalles", "características", "medidas"],
            IntentionType.PAGO: ["pago", "bizum", "efectivo", "transferencia"]
        }
    
    def analyze_message(self, message: str, buyer: Buyer, product: Product) -> Dict:
        """Analiza un mensaje y devuelve intención, prioridad y riesgo de fraude"""
        message_lower = message.lower()
        
        # Detectar intención
        intention = self._detect_intention(message_lower)
        
        # Calcular prioridad
        priority = self._calculate_priority(intention, buyer, message_lower)
        
        # Calcular riesgo de fraude
        fraud_risk = self._calculate_fraud_risk(message_lower, buyer)
        
        # Detectar estado de conversación
        state = self._detect_conversation_state(intention, buyer.id)
        
        result = {
            "intention": intention,
            "priority": priority,
            "fraud_risk": fraud_risk,
            "state": state,
            "requires_human": fraud_risk > 70
        }
        
        logger.debug(f"Message analysis result: {result}")
        return result
    
    def _detect_intention(self, message: str) -> IntentionType:
        """Detecta la intención principal del mensaje"""
        # Primero verificar si es potencial fraude
        for pattern in self.fraud_patterns["palabras_fraude"]:
            if pattern in message:
                return IntentionType.FRAUDE
        
        # Luego buscar intenciones normales
        max_matches = 0
        detected_intention = IntentionType.INFORMACION
        
        for intention, keywords in self.intention_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in message)
            if matches > max_matches:
                max_matches = matches
                detected_intention = intention
        
        return detected_intention
    
    def _calculate_priority(self, intention: IntentionType, buyer: Buyer, message: str) -> BuyerPriority:
        """Calcula la prioridad del comprador"""
        # Alta prioridad
        if intention == IntentionType.COMPRA_DIRECTA:
            return BuyerPriority.ALTA
        if intention == IntentionType.PAGO and "ahora" in message:
            return BuyerPriority.ALTA
        if "urgente" in message and buyer.valoraciones > 10:
            return BuyerPriority.ALTA
        
        # Baja prioridad
        if intention == IntentionType.FRAUDE:
            return BuyerPriority.BAJA
        if buyer.valoraciones == 0 and buyer.num_compras == 0:
            return BuyerPriority.BAJA
        if intention == IntentionType.NEGOCIACION and any(x in message for x in ["10€", "20€", "mitad"]):
            return BuyerPriority.BAJA
        
        # Media por defecto
        return BuyerPriority.MEDIA
    
    def _calculate_fraud_risk(self, message: str, buyer: Buyer) -> int:
        """Calcula el riesgo de fraude (0-100)"""
        score = 0
        
        # Usuario nuevo
        if buyer.valoraciones == 0:
            score += 30
        
        # Sin foto de perfil
        if not buyer.tiene_foto:
            score += 10
        
        # Ubicación lejana
        if buyer.distancia_km > 500:
            score += 20
        
        # Patrones de fraude en mensaje
        for pattern in self.fraud_patterns["palabras_fraude"]:
            if pattern in message:
                score += 25
        
        # Solicitudes peligrosas
        for solicitud in self.fraud_patterns["solicitudes_peligrosas"]:
            if solicitud in message:
                score += 30
        
        # URLs sospechosas
        for pattern in self.fraud_patterns["urls_sospechosas"]:
            if re.search(pattern, message):
                score += 40
        
        return min(score, 100)
    
    def _detect_conversation_state(self, intention: IntentionType, buyer_id: str) -> ConversationState:
        """Detecta el estado actual de la conversación"""
        if buyer_id not in self.conversations:
            self.conversations[buyer_id] = {
                "state": ConversationState.INICIAL, 
                "messages": 0,
                "last_activity": datetime.now(),
                "fraud_score": 0
            }
            return ConversationState.INICIAL
        
        conv = self.conversations[buyer_id]
        conv["messages"] += 1
        conv["last_activity"] = datetime.now()
        
        # Lógica de transición de estados
        if intention == IntentionType.COMPRA_DIRECTA:
            conv["state"] = ConversationState.COMPROMETIDO
        elif intention == IntentionType.NEGOCIACION:
            conv["state"] = ConversationState.NEGOCIANDO
        elif intention in [IntentionType.UBICACION, IntentionType.PAGO]:
            conv["state"] = ConversationState.COORDINANDO
        elif conv["messages"] > 20:
            conv["state"] = ConversationState.ABANDONADO
        
        return conv["state"]

    def generate_response(self, 
                         analysis: Dict, 
                         message: str, 
                         buyer: Buyer, 
                         product: Product) -> Optional[str]:
        """Genera una respuesta apropiada basada en el análisis"""
        
        # Si el riesgo de fraude es muy alto, respuesta de seguridad
        if analysis["fraud_risk"] > 70:
            return self._get_security_response(message)
        
        # Generar respuesta según intención
        intention = analysis["intention"]
        response_category = self._map_intention_to_category(intention)
        
        if response_category:
            response = self._select_response_template(response_category, analysis["state"])
            response = self._personalize_response(response, product, buyer)
            return response
        
        return None
    
    def _get_security_response(self, message: str) -> str:
        """Obtiene respuesta de seguridad para mensajes sospechosos"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["whatsapp", "telegram", "teléfono"]):
            return random.choice(self.templates.get("respuestas_seguridad", {}).get("no_whatsapp", ["Prefiero mantener la comunicación por Wallapop"]))
        
        if any(word in message_lower for word in ["dni", "documento", "tarjeta"]):
            return random.choice(self.templates.get("respuestas_seguridad", {}).get("no_datos_personales", ["No comparto datos personales"]))
        
        if "adelantado" in message_lower or "por adelantado" in message_lower:
            return random.choice(self.templates.get("respuestas_seguridad", {}).get("pago_anticipado", ["El pago se hace en la entrega"]))
        
        if re.search(r"https?://", message_lower):
            return random.choice(self.templates.get("respuestas_seguridad", {}).get("no_enlaces", ["No puedo acceder a enlaces externos"]))
        
        # Respuesta genérica de sospecha
        return random.choice(self.templates.get("respuestas_seguridad", {}).get("sospecha_fraude", ["Lo siento, no me parece seguro"]))
    
    def _map_intention_to_category(self, intention: IntentionType) -> Optional[str]:
        """Mapea la intención a una categoría de respuesta"""
        mapping = {
            IntentionType.SALUDO: "saludos",
            IntentionType.PRECIO: "precio",
            IntentionType.NEGOCIACION: "precio",
            IntentionType.DISPONIBILIDAD: "disponibilidad",
            IntentionType.ESTADO_PRODUCTO: "estado_producto",
            IntentionType.UBICACION: "ubicacion",
            IntentionType.ENVIO: "envio",
            IntentionType.COMPRA_DIRECTA: "cierre_venta",
            IntentionType.PAGO: "metodo_pago"
        }
        return mapping.get(intention)
    
    def _select_response_template(self, category: str, state: ConversationState) -> str:
        """Selecciona una plantilla de respuesta apropiada"""
        # Ajustar subcategoría según el estado
        if category == "saludos":
            subcategory = "inicial" if state == ConversationState.INICIAL else "respuesta"
        elif category == "precio" and state == ConversationState.NEGOCIANDO:
            subcategory = "negociacion"
        elif category == "disponibilidad":
            subcategory = "disponible"  # Asumimos disponible por defecto
        else:
            # Para otras categorías, tomar la primera subcategoría disponible
            subcategories = list(self.templates.get(category, {}).keys())
            subcategory = subcategories[0] if subcategories else None
        
        # Obtener respuestas de la categoría/subcategoría
        if category in self.templates:
            if isinstance(self.templates[category], dict) and subcategory:
                responses = self.templates[category].get(subcategory, [])
                if isinstance(responses, list):
                    return random.choice(responses) if responses else ""
                elif isinstance(responses, dict):
                    # Si es un diccionario anidado, elegir una respuesta aleatoria
                    sub_responses = []
                    for key, value in responses.items():
                        if isinstance(value, list):
                            sub_responses.extend(value)
                    if sub_responses:
                        return random.choice(sub_responses)
            elif isinstance(self.templates[category], list):
                return random.choice(self.templates[category]) if self.templates[category] else ""
        
        return "Lo siento, no entendí bien tu pregunta. ¿Puedes ser más específico?"
    
    def _personalize_response(self, template: str, product: Product, buyer: Buyer) -> str:
        """Personaliza la respuesta con datos específicos"""
        replacements = {
            "{producto}": product.titulo,
            "{precio}": str(product.precio),
            "{precio_minimo}": str(product.precio_minimo),
            "{precio_rebajado}": str(int(product.precio * 0.95)),
            "{descuento}": str(int(product.precio * 0.05)),
            "{zona}": product.zona,
            "{estado}": product.estado,
            "{coste_envio}": "5-7",  # Aproximado
            "{telefono}": "XXX XXX XXX",  # Se rellenará después
            "{dias}": "esta semana",
            "{dia}": "mañana",
            "{hora}": "18:00",
            "{horario}": "la tarde",
            "{lugar}": "centro comercial",
            "{lugar_publico}": "la estación de metro",
            "{descripcion_vendedor}": "una camiseta azul"
        }
        
        for key, value in replacements.items():
            template = template.replace(key, value)
        
        return template
    
    def should_respond(self, buyer: Buyer, last_message_time: datetime) -> bool:
        """Determina si se debe responder basado en el timing"""
        # No responder después de medianoche
        current_hour = datetime.now().hour
        if current_hour < 9 or current_hour > 22:
            return False
        
        # Calcular delay apropiado
        time_since_message = (datetime.now() - last_message_time).seconds
        
        # Delays según configuración
        min_delay = self.templates.get("variables_sistema", {}).get("tiempo_respuesta", {}).get("min", 30)
        max_delay = self.templates.get("variables_sistema", {}).get("tiempo_respuesta", {}).get("max", 120)
        
        required_delay = random.randint(min_delay, max_delay)
        
        return time_since_message >= required_delay
    
    def handle_conversation_flow(self, 
                                buyer_id: str, 
                                messages: List[Dict],
                                product: Product) -> Dict:
        """Gestiona el flujo completo de una conversación"""
        if buyer_id not in self.conversations:
            self.conversations[buyer_id] = {
                "state": ConversationState.INICIAL,
                "messages": 0,
                "last_activity": datetime.now(),
                "fraud_score": 0
            }
        
        conv = self.conversations[buyer_id]
        
        # Verificar si la conversación está abandonada
        if (datetime.now() - conv["last_activity"]).days > 2:
            conv["state"] = ConversationState.ABANDONADO
        
        # Actualizar actividad
        conv["last_activity"] = datetime.now()
        
        # Determinar siguiente acción
        if conv["state"] == ConversationState.ABANDONADO:
            # Intentar recuperación
            if conv["messages"] < 10:
                recovery_msg = self._get_recovery_message(conv["last_activity"])
                if recovery_msg:
                    return {
                        "action": "recuperar",
                        "message": recovery_msg
                    }
        
        return {"action": "continuar", "state": conv["state"]}
    
    def _get_recovery_message(self, last_activity: datetime) -> Optional[str]:
        """Obtiene mensaje de recuperación según el tiempo transcurrido"""
        hours_passed = (datetime.now() - last_activity).total_seconds() / 3600
        
        if hours_passed < 24:
            return None  # Muy pronto para recuperar
        elif hours_passed < 48:
            return random.choice(self.templates.get("recuperacion_venta", {}).get("24h", []))
        else:
            return random.choice(self.templates.get("recuperacion_venta", {}).get("48h", []))
    
    def get_conversation_summary(self, buyer_id: str) -> Dict:
        """Obtiene un resumen del estado de la conversación"""
        if buyer_id not in self.conversations:
            return {"exists": False}
        
        conv = self.conversations[buyer_id]
        return {
            "exists": True,
            "state": conv["state"].value,
            "messages_count": conv["messages"],
            "last_activity": conv["last_activity"].isoformat(),
            "fraud_score": conv.get("fraud_score", 0),
            "requires_attention": conv["state"] in [
                ConversationState.COMPROMETIDO,
                ConversationState.COORDINANDO
            ]
        }