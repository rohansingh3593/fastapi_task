"""Main entry point for Konsole UI FastAPI application"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
from pathlib import Path

from app.core.config import get_settings
from app.database import connect_to_mongo, close_mongo_connection, DatabaseConnectionError
from app.routers import namespaces as namespaces_router
from app.routers import applications as applications_router
from app.routers import health as health_router
from app.services.kube_service import KubeServiceError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown events.
    Handles MongoDB connection initialization and cleanup.
    """
    # Startup
    logger.info("Starting Konsole UI application...")
    try:
        await connect_to_mongo()
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Konsole UI application...")
    try:
        await close_mongo_connection()
    except Exception as e:
        logger.warning(f"Error during shutdown: {e}")


# Initialize FastAPI application
app = FastAPI(
    title="Konsole UI",
    description="FastAPI backend for Konsole UI application",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
else:
    logger.warning(f"Frontend directory not found at {frontend_path}")


# Exception handlers
@app.exception_handler(KubeServiceError)
async def kube_exception_handler(request: Request, exc: KubeServiceError):
    logger.error(f"Kubernetes service error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc), "message": "Kubernetes cluster unavailable"},
    )


@app.exception_handler(DatabaseConnectionError)
async def database_exception_handler(request: Request, exc: DatabaseConnectionError):
    logger.error(f"Database connection error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc), "message": "MongoDB connection unavailable"},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler for consistent error responses"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "message": "Internal server error"
        }
    )


# Include API routers
app.include_router(namespaces_router.router, prefix="/api")
app.include_router(applications_router.router, prefix="/api")
app.include_router(health_router.router, prefix="/api")


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Konsole UI API"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Konsole UI API",
        "docs": "/docs",
        "dashboard": "/static/index.html",
        "version": "0.1.0"
    }


# Include API routers
# (To be added in subsequent phases)
# from app.routers import example
# app.include_router(example.router, prefix="/api", tags=["example"])


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting Konsole UI on http://localhost:{settings.server_port}")
    logger.info(f"Dashboard: http://localhost:{settings.server_port}/static/index.html")
    logger.info(f"API Docs: http://localhost:{settings.server_port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.server_port,
        reload=settings.debug,
        log_level=settings.log_level
    )
