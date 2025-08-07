"""Persona service for managing persona data and operations."""

import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

from app.config import LoggerMixin
from app.models.personas import Persona, PersonaCreate, PersonaUpdate, PersonaType, Industry
from app.utils.helpers import generate_id, get_current_timestamp


class PersonaService(LoggerMixin):
    """Service for persona management operations."""
    
    def __init__(self):
        self.personas_file = Path("data/personas/default_personas.json")
        self._personas: Dict[str, Persona] = {}
        self._load_default_personas()
    
    def _load_default_personas(self) -> None:
        """Load default personas from JSON file."""
        try:
            if self.personas_file.exists():
                with open(self.personas_file, 'r') as f:
                    personas_data = json.load(f)
                    
                for persona_data in personas_data.get("personas", []):
                    persona = Persona(**persona_data)
                    self._personas[persona.id] = persona
                    
                self.log_event("Default personas loaded", count=len(self._personas))
            else:
                # Create default personas if file doesn't exist
                self._create_default_personas()
                
        except Exception as e:
            self.log_error(e, {"context": "Loading default personas"})
            self._create_default_personas()
    
    def _create_default_personas(self) -> None:
        """Create default personas."""
        default_personas = [
            {
                "id": "startup_founder_tech",
                "name": "Tech Startup Founder",
                "type": PersonaType.STARTUP_FOUNDER,
                "industry": Industry.TECHNOLOGY,
                "age_range": "28-40",
                "experience_level": "intermediate",
                "company_size": "startup",
                "primary_goals": [
                    "Acquire early customers",
                    "Raise Series A funding", 
                    "Build brand awareness",
                    "Scale product-market fit"
                ],
                "pain_points": [
                    "Limited marketing budget",
                    "Need quick, measurable results",
                    "Wearing multiple hats",
                    "Competition from established players"
                ],
                "preferred_channels": ["social_media", "content_marketing", "email", "partnerships"],
                "tone_preference": "innovative",
                "content_types": ["blog_posts", "social_media", "pitch_decks", "case_studies"],
                "description": "A tech-savvy entrepreneur building a disruptive product, focused on rapid growth and investor attraction.",
                "is_active": True,
                "created_at": get_current_timestamp()
            },
            {
                "id": "marketing_manager_saas",
                "name": "SaaS Marketing Manager",
                "type": PersonaType.MARKETING_MANAGER,
                "industry": Industry.TECHNOLOGY,
                "age_range": "30-45",
                "experience_level": "advanced",
                "company_size": "medium",
                "primary_goals": [
                    "Increase lead generation",
                    "Improve conversion rates",
                    "Reduce customer acquisition cost",
                    "Build thought leadership"
                ],
                "pain_points": [
                    "Proving marketing ROI",
                    "Long sales cycles",
                    "Technical product complexity",
                    "Competitive market saturation"
                ],
                "preferred_channels": ["content_marketing", "paid_ads", "webinars", "email"],
                "tone_preference": "professional",
                "content_types": ["whitepapers", "webinars", "email_campaigns", "landing_pages"],
                "description": "An experienced marketing professional focused on data-driven growth strategies for B2B SaaS products.",
                "is_active": True,
                "created_at": get_current_timestamp()
            },
            {
                "id": "small_business_owner",
                "name": "Small Business Owner",
                "type": PersonaType.BUSINESS_OWNER,
                "industry": Industry.RETAIL,
                "age_range": "35-55",
                "experience_level": "intermediate",
                "company_size": "small",
                "primary_goals": [
                    "Increase local visibility",
                    "Drive foot traffic",
                    "Build customer loyalty",
                    "Compete with chains"
                ],
                "pain_points": [
                    "Limited time for marketing",
                    "Small advertising budget",
                    "Lack of marketing expertise",
                    "Competing with big brands"
                ],
                "preferred_channels": ["local_seo", "social_media", "email", "community"],
                "tone_preference": "friendly",
                "content_types": ["social_media", "newsletters", "local_ads", "promotions"],
                "description": "A dedicated business owner focused on serving their local community while growing sustainably.",
                "is_active": True,
                "created_at": get_current_timestamp()
            }
        ]
        
        for persona_data in default_personas:
            persona = Persona(**persona_data)
            self._personas[persona.id] = persona
            
        self._save_personas()
        self.log_event("Default personas created", count=len(default_personas))
    
    def _save_personas(self) -> None:
        """Save personas to JSON file."""
        try:
            # Ensure directory exists
            self.personas_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert personas to dict for JSON serialization
            personas_data = {
                "personas": [persona.model_dump() for persona in self._personas.values()]
            }
            
            with open(self.personas_file, 'w') as f:
                json.dump(personas_data, f, indent=2, default=str)
                
        except Exception as e:
            self.log_error(e, {"context": "Saving personas"})
    
    def get_all_personas(self, active_only: bool = True) -> List[Persona]:
        """Get all personas."""
        personas = list(self._personas.values())
        
        if active_only:
            personas = [p for p in personas if p.is_active]
        
        self.log_event("Personas retrieved", count=len(personas), active_only=active_only)
        return personas
    
    def get_persona_by_id(self, persona_id: str) -> Optional[Persona]:
        """Get persona by ID."""
        persona = self._personas.get(persona_id)
        
        if persona:
            self.log_event("Persona retrieved", persona_id=persona_id)
        else:
            self.log_event("Persona not found", persona_id=persona_id)
            
        return persona
    
    def create_persona(self, persona_data: PersonaCreate) -> Persona:
        """Create new persona."""
        try:
            persona_id = generate_id("persona")
            
            persona = Persona(
                id=persona_id,
                **persona_data.model_dump(),
                created_at=get_current_timestamp(),
                updated_at=get_current_timestamp()
            )
            
            self._personas[persona.id] = persona
            self._save_personas()
            
            self.log_event("Persona created", persona_id=persona.id, name=persona.name)
            return persona
            
        except Exception as e:
            self.log_error(e, {"context": "Creating persona"})
            raise
    
    def update_persona(self, persona_id: str, update_data: PersonaUpdate) -> Optional[Persona]:
        """Update existing persona."""
        try:
            if persona_id not in self._personas:
                return None
            
            persona = self._personas[persona_id]
            
            # Update fields that are provided
            update_dict = update_data.model_dump(exclude_unset=True)
            
            for field, value in update_dict.items():
                setattr(persona, field, value)
            
            persona.updated_at = get_current_timestamp()
            
            self._save_personas()
            
            self.log_event("Persona updated", persona_id=persona_id, updated_fields=list(update_dict.keys()))
            return persona
            
        except Exception as e:
            self.log_error(e, {"context": "Updating persona", "persona_id": persona_id})
            raise
    
    def delete_persona(self, persona_id: str) -> bool:
        """Delete persona (soft delete by setting inactive)."""
        try:
            if persona_id not in self._personas:
                return False
            
            self._personas[persona_id].is_active = False
            self._personas[persona_id].updated_at = get_current_timestamp()
            
            self._save_personas()
            
            self.log_event("Persona deleted", persona_id=persona_id)
            return True
            
        except Exception as e:
            self.log_error(e, {"context": "Deleting persona", "persona_id": persona_id})
            return False
    
    def get_personas_by_type(self, persona_type: PersonaType) -> List[Persona]:
        """Get personas by type."""
        personas = [p for p in self._personas.values() if p.type == persona_type and p.is_active]
        
        self.log_event("Personas retrieved by type", persona_type=persona_type, count=len(personas))
        return personas
    
    def get_personas_by_industry(self, industry: Industry) -> List[Persona]:
        """Get personas by industry."""
        personas = [p for p in self._personas.values() if p.industry == industry and p.is_active]
        
        self.log_event("Personas retrieved by industry", industry=industry, count=len(personas))
        return personas
    
    def search_personas(self, query: str) -> List[Persona]:
        """Search personas by name or description."""
        query_lower = query.lower()
        matching_personas = []
        
        for persona in self._personas.values():
            if not persona.is_active:
                continue
                
            if (query_lower in persona.name.lower() or 
                (persona.description and query_lower in persona.description.lower())):
                matching_personas.append(persona)
        
        self.log_event("Persona search completed", query=query, results=len(matching_personas))
        return matching_personas


# Global service instance
_persona_service: Optional[PersonaService] = None


def get_persona_service() -> PersonaService:
    """Get global persona service instance."""
    global _persona_service
    if _persona_service is None:
        _persona_service = PersonaService()
    return _persona_service
