# price_analyzer.py
"""
Analizador de Precios Competitivos
Analiza precios en Wallapop, Amazon y otras plataformas
para sugerir el precio óptimo de venta
"""

import asyncio
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import json
from bs4 import BeautifulSoup
import httpx

@dataclass
class PriceData:
    """Datos de precio de un producto"""
    platform: str
    title: str
    price: float
    condition: str  # nuevo, como nuevo, buen estado, usado
    shipping_included: bool
    location: str
    url: str
    date_scraped: datetime
    seller_rating: Optional[float] = None
    sold: bool = False

@dataclass
class PriceAnalysis:
    """Resultado del análisis de precios"""
    avg_price: float
    median_price: float
    min_price: float
    max_price: float
    suggested_price: float
    competitive_price: float  # Para venta rápida
    premium_price: float      # Para maximizar ganancia
    total_listings: int
    active_listings: int
    price_distribution: Dict[str, int]
    market_trend: str  # subiendo, bajando, estable
    confidence_score: float  # 0-100

class PriceAnalyzer:
    def __init__(self):
        self.wallapop_scraper = WallapopPriceScraper()
        self.amazon_scraper = AmazonPriceScraper()
        self.other_scrapers = {
            "ebay": EbayScraper(),
            "milanuncios": MilanunciosScraper(),
            "vinted": VintedScraper()
        }
        
    async def analyze_product_price(self, 
                                   product_name: str,
                                   product_condition: str = "buen estado",
                                   include_shipping: bool = True,
                                   location: str = "España") -> PriceAnalysis:
        """Analiza el precio óptimo para un producto"""
        
        # Recopilar datos de precios
        all_prices = []
        
        # 1. Buscar en Wallapop (prioridad)
        wallapop_prices = await self.wallapop_scraper.search_prices(
            product_name, 
            condition=product_condition,
            location=location
        )
        all_prices.extend(wallapop_prices)
        
        # 2. Buscar en Amazon (referencia)
        amazon_prices = await self.amazon_scraper.search_prices(
            product_name,
            only_new=(product_condition == "nuevo")
        )
        
        # 3. Buscar en otras plataformas
        for platform, scraper in self.other_scrapers.items():
            try:
                prices = await scraper.search_prices(product_name)
                all_prices.extend(prices)
            except:
                pass  # Ignorar errores en plataformas secundarias
        
        # Analizar datos recopilados
        analysis = self._analyze_price_data(
            all_prices,
            amazon_prices,
            product_condition,
            include_shipping
        )
        
        return analysis
    
    def _analyze_price_data(self,
                          all_prices: List[PriceData],
                          amazon_prices: List[PriceData],
                          condition: str,
                          include_shipping: bool) -> PriceAnalysis:
        """Analiza los datos de precios recopilados"""
        
        # Filtrar por condición similar
        relevant_prices = self._filter_by_condition(all_prices, condition)
        
        # Extraer solo los valores de precio
        price_values = [p.price for p in relevant_prices if p.price > 0]
        
        if not price_values:
            return self._create_empty_analysis()
        
        # Calcular estadísticas básicas
        avg_price = statistics.mean(price_values)
        median_price = statistics.median(price_values)
        min_price = min(price_values)
        max_price = max(price_values)
        
        # Calcular precios sugeridos
        suggested_price = self._calculate_suggested_price(
            price_values, amazon_prices, condition
        )
        
        # Precio competitivo (percentil 25 - venta rápida)
        competitive_price = self._calculate_percentile(price_values, 25)
        
        # Precio premium (percentil 75 - maximizar ganancia)
        premium_price = self._calculate_percentile(price_values, 75)
        
        # Distribución de precios
        distribution = self._calculate_price_distribution(price_values)
        
        # Tendencia del mercado
        trend = self._analyze_market_trend(relevant_prices)
        
        # Calcular confianza en el análisis
        confidence = self._calculate_confidence_score(
            len(price_values),
            len(amazon_prices),
            statistics.stdev(price_values) if len(price_values) > 1 else 0
        )
        
        return PriceAnalysis(
            avg_price=round(avg_price, 2),
            median_price=round(median_price, 2),
            min_price=round(min_price, 2),
            max_price=round(max_price, 2),
            suggested_price=round(suggested_price, 2),
            competitive_price=round(competitive_price, 2),
            premium_price=round(premium_price, 2),
            total_listings=len(all_prices),
            active_listings=len([p for p in all_prices if not p.sold]),
            price_distribution=distribution,
            market_trend=trend,
            confidence_score=confidence
        )
    
    def _filter_by_condition(self, prices: List[PriceData], target_condition: str) -> List[PriceData]:
        """Filtra precios por condición similar"""
        condition_groups = {
            "nuevo": ["nuevo", "precintado", "sin abrir", "new"],
            "como nuevo": ["como nuevo", "casi nuevo", "perfecto estado", "mint"],
            "buen estado": ["buen estado", "muy buen estado", "bueno", "good"],
            "usado": ["usado", "normal", "con uso", "aceptable", "used"]
        }
        
        # Encontrar grupo de condición
        target_group = None
        for group, conditions in condition_groups.items():
            if any(cond in target_condition.lower() for cond in conditions):
                target_group = conditions
                break
        
        if not target_group:
            target_group = condition_groups["buen estado"]
        
        # Filtrar precios
        filtered = []
        for price in prices:
            if any(cond in price.condition.lower() for cond in target_group):
                filtered.append(price)
        
        return filtered if filtered else prices
    
    def _calculate_suggested_price(self, 
                                 wallapop_prices: List[float],
                                 amazon_prices: List[PriceData],
                                 condition: str) -> float:
        """Calcula el precio sugerido óptimo"""
        
        if not wallapop_prices:
            return 0.0
        
        # Precio base: mediana de Wallapop
        base_price = statistics.median(wallapop_prices)
        
        # Ajustar según Amazon (si hay datos)
        if amazon_prices:
            amazon_min = min([p.price for p in amazon_prices])
            
            # El precio de segunda mano suele ser 60-80% del nuevo
            if condition == "nuevo":
                suggested = min(base_price, amazon_min * 0.95)
            elif condition == "como nuevo":
                suggested = min(base_price, amazon_min * 0.80)
            elif condition == "buen estado":
                suggested = min(base_price, amazon_min * 0.65)
            else:  # usado
                suggested = min(base_price, amazon_min * 0.50)
        else:
            suggested = base_price
        
        # Ajustar para ser competitivo (5% menos que la mediana)
        suggested = suggested * 0.95
        
        # Redondear a número bonito
        return self._round_to_nice_number(suggested)
    
    def _round_to_nice_number(self, price: float) -> float:
        """Redondea a un número 'bonito' para el precio"""
        if price < 10:
            return round(price, 0)
        elif price < 50:
            return round(price / 5) * 5
        elif price < 100:
            return round(price / 10) * 10
        elif price < 500:
            return round(price / 25) * 25
        else:
            return round(price / 50) * 50
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calcula un percentil específico"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        
        if index >= len(sorted_values):
            index = len(sorted_values) - 1
        
        return sorted_values[index]
    
    def _calculate_price_distribution(self, prices: List[float]) -> Dict[str, int]:
        """Calcula la distribución de precios por rangos"""
        if not prices:
            return {}
        
        distribution = {
            "0-25": 0,
            "25-50": 0,
            "50-100": 0,
            "100-200": 0,
            "200-500": 0,
            "500+": 0
        }
        
        for price in prices:
            if price <= 25:
                distribution["0-25"] += 1
            elif price <= 50:
                distribution["25-50"] += 1
            elif price <= 100:
                distribution["50-100"] += 1
            elif price <= 200:
                distribution["100-200"] += 1
            elif price <= 500:
                distribution["200-500"] += 1
            else:
                distribution["500+"] += 1
        
        # Eliminar rangos vacíos
        return {k: v for k, v in distribution.items() if v > 0}
    
    def _analyze_market_trend(self, prices: List[PriceData]) -> str:
        """Analiza la tendencia del mercado basándose en fechas"""
        if len(prices) < 5:
            return "datos_insuficientes"
        
        # Ordenar por fecha
        sorted_prices = sorted(prices, key=lambda p: p.date_scraped)
        
        # Comparar primera mitad con segunda mitad
        mid = len(sorted_prices) // 2
        first_half_avg = statistics.mean([p.price for p in sorted_prices[:mid]])
        second_half_avg = statistics.mean([p.price for p in sorted_prices[mid:]])
        
        difference_percent = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        
        if difference_percent > 5:
            return "subiendo"
        elif difference_percent < -5:
            return "bajando"
        else:
            return "estable"
    
    def _calculate_confidence_score(self, 
                                  num_samples: int,
                                  num_amazon: int,
                                  std_deviation: float) -> float:
        """Calcula la confianza en el análisis (0-100)"""
        score = 50.0  # Base
        
        # Más muestras = más confianza
        if num_samples >= 20:
            score += 20
        elif num_samples >= 10:
            score += 15
        elif num_samples >= 5:
            score += 10
        elif num_samples >= 3:
            score += 5
        
        # Datos de Amazon = más confianza
        if num_amazon > 0:
            score += 15
        
        # Menor desviación = más confianza
        if num_samples > 1:
            if std_deviation < 10:
                score += 15
            elif std_deviation < 25:
                score += 10
            elif std_deviation < 50:
                score += 5
        
        return min(score, 100.0)
    
    def _create_empty_analysis(self) -> PriceAnalysis:
        """Crea un análisis vacío cuando no hay datos"""
        return PriceAnalysis(
            avg_price=0,
            median_price=0,
            min_price=0,
            max_price=0,
            suggested_price=0,
            competitive_price=0,
            premium_price=0,
            total_listings=0,
            active_listings=0,
            price_distribution={},
            market_trend="sin_datos",
            confidence_score=0
        )
