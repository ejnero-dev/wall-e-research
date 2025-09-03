"""
API module for Wall-E Research Dashboard
"""

from .dashboard_routes import router as dashboard_router
from .dashboard_server import app

__all__ = ["dashboard_router", "app"]
