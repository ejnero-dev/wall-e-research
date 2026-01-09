# amazon_scraper.py
"""
Scraper de precios para Amazon España
Obtiene precios de referencia para comparación
"""

import asyncio
import re
from typing import List, Dict, Optional
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class AmazonPriceScraper:
    def __init__(self):
        self.base_url = "https://www.amazon.es"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    async def search_prices(
        self, product_name: str, only_new: bool = True, max_results: int = 20
    ) -> List[Dict]:
        """Busca precios en Amazon España"""

        try:
            # Construir URL de búsqueda
            search_query = product_name.replace(" ", "+")
            url = f"{self.base_url}/s?k={search_query}"

            # Si solo queremos productos nuevos
            if only_new:
                url += "&p_n_condition-type=new"

            async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
                response = await client.get(url)

                if response.status_code != 200:
                    logger.warning(f"Amazon returned status {response.status_code}")
                    return []

                # Parsear HTML
                soup = BeautifulSoup(response.text, "html.parser")

                # Extraer productos
                products = self._extract_products(soup, max_results)

                logger.info(f"Encontrados {len(products)} productos en Amazon")
                return products

        except Exception as e:
            logger.error(f"Error scraping Amazon: {e}")
            return []

    def _extract_products(self, soup: BeautifulSoup, max_results: int) -> List[Dict]:
        """Extrae información de productos del HTML de Amazon"""
        products = []

        # Buscar todos los items de resultados
        items = soup.find_all("div", {"data-component-type": "s-search-result"})

        for item in items[:max_results]:
            try:
                product_data = self._parse_product_item(item)
                if product_data and product_data["price"] > 0:
                    products.append(product_data)
            except Exception as e:
                logger.debug(f"Error parsing product item: {e}")
                continue

        return products

    def _parse_product_item(self, item) -> Optional[Dict]:
        """Parsea un item individual de producto"""
        try:
            # Título
            title_elem = item.find(
                "h2",
                class_="s-size-mini s-spacing-none s-color-base s-line-height-normal",
            )
            if not title_elem:
                title_elem = item.find("h2")

            title = title_elem.text.strip() if title_elem else ""

            # Precio
            price = self._extract_price(item)
            if not price:
                return None

            # URL
            link_elem = item.find("a", class_="s-link")
            if not link_elem:
                link_elem = item.find("a")

            url = (
                f"{self.base_url}{link_elem['href']}"
                if link_elem and "href" in link_elem.attrs
                else ""
            )

            # Valoraciones
            rating_elem = item.find("span", class_="a-icon-alt")
            rating = self._extract_rating(rating_elem.text) if rating_elem else None

            # Número de reseñas
            reviews_elem = item.find("span", {"aria-label": True})
            num_reviews = (
                self._extract_review_count(reviews_elem) if reviews_elem else 0
            )

            # Prime
            is_prime = bool(item.find("i", class_="a-icon-prime"))

            # Vendedor
            seller = self._extract_seller(item)

            return {
                "platform": "amazon",
                "title": title,
                "price": price,
                "condition": "nuevo",  # Amazon principalmente vende nuevo
                "shipping_included": is_prime,  # Prime incluye envío
                "location": "España",
                "url": url,
                "date_scraped": datetime.now(),
                "seller_rating": rating,
                "num_reviews": num_reviews,
                "seller": seller,
                "is_prime": is_prime,
            }

        except Exception as e:
            logger.debug(f"Error parsing Amazon product: {e}")
            return None

    def _extract_price(self, item) -> Optional[float]:
        """Extrae el precio del item"""
        # Buscar precio principal
        price_whole = item.find("span", class_="a-price-whole")
        if price_whole:
            price_text = price_whole.text.strip()
            # Limpiar y convertir
            price_text = price_text.replace(",", ".").replace("€", "").strip()
            try:
                return float(price_text)
            except Exception:
                pass

        # Buscar precio alternativo
        price_elem = item.find("span", class_="a-price")
        if price_elem:
            price_text = price_elem.text.strip()
            # Extraer números
            match = re.search(r"(\d+[,.]?\d*)", price_text)
            if match:
                price_str = match.group(1).replace(",", ".")
                try:
                    return float(price_str)
                except Exception:
                    pass

        return None

    def _extract_rating(self, rating_text: str) -> Optional[float]:
        """Extrae la valoración del texto"""
        match = re.search(r"(\d+[,.]?\d*)", rating_text)
        if match:
            rating_str = match.group(1).replace(",", ".")
            try:
                return float(rating_str)
            except Exception:
                pass
        return None

    def _extract_review_count(self, reviews_elem) -> int:
        """Extrae el número de reseñas"""
        if reviews_elem and "aria-label" in reviews_elem.attrs:
            text = reviews_elem["aria-label"]
            match = re.search(r"(\d+)", text)
            if match:
                try:
                    return int(match.group(1))
                except Exception:
                    pass
        return 0

    def _extract_seller(self, item) -> str:
        """Extrae información del vendedor"""
        # Por defecto Amazon
        seller = "Amazon"

        # Buscar si es vendedor tercero
        seller_elem = item.find("span", text=re.compile(r"Vendido por"))
        if seller_elem:
            next_elem = seller_elem.find_next("span")
            if next_elem:
                seller = next_elem.text.strip()

        return seller

    async def get_product_details(self, product_url: str) -> Optional[Dict]:
        """Obtiene detalles específicos de un producto"""
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
                response = await client.get(product_url)

                if response.status_code != 200:
                    return None

                soup = BeautifulSoup(response.text, "html.parser")

                # Extraer detalles adicionales
                details = {
                    "variations": self._extract_variations(soup),
                    "features": self._extract_features(soup),
                    "availability": self._extract_availability(soup),
                    "other_sellers": self._extract_other_sellers(soup),
                }

                return details

        except Exception as e:
            logger.error(f"Error getting Amazon product details: {e}")
            return None

    def _extract_variations(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrae variaciones del producto (color, tamaño, etc)"""
        variations = []

        # Buscar selector de variaciones
        variation_elements = soup.find_all("li", class_="swatchSelect")

        for elem in variation_elements:
            price_elem = elem.find("span", class_="a-size-mini")
            if price_elem:
                variations.append(
                    {
                        "type": elem.get("title", ""),
                        "price": self._extract_price_from_text(price_elem.text),
                    }
                )

        return variations

    def _extract_features(self, soup: BeautifulSoup) -> List[str]:
        """Extrae características principales del producto"""
        features = []

        feature_list = soup.find("div", id="feature-bullets")
        if feature_list:
            items = feature_list.find_all("span", class_="a-list-item")
            features = [item.text.strip() for item in items if item.text.strip()]

        return features[:5]  # Limitar a 5 características

    def _extract_availability(self, soup: BeautifulSoup) -> str:
        """Extrae disponibilidad del producto"""
        availability_elem = soup.find("div", id="availability")
        if availability_elem:
            text_elem = availability_elem.find("span")
            if text_elem:
                return text_elem.text.strip()

        return "No especificado"

    def _extract_other_sellers(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrae información de otros vendedores"""
        other_sellers = []

        # Buscar sección de otros vendedores
        sellers_elem = soup.find("div", id="aod-offer-list")
        if not sellers_elem:
            sellers_elem = soup.find("div", class_="a-section a-spacing-base")

        # Por ahora retornar vacío, esta parte es compleja
        return other_sellers

    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """Extrae precio de un texto"""
        match = re.search(r"(\d+[,.]?\d*)\s*€", text)
        if match:
            price_str = match.group(1).replace(",", ".")
            try:
                return float(price_str)
            except Exception:
                pass
        return None
