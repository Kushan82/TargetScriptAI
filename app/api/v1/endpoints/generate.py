"""Content generation API endpoints."""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field

from app.agents.orchestrator import get_content_orchestrator
from app.api.dependencies import validate_persona_exists, validate_content_config
from app.config import LoggerMixin

router = APIRouter(prefix="/generate", tags=["content_generation"])


class ContentGenerationRequest(BaseModel):
    """Request model for content generation API."""
    
    persona_id: str = Field(..., description="ID of the target persona")
    topic: str = Field(..., min_length=5, max_length=200, description="Content topic")
    content_config: Dict[str, Any] = Field(..., description="Content configuration")
    context: Optional[str] = Field(None, max_length=1000, description="Additional context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "persona_id": "startup_founder_tech",
                "topic": "How to validate your startup idea with real customers",
                "content_config": {
                    "content_type": "blog_post",
                    "tone": "professional",
                    "length": "medium",
                    "platform": "blog",
                    "include_cta": True,
                    "keywords": ["MVP", "validation", "customer feedback"]
                },
                "context": "Focus on practical, actionable steps that can be implemented quickly"
            }
        }


class ContentGenerationResponse(BaseModel):
    """Response model for content generation."""
    
    success: bool = Field(..., description="Whether generation was successful")
    workflow_id: str = Field(..., description="Unique workflow identifier")
    execution_time: float = Field(..., description="Total execution time in seconds")
    current_stage: str = Field(..., description="Final workflow stage")
    
    # Content results (only if successful)
    content: Optional[Dict[str, Any]] = Field(None, description="Generated content")
    persona_analysis: Optional[Dict[str, Any]] = Field(None, description="Persona analysis results")
    strategy_plan: Optional[Dict[str, Any]] = Field(None, description="Content strategy plan")
    qa_feedback: Optional[Dict[str, Any]] = Field(None, description="Quality assurance feedback")
    
    # Metrics
    metrics: Dict[str, Any] = Field(..., description="Generation metrics")
    
    # Error information (only if failed)
    error: Optional[str] = Field(None, description="Error message if generation failed")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="Detailed error list")
    warnings: Optional[List[str]] = Field(None, description="Warning messages")


@router.post("/", response_model=ContentGenerationResponse)
async def generate_content(
    request: ContentGenerationRequest,
    orchestrator = Depends(get_content_orchestrator)
):
    """
    Generate content using the multi-agent workflow.
    
    This endpoint orchestrates the complete content generation process:
    1. **Persona Analysis**: Analyzes the target audience and their needs
    2. **Strategy Planning**: Develops content strategy and positioning  
    3. **Creative Generation**: Creates the actual content based on strategy
    4. **Quality Assurance**: Reviews and improves content quality
    
    The process typically takes 15-30 seconds depending on content complexity.
    """
    
    try:
        # Validate persona exists
        await validate_persona_exists(request.persona_id)
        
        # Validate content configuration
        validated_config = validate_content_config(request.content_config)
        
        # Generate content using orchestrator
        result = await orchestrator.generate_content(
            persona_id=request.persona_id,
            topic=request.topic,
            content_config=validated_config,
            context=request.context
        )
        
        # Return structured response
        return ContentGenerationResponse(**result)
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )


@router.get("/status/{workflow_id}")
async def get_workflow_status(
    workflow_id: str,
    orchestrator = Depends(get_content_orchestrator)
):
    """
    Get the status of a specific workflow.
    
    Returns the current status and progress of a content generation workflow.
    """
    
    try:
        status_info = await orchestrator.get_workflow_status(workflow_id)
        return status_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow status: {str(e)}"
        )


@router.get("/content-types")
async def get_supported_content_types(
    orchestrator = Depends(get_content_orchestrator)
):
    """
    Get list of supported content types and their descriptions.
    
    Returns all content types that can be generated by the system.
    """
    
    return {
        "content_types": orchestrator.get_supported_content_types(),
        "count": len(orchestrator.get_supported_content_types())
    }


@router.post("/batch")
async def generate_batch_content(
    requests: List[ContentGenerationRequest],
    background_tasks: BackgroundTasks,
    orchestrator = Depends(get_content_orchestrator)
):
    """
    Generate multiple content pieces in batch.
    
    Processes multiple content generation requests in parallel.
    Returns immediately with workflow IDs for tracking progress.
    """
    
    if len(requests) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 requests allowed per batch"
        )
    
    workflow_ids = []
    
    for req in requests:
        try:
            # Validate each request
            await validate_persona_exists(req.persona_id)
            validate_content_config(req.content_config)
            
            # Start background task for each generation
            result = await orchestrator.generate_content(
                persona_id=req.persona_id,
                topic=req.topic,
                content_config=req.content_config,
                context=req.context
            )
            
            workflow_ids.append({
                "topic": req.topic,
                "workflow_id": result["workflow_id"],
                "status": "started"
            })
            
        except Exception as e:
            workflow_ids.append({
                "topic": req.topic,
                "workflow_id": None,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "batch_id": f"batch_{len(workflow_ids)}_items",
        "workflows": workflow_ids,
        "total": len(workflow_ids),
        "message": "Batch processing started. Use workflow IDs to check individual status."
    }
