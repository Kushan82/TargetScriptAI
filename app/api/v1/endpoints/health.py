"""Health check and system status endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from app.models import HealthResponse
from app.services.llm_service import get_llm_service
from app.services.persona_service import get_persona_service
from app.agents.orchestrator import get_content_orchestrator
from app.config import get_settings
import time 
import psutil

router = APIRouter(prefix="/health", tags=["health"])

# Store startup time
startup_time = time.time()


@router.get("/", response_model=HealthResponse)
async def health_check(
    llm_service = Depends(get_llm_service),
    persona_service = Depends(get_persona_service),
    orchestrator = Depends(get_content_orchestrator),
    settings = Depends(get_settings)
):
    """
    Comprehensive health check for all system components.
    
    Returns detailed status information about:
    - Core services (LLM, Persona, Orchestrator)
    - Available AI models
    - System resources
    - Component availability
    """
    
    try:
        # Check core components
        components = {}
        models = {}
        
        # Test LLM service
        try:
            llm_test = await llm_service.test_connection("fast")
            components["llm_service"] = "healthy" if llm_test["connected"] else "unhealthy"
            
            # Get available models
            models = {
                "smart": settings.llm.groq_model_smart,
                "fast": settings.llm.groq_model_fast,
                "creative": settings.llm.groq_model_creative
            }
        except Exception:
            components["llm_service"] = "unhealthy"
        
        # Test persona service
        try:
            personas = persona_service.get_all_personas()
            components["persona_service"] = "healthy"
            components["persona_count"] = str(len(personas))
        except Exception:
            components["persona_service"] = "unhealthy"
        
        # Test orchestrator
        try:
            content_types = orchestrator.get_supported_content_types()
            components["orchestrator"] = "healthy" if content_types else "unhealthy"
            components["content_types_count"] = str(len(content_types))
        except Exception:
            components["orchestrator"] = "unhealthy"
        
        # Calculate uptime
        uptime = time.time() - startup_time
        
        # Get system resources (optional)
        try:
            resources = {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent if psutil.disk_usage('/') else 0
            }
        except Exception:
            resources = {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_percent": 0
            }
        
        # Determine overall status
        overall_status = "healthy" if all(
            status == "healthy" for status in [components.get("llm_service"), components.get("persona_service"), components.get("orchestrator")]
        ) else "degraded"
        
        return HealthResponse(
            status=overall_status,
            service="TargetScriptAI",
            version="1.0.0",
            environment=settings.app.environment,
            components=components,
            models=models,
            uptime=uptime,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            resources=resources
        )
        
    except Exception as e:
        return HealthResponse(
            status="error",
            service="TargetScriptAI",
            version="1.0.0",
            environment=settings.app.environment,
            components={"error": str(e)},
            models={},
            uptime=time.time() - startup_time,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            resources={}
        )


@router.get("/live")
async def liveness_probe():
    """
    Simple liveness probe for container orchestration.
    
    Returns 200 OK if the service is running.
    """
    return {"status": "alive", "timestamp": time.time()}


@router.get("/ready")
async def readiness_probe(
    llm_service = Depends(get_llm_service)
):
    """
    Readiness probe to check if service can handle requests.
    
    Returns 200 OK if all critical services are ready.
    """
    
    try:
        # Quick test of critical components
        llm_test = await llm_service.test_connection("fast")
        
        if llm_test["connected"]:
            return {"status": "ready", "timestamp": time.time()}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM service unavailable"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )
