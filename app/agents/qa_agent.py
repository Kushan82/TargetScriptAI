"""QA agent for content validation and improvement."""

import json
import re
from typing import Dict, Any, List
from app.utils.helpers import get_current_timestamp
from .base import BaseAgent, AgentState


class QAAgent(BaseAgent):
    """Agent responsible for content quality assurance and improvement."""
    
    def __init__(self):
        super().__init__(name="QAAgent", model_type="fast")

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute quality assurance and return state updates."""
        
        # Validate required inputs
        if not state["generated_content"]:
            return {
                "errors": state["errors"] + [{"agent": self.name, "error": "No generated content available for QA", "timestamp": get_current_timestamp()}],
                "current_stage": "error"
            }
        
        # Check if content generation was successful
        warnings = list(state["warnings"])
        if "error" in state["generated_content"]:
            warnings.append(f"Content generation had errors: {state['generated_content'].get('error')}")
        
        # Perform QA analysis
        qa_result = await self._analyze_content_quality(state)
        
        # Prepare state updates
        state_updates = {
            "qa_feedback": qa_result,
            "current_stage": "quality_assurance",
            "warnings": warnings
        }
        
        # Apply improvements if needed
        if qa_result.get("needs_improvement") and qa_result.get("improvement_suggestions"):
            improved_content = await self._improve_content(state)
            if improved_content.get("success"):
                # Update the generated content with improvements
                updated_content = dict(state["generated_content"])
                updated_content.update(improved_content.get("improved_content", {}))
                state_updates["generated_content"] = updated_content
                state_updates["current_stage"] = "completed"
        else:
            state_updates["current_stage"] = "completed"
        
        self.log_event(
            "QA analysis completed",
            quality_score=qa_result.get("quality_score", 0),
            needs_improvement=qa_result.get("needs_improvement", False),
            improvements_applied=bool(qa_result.get("needs_improvement") and improved_content.get("success", False) if 'improved_content' in locals() else False)
        )
        
        return state_updates


    def _extract_json_from_response(self, content: str) -> str:
        """Extract JSON from LLM response, handling markdown and extra text."""
        
        if not content:
            return ""
        
        content = content.strip()
        # Clean control characters that cause JSON parsing issues
        content = content.replace('\r', '').replace('\t', ' ')
    
        # Fix common quote/apostrophe issues
        content = content.replace("'", "'").replace("'", "'")
        content = content.replace(""", '"').replace(""", '"')
        # If content starts directly with {, it's likely clean JSON
        if content.startswith('{') and content.endswith('}'):
            return content
        
        # Look for JSON within markdown code blocks
        json_patterns = [
            r'``````',
            r'``````',
        ]
    
        for pattern in json_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # Look for JSON object in the text (between first { and last })
        first_brace = content.find('{')
        last_brace = content.rfind('}')
        
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            json_content = content[first_brace:last_brace + 1]
        
            # Additional cleaning for the extracted JSON
            json_content = json_content.replace("'", "'").replace("'", "'")
            json_content = json_content.replace(""", '"').replace(""", '"')
            
            return json_content
    
        return content

    async def _analyze_content_quality(self, state: AgentState) -> Dict[str, Any]:
        """Analyze the quality of generated content."""

        generated_content = state["generated_content"]
        persona_analysis = state["persona_analysis"]
        strategy_plan = state["strategy_plan"]
        content_config = state["content_config"]

        system_prompt = self._create_system_prompt(
            "a content quality analyst and editor with expertise in marketing effectiveness and user engagement",
            {
                "persona_data": state["persona_data"],
                "content_config": content_config
            }
        )
        
        user_prompt = f"""
Analyze the quality of this generated content against the requirements:

GENERATED CONTENT:
{json.dumps(generated_content, indent=2)}

ORIGINAL REQUIREMENTS:
- Persona Analysis: {json.dumps(persona_analysis, indent=2)}
- Strategy Plan: {json.dumps(strategy_plan, indent=2)}
- Content Config: {json.dumps(content_config, indent=2)}

Evaluate the content on these criteria:
1. Persona Alignment: Does it speak to the target persona's needs, pain points, and goals?
2. Strategy Adherence: Does it follow the recommended content strategy?
3. Engagement Quality: Is it engaging and likely to hold attention?
4. Clarity & Readability: Is it clear, well-structured, and easy to read?
5. Call-to-Action Effectiveness: Is the CTA compelling and appropriate?
6. Value Delivery: Does it provide genuine value to the reader?
7. Brand Consistency: Does it match the required tone and style?
8. SEO Optimization: Are title, meta description, and tags appropriate?

Provide analysis in JSON format:

{{
    "quality_score": 85,
    "persona_alignment_score": 90,
    "strategy_adherence_score": 80,
    "engagement_score": 85,
    "clarity_score": 90,
    "cta_effectiveness_score": 75,
    "value_score": 85,
    "brand_consistency_score": 80,
    "seo_score": 70,
    "strengths": ["Strength 1", "Strength 2", "Strength 3"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "improvement_suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"],
    "needs_improvement": false,
    "overall_assessment": "Brief overall assessment",
    "recommended_changes": ["Change 1", "Change 2"]
}}

Be thorough but constructive in your analysis.
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
                qa_analysis = json.loads(json_content)
                
                # Add metadata
                qa_analysis["qa_timestamp"] = state["created_at"]
                qa_analysis["tokens_used"] = result.get("tokens", {})
                
                return qa_analysis
                
            except (json.JSONDecodeError, ValueError) as e:
                self.log_error(e, {
                    "context": "Parsing QA analysis JSON",
                    "raw_content": result.get("content", "")[:300]
                })
                
                return {
                    "error": "Failed to parse QA analysis",
                    "quality_score": 70,  # Default moderate score
                    "needs_improvement": False,
                    "raw_content": result.get("content", "")[:500],
                    "tokens_used": result.get("tokens", {})
                }
        else:
            return {
                "error": result.get("error", "QA analysis failed"),
                "quality_score": 50,  # Conservative default
                "needs_improvement": True,
                "tokens_used": result.get("tokens", {})
            }

    async def _improve_content(self, state: AgentState) -> Dict[str, Any]:
        """Improve content based on QA feedback."""

        generated_content = state["generated_content"]
        qa_feedback = state["qa_feedback"]

        if not qa_feedback.get("improvement_suggestions"):
            return {"success": False, "reason": "No improvement suggestions available"}
        
        system_prompt = self._create_system_prompt(
            "a content editor and improvement specialist focused on optimization and engagement",
            {
                "persona_data": state["persona_data"],
                "content_config": state["content_config"]
            }
        )
        
        user_prompt = f"""
You are an expert content optimizer working collaboratively with strategy, persona, and creative agents.

Your role is to enhance the following piece of content using feedback from the QA agent, while preserving its core intent, structure, and messaging.

ORIGINAL CONTENT:
{json.dumps(generated_content, indent=2)}

QA FEEDBACK:
{json.dumps(qa_feedback, indent=2)}

INSTRUCTIONS:

1. Carefully analyze the QA feedback and identify weak areas, particularly those with the lowest scores or critical comments.
2. Improve those sections while retaining high-performing elements—do **not** modify content that is already effective.
3. Ensure that tone, structure, and messaging stay aligned with the original strategic and persona direction.
4. Incorporate all feasible suggestions from QA where appropriate and meaningful.
5. Apply clarity, conciseness, and persuasive copywriting best practices without deviating from the intended platform, audience, or CTA strategy.

IMPORTANT: Respond with ONLY a valid JSON object using straight quotes (not curly quotes).
Use simple apostrophes (') instead of smart quotes.

Return the improved content in this exact format:

{{
  "title": "Improved title",
  "subtitle": "Improved subtitle",
  "introduction": "Improved introduction",
  "main_content": "Improved main content",
  "key_points": ["Improved point 1", "Improved point 2"],
  "call_to_action": "Improved CTA",
  "meta_description": "Improved meta description",
  "tags": ["improved", "tags"],
  "improvements_applied": ["List of specific improvements made"],
  "word_count": 0,
  "readability_notes": "Brief notes about clarity, tone, structure, and improvements applied"
}}

DO NOT include any commentary, reasoning steps, or notes outside the JSON structure.
Use only standard ASCII quotes and apostrophes.
"""


        result = await self._generate_response(system_prompt, user_prompt, temperature=0.4)
        
        if result.get("success"):
            try:
                # Extract and clean JSON from response
                raw_content = result.get("content", "")
                json_content = self._extract_json_from_response(raw_content)
                
                if not json_content:
                    raise ValueError("No JSON content found in response")
                
                json_content = self._clean_json_string(json_content)
                # Parse JSON response
                improved_content = json.loads(json_content)
                
                # Recalculate word count        
                full_content = f"{improved_content.get('introduction', '')} {improved_content.get('main_content', '')}"
                improved_content["word_count"] = len(full_content.split()) if full_content else 0
                
                return {
                    "success": True,
                    "improved_content": improved_content,
                    "tokens_used": result.get("tokens", {})
                }
                
            except (json.JSONDecodeError, ValueError) as e:
                self.log_error(e, {
                    "context": "Parsing improved content JSON",
                    "raw_content": result.get("content", "")[:300],
                    "error_details": str(e)
                })
                
                return {
                    "success": False,
                    "error": "Failed to parse improved content{str(e)}",
                    "raw_content": result.get("content", "")[:500],
                    "tokens_used": result.get("tokens", {})
                }
        else:
            return {
                "success": False,
                "error": result.get("error", "Content improvement failed"),
                "tokens_used": result.get("tokens", {})
            }

    def _clean_json_string(self, json_str: str) -> str:
        """Clean JSON string of problematic characters."""
    
        # Replace smart quotes with regular quotes
        replacements = {
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '…': '...',
            '–': '-',
            '—': '-',
            '\u00a0': ' ',  # Non-breaking space
            '\u2028': ' ',  # Line separator
            '\u2029': ' ',  # Paragraph separator
        }
    
        for old, new in replacements.items():
            json_str = json_str.replace(old, new)
        
        # Remove any remaining control characters
        import re
        json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', json_str)
        
        return json_str
    async def _perform_action(self, state: AgentState, action_name: str) -> Dict[str, Any]:
        """Perform specific QA agent actions."""
        
        if action_name == "analyze_quality":
            return await self._analyze_content_quality(state)
        elif action_name == "improve_content":
            return await self._improve_content(state)
        else:
            raise ValueError(f"Unknown action: {action_name}")
