"""Creative agent for content generation and creative writing."""

import json
import re
from typing import Dict, Any, List
from app.utils.helpers import get_current_timestamp
from .base import BaseAgent, AgentState


class CreativeAgent(BaseAgent):
    """Agent responsible for creative content generation."""
    
    def __init__(self):
        super().__init__(name="CreativeAgent", model_type="creative")

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute content generation and return state updates."""
        
        # Validate required inputs
        if not state["persona_analysis"]:
            return {
                "errors": state["errors"] + [{"agent": self.name, "error": "No persona analysis available", "timestamp": get_current_timestamp()}],
                "current_stage": "error"
            }
            
        if not state["strategy_plan"]:
            return {
                "errors": state["errors"] + [{"agent": self.name, "error": "No strategy plan available", "timestamp": get_current_timestamp()}],
                "current_stage": "error"
            }
        
        # Generate content
        content_result = await self._generate_content(state)
        
        self.log_event(
            "Content generation completed",
            content_type=state["content_config"].get("content_type"),
            word_count=content_result.get("word_count", 0),
            has_title=bool(content_result.get("title")),
            has_cta=bool(content_result.get("call_to_action"))
        )
        
        # Return state updates
        return {
            "generated_content": content_result,
            "current_stage": "content_generation"
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

    def _estimate_word_count(self, text: str) -> int:
        """Estimate word count from text."""
        return len(text.split()) if text else 0
    def _convert_text_to_json(self, text_content: str, state: AgentState) -> Dict[str, Any]:
        """Convert plain text content to JSON structure when JSON parsing fails."""
        
        if not text_content:
            return self._create_fallback_content(state)
        
        # Try to extract title from markdown heading
        title = "Generated Content"
        lines = text_content.split('\n')
        
        for line in lines[:10]:  # Check first 10 lines for title
            line = line.strip()
            if line.startswith('# '):
                title = line[2:].strip()
                break
            elif line.startswith('## '):
                title = line[3:].strip()
                break
            elif line.startswith('### '):
                title = line[4:].strip()
                break
        
        # Extract first paragraph as introduction
        paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip() and not p.strip().startswith('#')]
        introduction = paragraphs[0] if paragraphs else "Generated introduction"
        
        # Use remaining content as main content, removing any title lines
        main_paragraphs = []
        for para in paragraphs[1:]:
            if not para.strip().startswith('#'):
                main_paragraphs.append(para.strip())
        
        main_content = '\n\n'.join(main_paragraphs) if main_paragraphs else ""
        
        # Extract key points (look for bullet points or numbered lists)
        key_points = []
        for para in paragraphs:
            lines_in_para = para.split('\n')
            for line in lines_in_para:
                line = line.strip()
                if line.startswith('•') or line.startswith('- '):
                    key_points.append(line[2:].strip())
                elif line.startswith('* '):
                    key_points.append(line[2:].strip())
                elif any(line.startswith(f"{i}. ") for i in range(1, 10)):
                    # Extract numbered list item
                    key_points.append(line.split('. ', 1)[1] if '. ' in line else line)
        
        # Generate key points from strategy if none found in content
        if not key_points and state["strategy_plan"]:
            key_points = state["strategy_plan"].get("key_messages", ["Key insight 1", "Key insight 2", "Key insight 3"])

        # Default key points if still none found
        if not key_points:
            key_points = ["Key insight from content", "Important takeaway", "Actionable advice"]
        
        # Create CTA based on strategy
        cta_strategy = state["strategy_plan"].get("cta_strategy", {}) if state["strategy_plan"] else {}
        call_to_action = cta_strategy.get("message", "Ready to get started? Learn more about how we can help you succeed.")
        
        # Generate tags from topic and keywords
        topic = state["request_data"].get('topic', '').lower()
        keywords = state["content_config"].get('keywords', [])
        tags = keywords[:3] if keywords else [topic.replace(' ', '_'), "guide", "strategy"]
        
        # Calculate word count
        word_count = self._estimate_word_count(f"{introduction} {main_content}")
        
        return {
            "title": title,
            "subtitle": f'A comprehensive guide to {state["request_data"].get("topic", "your topic")}',
            "introduction": introduction,
            "main_content": main_content,
            "key_points": key_points[:5],  # Limit to 5 key points
            "call_to_action": call_to_action,
            "meta_description": f"{title[:150]}..." if len(title) > 150 else title,
            "tags": tags,
            "word_count": word_count,
            "estimated_read_time": max(1, round(word_count / 200)),
            "readability_notes": "Content converted from well-formatted text to JSON structure",
            "conversion_note": "Successfully extracted structured content from LLM response",
            "generation_timestamp": state["created_at"],
            "tokens_used": {},
            "model_used": "text_to_json_conversion"
        }


    async def _generate_content(self, state: AgentState) -> Dict[str, Any]:
        """Generate creative content based on analysis and strategy."""
        
        persona_analysis = state["persona_analysis"]
        strategy_plan = state["strategy_plan"]
        request_data = state["request_data"]
        content_config = state["content_config"]

        system_prompt = self._create_system_prompt(
            "an expert content creator and copywriter specializing in engaging, conversion-focused content",
            {
                "persona_data": state["persona_data"],
                "content_config": content_config
            }
        )
        
        # Build context for content generation
        content_requirements = self._build_content_requirements(content_config)
        
        user_prompt = f"""
    You are an elite creative content specialist collaborating with strategy and persona agents in a multi-agent content generation system.

    Your mission is to craft high-performing, platform-optimized content that is deeply aligned with both the persona's needs and strategic goals.

    Here are the content parameters:
    - Content Type: {content_config.get('content_type','blog_post')}
    - Platform: {content_config.get('platform')}
    - Topic: {request_data.get('topic')}
    - Target Length: {content_config.get('length')} words
    - Tone: {content_config.get('tone', 'professional')}
    - Include CTA: {content_config.get('include_cta', True)}
    - Keywords: {', '.join(content_config.get('keywords', [])) or 'None specified'}

    You must base your content on the following insights:

    CONTENT STRATEGY:
    {json.dumps(strategy_plan, indent=2)}

    PERSONA INSIGHTS:
    {json.dumps(persona_analysis, indent=2)}

    ---

    ### INSTRUCTIONS

    Carefully follow the steps below to ensure the content is effective, audience-aligned, and conversion-optimized:

    1. **Audience Alignment**: Reflect internally on:
    - Who the persona is
    - What they care about  
    - What beliefs, objections, or motivators should be addressed

    2. **Opening Hook**: Start with a compelling, persona-relevant hook that grabs attention within the first few seconds (or lines).

    3. **Key Messaging & Flow**:
    - Seamlessly integrate 2–3 key messages from the strategy.
    - Reflect the recommended angle and value proposition.
    - Maintain a persuasive, natural flow.

    4. **Tone & Voice**:
    - Match the tone adjustments suggested for the persona.
    - Stay consistent with brand guidelines and platform norms.

    5. **Call to Action (CTA)**:
    - Include a clear CTA with the recommended type, placement, and message.
    - Ensure it feels like a natural next step for the reader.

    6. **Social Proof & Trust Builders**:
    - Include at least one form of credibility or social proof (testimonial, stat, etc.) as recommended.

    7. **Optimization**:
    - Ensure readability (short paragraphs, clear headings, platform-appropriate structure).
    - Make it mobile-friendly if applicable (e.g., Instagram, Twitter, etc.)

    8. **Final Output Format**:
    - Output only the final, polished content.
    - Do NOT include commentary, notes, or extra explanations.

    ---

    ### GOAL

    Your goal is to write creative, conversion-oriented content that resonates with the target audience and fulfills the intended strategic purpose.

    Think before you write. Execute with clarity, creativity, and precision.
    """

        result = await self._generate_response(system_prompt, user_prompt, temperature=0.7)
        
        if result.get("success"):
            raw_content = result.get("content", "")
            
            # Try JSON parsing first, but don't log errors if it fails
            json_content = self._extract_json_from_response(raw_content)
            
            if json_content:
                try:
                    # Parse JSON response
                    content = json.loads(json_content)
                    
                    # Calculate actual word count
                    full_content = f"{content.get('introduction', '')} {content.get('main_content', '')}"
                    actual_word_count = self._estimate_word_count(full_content)
                    content["word_count"] = actual_word_count
                    
                    # Add estimated read time
                    content["estimated_read_time"] = max(1, round(actual_word_count / 200))
                    
                    # Add generation metadata
                    content["generation_timestamp"] = state["created_at"]
                    content["tokens_used"] = result.get("tokens", {})
                    content["model_used"] = result.get("model_name", "unknown")
                    
                    self.log_event("Content generated in JSON format", word_count=actual_word_count)
                    return content
                    
                except (json.JSONDecodeError, ValueError):
                    # JSON parsing failed, fall back to text conversion
                    pass
            
            # Convert text to JSON structure (this is working perfectly!)
            converted_content = self._convert_text_to_json(raw_content, state)
            self.log_event(
                "Content generated and converted from text", 
                word_count=converted_content.get("word_count", 0),
                conversion_method="text_to_json"
            )
            return converted_content
            
        else:
            return {
                "error": result.get("error", "Content generation failed"),
                "fallback_content": self._create_fallback_content(state),
                "tokens_used": result.get("tokens", {})
            }


    def _build_content_requirements(self, content_config: Dict[str, Any]) -> str:
        """Build detailed content requirements based on configuration."""
        
        content_type = content_config.get('content_type', 'blog_post')
        length = content_config.get('length', 'medium')
        
        # Length guidelines
        length_guides = {
            'short': "Keep it concise (150-300 words). Focus on one key message.",
            'medium': "Provide comprehensive coverage (500-800 words). Include examples and details.",
            'long': "Create in-depth content (1000-1500 words). Cover topic thoroughly with examples, data, and actionable insights.",
            'extended': "Develop extensive content (1500+ words). Include comprehensive analysis, multiple examples, and detailed implementation guidance."
        }
        
        # Content type specific requirements
        type_requirements = {
            'blog_post': "Structure with clear headings, include practical examples, and make it scannable with bullet points or numbered lists.",
            'social_media': "Keep it engaging and shareable. Use hashtags if appropriate. Focus on immediate value or entertainment.",
            'email_campaign': "Write compelling subject line, personalized opening, clear value proposition, and strong CTA.",
            'ad_copy': "Focus on benefits over features. Create urgency. Include social proof if possible.",
            'landing_page': "Lead with a strong headline, explain benefits clearly, address objections, and guide to single action.",
            'newsletter': "Mix valuable content with personal touch. Include multiple content sections and clear next steps.",
            'case_study': "Follow problem-solution-results structure. Include specific metrics and outcomes.",
            'whitepaper': "Provide authoritative, research-backed insights. Use professional tone and include actionable conclusions."
        }
        
        requirements = f"""
