"""Common API dependencies for TargetScriptAI."""

from typing import Dict, Any
from fastapi import Depends, HTTPException, status

from app.config import get_settings
from app.services.llm_service import get_llm_service
from app.services.persona_service import get_persona_service
from app.agents.orchestrator import get_content_orchestrator


async def get_orchestrator():
    """Dependency to get content orchestrator."""
    return get_content_orchestrator()


async def validate_persona_exists(persona_id: str):
    """Validate that a persona exists."""
    persona_service = get_persona_service()
    persona = persona_service.get_persona_by_id(persona_id)
    
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona not found: {persona_id}"
        )
    
    return persona


def validate_content_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate content configuration."""
    
    required_fields = ["content_type", "tone", "length"]
    
    for field in required_fields:
        if field not in config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field in content config: {field}"
            )
    
    # Validate content type
    valid_content_types = ["blog_post", "social_media", "email_campaign", "ad_copy", "landing_page", "case_study", "newsletter", "whitepaper"]
    if config["content_type"] not in valid_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid content type. Must be one of: {valid_content_types}"
        )
    
    # Validate tone
    valid_tones = ["professional", "casual", "friendly", "authoritative", "conversational", "formal", "innovative"]
    if config["tone"] not in valid_tones:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tone. Must be one of: {valid_tones}"
        )
    
    # Validate length
    valid_lengths = ["short", "medium", "long", "extended"]
    if config["length"] not in valid_lengths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid length. Must be one of: {valid_lengths}"
        )
    
    return config
