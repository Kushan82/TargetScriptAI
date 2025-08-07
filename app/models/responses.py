"""Response models for API endpoints."""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

from .content import ContentResponse, ContentVariation
from .personas import Persona


class GenerateResponse(BaseModel):
    """Response model for content generation."""
    
    # Generation results
    success: bool = Field(..., description="Whether generation was successful")
    content: Optional[ContentResponse] = Field(None, description="Generated content")
    variations: Optional[List[ContentVariation]] = Field(None, description="Content variations")
    
    # Strategy analysis (from strategy agent)
    strategy: Optional[Dict[str, Any]] = Field(None, description="Content strategy analysis")
    
    # Agent workflow data
    agent_logs: Optional[List[Dict[str, Any]]] = Field(None, description="Agent execution logs")
    workflow_duration: Optional[float] = Field(None, description="Total workflow duration in seconds")
    
    # Metadata
    request_id: str = Field(..., description="Unique request identifier")
    generated_at: str = Field(..., description="Generation timestamp")
    
    # Error handling
    error_message: Optional[str] = Field(None, description="Error message if generation failed")
    warnings: Optional[List[str]] = Field(None, description="Warning messages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "content": {
                    "title": "Building Your First MVP: A Founder's Guide",
                    "content": "Creating a minimum viable product (MVP) is crucial...",
                    "persona_id": "startup_founder_tech",
                    "content_type": "blog_post",
                    "word_count": 1247,
                    "model_used": "llama-3.1-70b-versatile"
                },
                "strategy": {
                    "funnel_stage": "awareness",
                    "recommended_cta": "Download MVP Template",
                    "key_messages": ["Validate early", "Build lean", "Iterate fast"]
                },
                "request_id": "req_123",
                "generated_at": "2024-01-01T12:00:00Z",
                "workflow_duration": 15.3
            }
        }


class ExportResponse(BaseModel):
    """Response model for content export."""
    
    success: bool = Field(..., description="Whether export was successful")
    
    # File information
    filename: str = Field(..., description="Generated filename")
    file_size: int = Field(..., description="File size in bytes")
    format: str = Field(..., description="Export format")
    
    # Download information
    download_url: Optional[str] = Field(None, description="Temporary download URL")
    expires_at: Optional[str] = Field(None, description="Download URL expiration")
    
    # Export metadata
    exported_at: str = Field(..., description="Export timestamp")
    export_id: str = Field(..., description="Unique export identifier")
    
    # Content information
    content_id: str = Field(..., description="ID of exported content")
    included_sections: List[str] = Field(..., description="Sections included in export")
    
    # Error handling
    error_message: Optional[str] = Field(None, description="Error message if export failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "filename": "mvp_blog_post.docx",
                "file_size": 45672,
                "format": "docx",
                "download_url": "https://api.example.com/downloads/temp_abc123",
                "expires_at": "2024-01-01T18:00:00Z",
                "exported_at": "2024-01-01T12:00:00Z",
                "export_id": "exp_456",
                "content_id": "content_123",
                "included_sections": ["content", "metadata", "analytics"]
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Environment name")
    
    # Service health details
    components: Dict[str, str] = Field(..., description="Component health status")
    models: Dict[str, str] = Field(..., description="Available AI models")
    
    # System information
    uptime: float = Field(..., description="Service uptime in seconds")
    timestamp: str = Field(..., description="Health check timestamp")
    
    # Resource usage (optional)
    resources: Optional[Dict[str, Any]] = Field(None, description="Resource usage metrics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "TargetScriptAI",
                "version": "0.1.0",
                "environment": "development",
                "components": {
                    "database": "healthy",
                    "llm_service": "healthy",
                    "persona_service": "healthy"
                },
                "models": {
                    "smart": "llama-3.1-70b-versatile",
                    "fast": "llama-3.1-8b-instant",
                    "creative": "mixtral-8x7b-32768"
                },
                "uptime": 3661.5,
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }


class BulkGenerateResponse(BaseModel):
    """Response model for bulk content generation."""
    
    success: bool = Field(..., description="Whether bulk operation was successful")
    
    # Results
    completed: int = Field(..., description="Number of completed requests")
    failed: int = Field(..., description="Number of failed requests")
    total: int = Field(..., description="Total number of requests")
    
    # Individual results
    results: List[Union[GenerateResponse, Dict[str, str]]] = Field(
        ..., description="Individual generation results or errors"
    )
    
    # Timing information
    total_duration: float = Field(..., description="Total processing time")
    average_duration: float = Field(..., description="Average time per request")
    
    # Export information (if auto-export enabled)
    export_info: Optional[ExportResponse] = Field(None, description="Export information if auto-export was used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "completed": 3,
                "failed": 0,
                "total": 3,
                "results": [
                    {"success": True, "content": {"title": "Blog Post 1"}},
                    {"success": True, "content": {"title": "Blog Post 2"}},
                    {"success": True, "content": {"title": "Blog Post 3"}}
                ],
                "total_duration": 45.2,
                "average_duration": 15.1
            }
        }


class PersonaListResponse(BaseModel):
    """Response model for persona listing."""
    
    personas: List[Persona] = Field(..., description="List of personas")
    total: int = Field(..., description="Total number of personas")
    active: int = Field(..., description="Number of active personas")
    
    # Filtering information
    filtered: bool = Field(False, description="Whether results were filtered")
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Applied filters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "personas": [
                    {
                        "id": "startup_founder_tech",
                        "name": "Tech Startup Founder",
                        "type": "startup_founder",
                        "industry": "technology"
                    }
                ],
                "total": 3,
                "active": 3,
                "filtered": False
            }
        }


class AnalyticsResponse(BaseModel):
    """Response model for analytics data."""
    
    # Time range
    start_date: str = Field(..., description="Analysis start date")
    end_date: str = Field(..., description="Analysis end date")
    
    # Usage metrics
    usage_metrics: Dict[str, Any] = Field(..., description="Usage statistics")
    
    # Performance metrics
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="Performance statistics")
    
    # Cost analysis
    cost_analysis: Optional[Dict[str, Any]] = Field(None, description="Cost analysis data")
    
    # Trends and insights
    trends: Optional[List[Dict[str, Any]]] = Field(None, description="Usage trends")
    insights: Optional[List[str]] = Field(None, description="Key insights")
    
    # Generated at
    generated_at: str = Field(..., description="Report generation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-01-31T23:59:59Z",
                "usage_metrics": {
                    "total_generations": 156,
                    "total_tokens": 45672,
                    "avg_generation_time": 12.3
                },
                "performance_metrics": {
                    "success_rate": 0.98,
                    "avg_quality_score": 4.2
                },
                "generated_at": "2024-01-01T12:00:00Z"
            }
        }