SPECIFIC REQUIREMENTS:
- Length Guide: {length_guides.get(length, length_guides['medium'])}
- Content Type: {type_requirements.get(content_type, 'Create valuable, engaging content appropriate for the format.')}
"""
        
        return requirements

    def _create_fallback_content(self, state: AgentState) -> Dict[str, Any]:
        """Create basic fallback content when generation fails."""
        
        topic = state["request_data"].get('topic', 'Your Topic')
        content_type = state["content_config"].get('content_type', 'blog_post')

        return {
            "title": f"Understanding {topic}: A Guide",
            "subtitle": "Key insights and actionable strategies",
            "introduction": f"In today's competitive landscape, understanding {topic.lower()} is crucial for success. This guide will provide you with practical insights and actionable strategies.",
            "main_content": f"When it comes to {topic.lower()}, there are several key factors to consider. First, it's important to understand the fundamentals. Second, you need to develop a clear strategy. Finally, implementation and measurement are critical for success.",
            "key_points": [
                "Understand the fundamentals",
                "Develop a clear strategy", 
                "Focus on implementation",
                "Measure and optimize results"
            ],
            "call_to_action": "Ready to get started? Contact us to learn more about how we can help you succeed.",
            "meta_description": f"Learn about {topic.lower()} with our comprehensive guide covering key strategies and practical implementation tips.",
            "tags": [topic.lower().replace(' ', '_'), "guide", "strategy"],
            "word_count": 100,
            "readability_notes": "Fallback content - basic structure provided"
        }

    async def _perform_action(self, state: AgentState, action_name: str) -> Dict[str, Any]:
        """Perform specific creative agent actions."""
        
        if action_name == "generate_content":
            return await self._generate_content(state)
        else:
            raise ValueError(f"Unknown action: {action_name}")
    