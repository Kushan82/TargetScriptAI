
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import uvicorn

from app.config import get_settings, LoggerMixin
from app.api.v1.router import router as v1_router


class TargetScriptAI(LoggerMixin):
    """Main FastAPI application class."""
    
    def __init__(self):
        self.settings = get_settings()
        self.app = self._create_app()
        
    def _create_app(self) -> FastAPI:
        """Create and configure FastAPI application."""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            
            self.log_event("Starting TargetScriptAI", version="1.0.0", environment=self.settings.app.environment)
            yield
            
            self.log_event("Shutting down TargetScriptAI")
        
        app = FastAPI(
            title="TargetScriptAI",
            description="Multi-agent AI system for targeted content generation",
            version="1.0.0",
            docs_url="/docs" if self.settings.app.environment != "production" else None,
            redoc_url="/redoc" if self.settings.app.environment != "production" else None,
            lifespan=lifespan,
            openapi_tags=v1_router.tags_metadata if hasattr(v1_router, 'tags_metadata') else []
        )
        
        
        self._setup_middleware(app)
        
        
        self._setup_routes(app)
        
        
        self._setup_exception_handlers(app)
        
        return app
    
    def _setup_middleware(self, app: FastAPI):
        """Setup application middleware."""
        
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.settings.app.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=self.settings.app.allowed_hosts
        )
        
        
        @app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            
            request_id = f"req_{int(time.time() * 1000000)}"
            response.headers["X-Request-ID"] = request_id
            
            return response
    
    def _setup_routes(self, app: FastAPI):
        """Setup application routes."""
        
        
        app.include_router(v1_router, prefix="/api")
        
        
        @app.get("/")
        async def root():
            return {
                "service": "TargetScriptAI",
                "description": "Multi-agent AI system for targeted content generation",
                "version": "1.0.0",
                "status": "running",
                "docs": "/docs",
                "api": {
                    "v1": "/api/v1",
                    "generate": "/api/v1/generate",
                    "personas": "/api/v1/personas",
                    "health": "/api/v1/health"
                },
                "endpoints": {
                    "generate_content": "POST /api/v1/generate/",
                    "list_personas": "GET /api/v1/personas/",
                    "health_check": "GET /api/v1/health/",
                    "content_types": "GET /api/v1/generate/content-types"
                }
            }
    
    def _setup_exception_handlers(self, app: FastAPI):
        """Setup global exception handlers."""
        
        @app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            self.log_error(exc, {
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers)
            })
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    "service": "TargetScriptAI"
                }
            )



target_script_ai = TargetScriptAI()
app = target_script_ai.app


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
