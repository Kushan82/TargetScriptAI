from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class PersonaType(str, Enum):
    BUSINESS_OWNER = "business_owner"
    MARKETING_MANAGER = "marketing_manager" 
    CONTENT_CREATOR = "content_creator"
    SALES_PROFESSIONAL = "sales_professional"
    STARTUP_FOUNDER = "startup_founder"
    FREELANCER = "freelancer"
    CUSTOM = "custom"


class Industry(str, Enum):
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    RETAIL = "retail"
    REAL_ESTATE = "real_estate"
    CONSULTING = "consulting"
    MANUFACTURING = "manufacturing"
    OTHER = "other"


class Persona(BaseModel):
    id: str = Field(..., description="Unique persona identifier")
    name: str = Field(..., description="Persona name")
    type: PersonaType = Field(..., description="Persona type")
    industry: Industry = Field(..., description="Industry category")
    
    # Demographic info
    age_range: str = Field("25-45", description="Age range")
    experience_level: str = Field("intermediate", description="Experience level")
    company_size: str = Field("small", description="Company size")
    
    # Goals and challenges
    primary_goals: List[str] = Field(..., description="Primary business goals")
    pain_points: List[str] = Field(..., description="Main pain points")
    preferred_channels: List[str] = Field(..., description="Preferred marketing channels")
    
    # Communication preferences
    tone_preference: str = Field("professional", description="Preferred communication tone")
    content_types: List[str] = Field(..., description="Preferred content types")
    
    # Context
    description: Optional[str] = Field(None, description="Detailed persona description")
    avatar_url: Optional[str] = Field(None, description="Persona avatar image URL")
    
    # Metadata
    is_active: bool = Field(True, description="Whether persona is active")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "startup_founder_tech",
                "name": "Tech Startup Founder",
                "type": "startup_founder",
                "industry": "technology",
                "age_range": "28-40",
                "experience_level": "intermediate",
                "company_size": "startup",
                "primary_goals": ["Acquire customers", "Raise funding", "Build brand awareness"],
                "pain_points": ["Limited marketing budget", "Need quick results", "Wearing multiple hats"],
                "preferred_channels": ["social_media", "content_marketing", "email"],
                "tone_preference": "innovative",
                "content_types": ["blog_posts", "social_media", "pitch_decks"],
                "description": "A tech-savvy entrepreneur building a disruptive product"
            }
        }


class PersonaCreate(BaseModel):
 
    name: str = Field(..., description="Persona name")
    type: PersonaType = Field(..., description="Persona type")
    industry: Industry = Field(..., description="Industry category")
    primary_goals: List[str] = Field(..., description="Primary business goals")
    pain_points: List[str] = Field(..., description="Main pain points")
    preferred_channels: List[str] = Field(..., description="Preferred marketing channels")
    tone_preference: str = Field("professional", description="Preferred communication tone")
    content_types: List[str] = Field(..., description="Preferred content types")
    description: Optional[str] = Field(None, description="Detailed persona description")


class PersonaUpdate(BaseModel):
    
    
    name: Optional[str] = Field(None, description="Persona name")
    primary_goals: Optional[List[str]] = Field(None, description="Primary business goals")
    pain_points: Optional[List[str]] = Field(None, description="Main pain points")
    preferred_channels: Optional[List[str]] = Field(None, description="Preferred marketing channels")
    tone_preference: Optional[str] = Field(None, description="Preferred communication tone")
    content_types: Optional[List[str]] = Field(None, description="Preferred content types")
    description: Optional[str] = Field(None, description="Detailed persona description")
    is_active: Optional[bool] = Field(None, description="Whether persona is active")
