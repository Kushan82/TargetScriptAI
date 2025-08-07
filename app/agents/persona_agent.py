"""Persona agent for understanding target audience context - Fixed JSON parsing."""

import json
import re
from typing import Dict, Any
from app.utils.helpers import get_current_timestamp
from .base import BaseAgent, AgentState
from app.services.persona_service import get_persona_service


class PersonaAgent(BaseAgent):
    """Agent responsible for persona analysis and context understanding."""
    
    def __init__(self):
        super().__init__(name="PersonaAgent", model_type="smart")
        self.persona_service = get_persona_service()

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute persona analysis and return state updates."""
        
        # Get persona data
        persona_id = state["request_data"].get("persona_id")
        if not persona_id:
            return {
                "errors": state["errors"] + [{"agent": self.name, "error": "No persona_id provided in request", "timestamp": get_current_timestamp()}],
                "current_stage": "error"
            }
        
        persona = self.persona_service.get_persona_by_id(persona_id)
        if not persona:
            return {
                "errors": state["errors"] + [{"agent": self.name, "error": f"Persona not found: {persona_id}", "timestamp": get_current_timestamp()}],
                "current_stage": "error"
            }
        
        # Generate persona analysis
        analysis_result = await self._analyze_persona_context(state)
        
        self.log_event(
            "Persona analysis completed",
            persona_id=persona_id,
            persona_name=persona.name,
            analysis_points=len(analysis_result.get("key_insights", []))
        )
        
        # Return state updates
        return {
            "persona_data": persona.model_dump(),
            "persona_analysis": analysis_result,
            "current_stage": "persona_analysis"
        }


    def _extract_json_from_response(self, content: str) -> str:
        """Extract JSON from LLM response, handling markdown and extra text."""
        
        if not content:
            return ""
        
        content = content.strip()
        
        # If content starts directly with {, it's likely clean JSON
        if content.startswith('{') and content.endswith('}'):
            return content
        
        # Look for JSON within markdown code blocks
        json_pattern = r'``````'
        match = re.search(json_pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Look for JSON object in the text (between first { and last })
        first_brace = content.find('{')
        last_brace = content.rfind('}')
        
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            return content[first_brace:last_brace + 1]
        
        return content

    async def _analyze_persona_context(self, state: AgentState) -> Dict[str, Any]:
        """Generate deep persona analysis for content targeting."""
        
        persona_data = state["persona_data"]
        request_data = state["request_data"]
        
        system_prompt = self._create_system_prompt(
            "a persona analysis expert specializing in marketing psychology and audience targeting",
            {"persona_data": persona_data, "content_config": state["content_config"]}
        )
        
        user_prompt = f"""
You are tasked with analyzing a user persona to support high-impact content generation. Carefully review the details below and then provide your output strictly in the required JSON format.

Persona profile:
- Name: {persona_data.get('name')}
- Type: {persona_data.get('type')}
- Industry: {persona_data.get('industry')}

Goals: {', '.join(persona_data.get('primary_goals', [])) or 'Not provided'}
Pain Points: {', '.join(persona_data.get('pain_points', [])) or 'Not provided'}
Preferred Channels: {', '.join(persona_data.get('preferred_channels', [])) or 'Not provided'}

Content Topic: {request_data.get('topic', 'Not specified')}
Additional Context: {request_data.get('context', 'None provided')}

Respond only with a valid and properly structured JSON object in the following format:

{{
    "key_insights": ["...", "...", "..."],
    "content_angles": ["...", "...", "..."],
    "messaging_strategy": "...",
    "pain_point_focus": ["...", "..."],
    "motivation_triggers": ["...", "..."],
    "language_preferences": "...",
    "success_metrics": ["...", "..."],
    "decision_factors": ["...", "..."]
}}

Rules:
- Ensure all string values are concise, insightful, and free of generic filler.
- Maintain proper JSON syntax with double quotes for keys and values.
- Do not include explanations or extra commentary outside the JSON.
"""

        result = await self._generate_response(system_prompt, user_prompt, temperature=0.2)
        
        if result.get("success"):
            try:
                # Extract and clean JSON from response
                raw_content = result.get("content", "")
                json_content = self._extract_json_from_response(raw_content)
                
                if not json_content:
                    raise ValueError("No JSON content found in response")
                
                # Parse JSON response
                analysis = json.loads(json_content)
                
                # Add metadata
                analysis["persona_id"] = persona_data.get("id")
                analysis["analysis_timestamp"] = state["created_at"]
                analysis["tokens_used"] = result.get("tokens", {})
                
                return analysis
                
            except (json.JSONDecodeError, ValueError) as e:
                self.log_error(e, {
                    "context": "Parsing persona analysis JSON",
                    "raw_content": result.get("content", "")[:200]
                })
                return {
                    "error": "Failed to parse analysis",
                    "raw_content": result.get("content", ""),
                    "tokens_used": result.get("tokens", {})
                }
        else:
            return {
                "error": result.get("error", "Analysis failed"),
                "tokens_used": result.get("tokens", {})
            }

    async def _perform_action(self, state: AgentState, action_name: str) -> Dict[str, Any]:
        """Perform specific persona agent actions."""
        
        if action_name == "analyze_persona":
            return await self._analyze_persona_context(state)
        else:
            raise ValueError(f"Unknown action: {action_name}")
