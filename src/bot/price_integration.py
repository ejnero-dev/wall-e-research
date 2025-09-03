# price_integration.py
"""
Integración del Sistema de Análisis de Precios con el Bot Principal
Ejemplo de cómo usar el análisis de precios en el flujo del bot
"""

import asyncio
from typing import Dict, Optional
from datetime import datetime
import logging

from price_analyzer import PriceAnalyzer
from conversation_engine.engine import ConversationEngine

logger = logging.getLogger(__name__)


class PriceAwareBot:
    """Bot con capacidad de análisis de precios integrada"""

    def __init__(self):
        self.price_analyzer = PriceAnalyzer()
        self.conversation_engine = ConversationEngine()
        self.product_prices = {}  # Cache de precios analizados

    async def handle_new_product(self, product: Dict) -> Dict:
        """Maneja un nuevo producto y sugiere precio óptimo"""

        logger.info(f"Analizando precio para: {product['title']}")

        # Analizar precio del mercado
        analysis = await self.price_analyzer.analyze_product_price(
            product_name=product["title"],
            product_condition=product["condition"],
            location=product.get("location", "España"),
        )

        # Determinar estrategia de precio
        pricing_strategy = self._determine_pricing_strategy(product, analysis)

        # Guardar en cache
        self.product_prices[product["id"]] = {
            "analysis": analysis,
            "strategy": pricing_strategy,
            "timestamp": datetime.now(),
        }

        return pricing_strategy

    def _determine_pricing_strategy(self, product: Dict, analysis: Dict) -> Dict:
        """Determina la estrategia de precio óptima"""

        # Si el usuario tiene prisa por vender
        if product.get("urgent_sale", False):
            return {
                "recommended_price": analysis.competitive_price,
                "strategy": "competitive",
                "reason": "Venta urgente - precio competitivo para venta rápida",
                "expected_days": "1-3 días",
            }

        # Si es un producto de alta demanda
        if analysis.market_trend == "subiendo":
            return {
                "recommended_price": analysis.premium_price,
                "strategy": "premium",
                "reason": "Alta demanda - puedes pedir precio premium",
                "expected_days": "7-14 días",
            }

        # Estrategia por defecto: equilibrada
        return {
            "recommended_price": analysis.suggested_price,
            "strategy": "balanced",
            "reason": "Precio equilibrado para venta en tiempo razonable",
            "expected_days": "5-7 días",
        }

    async def handle_price_negotiation(
        self, product_id: str, offered_price: float, buyer_profile: Dict
    ) -> str:
        """Maneja negociaciones de precio con compradores"""

        if product_id not in self.product_prices:
            return "Lo siento, necesito verificar el precio del mercado primero."

        price_data = self.product_prices[product_id]
        analysis = price_data["analysis"]

        # Calcular margen de negociación
        min_acceptable = analysis.competitive_price * 0.95  # 5% menos que competitivo

        if offered_price >= analysis.suggested_price:
            return "¡Perfecto! Acepto tu oferta. ¿Cuándo podemos quedar?"

        elif offered_price >= min_acceptable:
            # Considerar perfil del comprador
            if buyer_profile["valoraciones"] > 20 and buyer_profile["compras"] > 5:
                return f"Me gustaría {analysis.suggested_price}€, pero por tus buenas valoraciones te lo dejo en {offered_price}€"
            else:
                return f"Mi último precio sería {analysis.suggested_price * 0.97:.0f}€, no puedo bajar más"

        else:
            return f"Lo siento, es muy poco. El precio mínimo sería {min_acceptable:.0f}€ y ya es una ganga"

    async def monitor_market_changes(self, check_interval_hours: int = 24):
        """Monitorea cambios en el mercado y ajusta precios"""

        while True:
            for product_id, price_data in self.product_prices.items():
                try:
                    # Re-analizar si han pasado más de X horas
                    hours_passed = (
                        datetime.now() - price_data["timestamp"]
                    ).total_seconds() / 3600

                    if hours_passed > check_interval_hours:
                        logger.info(f"Re-analizando precio para producto {product_id}")

                        # Obtener datos del producto (desde DB en producción)
                        product = await self._get_product_data(product_id)

                        # Nuevo análisis
                        new_analysis = await self.price_analyzer.analyze_product_price(
                            product_name=product["title"],
                            product_condition=product["condition"],
                        )

                        # Comparar con análisis anterior
                        old_price = price_data["analysis"].suggested_price
                        new_price = new_analysis.suggested_price

                        price_change = ((new_price - old_price) / old_price) * 100

                        if abs(price_change) > 5:  # Cambio significativo
                            await self._notify_price_change(
                                product_id, old_price, new_price, price_change
                            )

                            # Actualizar cache
                            self.product_prices[product_id]["analysis"] = new_analysis
                            self.product_prices[product_id][
                                "timestamp"
                            ] = datetime.now()

                except Exception as e:
                    logger.error(f"Error monitoreando producto {product_id}: {e}")

            await asyncio.sleep(check_interval_hours * 3600)

    async def suggest_price_for_quick_sale(self, product_id: str) -> Dict:
        """Sugiere precio para venta rápida cuando hay muchos mensajes"""

        if product_id not in self.product_prices:
            return {"error": "Producto no analizado"}

        analysis = self.product_prices[product_id]["analysis"]

        # Estrategias progresivas según tiempo sin vender
        suggestions = [
            {
                "days": 7,
                "discount": 0.05,
                "price": analysis.suggested_price * 0.95,
                "message": "Baja un 5% para aumentar interés",
            },
            {
                "days": 14,
                "discount": 0.10,
                "price": analysis.suggested_price * 0.90,
                "message": "Precio competitivo para venta rápida",
            },
            {
                "days": 21,
                "discount": 0.15,
                "price": analysis.competitive_price,
                "message": "Precio mínimo recomendado del mercado",
            },
        ]

        return suggestions

    async def _get_product_data(self, product_id: str) -> Dict:
        """Obtiene datos del producto (desde DB en producción)"""
        # Simulado - en producción vendría de la base de datos
        return {
            "id": product_id,
            "title": "iPhone 12 128GB",
            "condition": "buen estado",
            "location": "Madrid",
        }

    async def _notify_price_change(
        self, product_id: str, old_price: float, new_price: float, change_percent: float
    ):
        """Notifica cambios significativos de precio"""

        if change_percent > 0:
            message = f"📈 El precio de mercado ha subido un {change_percent:.1f}%"
            recommendation = "Considera subir tu precio"
        else:
            message = f"📉 El precio de mercado ha bajado un {abs(change_percent):.1f}%"
            recommendation = "Considera bajar tu precio para mantener competitividad"

        logger.info(f"{message}. {recommendation}")

        # Aquí se enviaría notificación al usuario
        # await send_notification(user_id, message, recommendation)


# Ejemplo de uso
async def example_usage():
    """Ejemplo de cómo usar el bot con análisis de precios"""

    bot = PriceAwareBot()

    # Nuevo producto
    product = {
        "id": "prod123",
        "title": "iPhone 12 Pro 256GB",
        "condition": "como nuevo",
        "location": "Barcelona",
        "urgent_sale": False,
    }

    # Analizar y obtener estrategia de precio
    strategy = await bot.handle_new_product(product)
    print(f"Precio recomendado: {strategy['recommended_price']}€")
    print(f"Estrategia: {strategy['strategy']}")
    print(f"Razón: {strategy['reason']}")

    # Simular negociación
    response = await bot.handle_price_negotiation(
        "prod123", 550.0, {"valoraciones": 25, "compras": 10}
    )
    print(f"Respuesta a negociación: {response}")

    # Sugerencias para venta rápida
    suggestions = await bot.suggest_price_for_quick_sale("prod123")
    for sugg in suggestions:
        print(
            f"Después de {sugg['days']} días: {sugg['price']:.2f}€ - {sugg['message']}"
        )


if __name__ == "__main__":
    asyncio.run(example_usage())
