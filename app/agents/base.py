"""Base agent class with common functionality - Fixed for LangGraph."""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, TypedDict
from typing_extensions import Annotated
from datetime import datetime

from langgraph.graph import add_messages
from app.config import LoggerMixin
from app.services.llm_service import get_llm_service
from app.utils.helpers import generate_id, get_current_timestamp


class AgentState(TypedDict):
    """State object passed between agents in the workflow."""
    
    # Required: Core workflow data
    workflow_id: str
    created_at: str
    
    # Input data
    persona_data: Dict[str, Any]
    request_data: Dict[str, Any]
    content_config: Dict[str, Any]
    
    # Agent outputs - these MUST be updated by nodes
    persona_analysis: Dict[str, Any]
    strategy_plan: Dict[str, Any]
    generated_content: Dict[str, Any]
    qa_feedback: Dict[str, Any]
    
    # Workflow metadata
    agent_logs: List[Dict[str, Any]]
    current_stage: str
    errors: List[Dict[str, Any]]
    warnings: List[str]
    
    # Performance metrics
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    total_tokens_used: int
    total_cost: float


def create_agent_state(
    workflow_id: Optional[str] = None,
    request_data: Optional[Dict[str, Any]] = None,
    content_config: Optional[Dict[str, Any]] = None
) -> AgentState:
    """Create a properly initialized AgentState."""
    return AgentState(
        workflow_id=workflow_id or generate_id("workflow"),
        created_at=get_current_timestamp(),
        persona_data={},
        request_data=request_data or {},
        content_config=content_config or {},
        persona_analysis={},
        strategy_plan={},
        generated_content={},
        qa_feedback={},
        agent_logs=[],
        current_stage="initialized",
        errors=[],
        warnings=[],
        start_time=None,
        end_time=None,
        total_tokens_used=0,
        total_cost=0.0
    )


class BaseAgent(ABC, LoggerMixin):
    """Base class for all agents in the workflow."""
    
    def __init__(self, name: str, model_type: str = "smart"):
        self.name = name
        self.model_type = model_type
        self.llm_service = get_llm_service()
        self.log_event(f"{name} agent initialized", model_type=model_type)

    @abstractmethod
    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute the agent's main functionality and return state updates."""
        pass
    
    async def _generate_response(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """Generate LLM response with the agent's model type."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        result = await self.llm_service.generate_response(
            messages=messages,
            model_type=self.model_type,
            temperature=temperature
        )
        
        self.log_event(
            f"{self.name} generated response",
            success=result.get("success", False),
            tokens_used=result.get("tokens", {}).get("total", 0),
            model_used=result.get("model_name", "unknown")
        )
        
        return result

    def _create_system_prompt(self, role_description: str, context: Dict[str, Any]) -> str:
        """Create a system prompt for the agent."""
        
        base_prompt = f"""You are {role_description}, an expert agent in a multi-agent content generation system.

Your responsibilities:
- Act only within your assigned area of expertise.
- Analyze the provided context carefully before answering.
- Think step-by-step and reason before generating output.
- Ensure clarity, factual accuracy, and alignment with brand tone and guidelines.
- Output only what is necessary and actionable for the next step in the workflow.
- Maintain consistency with brand guidelines.
Instructions:
- If multiple interpretations are possible, list them and recommend the most suitable one.
- Use markdown formatting for clarity (e.g., headers, bullet points) if applicable.
- Avoid repetition. Be concise yet complete.

Context for this request:
"""

        
        # Add context information
        if context.get("persona_data"):
            persona = context["persona_data"]
            base_prompt += f"""
Target Persona: {persona.get('name', 'Unknown')}
- Type: {persona.get('type', 'Unknown')}
- Industry: {persona.get('industry', 'Unknown')}
- Primary Goals: {', '.join(persona.get('primary_goals', []))}
- Pain Points: {', '.join(persona.get('pain_points', []))}
- Preferred Tone: {persona.get('tone_preference', 'professional')}
"""

        if context.get("content_config"):
            config = context["content_config"]
            base_prompt += f"""
Content Requirements:
- Type: {config.get('content_type', 'Unknown')}
- Tone: {config.get('tone', 'professional')}
- Length: {config.get('length', 'medium')}
- Platform: {config.get('platform', 'general')}
- Include CTA: {config.get('include_cta', True)}
"""

        return base_prompt

    async def _execute_with_metrics(self, state: AgentState, action_name: str) -> Dict[str, Any]:
        """Execute an action with performance metrics."""
        
        start_time = datetime.now()
        
        try:
            result = await self._perform_action(state, action_name)
            success = True
            error = None
            
        except Exception as e:
            self.log_error(e, {"agent": self.name, "action": action_name})
            result = {"error": str(e)}
            success = False
            error = str(e)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Log the execution
        log_result = {
            "success": success,
            "duration": duration,
            "result": result
        }
        
        if error:
            log_result["error"] = error

        state["add_agent_log"](self.name, action_name, log_result, duration)

        return result

    @abstractmethod
    async def _perform_action(self, state: AgentState, action_name: str) -> Dict[str, Any]:
        """Perform the specific action - implemented by each agent."""
        pass
