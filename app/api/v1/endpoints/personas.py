"""Persona management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.models import Persona, PersonaCreate, PersonaUpdate
from app.services.persona_service import get_persona_service

router = APIRouter(prefix="/personas", tags=["persona_management"])


@router.get("/", response_model=List[Persona])
async def list_personas(
    persona_service = Depends(get_persona_service)
):
    """
    Get all available personas.
    
    Returns a list of all personas that can be used for content targeting.
    """
    
    personas = persona_service.get_all_personas()
    return personas


@router.get("/{persona_id}", response_model=Persona)
async def get_persona(
    persona_id: str,
    persona_service = Depends(get_persona_service)
):
    """
    Get a specific persona by ID.
    
    Returns detailed information about a single persona.
    """
    
    persona = persona_service.get_persona_by_id(persona_id)
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona not found: {persona_id}"
        )
    
    return persona


@router.post("/", response_model=Persona, status_code=status.HTTP_201_CREATED)
async def create_persona(
    persona_data: PersonaCreate,
    persona_service = Depends(get_persona_service)
):
    """
    Create a new persona.
    
    Creates a new persona that can be used for targeted content generation.
    """
    
    try:
        persona = persona_service.create_persona(persona_data)
        return persona
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create persona: {str(e)}"
        )


@router.put("/{persona_id}", response_model=Persona)
async def update_persona(
    persona_id: str,
    persona_data: PersonaUpdate,
    persona_service = Depends(get_persona_service)
):
    """
    Update an existing persona.
    
    Updates the specified persona with new information.
    """
    
    try:
        persona = persona_service.update_persona(persona_id, persona_data)
        if not persona:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Persona not found: {persona_id}"
            )
        
        return persona
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update persona: {str(e)}"
        )


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_persona(
    persona_id: str,
    persona_service = Depends(get_persona_service)
):
    """
    Delete a persona.
    
    Permanently removes the specified persona from the system.
    """
    
    success = persona_service.delete_persona(persona_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona not found: {persona_id}"
        )


class PersonaSearchRequest(BaseModel):
    """Request model for persona search."""
    
    query: Optional[str] = None
    persona_type: Optional[str] = None
    industry: Optional[str] = None


@router.post("/search", response_model=List[Persona])
async def search_personas(
    search_request: PersonaSearchRequest,
    persona_service = Depends(get_persona_service)
):
    """
    Search personas by criteria.
    
    Search for personas matching specific criteria like type, industry, or keywords.
    """
    
    personas = persona_service.search_personas(
        query=search_request.query,
        persona_type=search_request.persona_type,
        industry=search_request.industry
    )
    
    return personas


@router.get("/{persona_id}/analytics")
async def get_persona_analytics(
    persona_id: str,
    persona_service = Depends(get_persona_service)
):
    """
    Get analytics for a specific persona.
    
    Returns usage statistics and performance metrics for the persona.
    """
    
    persona = persona_service.get_persona_by_id(persona_id)
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona not found: {persona_id}"
        )
    
    # TODO: Implement actual analytics from usage logs
    analytics = {
        "persona_id": persona_id,
        "name": persona.name,
        "total_content_generated": 0,  # Placeholder
        "popular_content_types": [],   # Placeholder
        "avg_quality_score": 0.0,      # Placeholder
        "last_used": None,             # Placeholder
        "success_rate": 100.0          # Placeholder
    }
    
    return analytics
