"""LangGraph orchestrator for managing the multi-agent content generation workflow."""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .base import BaseAgent, AgentState, LoggerMixin,create_agent_state
from .persona_agent import PersonaAgent
from .strategy_agent import StrategyAgent
from .creative_agent import CreativeAgent
from .qa_agent import QAAgent
from app.utils.helpers import generate_id


class ContentOrchestrator(LoggerMixin):
    """Orchestrator for the multi-agent content generation workflow."""
    
    def __init__(self):
        self.workflow_id = generate_id("workflow")
        self.graph = None
        self._initialize_workflow()
        
        # Initialize agents
        self.persona_agent = PersonaAgent()
        self.strategy_agent = StrategyAgent()
        self.creative_agent = CreativeAgent()
        self.qa_agent = QAAgent()
        
        self.log_event("Content orchestrator initialized", workflow_id=self.workflow_id)

    def _initialize_workflow(self):
        """Initialize the LangGraph workflow."""
        
        # Create the workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        workflow.add_node("agent_persona", self._agent_persona_node)
        workflow.add_node("agent_strategy", self._agent_strategy_node)
        workflow.add_node("agent_creative", self._agent_creative_node)
        workflow.add_node("agent_qa", self._agent_qa_node)

        # Define the workflow edges
        workflow.set_entry_point("agent_persona")
        workflow.add_edge("agent_persona", "agent_strategy")
        workflow.add_edge("agent_strategy", "agent_creative")
        workflow.add_edge("agent_creative", "agent_qa")
        workflow.add_edge("agent_qa", END)

        # Add conditional edges for error handling
        workflow.add_conditional_edges(
            "agent_persona",
            self._should_continue_after_persona,
            {
                "continue": "agent_strategy",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "agent_strategy",
            self._should_continue_after_strategy,
            {
                "continue": "agent_creative",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "agent_creative",
            self._should_continue_after_creative,
            {
                "continue": "agent_qa",
                "error": END
            }
        )
        
        # Compile the workflow
        memory = MemorySaver()
        self.graph = workflow.compile(checkpointer=memory)

    # Node functions
    async def _agent_persona_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute persona analysis node."""
        self.log_event("Executing persona analysis node", workflow_id=state["workflow_id"])
        return await self.persona_agent.execute(state)

    async def _agent_strategy_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute strategy planning node."""
        self.log_event("Executing strategy planning node", workflow_id=state["workflow_id"])
        return await self.strategy_agent.execute(state)

    async def _agent_creative_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute content generation node."""
        self.log_event("Executing content generation node", workflow_id=state["workflow_id"])
        return await self.creative_agent.execute(state)

    async def _agent_qa_node(self, state: AgentState) -> Dict[str, Any]:
        """Execute quality assurance node."""
        self.log_event("Executing quality assurance node", workflow_id=state["workflow_id"])
        return await self.qa_agent.execute(state)

    # Conditional edge functions
    def _should_continue_after_persona(self, state: AgentState) -> str:
        """Determine if workflow should continue after persona analysis."""
        if state["errors"]:
            self.log_event("Workflow stopped due to persona errors", errors=len(state["errors"]))
            return "error"
        return "continue"

    def _should_continue_after_strategy(self, state: AgentState) -> str:
        """Determine if workflow should continue after strategy planning."""
        if state["errors"]:
            self.log_event("Workflow stopped due to strategy errors", errors=len(state["errors"]))
            return "error"
        return "continue"

    def _should_continue_after_creative(self, state: AgentState) -> str:
        """Determine if workflow should continue after content generation."""
        if state["errors"]:
            self.log_event("Workflow stopped due to creative errors", errors=len(state["errors"]))
            return "error"
        return "continue"   

    async def generate_content(
        self,
        persona_id: str,
        topic: str,
        content_config: Dict[str, Any],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        
        """Generate content using the multi-agent workflow."""
    
        start_time = datetime.now()
        
        try:
            # Create initial state
            state = create_agent_state(
                request_data={
                "persona_id": persona_id,
                "topic": topic,
                "context": context or ""
            },
            content_config=content_config
)
            state["start_time"] = start_time
            self.log_event(
                "Starting content generation workflow",
                workflow_id=state["workflow_id"],
                persona_id=persona_id,
                topic=topic,
                content_type=content_config.get("content_type")
            )
            
            # Execute the workflow
            config = {"configurable": {"thread_id": state["workflow_id"]}}
            final_state = await self.graph.ainvoke(state, config=config)
            
            # Calculate total execution time
            end_time = datetime.now()
            final_state["end_time"] = end_time
            execution_time = (end_time - start_time).total_seconds()
            
            # Compile results
            results = self._compile_results(final_state, execution_time)
            
            self.log_event(
                "Content generation workflow completed",
                workflow_id=state["workflow_id"],
                success=not bool(final_state["errors"]),
                execution_time=execution_time,
                total_tokens=final_state["total_tokens_used"]
            )
            
            return results
            
        except Exception as e:
            self.log_error(e, {
                "context": "Content generation workflow",
                "workflow_id": state.get("workflow_id", "unknown") if "state" in locals() else "unknown"
            })
            
            return {
                "success": False,
                "error": str(e),
                "workflow_id": state.get("workflow_id", "unknown") if 'state' in locals() else 'unknown',
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "current_stage": state.get("current_stage", "error") if 'state' in locals() else "error",
                "metrics": {
                "total_tokens_used": 0,
                "estimated_cost": 0.0,
                "quality_score": 0,
                "agent_count": 0,
                "warnings_count": 0,
                "errors_count": 1
            }
            }

    def _compile_results(self, state: AgentState, execution_time: float) -> Dict[str, Any]:
        """Compile workflow results into a structured response."""
        
        # Determine overall success
        success = len(state["errors"]) == 0
        
        # Extract quality score
        quality_score = state["qa_feedback"].get("quality_score", 0) if state["qa_feedback"] else 0

        # Calculate estimated cost (placeholder - adjust based on actual pricing)
        estimated_cost = state["total_tokens_used"] * 0.0001  # $0.0001 per token estimate

        results = {
            "success": success,
            "workflow_id": state["workflow_id"],
            "execution_time": execution_time,
            "current_stage": state["current_stage"],
            
            # Content results
            "content": state["generated_content"] if success else None,
            "persona_analysis": state["persona_analysis"] if success else None,
            "strategy_plan": state["strategy_plan"] if success else None,
            "qa_feedback": state["qa_feedback"] if success else None,

            # Metrics
            "metrics": {
                "total_tokens_used": state["total_tokens_used"],
                "estimated_cost": estimated_cost,
                "quality_score": quality_score,
                "agent_count": len([a for a in [state["persona_analysis"], state["strategy_plan"], state["generated_content"], state["qa_feedback"]] if a]),
                "warnings_count": len(state["warnings"]),
                "errors_count": len(state["errors"])
            },
            
            # Detailed logs
            "agent_logs": state["agent_logs"],
            "errors": state["errors"],
            "warnings": state["warnings"],

            # Timestamps
            "created_at": state["created_at"],
            "started_at": state["start_time"].isoformat() if state["start_time"] else None,
            "completed_at": state["end_time"].isoformat() if state["end_time"] else None
        }
        
        return results

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a specific workflow."""
        
        try:
            config = {"configurable": {"thread_id": workflow_id}}
            # Get workflow state (this is a simplified version)
            # In a real implementation, you'd query the checkpointer
            
            return {
                "workflow_id": workflow_id,
                "status": "completed",  # You'd determine this from the actual state
                "message": "Workflow status retrieved successfully"
            }
            
        except Exception as e:
            self.log_error(e, {"context": "Get workflow status", "workflow_id": workflow_id})
            return {
                "workflow_id": workflow_id,
                "status": "error",
                "error": str(e)
            }

    def get_supported_content_types(self) -> List[Dict[str, str]]:
        """Get list of supported content types and their descriptions."""
        
        return [
            {
                "type": "blog_post",
                "name": "Blog Post",
                "description": "Long-form educational or informational content"
            },
            {
                "type": "social_media",
                "name": "Social Media Post",
                "description": "Short, engaging posts for social platforms"
            },
            {
                "type": "email_campaign",
                "name": "Email Campaign",
                "description": "Email marketing content with strong CTAs"
            },
            {
                "type": "ad_copy",
                "name": "Advertisement Copy",
                "description": "Persuasive copy for paid advertisements"
            },
            {
                "type": "landing_page",
                "name": "Landing Page",
                "description": "Conversion-focused page content"
            },
            {
                "type": "case_study",
                "name": "Case Study",
                "description": "Problem-solution-results format content"
            }
        ]


# Global orchestrator instance
_orchestrator: Optional[ContentOrchestrator] = None


def get_content_orchestrator() -> ContentOrchestrator:
    """Get global content orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ContentOrchestrator()
    return _orchestrator
