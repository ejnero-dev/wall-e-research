"""
Dashboard Server for Wall-E Research
FastAPI application with WebSocket support for real-time dashboard
"""
import asyncio
import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.api.dashboard_routes import router as dashboard_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown
    """
    # Startup
    logger.info("Starting Wall-E Dashboard API...")
    
    # Initialize any required services here
    # For example: database connections, Redis, etc.
    
    yield
    
    # Shutdown
    logger.info("Shutting down Wall-E Dashboard API...")
    
    # Clean up resources here
    

# Create FastAPI app
app = FastAPI(
    title="Wall-E Research Dashboard API",
    description="Real-time monitoring and control API for Wall-E bot",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js development
        "http://localhost:3001",  # Alternative port
        "http://localhost:8080",  # Vite development (puerto actual)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8080",  # Vite development (127.0.0.1)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include dashboard routes
app.include_router(dashboard_router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Wall-E Research Dashboard API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "dashboard": "/api/dashboard",
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/api/dashboard/health"
        }
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Additional startup tasks"""
    logger.info("Dashboard API ready to accept connections")
    logger.info("Documentation available at: http://localhost:8000/docs")


def main():
    """Main entry point for running the server"""
    # Server configuration
    config = {
        "app": "src.api.dashboard_server:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,  # Enable auto-reload for development
        "reload_dirs": ["src/api"],  # Watch these directories
        "log_level": "info",
        "access_log": True,
        # WebSocket support
        "ws_ping_interval": 20,
        "ws_ping_timeout": 10,
    }
    
    logger.info(f"Starting server on http://{config['host']}:{config['port']}")
    
    # Run the server
    uvicorn.run(**config)


if __name__ == "__main__":
    main()
