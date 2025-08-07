"""Request models for API endpoints."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .content import ContentRequest, ContentConfig
from .personas import PersonaCreate, PersonaUpdate


class GenerateRequest(BaseModel):
    """Request model for content generation endpoint."""
    
    # Core request data
    persona_id: str = Field(..., description="ID of the persona to target")
    topic: str = Field(..., description="Main topic or subject for content")
    content_config: ContentConfig = Field(..., description="Content generation configuration")
    
    # Optional enhancements
    context: Optional[str] = Field(None, description="Additional context or background information")
    references: Optional[List[str]] = Field(None, description="Reference materials, URLs, or sources")
    custom_instructions: Optional[str] = Field(None, description="Custom instructions for the AI")
    
    # Generation parameters
    use_multi_agent: bool = Field(True, description="Use multi-agent workflow")
    include_strategy: bool = Field(True, description="Include strategy analysis")
    generate_variations: bool = Field(False, description="Generate content variations")
    variation_count: int = Field(1, ge=1, le=5, description="Number of variations to generate")
    
    # Override settings
    temperature_override: Optional[float] = Field(None, ge=0.0, le=2.0, description="Override default temperature")
    max_tokens_override: Optional[int] = Field(None, ge=100, le=8192, description="Override default max tokens")
    
    class Config:
        json_schema_extra = {
            "example": {
                "persona_id": "startup_founder_tech",
                "topic": "How to build a minimum viable product (MVP)",
                "content_config": {
                    "content_type": "blog_post",
                    "tone": "professional",
                    "length": "long",
                    "platform": "blog",
                    "include_cta": True,
                    "keywords": ["MVP", "startup", "product development"]
                },
                "context": "Focus on lean startup methodology and rapid iteration",
                "use_multi_agent": True,
                "include_strategy": True,
                "generate_variations": False
            }
        }


class ExportFormat(str, Enum):
    """Available export formats."""
    JSON = "json"
    TXT = "txt"
    DOCX = "docx"
    HTML = "html"
    MARKDOWN = "md"
    PDF = "pdf"


class ExportRequest(BaseModel):
    """Request model for content export."""
    
    content_id: str = Field(..., description="ID of the content to export")
    format: ExportFormat = Field(ExportFormat.JSON, description="Export format")
    
    # Export options
    include_metadata: bool = Field(True, description="Include generation metadata")
    include_analytics: bool = Field(False, description="Include analytics data")
    include_variations: bool = Field(False, description="Include content variations")
    
    # Formatting options
    custom_template: Optional[str] = Field(None, description="Custom export template")
    styling_options: Optional[Dict[str, Any]] = Field(None, description="Styling options for formatted exports")
    
    # File options
    filename: Optional[str] = Field(None, description="Custom filename (without extension)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_id": "content_123",
                "format": "docx",
                "include_metadata": True,
                "include_analytics": False,
                "filename": "my_blog_post"
            }
        }


class BulkGenerateRequest(BaseModel):
    """Request model for bulk content generation."""
    
    requests: List[GenerateRequest] = Field(..., description="List of generation requests")
    
    # Bulk options
    parallel_processing: bool = Field(True, description="Process requests in parallel")
    max_concurrent: int = Field(3, ge=1, le=10, description="Maximum concurrent requests")
    
    # Output options
    auto_export: bool = Field(False, description="Automatically export generated content")
    export_format: Optional[ExportFormat] = Field(None, description="Format for auto-export")
    
    class Config:
        json_schema_extra = {
            "example": {
                "requests": [
                    {
                        "persona_id": "startup_founder_tech",
                        "topic": "MVP development",
                        "content_config": {
                            "content_type": "blog_post",
                            "tone": "professional",
                            "length": "medium"
                        }
                    }
                ],
                "parallel_processing": True,
                "max_concurrent": 3
            }
        }


class PersonaManagementRequest(BaseModel):
    """Request model for persona management operations."""
    
    action: str = Field(..., description="Action to perform (create, update, delete)")
    persona_data: Optional[PersonaCreate] = Field(None, description="Data for creating persona")
    update_data: Optional[PersonaUpdate] = Field(None, description="Data for updating persona")
    persona_id: Optional[str] = Field(None, description="ID of persona to update/delete")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "create",
                "persona_data": {
                    "name": "E-commerce Manager",
                    "type": "marketing_manager",
                    "industry": "retail",
                    "primary_goals": ["Increase online sales", "Improve conversion rate"],
                    "pain_points": ["Cart abandonment", "Customer acquisition cost"],
                    "preferred_channels": ["email", "paid_ads"],
                    "content_types": ["email_campaigns", "product_descriptions"]
                }
            }
        }


class AnalyticsRequest(BaseModel):
    """Request model for analytics and reporting."""
    
    # Time range
    start_date: Optional[str] = Field(None, description="Start date (ISO format)")
    end_date: Optional[str] = Field(None, description="End date (ISO format)")
    
    # Filters
    persona_ids: Optional[List[str]] = Field(None, description="Filter by persona IDs")
    content_types: Optional[List[str]] = Field(None, description="Filter by content types")
    
    # Metrics
    include_usage_metrics: bool = Field(True, description="Include usage metrics")
    include_performance_metrics: bool = Field(True, description="Include performance metrics")
    include_cost_analysis: bool = Field(False, description="Include cost analysis")
    
    # Grouping
    group_by: Optional[str] = Field("day", description="Group results by (day, week, month)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-01-31T23:59:59Z",
                "persona_ids": ["startup_founder_tech"],
                "include_usage_metrics": True,
                "group_by": "day"
            }
        }
