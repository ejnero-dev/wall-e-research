#!/usr/bin/env python3
"""
💰 DEMO: Análisis de Precios Competitivos Wall-E
Demuestra las capacidades de análisis de mercado y pricing strategy
"""
import logging
import os
import sys
from datetime import datetime
from dataclasses import dataclass
from typing import List
import statistics

# Añadir el directorio padre al path para importar módulos src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PriceData:
    """Datos de precio de un producto"""
    platform: str
    title: str
    price: float
    condition: str
    shipping_included: bool
    location: str
    url: str
    date_scraped: datetime
    seller_rating: float = None
    sold: bool = False

def analyze_iphone_market():
    """Análisis completo del mercado iPhone 12"""
    logger.info("💰 === DEMO: ANÁLISIS DE PRECIOS COMPETITIVOS ===")
    
    # Datos reales simulados del mercado
    market_data = [
        PriceData("wallapop", "iPhone 12 128GB Negro", 380, "usado", True, "Barcelona", "", datetime.now(), 4.2),
        PriceData("wallapop", "iPhone 12 128GB Negro", 420, "como nuevo", True, "Madrid", "", datetime.now(), 4.8),
        PriceData("wallapop", "iPhone 12 128GB Negro", 450, "nuevo", True, "Valencia", "", datetime.now(), 4.9),
        PriceData("wallapop", "iPhone 12 128GB Azul", 400, "buen estado", False, "Sevilla", "", datetime.now(), 4.5),
        PriceData("wallapop", "iPhone 12 128GB Blanco", 390, "usado", True, "Bilbao", "", datetime.now(), 4.1),
        PriceData("amazon", "iPhone 12 128GB", 529, "nuevo", True, "Online", "", datetime.now(), 4.7),
        PriceData("wallapop", "iPhone 12 128GB Verde", 410, "como nuevo", False, "Granada", "", datetime.now(), 4.6),
        PriceData("wallapop", "iPhone 12 128GB Negro", 370, "usado", True, "Málaga", "", datetime.now(), 4.0),
    ]
    
    # Tu producto
    your_product = {
        "name": "iPhone 12 128GB Negro",
        "price": 420.0,
        "condition": "como nuevo",
        "location": "Madrid"
    }
    
    # Análisis estadístico
    wallapop_prices = [p.price for p in market_data if p.platform == "wallapop"]
    all_prices = [p.price for p in market_data]
    
    avg_price = statistics.mean(wallapop_prices)
    median_price = statistics.median(wallapop_prices)
    min_price = min(wallapop_prices)
    max_price = max(wallapop_prices)
    
    logger.info(f"📊 ANÁLISIS DE MERCADO - {your_product['name']}")
    logger.info(f"   📈 Precio promedio Wallapop: {avg_price:.2f}€")
    logger.info(f"   📊 Precio mediano: {median_price:.2f}€")
    logger.info(f"   📉 Rango de precios: {min_price}€ - {max_price}€")
    logger.info(f"   🔢 Total anuncios analizados: {len(wallapop_prices)}")
    
    # Análisis por estado
    condition_prices = {}
    for p in market_data:
        if p.platform == "wallapop":
            if p.condition not in condition_prices:
                condition_prices[p.condition] = []
            condition_prices[p.condition].append(p.price)
    
    logger.info(f"\n📋 PRECIOS POR ESTADO:")
    for condition, prices in condition_prices.items():
        avg_condition = statistics.mean(prices) if prices else 0
        logger.info(f"   {condition.upper()}: {avg_condition:.2f}€ (promedio de {len(prices)} anuncios)")
    
    # Estrategias de pricing
    competitive_price = avg_price * 0.95  # 5% below average
    premium_price = avg_price * 1.05     # 5% above average
    quick_sale_price = avg_price * 0.90   # 10% below average
    
    logger.info(f"\n💡 ESTRATEGIAS RECOMENDADAS:")
    logger.info(f"   🏃 Venta rápida (10% descuento): {quick_sale_price:.2f}€")
    logger.info(f"   ⚖️ Precio competitivo (5% descuento): {competitive_price:.2f}€")
    logger.info(f"   💰 Maximizar ganancia (5% premium): {premium_price:.2f}€")
    
    # Evaluación de tu precio
    your_price = your_product['price']
    logger.info(f"\n🎯 EVALUACIÓN DE TU PRECIO ({your_price}€):")
    
    if your_price < competitive_price:
        logger.info(f"   ✅ EXCELENTE - Tu precio es muy competitivo")
        logger.info(f"   📈 Posibilidad alta de venta rápida")
    elif your_price <= premium_price:
        logger.info(f"   ⚖️ BUENO - Tu precio está en rango óptimo")
        logger.info(f"   📊 Precio balanceado entre competitividad y ganancia")
    else:
        logger.info(f"   ⚠️ ALTO - Tu precio está por encima del mercado")
        logger.info(f"   📉 Considera bajar para mejorar competitividad")
    
    # Comparación con tu condición específica
    same_condition_prices = condition_prices.get(your_product['condition'], [])
    if same_condition_prices:
        avg_same_condition = statistics.mean(same_condition_prices)
        logger.info(f"\n🔍 COMPARACIÓN ESPECÍFICA ({your_product['condition'].upper()}):")
        logger.info(f"   📊 Promedio misma condición: {avg_same_condition:.2f}€")
        if your_price <= avg_same_condition:
            logger.info(f"   ✅ Tu precio está bien posicionado para tu condición")
        else:
            logger.info(f"   ⚠️ Tu precio es alto comparado con misma condición")
    
    # Tendencia de mercado simulada
    logger.info(f"\n📈 TENDENCIA DE MERCADO:")
    logger.info(f"   📊 iPhone 12 128GB: ESTABLE")
    logger.info(f"   💡 Demanda: ALTA (producto popular)")
    logger.info(f"   ⏰ Mejor momento venta: FINES DE SEMANA")
    logger.info(f"   📍 Tu ubicación (Madrid): VENTAJA (mercado grande)")
    
    return True

if __name__ == "__main__":
    success = analyze_iphone_market()
    if success:
        print("\n🎯 SUCCESS: Análisis de precios completado!")
    else:
        print("\n❌ ERROR: Falló el análisis de precios")