from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ContentType(str, Enum):
    """Types of content that can be generated."""
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    EMAIL_CAMPAIGN = "email_campaign"
    AD_COPY = "ad_copy"
    LANDING_PAGE = "landing_page"
    NEWSLETTER = "newsletter"
    CASE_STUDY = "case_study"
    WHITEPAPER = "whitepaper"
    PRESS_RELEASE = "press_release"
    PRODUCT_DESCRIPTION = "product_description"


class ToneStyle(str, Enum):
    """Tone styles for content."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    CONVERSATIONAL = "conversational"
    FORMAL = "formal"
    HUMOROUS = "humorous"
    INSPIRING = "inspiring"
    URGENT = "urgent"
    EMPATHETIC = "empathetic"


class ContentLength(str, Enum):
    """Content length options."""
    SHORT = "short"       # 50-150 words
    MEDIUM = "medium"     # 150-500 words
    LONG = "long"         # 500-1000 words
    EXTENDED = "extended" # 1000+ words


class Platform(str, Enum):
    """Target platforms for content."""
    WEBSITE = "website"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    EMAIL = "email"
    BLOG = "blog"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    MEDIUM = "medium"


class ContentConfig(BaseModel):
    """Configuration for content generation."""
    
    content_type: ContentType = Field(..., description="Type of content to generate")
    tone: ToneStyle = Field(ToneStyle.PROFESSIONAL, description="Tone and style")
    length: ContentLength = Field(ContentLength.MEDIUM, description="Target length")
    platform: Optional[Platform] = Field(None, description="Target platform")
    
    # Target audience
    target_audience: Optional[str] = Field(None, description="Specific target audience")
    industry_context: Optional[str] = Field(None, description="Industry-specific context")
    
    # Content parameters
    creativity_level: float = Field(0.7, ge=0.0, le=1.0, description="Creativity level (0=conservative, 1=very creative)")
    include_cta: bool = Field(True, description="Include call-to-action")
    keywords: Optional[List[str]] = Field(None, description="Keywords to include")
    
    # Brand guidelines
    brand_voice: Optional[str] = Field(None, description="Brand voice guidelines")
    brand_values: Optional[List[str]] = Field(None, description="Brand values to reflect")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_type": "blog_post",
                "tone": "professional",
                "length": "medium",
                "platform": "blog",
                "target_audience": "Small business owners",
                "creativity_level": 0.7,
                "include_cta": True,
                "keywords": ["marketing", "growth", "strategy"]
            }
        }


class ContentRequest(BaseModel):
    """Request model for content generation."""
    
    persona_id: str = Field(..., description="ID of the persona to target")
    topic: str = Field(..., description="Main topic or subject")
    config: ContentConfig = Field(..., description="Content configuration")
    
    # Additional context
    context: Optional[str] = Field(None, description="Additional context or background")
    references: Optional[List[str]] = Field(None, description="Reference materials or URLs")
    
    # Generation parameters
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Override default temperature")
    max_tokens: Optional[int] = Field(None, ge=100, le=8192, description="Override default max tokens")
    
    class Config:
        json_schema_extra = {
            "example": {
                "persona_id": "startup_founder_tech",
                "topic": "How to validate your startup idea",
                "config": {
                    "content_type": "blog_post",
                    "tone": "professional",
                    "length": "medium",
                    "include_cta": True
                },
                "context": "Focus on lean startup methodology"
            }
        }


class ContentResponse(BaseModel):
    """Response model for generated content."""
    # model_config = ConfigDict(protected_namespaces=())
    # Generated content
    title: Optional[str] = Field(None, description="Generated title")
    content: str = Field(..., description="Generated content")
    meta_description: Optional[str] = Field(None, description="SEO meta description")
    tags: Optional[List[str]] = Field(None, description="Suggested tags")
    
    # Generation metadata
    persona_id: str = Field(..., description="Persona used for generation")
    content_type: ContentType = Field(..., description="Type of content generated")
    tone: ToneStyle = Field(..., description="Tone used")
    
    # Metrics
    word_count: int = Field(..., description="Word count of generated content")
    estimated_read_time: int = Field(..., description="Estimated read time in minutes")
    
    # AI metadata
    model_used: str = Field(..., description="AI model used for generation")
    tokens_used: Dict[str, int] = Field(..., description="Token usage statistics")
    generation_time: float = Field(..., description="Generation time in seconds")
    
    # Quality metrics
    creativity_score: Optional[float] = Field(None, description="Estimated creativity score")
    readability_score: Optional[float] = Field(None, description="Estimated readability score")
    
    # Suggestions
    improvement_suggestions: Optional[List[str]] = Field(None, description="Suggestions for improvement")
    alternative_titles: Optional[List[str]] = Field(None, description="Alternative title suggestions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "5 Proven Methods to Validate Your Startup Idea",
                "content": "Starting a business without validating your idea is like...",
                "meta_description": "Learn 5 proven methods to validate your startup idea before investing time and money.",
                "tags": ["startup", "validation", "entrepreneurship"],
                "persona_id": "startup_founder_tech",
                "content_type": "blog_post",
                "tone": "professional",
                "word_count": 847,
                "estimated_read_time": 4,
                "model_used": "llama-3.1-70b-versatile",
                "tokens_used": {"input": 156, "output": 823, "total": 979},
                "generation_time": 3.2
            }
        }


class ContentVariation(BaseModel):
    """Model for content variations."""
    
    variation_id: str = Field(..., description="Unique variation identifier")
    content: str = Field(..., description="Variation content")
    tone: ToneStyle = Field(..., description="Tone of this variation")
    differences: List[str] = Field(..., description="Key differences from original")
    
    class Config:
        json_schema_extra = {
            "example": {
                "variation_id": "var_001",
                "content": "Alternative version of the content...",
                "tone": "casual",
                "differences": ["More conversational tone", "Added humor", "Shorter paragraphs"]
            }
        }


class ContentFeedback(BaseModel):
    """Model for content feedback and ratings."""
    
    content_id: str = Field(..., description="ID of the content being rated")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    feedback_text: Optional[str] = Field(None, description="Written feedback")
    aspects: Optional[Dict[str, int]] = Field(None, description="Ratings for specific aspects")
    
    # User info
    user_id: Optional[str] = Field(None, description="User providing feedback")
    timestamp: Optional[str] = Field(None, description="Feedback timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_id": "content_123",
                "rating": 4,
                "feedback_text": "Great content, but could be more actionable",
                "aspects": {
                    "relevance": 5,
                    "clarity": 4,
                    "actionability": 3,
                    "engagement": 4
                }
            }
        }
