# __init__.py
"""
Price Scrapers
Scrapers para diferentes plataformas de venta
"""

from .wallapop_scraper import WallapopPriceScraper
from .amazon_scraper import AmazonPriceScraper

__all__ = ["WallapopPriceScraper", "AmazonPriceScraper"]
