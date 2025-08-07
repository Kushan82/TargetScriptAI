"""Strategy agent for content planning and funnel positioning - Fixed JSON parsing."""

import json
import re
from typing import Dict, Any
from app.utils.helpers import get_current_timestamp
from .base import BaseAgent, AgentState


class StrategyAgent(BaseAgent):
    """Agent responsible for content strategy and funnel positioning."""
    
    def __init__(self):
        super().__init__(name="StrategyAgent", model_type="smart")

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute strategy planning and return state updates."""
        
        if not state["persona_analysis"]:
            return {
                "errors": state["errors"] + [{"agent": self.name, "error": "No persona analysis available", "timestamp": get_current_timestamp()}],
                "current_stage": "error"
            }
        
        # Generate strategy plan
        strategy_result = await self._create_content_strategy(state)
        
        self.log_event(
            "Content strategy completed",
            funnel_stage=strategy_result.get("funnel_stage"),
            content_angle=strategy_result.get("recommended_angle"),
            cta_type=strategy_result.get("cta_strategy", {}).get("type")
        )
        
        # Return state updates
        return {
            "strategy_plan": strategy_result,
            "current_stage": "strategy_planning"
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

    async def _create_content_strategy(self, state: AgentState) -> Dict[str, Any]:
        """Generate comprehensive content strategy."""
        
        persona_analysis = state["persona_analysis"]
        request_data = state["request_data"]
        content_config = state["content_config"]
        
        system_prompt = self._create_system_prompt(
            "a content marketing strategist expert in funnel optimization and conversion psychology",
            {
                "persona_data": state["persona_data"],
                "content_config": content_config
            }
        )
        
        # Use the same prompt that worked in debug
        user_prompt = f"""
You are a strategic content planner. Based on the provided persona insights and content request, develop a precise, actionable content strategy tailored for maximum impact.

PERSONA INSIGHTS:
{json.dumps(persona_analysis, indent=2)}

CONTENT REQUEST DETAILS:
- Topic: {request_data.get('topic')}
- Content Type: {content_config.get('content_type')}
- Platform: {content_config.get('platform')}
- Target Length: {content_config.get('length')}

Generate a detailed content strategy in valid JSON format with the following fields:

{{
  "funnel_stage": "awareness | consideration | decision | retention", 
  "recommended_angle": "Best content angle based on persona needs and motivations",
  "key_messages": ["...", "...", "..."], 
  "content_structure": ["Introduction", "Main Points", "Examples", "CTA", "..."],
  "cta_strategy": {{
    "type": "learn_more | download | signup | purchase | contact",
    "placement": "e.g. after main body, mid-article, post-conclusion",
    "message": "Suggested CTA text that resonates with persona"
  }},
  "tone_adjustments": "Specific tone and style guidance based on language preferences of persona",
  "engagement_hooks": ["Hook 1", "Hook 2", "Hook 3"],
  "value_proposition": "Clear value that aligns with persona goals and pain points",
  "social_proof_types": ["testimonials", "statistics", "case studies", "influencer quotes"],
  "urgency_elements": ["limited-time offer", "fear of missing out", "trend-based timing"],
  "expected_outcomes": ["drive awareness", "generate leads", "convert interest", "build trust"]
}}

Guidelines:
- Tailor every section to align with the persona’s key insights, pain points, and decision triggers.
- Maintain clarity and structure — each field must be filled meaningfully.
- Avoid generic recommendations; make your outputs context-aware and persona-specific.

Respond with a valid and properly structured JSON object only.
"""


        result = await self._generate_response(system_prompt, user_prompt, temperature=0.3)
        
        if result.get("success"):
            try:
                # Extract and clean JSON from response
                raw_content = result.get("content", "")
                json_content = self._extract_json_from_response(raw_content)
                
                if not json_content:
                    raise ValueError("No JSON content found in response")
                
                # Parse JSON response
                strategy = json.loads(json_content)
                
                # Validate required fields and add defaults if missing
                required_fields = ["funnel_stage", "recommended_angle", "key_messages", "cta_strategy"]
                for field in required_fields:
                    if field not in strategy:
                        if field == "key_messages":
                            strategy[field] = ["Key message not specified"]
                        elif field == "cta_strategy":
                            strategy[field] = {"type": "learn_more", "placement": "end", "message": "Learn more"}
                        else:
                            strategy[field] = f"Not specified for {field}"
                
                # Add metadata
                strategy["strategy_timestamp"] = state["created_at"]
                strategy["tokens_used"] = result.get("tokens", {})
                
                return strategy
                
            except (json.JSONDecodeError, ValueError) as e:
                self.log_error(e, {
                    "context": "Parsing strategy JSON", 
                    "raw_content": result.get("content", "")[:200],
                    "json_extracted": json_content[:200] if 'json_content' in locals() else "No extraction attempted"
                })
                
                # Return fallback strategy
                return {
                    "error": "Failed to parse strategy JSON",
                    "fallback_strategy": self._create_fallback_strategy(persona_analysis, request_data),
                    "raw_content": result.get("content", "")[:500],
                    "tokens_used": result.get("tokens", {})
                }
        else:
            return {
                "error": result.get("error", "Strategy generation failed"),
                "tokens_used": result.get("tokens", {})
            }

    def _create_fallback_strategy(self, persona_analysis: Dict[str, Any], request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic fallback strategy when JSON parsing fails."""
        
        return {
            "funnel_stage": "awareness",
            "recommended_angle": f"Educational content about {request_data.get('topic', 'the topic')}",
            "key_messages": [
                "Address primary pain points",
                "Provide actionable insights", 
                "Build trust and authority"
            ],
            "content_structure": ["Introduction", "Problem", "Solution", "Benefits", "CTA"],
            "cta_strategy": {
                "type": "learn_more",
                "placement": "end of content",
                "message": "Learn more about solving this challenge"
            },
            "tone_adjustments": "Professional and helpful",
            "engagement_hooks": ["Question", "Statistic"],
            "value_proposition": "Practical solutions for your challenges",
            "social_proof_types": ["case studies"],
            "urgency_elements": ["limited time insights"],
            "expected_outcomes": ["educate", "engage", "generate interest"]
        }

    async def _perform_action(self, state: AgentState, action_name: str) -> Dict[str, Any]:
        """Perform specific strategy agent actions."""
        
        if action_name == "create_strategy":
            return await self._create_content_strategy(state)
        else:
            raise ValueError(f"Unknown action: {action_name}")
