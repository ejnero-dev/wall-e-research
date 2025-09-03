# wallapop_scraper.py
"""
Scraper de precios para Wallapop
Busca productos similares y extrae información de precios
"""

import asyncio
import re
from typing import List, Dict, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page
import json
import logging

logger = logging.getLogger(__name__)


class WallapopPriceScraper:
    def __init__(self):
        self.base_url = "https://es.wallapop.com"
        self.search_url = f"{self.base_url}/search"

    async def search_prices(
        self,
        product_name: str,
        condition: str = "all",
        location: str = "España",
        max_results: int = 50,
    ) -> List[Dict]:
        """Busca precios de productos similares en Wallapop"""

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            try:
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                )

                page = await context.new_page()

                # Construir URL de búsqueda
                search_params = self._build_search_url(product_name, location)

                logger.info(f"Buscando en Wallapop: {product_name}")
                await page.goto(search_params, wait_until="networkidle")

                # Esperar a que carguen los resultados
                await page.wait_for_selector(".ItemCardList__item", timeout=10000)

                # Extraer datos de productos
                products = await self._extract_products(page, max_results)

                # Filtrar por condición si es necesario
                if condition != "all":
                    products = [
                        p for p in products if self._matches_condition(p, condition)
                    ]

                logger.info(f"Encontrados {len(products)} productos en Wallapop")
                return products

            except Exception as e:
                logger.error(f"Error scraping Wallapop: {e}")
                return []
            finally:
                await browser.close()

    def _build_search_url(self, query: str, location: str) -> str:
        """Construye la URL de búsqueda"""
        # Limpiar y formatear query
        clean_query = re.sub(r"[^\w\s-]", "", query)
        query_param = clean_query.replace(" ", "-").lower()

        # URL base con parámetros
        url = f"{self.search_url}?keywords={query_param}"

        # Añadir ubicación si es específica
        if location and location != "España":
            url += f"&latitude=40.4168&longitude=-3.7038"  # Madrid por defecto

        return url

    async def _extract_products(self, page: Page, max_results: int) -> List[Dict]:
        """Extrae información de productos de la página"""
        products = []

        # Scroll para cargar más resultados
        for _ in range(3):  # 3 scrolls máximo
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

        # Extraer datos usando JavaScript en el navegador
        items_data = await page.evaluate(
            """
            () => {
                const items = document.querySelectorAll('.ItemCardList__item');
                return Array.from(items).map(item => {
                    try {
                        // Título
                        const titleEl = item.querySelector('.ItemCard__title');
                        const title = titleEl ? titleEl.textContent.trim() : '';
                        
                        // Precio
                        const priceEl = item.querySelector('.ItemCard__price');
                        const priceText = priceEl ? priceEl.textContent.trim() : '';
                        const price = parseFloat(priceText.replace('€', '').replace(',', '.')) || 0;
                        
                        // Descripción/Estado
                        const descEl = item.querySelector('.ItemCard__description');
                        const description = descEl ? descEl.textContent.trim() : '';
                        
                        // Ubicación
                        const locationEl = item.querySelector('.ItemCard__location');
                        const location = locationEl ? locationEl.textContent.trim() : '';
                        
                        // URL del producto
                        const linkEl = item.querySelector('a');
                        const url = linkEl ? linkEl.href : '';
                        
                        // Vendido o no
                        const soldEl = item.querySelector('.ItemCard__sold');
                        const sold = !!soldEl;
                        
                        // Imagen para análisis posterior
                        const imgEl = item.querySelector('img');
                        const image = imgEl ? imgEl.src : '';
                        
                        return {
                            title,
                            price,
                            description,
                            location,
                            url,
                            sold,
                            image
                        };
                    } catch (e) {
                        return null;
                    }
                }).filter(item => item !== null);
            }
        """
        )

        # Procesar y enriquecer datos
        for item in items_data[:max_results]:
            if item["price"] > 0:  # Solo productos con precio
                product = {
                    "platform": "wallapop",
                    "title": item["title"],
                    "price": item["price"],
                    "condition": self._extract_condition(
                        item["title"], item["description"]
                    ),
                    "shipping_included": self._has_shipping(item["description"]),
                    "location": item["location"],
                    "url": item["url"],
                    "date_scraped": datetime.now(),
                    "sold": item["sold"],
                    "image": item["image"],
                }
                products.append(product)

        return products

    def _extract_condition(self, title: str, description: str) -> str:
        """Extrae la condición del producto del título o descripción"""
        text = f"{title} {description}".lower()

        conditions = {
            "nuevo": ["nuevo", "precintado", "sin abrir", "sellado", "new"],
            "como nuevo": ["como nuevo", "casi nuevo", "perfecto estado"],
            "buen estado": ["buen estado", "muy buen estado", "poco uso"],
            "usado": ["usado", "segunda mano", "con uso"],
        }

        for condition, keywords in conditions.items():
            if any(keyword in text for keyword in keywords):
                return condition

        return "usado"  # Por defecto

    def _has_shipping(self, description: str) -> bool:
        """Detecta si incluye envío"""
        shipping_keywords = [
            "envío incluido",
            "envio incluido",
            "gastos incluidos",
            "envío gratis",
            "envio gratis",
            "portes incluidos",
        ]
        return any(keyword in description.lower() for keyword in shipping_keywords)

    def _matches_condition(self, product: Dict, target_condition: str) -> bool:
        """Verifica si el producto coincide con la condición buscada"""
        if target_condition == "all":
            return True

        condition_map = {
            "nuevo": ["nuevo"],
            "como_nuevo": ["como nuevo", "nuevo"],
            "buen_estado": ["buen estado", "como nuevo"],
            "usado": ["usado", "buen estado"],
        }

        allowed_conditions = condition_map.get(target_condition, [target_condition])
        return product["condition"] in allowed_conditions

    async def get_product_details(self, product_url: str) -> Optional[Dict]:
        """Obtiene detalles adicionales de un producto específico"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            try:
                page = await browser.new_page()
                await page.goto(product_url, wait_until="networkidle")

                # Extraer información detallada
                details = await page.evaluate(
                    """
                    () => {
                        try {
                            // Vendedor
                            const sellerEl = document.querySelector('.UserInfo__name');
                            const seller = sellerEl ? sellerEl.textContent.trim() : '';
                            
                            // Valoraciones del vendedor
                            const ratingsEl = document.querySelector('.UserInfo__rating');
                            const ratings = ratingsEl ? ratingsEl.textContent.trim() : '';
                            
                            // Vistas
                            const viewsEl = document.querySelector('.ItemDetail__views');
                            const views = viewsEl ? viewsEl.textContent.trim() : '';
                            
                            // Favoritos
                            const favsEl = document.querySelector('.ItemDetail__favorites');
                            const favorites = favsEl ? favsEl.textContent.trim() : '';
                            
                            // Descripción completa
                            const descEl = document.querySelector('.ItemDetail__description');
                            const fullDescription = descEl ? descEl.textContent.trim() : '';
                            
                            return {
                                seller,
                                ratings,
                                views,
                                favorites,
                                fullDescription
                            };
                        } catch (e) {
                            return null;
                        }
                    }
                """
                )

                return details

            except Exception as e:
                logger.error(f"Error getting product details: {e}")
                return None
            finally:
                await browser.close()

    async def monitor_price_changes(
        self, product_urls: List[str], interval_hours: int = 24
    ) -> Dict:
        """Monitorea cambios de precio en productos específicos"""
        price_history = {}

        while True:
            for url in product_urls:
                try:
                    # Obtener precio actual
                    details = await self.get_product_details(url)
                    if details:
                        if url not in price_history:
                            price_history[url] = []

                        price_history[url].append(
                            {
                                "price": details.get("price"),
                                "timestamp": datetime.now(),
                                "sold": details.get("sold", False),
                            }
                        )

                        # Detectar cambios significativos
                        if len(price_history[url]) > 1:
                            last_price = price_history[url][-2]["price"]
                            current_price = price_history[url][-1]["price"]

                            if last_price and current_price:
                                change_percent = (
                                    (current_price - last_price) / last_price
                                ) * 100

                                if abs(change_percent) > 10:  # Cambio > 10%
                                    logger.info(
                                        f"Cambio de precio detectado en {url}: {change_percent:.1f}%"
                                    )

                except Exception as e:
                    logger.error(f"Error monitoring {url}: {e}")

            # Esperar hasta la próxima verificación
            await asyncio.sleep(interval_hours * 3600)
