"""Content configuration page for TargetScriptAI."""

import streamlit as st
import asyncio
from typing import Dict, Any, List
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from frontend.utils.api_client import TargetScriptAIClient

# Configure page
st.set_page_config(
    page_title="Content Configuration - TargetScriptAI",
    page_icon="⚙️",
    layout="wide"
)

# Custom CSS for configuration interface
st.markdown("""
<style>
    .config-section {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    
    .config-header {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .content-preview {
        background: #f8f9fa;
        border: 2px dashed #dee2e6;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .requirement-card {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    .validation-success {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    
    .validation-error {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state for content configuration."""
    
    if 'api_client' not in st.session_state:
        st.session_state.api_client = TargetScriptAIClient()
    
    if 'content_config' not in st.session_state:
        st.session_state.content_config = {}
    
    if 'content_types_cache' not in st.session_state:
        st.session_state.content_types_cache = None


@st.cache_data(ttl=600)
def load_content_types() -> Dict[str, Any]:
    """Load supported content types from API."""
    
    try:
        client = TargetScriptAIClient()
        content_types = asyncio.run(client.get_content_types())
        return content_types
    except Exception as e:
        st.error(f"Failed to load content types: {e}")
        return {"content_types": [], "count": 0}


def get_content_type_details(content_type: str) -> Dict[str, Any]:
    """Get detailed information about a content type."""
    
    content_type_info = {
        "blog_post": {
            "description": "Long-form content for thought leadership and SEO",
            "typical_length": "800-2000 words",
            "best_for": ["SEO", "Thought leadership", "Education", "Brand awareness"],
            "common_sections": ["Introduction", "Main content", "Key takeaways", "CTA"],
            "recommended_tone": ["professional", "authoritative", "educational"]
        },
        "social_media": {
            "description": "Short, engaging content for social platforms",
            "typical_length": "50-280 characters",
            "best_for": ["Engagement", "Brand awareness", "Community building", "Quick tips"],
            "common_sections": ["Hook", "Value proposition", "CTA", "Hashtags"],
            "recommended_tone": ["casual", "friendly", "conversational"]
        },
        "email_campaign": {
            "description": "Direct communication with subscribers",
            "typical_length": "150-500 words",
            "best_for": ["Lead nurturing", "Sales", "Retention", "Announcements"],
            "common_sections": ["Subject line", "Preview text", "Body", "CTA"],
            "recommended_tone": ["personal", "friendly", "professional"]
        },
        "ad_copy": {
            "description": "Persuasive content for paid advertising",
            "typical_length": "25-150 words",
            "best_for": ["Lead generation", "Sales", "Brand awareness", "Conversions"],
            "common_sections": ["Headline", "Description", "CTA", "Value proposition"],
            "recommended_tone": ["persuasive", "urgent", "benefit-focused"]
        },
        "landing_page": {
            "description": "Conversion-focused standalone web pages",
            "typical_length": "300-800 words",
            "best_for": ["Lead capture", "Sales", "Product launches", "Event registration"],
            "common_sections": ["Hero section", "Benefits", "Social proof", "CTA"],
            "recommended_tone": ["persuasive", "professional", "benefit-focused"]
        },
        "case_study": {
            "description": "Success stories showcasing results",
            "typical_length": "800-1500 words",
            "best_for": ["Social proof", "Sales enablement", "Credibility", "Lead nurturing"],
            "common_sections": ["Challenge", "Solution", "Results", "Testimonial"],
            "recommended_tone": ["professional", "analytical", "story-driven"]
        },
        "newsletter": {
            "description": "Regular updates and valuable content",
            "typical_length": "300-800 words",
            "best_for": ["Retention", "Education", "Community building", "Thought leadership"],
            "common_sections": ["Header", "Featured content", "Updates", "CTA"],
            "recommended_tone": ["friendly", "informative", "personal"]
        },
        "whitepaper": {
            "description": "In-depth research and analysis",
            "typical_length": "2000-5000 words",
            "best_for": ["Lead generation", "Thought leadership", "Education", "Authority building"],
            "common_sections": ["Executive summary", "Research", "Analysis", "Conclusions"],
            "recommended_tone": ["authoritative", "analytical", "professional"]
        }
    }
    
    return content_type_info.get(content_type, {
        "description": "Custom content type",
        "typical_length": "Variable",
        "best_for": ["Custom objectives"],
        "common_sections": ["As configured"],
        "recommended_tone": ["As specified"]
    })


def render_persona_status():
    """Display current persona selection status."""
    
    if 'selected_persona' not in st.session_state or not st.session_state.selected_persona:
        st.markdown("""
        <div class="validation-error">
            ❌ <strong>No Persona Selected</strong><br>
            Please select a target persona first to configure content effectively.
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🧠 Select Persona", type="primary"):
            st.switch_page("pages/Persona_Selection.py")
        
        return False
    
    persona = st.session_state.selected_persona
    st.markdown(f"""
    <div class="validation-success">
        ✅ <strong>Target Persona:</strong> {persona['name']}<br>
        <strong>Type:</strong> {persona.get('type', 'Unknown').replace('_', ' ').title()} | 
        <strong>Industry:</strong> {persona.get('industry', 'Unknown').replace('_', ' ').title()}
    </div>
    """, unsafe_allow_html=True)
    
    return True


def render_content_type_selector():
    """Render content type selection with detailed information."""
    
    st.markdown("### 📄 Content Type")
    
    # Load content types
    content_types_data = load_content_types()
    available_types = [
        "blog_post", "social_media", "email_campaign", "ad_copy",
        "landing_page", "case_study", "newsletter", "whitepaper"
    ]
    
    # Create columns for content type selection
    col1, col2 = st.columns([1, 2])
    
    with col1:
        content_type = st.selectbox(
            "Choose content type:",
            available_types,
            format_func=lambda x: x.replace('_', ' ').title(),
            help="Select the type of content you want to generate"
        )
        
        # Get content type details
        type_details = get_content_type_details(content_type)
        
        st.markdown(f"**Description:** {type_details['description']}")
        st.markdown(f"**Typical Length:** {type_details['typical_length']}")
    
    with col2:
        st.markdown("**Best Used For:**")
        for use_case in type_details['best_for']:
            st.markdown(f"• {use_case}")
        
        st.markdown("**Common Sections:**")
        for section in type_details['common_sections']:
            st.markdown(f"• {section}")
        
        st.markdown("**Recommended Tones:**")
        st.markdown(", ".join(type_details['recommended_tone']))
    
    return content_type, type_details


def render_content_parameters(content_type: str, type_details: Dict[str, Any]):
    """Render content parameters configuration."""
    
    st.markdown("### 🎨 Content Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Tone selection
        tone_options = [
            "professional", "casual", "friendly", "authoritative",
            "conversational", "formal", "innovative", "empathetic"
        ]
        
        # Get recommended tones for this content type
        recommended_tones = type_details.get('recommended_tone', [])
        default_tone_index = 0
        if recommended_tones and recommended_tones[0] in tone_options:
            default_tone_index = tone_options.index(recommended_tones[0])
        
        tone = st.selectbox(
            "Communication Tone:",
            tone_options,
            index=default_tone_index,
            help="How should the content sound to your audience?"
        )
        
        if tone in recommended_tones:
            st.success(f"✅ Recommended for {content_type.replace('_', ' ')}")
    
    with col2:
        # Length selection
        length_options = ["short", "medium", "long", "extended"]
        length_descriptions = {
            "short": "Quick read (200-500 words)",
            "medium": "Standard length (500-1000 words)", 
            "long": "Comprehensive (1000-2000 words)",
            "extended": "In-depth (2000+ words)"
        }
        
        length = st.selectbox(
            "Content Length:",
            length_options,
            index=1,  # Default to medium
            format_func=lambda x: f"{x.title()} - {length_descriptions[x]}",
            help="How detailed should the content be?"
        )
    
    with col3:
        # Platform selection
        platform_options = [
            "website", "blog", "linkedin", "twitter", "facebook", 
            "instagram", "email", "medium", "newsletter", "other"
        ]
        
        platform = st.selectbox(
            "Target Platform:",
            platform_options,
            format_func=lambda x: x.title(),
            help="Where will this content be published?"
        )
    
    return tone, length, platform


def render_advanced_options():
    """Render advanced content configuration options."""
    
    with st.expander("🔧 Advanced Options", expanded=False):
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Keywords
            st.markdown("**🎯 Target Keywords**")
            keywords_text = st.text_area(
                "Keywords (one per line):",
                placeholder="SEO keyword 1\nTarget phrase 2\nBrand term 3",
                help="Keywords to naturally incorporate into the content",
                height=100
            )
            
            keywords = [k.strip() for k in keywords_text.split('\n') if k.strip()] if keywords_text else []
            
            # Call-to-action preference
            include_cta = st.checkbox(
                "Include Call-to-Action",
                value=True,
                help="Should the content include a specific call-to-action?"
            )
            
            if include_cta:
                cta_type = st.selectbox(
                    "CTA Type:",
                    ["learn_more", "contact_us", "sign_up", "download", "book_demo", "get_started", "custom"],
                    format_func=lambda x: x.replace('_', ' ').title()
                )
            else:
                cta_type = None
        
        with col2:
            # Writing style preferences
            st.markdown("**✍️ Writing Style**")
            
            writing_style = st.multiselect(
                "Style Preferences:",
                [
                    "data_driven", "story_based", "step_by_step", "conversational",
                    "technical", "beginner_friendly", "expert_level", "actionable",
                    "inspirational", "problem_solving", "educational", "promotional"
                ],
                default=["actionable", "educational"],
                help="How should the content be structured and presented?"
            )
            
            # Content format preferences
            format_preferences = st.multiselect(
                "Format Elements:",
                [
                    "bullet_points", "numbered_lists", "subheadings", "quotes",
                    "statistics", "examples", "case_studies", "questions",
                    "action_items", "key_takeaways", "summary", "resources"
                ],
                default=["bullet_points", "subheadings", "key_takeaways"],
                help="What elements should be included in the content?"
            )
    
    return keywords, include_cta, cta_type, writing_style, format_preferences


def render_topic_and_context():
    """Render topic and context input section."""
    
    st.markdown("### 💡 Topic & Context")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input(
            "Content Topic*:",
            placeholder="e.g., How to validate your MVP with real customers",
            help="The main subject or title for your content",
            max_chars=200
        )
        
        context = st.text_area(
            "Additional Context:",
            placeholder="Provide specific details, angles, or requirements...\n\nExample:\n- Focus on B2B SaaS companies\n- Include practical examples\n- Mention common validation mistakes\n- Target early-stage founders",
            help="Any specific requirements, angles, or details to include",
            height=120
        )
    
    with col2:
        st.markdown("**💡 Topic Tips:**")
        st.markdown("""
        **Good topics are:**
        - Specific and actionable
        - Relevant to your persona
        - Solve a real problem
        - Include clear benefits
        
        **Examples:**
        - "5 Quick MVP Validation Tips"
        - "How to Reduce CAC by 30%"
        - "Building Your First Sales Funnel"
        """)
    
    return topic, context


def validate_configuration(config: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validate the content configuration."""
    
    errors = []
    
    # Required fields
    if not config.get('topic'):
        errors.append("Topic is required")
    
    if not config.get('content_type'):
        errors.append("Content type must be selected")
    
    if not config.get('tone'):
        errors.append("Communication tone must be selected")
    
    if not config.get('length'):
        errors.append("Content length must be selected")
    
    # Content-specific validations
    content_type = config.get('content_type')
    
    if content_type == 'ad_copy' and config.get('length') == 'extended':
        errors.append("Ad copy should typically be short or medium length")
    
    if content_type == 'whitepaper' and config.get('length') == 'short':
        errors.append("Whitepapers are typically long or extended length")
    
    # Topic validation
    topic = config.get('topic', '')
    if len(topic) < 10:
        errors.append("Topic should be at least 10 characters long")
    
    if len(topic) > 200:
        errors.append("Topic should be less than 200 characters")
    
    return len(errors) == 0, errors


def render_configuration_summary(config: Dict[str, Any]):
    """Render a summary of the current configuration."""
    
    if not config:
        return
    
    st.markdown("### 📋 Configuration Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📄 Content Details**")
        st.write(f"Type: {config.get('content_type', 'Not set').replace('_', ' ').title()}")
        st.write(f"Length: {config.get('length', 'Not set').title()}")
        st.write(f"Platform: {config.get('platform', 'Not set').title()}")
    
    with col2:
        st.markdown("**🎨 Style & Tone**")
        st.write(f"Tone: {config.get('tone', 'Not set').title()}")
        st.write(f"CTA: {'Yes' if config.get('include_cta') else 'No'}")
        keywords = config.get('keywords', [])
        st.write(f"Keywords: {len(keywords)} specified")
    
    with col3:
        st.markdown("**📝 Content Focus**")
        st.write(f"Topic: {config.get('topic', 'Not specified')[:30]}{'...' if len(config.get('topic', '')) > 30 else ''}")
        context_length = len(config.get('context', ''))
        st.write(f"Context: {context_length} characters")
        style_count = len(config.get('writing_style', []))
        st.write(f"Style elements: {style_count}")


def main():
    """Main content configuration interface."""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="config-header">
        <h1>⚙️ Content Configuration</h1>
        <p>Configure your content requirements for AI-powered generation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check persona selection
    persona_selected = render_persona_status()
    
    if not persona_selected:
        st.stop()
    
    # Main configuration form
    with st.form("content_config_form", clear_on_submit=False):
    
        # Content type selection
        content_type, type_details = render_content_type_selector()
        
        st.markdown("---")
        
        # Content parameters
        tone, length, platform = render_content_parameters(content_type, type_details)
        
        st.markdown("---")
        
        # Topic and context
        topic, context = render_topic_and_context()
        
        st.markdown("---")
        
        # Advanced options
        keywords, include_cta, cta_type, writing_style, format_preferences = render_advanced_options()
        
        st.markdown("---")
        
        # Submit button - FIX: Replace st.button with st.form_submit_button
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            submitted = st.form_submit_button(  # ✅ Fixed: Use form_submit_button
                "💾 Save Configuration",
                type="primary",
                use_container_width=True
            )
        
        if submitted:
            # Create configuration object
            config = {
                "content_type": content_type,
                "tone": tone,
                "length": length,
                "platform": platform,
                "topic": topic,
                "context": context,
                "keywords": keywords,
                "include_cta": include_cta,
                "cta_type": cta_type,
                "writing_style": writing_style,
                "format_preferences": format_preferences
            }
            
            # Validate configuration
            is_valid, errors = validate_configuration(config)
            
            if is_valid:
                # Save to session state
                st.session_state.content_config = config
                st.success("✅ Configuration saved successfully!")
                st.balloons()
            else:
                st.error("❌ Please fix the following errors:")
                for error in errors:
                    st.error(f"• {error}")

# Navigation button OUTSIDE the form - ✅ This is allowed
if st.session_state.get('content_config'):
    st.markdown("---")
    render_configuration_summary(st.session_state.content_config)
    
    # Quick action buttons outside form
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧠 Change Persona", use_container_width=True):
            st.switch_page("pages/Persona_Selection.py")
    
    with col2:
        if st.button("🗑️ Clear Config", use_container_width=True):
            st.session_state.content_config = {}
            st.rerun()
    
    with col3:
        if st.button("🎯 Generate Content", type="primary", use_container_width=True):  # ✅ This is outside form
            st.switch_page("pages/Generation.py")


if __name__ == "__main__":
    main()
