"""Sidebar component for navigation and status display."""

import streamlit as st


def render_sidebar():
    """Render the main navigation sidebar."""
    
    with st.sidebar:
        # Header
        st.markdown("## 🎯 TargetScriptAI")
        st.markdown("*Multi-Agent Content Generation*")
        
        # Current workflow status
        render_workflow_status()
        
        # Navigation menu
        render_navigation()
        
        # Current selections
        render_current_selections()
        
        # Quick actions
        render_quick_actions()
        
        # Help section
        render_help_section()


def render_workflow_status():
    """Render current workflow status."""
    
    st.markdown("### 📊 Workflow Status")
    
    # Check if we have an active workflow
    if 'current_workflow' in st.session_state and st.session_state.current_workflow:
        workflow = st.session_state.current_workflow
        st.success(f"🔄 Active: {workflow.get('workflow_id', 'Unknown')[:8]}...")
        
        # Show progress if available
        stage = workflow.get('current_stage', 'unknown')
        stage_emoji = {
            'persona_analysis': '🧠',
            'strategy_planning': '🎯', 
            'content_generation': '✍️',
            'quality_assurance': '🔍',
            'completed': '✅'
        }
        
        st.info(f"{stage_emoji.get(stage, '⏳')} Stage: {stage.replace('_', ' ').title()}")
    
    # Show workflow history count
    history_count = len(st.session_state.get('workflow_history', []))
    if history_count > 0:
        st.metric("Completed", history_count)
    else:
        st.info("No workflows completed yet")


def render_navigation():
    """Render navigation menu."""
    
    st.markdown("### 📋 Navigation")
    
    # Get current page
    current_page = st.session_state.get('current_page', 'home')
    
    # Navigation buttons
    if st.button("🏠 Home", use_container_width=True, type="primary" if current_page == 'home' else "secondary"):
        st.switch_page("app.py")
    
    if st.button("🧠 Persona Selection", use_container_width=True, type="primary" if current_page == 'persona' else "secondary"):
        st.switch_page("pages/Persona_Selection.py")
    
    if st.button("⚙️ Content Config", use_container_width=True, type="primary" if current_page == 'config' else "secondary"):
        st.switch_page("pages/Content_Config.py")
    
    if st.button("🎯 Generation", use_container_width=True, type="primary" if current_page == 'generation' else "secondary"):
        st.switch_page("pages/Generation.py")
    
    if st.button("📊 Analytics", use_container_width=True, type="primary" if current_page == 'analytics' else "secondary"):
        st.switch_page("pages/Analytics.py")


def render_current_selections():
    """Show current persona and content configuration."""
    
    st.markdown("### 🎯 Current Setup")
    
    # Persona selection status
    if 'selected_persona' in st.session_state and st.session_state.selected_persona:
        persona = st.session_state.selected_persona
        st.success(f"✅ **Persona:** {persona.get('name', 'Unknown')}")
        st.caption(f"Type: {persona.get('type', 'Unknown')}")
    else:
        st.warning("❌ **Persona:** Not selected")
    
    # Content config status
    if 'content_config' in st.session_state and st.session_state.content_config:
        config = st.session_state.content_config
        
        if config.get('content_type'):
            st.success(f"✅ **Type:** {config['content_type']}")
        
        if config.get('tone'):
            st.success(f"✅ **Tone:** {config['tone']}")
        
        if config.get('length'):
            st.success(f"✅ **Length:** {config['length']}")
    else:
        st.warning("❌ **Config:** Not set")
    
    # Generation readiness
    persona_ready = bool(st.session_state.get('selected_persona'))
    config_ready = bool(st.session_state.get('content_config', {}).get('content_type'))
    
    if persona_ready and config_ready:
        st.success("🚀 Ready to generate!")
    else:
        missing = []
        if not persona_ready:
            missing.append("Persona")
        if not config_ready:
            missing.append("Config")
        st.warning(f"⚠️ Missing: {', '.join(missing)}")


def render_quick_actions():
    """Render quick action buttons."""
    
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh", help="Refresh cached data", use_container_width=True):
            # Clear cache
            from frontend.utils.api_client import clear_cache
            clear_cache()
            
            # Clear session state cache
            cache_keys = ['personas_cache', 'content_types_cache']
            for key in cache_keys:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.success("Cache cleared!")
            st.rerun()
    
    with col2:
        if st.button("🗑️ Reset", help="Clear all selections", use_container_width=True):
            # Clear user selections
            selection_keys = ['selected_persona', 'content_config', 'generated_content', 'current_workflow']
            for key in selection_keys:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.success("Selections cleared!")
            st.rerun()
    
    if st.button("📋 History", help="View workflow history", use_container_width=True):
        with st.expander("📋 Workflow History", expanded=True):
            history = st.session_state.get('workflow_history', [])
            
            if not history:
                st.info("No workflows completed yet")
            else:
                for i, workflow in enumerate(reversed(history[-5:])):  # Show last 5
                    st.markdown(f"**{i+1}.** {workflow.get('topic', 'Unknown')} - {workflow.get('timestamp', 'Unknown time')}")


def render_help_section():
    """Render help and documentation."""
    
    st.markdown("### 🆘 Help & Support")
    
    with st.expander("📖 Quick Guide"):
        st.markdown("""
        **Getting Started:**
        1. Select or create a target persona
        2. Configure content type, tone & length
        3. Generate content with AI agents
        4. Review results and export
        
        **Tips:**
        - Be specific with persona details
        - Use context for better targeting
        - Try different tones and formats
        - Check QA feedback for improvements
        """)
    
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        **Common Issues:**
        
        **API Connection:**
        - Ensure FastAPI server is running
        - Check http://localhost:8000/health
        
        **Generation Errors:**
        - Verify persona is selected
        - Check content configuration
        - Review error messages in logs
        
        **Slow Performance:**
        - Content generation takes 15-30s
        - Complex content may take longer
        - Check internet connection
        """)
    
    with st.expander("ℹ️ About"):
        st.markdown("""
        **TargetScriptAI v1.0**
        
        Multi-agent AI system for targeted content generation using:
        - **Persona Agent**: Audience analysis
        - **Strategy Agent**: Content planning  
        - **Creative Agent**: Content generation
        - **QA Agent**: Quality assurance
        
        Built with FastAPI, LangGraph, Streamlit & Groq.
        """)


def render_workflow_progress(current_stage: str):
    """Render workflow progress indicator."""
    
    stages = [
        ("🧠", "Persona Analysis"),
        ("🎯", "Strategy Planning"), 
        ("✍️", "Content Generation"),
        ("🔍", "Quality Assurance")
    ]
    
    stage_mapping = {
        'persona_analysis': 0,
        'strategy_planning': 1,
        'content_generation': 2,
        'quality_assurance': 3,
        'completed': 4
    }
    
    current_index = stage_mapping.get(current_stage, -1)
    
    st.markdown("#### 🔄 Workflow Progress")
    
    for i, (emoji, name) in enumerate(stages):
        if i <= current_index:
            st.success(f"{emoji} {name} ✓")
        elif i == current_index + 1:
            st.info(f"{emoji} {name} 🔄")
        else:
            st.empty()
