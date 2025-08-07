from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
from contextlib import asynccontextmanager

# Import application components
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, redis_client
from app.api import api_router
from app.core import create_error_response
from app.core.rate_limiter import limiter, custom_rate_limit_handler
from slowapi.errors import RateLimitExceeded

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting application...")
    try:
        await connect_to_mongo()
        await redis_client.connect()
        logger.info("Application startup completed successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down application...")
        await close_mongo_connection()
        await redis_client.disconnect()
        logger.info("Application shutdown completed")

def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title="BFP API - Browser Fingerprinting Platform",
        description="Browser Fingerprinting and Analytics API - Collects and analyzes browser fingerprints, device information, and visitor analytics",
        version="1.0.0",
        debug=settings.debug,
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Setup templates
    templates = Jinja2Templates(directory="templates")
    
    # Include API routers
    app.include_router(api_router, prefix="/api")
    
    # Global exception handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                message=exc.detail,
                status_code=exc.status_code
            )
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                message="Internal server error",
                status_code=500,
                error_code="INTERNAL_ERROR"
            )
        )
    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return StaticFiles(directory="static", html=True)

    # Root endpoint - serve home page
    @app.get("/", tags=["Root"])
    async def root(request: Request):
        return templates.TemplateResponse("home.html", {"request": request})
    
    # API info endpoint
    @app.get("/info", tags=["Root"])
    async def api_info():
        return {
            "message": "Welcome to BFP API - Browser Fingerprinting Platform",
            "description": "Advanced browser fingerprinting and visitor analytics system",
            "version": "1.0.0",
            "docs": "/docs",
            "home": "/",
            "health": "/api/v1/health"
        }
    
    return app

# Create the application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level
    )
