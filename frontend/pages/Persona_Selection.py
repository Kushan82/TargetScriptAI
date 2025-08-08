"""Persona selection page for TargetScriptAI."""

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
    page_title="Persona Selection - TargetScriptAI",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS for persona cards
st.markdown("""
<style>
    .persona-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .persona-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .persona-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .persona-badge {
        background: #667eea;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .selected-persona {
        border-left-color: #28a745;
        background: #f8fff9;
    }
    
    .create-persona-form {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 12px;
        border: 2px dashed #667eea;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state for persona selection."""
    
    if 'api_client' not in st.session_state:
        st.session_state.api_client = TargetScriptAIClient()
    
    if 'selected_persona' not in st.session_state:
        st.session_state.selected_persona = None
    
    if 'personas_cache' not in st.session_state:
        st.session_state.personas_cache = None


@st.cache_data(ttl=300)
def load_personas() -> List[Dict[str, Any]]:
    """Load personas from API with caching."""
    
    try:
        client = TargetScriptAIClient()
        personas = asyncio.run(client.get_personas())
        return personas
    except Exception as e:
        st.error(f"Failed to load personas: {e}")
        return []


def render_persona_card(persona: Dict[str, Any], index: int) -> bool:
    """Render a persona card and return True if selected."""
    
    # Check if this persona is currently selected
    is_selected = bool (
        st.session_state.selected_persona and 
        st.session_state.selected_persona.get('id') == persona.get('id')
    )
    
    card_class = "persona-card selected-persona" if is_selected else "persona-card"
    
    with st.container():
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"### 👤 {persona['name']}")
            st.markdown(f"**Industry:** {persona.get('industry', 'General')}")
        
        with col2:
            st.markdown(f'<div class="persona-badge">{persona.get("type", "Unknown").replace("_", " ").title()}</div>', 
                       unsafe_allow_html=True)
        
        with col3:
            if is_selected:
                st.success("✅ Selected")
            else:
                if st.button("Select", key=f"select_persona_{index}"):
                    st.session_state.selected_persona = persona
                    st.success(f"✅ Selected: {persona['name']}")
                    st.rerun()
        
        # Show persona details
        with st.expander("📋 View Details", expanded=is_selected):
            
            col_left, col_right = st.columns(2)
            
            with col_left:
                # Primary Goals
                if persona.get('primary_goals'):
                    st.markdown("**🎯 Primary Goals:**")
                    for goal in persona['primary_goals']:
                        st.markdown(f"• {goal}")
                
                # Demographics
                if persona.get('demographics'):
                    st.markdown("**👥 Demographics:**")
                    st.markdown(persona['demographics'])
            
            with col_right:
                # Pain Points
                if persona.get('pain_points'):
                    st.markdown("**😤 Pain Points:**")
                    for pain in persona['pain_points']:
                        st.markdown(f"• {pain}")
                
                # Preferred Channels
                if persona.get('preferred_channels'):
                    st.markdown("**📢 Preferred Channels:**")
                    st.markdown(", ".join(persona['preferred_channels']))
            
            # Additional Context
            if persona.get('additional_context'):
                st.markdown("**📝 Additional Context:**")
                st.markdown(persona['additional_context'])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return is_selected


def create_new_persona():
    """Interface for creating a new persona."""
    
    st.markdown("""
    <div class="create-persona-form">
        <h2>🆕 Create New Persona</h2>
        <p>Define your target audience to generate highly targeted content.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("new_persona_form", clear_on_submit=True):
        
        # Basic Information
        st.markdown("### 📋 Basic Information")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Persona Name*", 
                placeholder="e.g., Tech Startup Founder",
                help="Give your persona a descriptive name"
            )
            
            persona_type = st.selectbox("Persona Type", [
                "startup_founder",
                "marketing_manager", 
                "content_creator",
                "small_business_owner",
                "enterprise_executive",
                "freelancer",
                "consultant",
                "agency_owner",
                "educator",
                "healthcare_professional",
                "finance_professional",
                "other"
            ])
        
        with col2:
            industry = st.text_input(
                "Industry", 
                placeholder="e.g., Technology, Healthcare, Finance",
                help="What industry does this persona work in?"
            )
            
            tone_preference = st.selectbox("Preferred Communication Tone", [
                "professional",
                "casual", 
                "friendly",
                "authoritative",
                "conversational",
                "formal",
                "innovative",
                "empathetic"
            ])
        
        # Demographics
        st.markdown("### 👥 Demographics")
        demographics = st.text_area(
            "Demographics Details",
            placeholder="Age range, location, company size, role level, experience, etc.",
            help="Provide details about age, location, company size, experience level, etc."
        )
        
        # Goals and Pain Points
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Primary Goals")
            goals_text = st.text_area(
                "Goals (one per line)",
                placeholder="Increase brand awareness\nGenerate more leads\nImprove conversion rates\nReduce customer acquisition costs",
                help="What are the main objectives this persona is trying to achieve?"
            )
        
        with col2:
            st.markdown("### 😤 Pain Points")
            pain_points_text = st.text_area(
                "Pain Points (one per line)",
                placeholder="Limited marketing budget\nNeed quick results\nLack of technical expertise\nToo much competition",
                help="What challenges and frustrations does this persona face?"
            )
        
        # Preferences
        st.markdown("### 📢 Communication Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            preferred_channels = st.multiselect(
                "Preferred Communication Channels",
                [
                    "Email", "LinkedIn", "Twitter", "Facebook", "Instagram", 
                    "Blog", "Website", "Video", "Podcast", "Webinar", 
                    "Direct Mail", "Phone", "In-Person", "Slack", "Teams"
                ],
                help="How does this persona prefer to receive information?"
            )
        
        with col2:
            content_preferences = st.multiselect(
                "Content Preferences",
                [
                    "Data-driven", "Story-based", "Visual", "Step-by-step guides",
                    "Case studies", "Expert opinions", "Peer reviews", "Video tutorials",
                    "Infographics", "Quick tips", "In-depth analysis", "Templates"
                ],
                help="What type of content resonates with this persona?"
            )
        
        # Additional Context
        st.markdown("### 📝 Additional Context")
        additional_context = st.text_area(
            "Additional Information",
            placeholder="Any other relevant information about this persona's behavior, motivations, decision-making process, etc.",
            help="Provide any additional insights that would help create better targeted content"
        )
        
        # Submit button
        submitted = st.form_submit_button("🚀 Create Persona", type="primary", use_container_width=True)
        
        if submitted:
            if not name:
                st.error("❌ Persona name is required!")
                return
            
            # Parse goals and pain points
            goals = [g.strip() for g in goals_text.split('\n') if g.strip()] if goals_text else []
            pain_points = [p.strip() for p in pain_points_text.split('\n') if p.strip()] if pain_points_text else []
            
            # Create persona data
            persona_data = {
                "name": name,
                "type": persona_type,
                "industry": industry or "General",
                "primary_goals": goals,
                "pain_points": pain_points,
                "preferred_channels": preferred_channels,
                "content_preferences": content_preferences,
                "tone_preference": tone_preference,
                "demographics": demographics,
                "additional_context": additional_context
            }
            
            try:
                with st.spinner(f"🔄 Creating persona: {name}..."):
                    new_persona = asyncio.run(st.session_state.api_client.create_persona(persona_data))
                
                st.success(f"🎉 Successfully created persona: **{new_persona['name']}**!")
                
                # Auto-select the new persona
                st.session_state.selected_persona = new_persona
                
                # Clear cache to reload personas
                st.cache_data.clear()
                
                st.balloons()
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Failed to create persona: {e}")


def main():
    """Main persona selection interface."""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("# 🧠 Persona Selection")
    st.markdown("Choose your target audience to create highly targeted, effective content.")
    
    # Current selection status
    if st.session_state.selected_persona:
        persona = st.session_state.selected_persona
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.success(f"🎯 **Currently Selected:** {persona['name']} ({persona.get('type', 'Unknown').replace('_', ' ').title()})")
        
        with col2:
            if st.button("🗑️ Clear Selection", use_container_width=True):
                st.session_state.selected_persona = None
                st.rerun()
        
        with col3:
            if st.button("➡️ Next: Configure Content", type="primary", use_container_width=True):
                st.switch_page("pages/Content_Config.py")
    else:
        st.info("👆 Please select a persona to continue with content generation")
    
    # Tabs for different actions
    tab1, tab2 = st.tabs(["📋 Available Personas", "🆕 Create New Persona"])
    
    with tab1:
        # Load personas
        personas = load_personas()
        
        if not personas:
            st.warning("⚠️ No personas available. Create your first persona to get started!")
        else:
            # Search and filter controls
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                search_term = st.text_input(
                    "🔍 Search personas",
                    placeholder="Search by name, type, or industry...",
                    help="Type to filter personas"
                )
            
            with col2:
                # Get unique types for filter
                available_types = list(set(p.get('type', 'Unknown') for p in personas))
                filter_type = st.selectbox(
                    "Filter by type",
                    ["All"] + [t.replace('_', ' ').title() for t in available_types]
                )
            
            with col3:
                # Get unique industries for filter
                available_industries = list(set(p.get('industry', 'General') for p in personas))
                filter_industry = st.selectbox(
                    "Filter by industry", 
                    ["All"] + available_industries
                )
            
            # Apply filters
            filtered_personas = personas
            
            if search_term:
                search_lower = search_term.lower()
                filtered_personas = [
                    p for p in filtered_personas 
                    if search_lower in p.get('name', '').lower()
                    or search_lower in p.get('type', '').lower()
                    or search_lower in p.get('industry', '').lower()
                ]
            
            if filter_type != "All":
                target_type = filter_type.lower().replace(' ', '_')
                filtered_personas = [p for p in filtered_personas if p.get('type') == target_type]
            
            if filter_industry != "All":
                filtered_personas = [p for p in filtered_personas if p.get('industry') == filter_industry]
            
            # Display results
            if not filtered_personas:
                st.info("🔍 No personas match your search criteria. Try adjusting your filters or create a new persona.")
            else:
                st.markdown(f"### Found {len(filtered_personas)} persona(s)")
                
                # Display personas
                for i, persona in enumerate(filtered_personas):
                    render_persona_card(persona, i)
    
    with tab2:
        create_new_persona()
    
    # Navigation hint
    if st.session_state.selected_persona:
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.success("🎉 **Next Step:** Configure your content settings to proceed with generation!")
        
        with col2:
            if st.button("⚙️ Configure Content →", type="primary", use_container_width=True):
                st.switch_page("pages/Content_Config.py")


if __name__ == "__main__":
    main()
