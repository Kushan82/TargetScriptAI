"""Content generation page for TargetScriptAI."""

import streamlit as st
import asyncio
from typing import Dict, Any, List
import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from frontend.utils.api_client import TargetScriptAIClient

# Configure page
st.set_page_config(
    page_title="Content Generation - TargetScriptAI",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS for generation interface
st.markdown("""
<style>
    .generation-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .workflow-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    .agent-stage {
        display: flex;
        align-items: center;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stage-pending {
        background: #f8f9fa;
        border-left: 4px solid #dee2e6;
    }
    
    .stage-active {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        animation: pulse 2s infinite;
    }
    
    .stage-completed {
        background: #d4edda;
        border-left: 4px solid #28a745;
    }
    
    .stage-error {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .stage-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }
    
    .stage-content {
        flex-grow: 1;
    }
    
    .stage-status {
        font-weight: bold;
        margin-left: 1rem;
    }
    
    .content-preview {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        max-height: 600px;
        overflow-y: auto;
    }
    
    .metrics-card {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem;
    }
    
    .success-banner {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
    }
    
    .error-banner {
        background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def render_badge(text: str, color: str = "#007bff"):
    """Render a custom badge using HTML."""
    st.markdown(
        f'<span style="background-color:{color};color:white;padding:2px 8px;border-radius:12px;margin-right:4px;display:inline-block;font-size:0.8em;">{text}</span>',
        unsafe_allow_html=True
    )

def initialize_session_state():
    """Initialize session state for content generation."""
    
    if 'api_client' not in st.session_state:
        st.session_state.api_client = TargetScriptAIClient()
    
    if 'generation_status' not in st.session_state:
        st.session_state.generation_status = 'idle'  # idle, generating, completed, error
    
    if 'current_workflow' not in st.session_state:
        st.session_state.current_workflow = None
    
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = None
    
    if 'workflow_history' not in st.session_state:
        st.session_state.workflow_history = []


def check_prerequisites() -> tuple[bool, List[str]]:
    """Check if all prerequisites are met for content generation."""
    
    missing = []
    
    if 'selected_persona' not in st.session_state or not st.session_state.selected_persona:
        missing.append("Target persona must be selected")
    
    if 'content_config' not in st.session_state or not st.session_state.content_config:
        missing.append("Content configuration must be completed")
    
    # Check required config fields
    config = st.session_state.get('content_config', {})
    required_fields = ['content_type', 'tone', 'length', 'topic']
    
    for field in required_fields:
        if not config.get(field):
            missing.append(f"Content {field} must be specified")
    
    return len(missing) == 0, missing


def render_prerequisites_check():
    """Render prerequisites check and return True if all are met."""
    
    is_ready, missing = check_prerequisites()
    
    if is_ready:
        # Show current setup
        persona = st.session_state.selected_persona
        config = st.session_state.content_config
        
        st.markdown("""
        <div class="workflow-container">
            <h3>✅ Ready for Content Generation</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success(f"**🧠 Persona:** {persona['name']}")
            st.caption(f"Type: {persona.get('type', 'Unknown').replace('_', ' ').title()}")
        
        with col2:
            st.success(f"**📄 Content:** {config['content_type'].replace('_', ' ').title()}")
            st.caption(f"Tone: {config['tone'].title()}, Length: {config['length'].title()}")
        
        with col3:
            st.success(f"**💡 Topic:** {config['topic'][:30]}{'...' if len(config['topic']) > 30 else ''}")
            st.caption(f"Platform: {config.get('platform', 'Not specified').title()}")
        
        return True
    
    else:
        st.markdown("""
        <div class="error-banner">
            <h3>❌ Prerequisites Not Met</h3>
            <p>Please complete the following steps before generating content:</p>
        </div>
        """, unsafe_allow_html=True)
        
        for item in missing:
            st.error(f"• {item}")
        
        # Quick action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧠 Select Persona", type="primary", use_container_width=True):
                st.switch_page("pages/Persona_Selection.py")
        
        with col2:
            if st.button("⚙️ Configure Content", type="primary", use_container_width=True):
                st.switch_page("pages/Content_Config.py")
        
        return False


def render_workflow_progress(current_stage: str = "idle"):
    """Render the 4-agent workflow progress."""
    
    stages = [
        {
            "id": "persona_analysis",
            "icon": "🧠",
            "title": "Persona Analysis",
            "description": "Analyzing target audience needs and motivations"
        },
        {
            "id": "strategy_planning", 
            "icon": "🎯",
            "title": "Strategy Planning",
            "description": "Developing content strategy and positioning"
        },
        {
            "id": "content_generation",
            "icon": "✍️", 
            "title": "Content Generation",
            "description": "Creating targeted, engaging content"
        },
        {
            "id": "quality_assurance",
            "icon": "🔍",
            "title": "Quality Assurance", 
            "description": "Reviewing and improving content quality"
        }
    ]
    
    st.markdown("""
    <div class="workflow-container">
        <h3>🤖 Multi-Agent Workflow Progress</h3>
    </div>
    """, unsafe_allow_html=True)
    
    for stage in stages:
        # Determine stage status
        if current_stage == "idle":
            status_class = "stage-pending"
            status_text = "Pending"
        elif current_stage == stage["id"]:
            status_class = "stage-active"
            status_text = "🔄 In Progress"
        elif current_stage == "completed" or (
            stages.index(stage) < [s["id"] for s in stages].index(current_stage)
        ):
            status_class = "stage-completed"
            status_text = "✅ Completed"
        elif current_stage == "error":
            status_class = "stage-error"
            status_text = "❌ Error"
        else:
            status_class = "stage-pending"
            status_text = "Pending"
        
        st.markdown(f"""
        <div class="agent-stage {status_class}">
            <div class="stage-icon">{stage["icon"]}</div>
            <div class="stage-content">
                <h4>{stage["title"]}</h4>
                <p>{stage["description"]}</p>
            </div>
            <div class="stage-status">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)


async def generate_content_async():
    """Asynchronously generate content using the API."""
    
    try:
        # Get current configuration
        persona = st.session_state.selected_persona
        config = st.session_state.content_config
        
        # Prepare request
        result = await st.session_state.api_client.generate_content(
            persona_id=persona['id'],
            topic=config['topic'],
            content_config=config,
            context=config.get('context')
        )
        
        return result
        
    except Exception as e:
        raise Exception(f"Content generation failed: {str(e)}")


def render_generation_interface():
    """Render the main content generation interface."""
    
    # Generation control
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.session_state.generation_status == 'idle':
            if st.button(
                "🚀 Generate Content", 
                type="primary", 
                use_container_width=True,
                help="Start the multi-agent content generation workflow"
            ):
                st.session_state.generation_status = 'generating'
                st.session_state.current_workflow = None
                st.session_state.generated_content = None
                st.rerun()
        
        elif st.session_state.generation_status == 'generating':
            st.info("🔄 Generation in progress... This typically takes 15-30 seconds.")
            
            if st.button("🛑 Cancel", use_container_width=True):
                st.session_state.generation_status = 'idle'
                st.rerun()
        
        elif st.session_state.generation_status == 'completed':
            if st.button("🔄 Generate New Content", use_container_width=True):
                st.session_state.generation_status = 'generating'
                st.session_state.current_workflow = None
                st.session_state.generated_content = None
                st.rerun()
        
        elif st.session_state.generation_status == 'error':
            if st.button("🔄 Try Again", type="primary", use_container_width=True):
                st.session_state.generation_status = 'generating'
                st.session_state.current_workflow = None
                st.session_state.generated_content = None
                st.rerun()


def handle_content_generation():
    """Handle the content generation process with real-time updates."""
    
    if st.session_state.generation_status != 'generating':
        return
    
    # Create placeholder for dynamic updates
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    try:
        with status_placeholder:
            st.info("🔄 Initializing content generation workflow...")
        
        # Simulate stage progression for demo (replace with real API calls)
        stages = ["persona_analysis", "strategy_planning", "content_generation", "quality_assurance"]
        
        for i, stage in enumerate(stages):
            with progress_placeholder:
                render_workflow_progress(stage)
            
            with status_placeholder:
                stage_names = {
                    "persona_analysis": "🧠 Analyzing target persona...",
                    "strategy_planning": "🎯 Developing content strategy...", 
                    "content_generation": "✍️ Creating engaging content...",
                    "quality_assurance": "🔍 Performing quality review..."
                }
                st.info(stage_names[stage])
            
            # Simulate processing time
            time.sleep(2)
        
        # Execute actual API call
        with status_placeholder:
            st.info("🔄 Finalizing content generation...")
        
        result = asyncio.run(generate_content_async())
        
        # Update state with results
        st.session_state.current_workflow = result
        st.session_state.generated_content = result.get('content')
        st.session_state.generation_status = 'completed'
        
        # Add to history
        workflow_summary = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "topic": st.session_state.content_config['topic'],
            "persona": st.session_state.selected_persona['name'],
            "content_type": st.session_state.content_config['content_type'],
            "workflow_id": result.get('workflow_id'),
            "success": result.get('success', False)
        }
        st.session_state.workflow_history.append(workflow_summary)
        
        # Clear placeholders and show completion
        progress_placeholder.empty()
        status_placeholder.empty()
        
        st.markdown("""
        <div class="success-banner">
            <h3>🎉 Content Generation Completed!</h3>
            <p>Your multi-agent AI system has successfully created targeted content.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.balloons()
        st.rerun()
        
    except Exception as e:
        st.session_state.generation_status = 'error'
        st.session_state.current_workflow = {"error": str(e)}
        
        progress_placeholder.empty()
        status_placeholder.empty()
        
        st.markdown(f"""
        <div class="error-banner">
            <h3>❌ Generation Failed</h3>
            <p>{str(e)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.rerun()


def render_generation_results():
    """Render the generated content and metrics."""
    
    if not st.session_state.current_workflow:
        return
    
    workflow = st.session_state.current_workflow
    
    # Check if generation was successful
    if workflow.get('success'):
        # Show metrics
        render_generation_metrics(workflow)
        
        # Show generated content
        render_generated_content(workflow.get('content'))
        
        # Show agent insights
        render_agent_insights(workflow)
        
        # Export options
        render_export_options(workflow)
    
    else:
        # Show error details
        st.error(f"❌ Generation failed: {workflow.get('error', 'Unknown error')}")
        
        if workflow.get('errors'):
            st.markdown("**Detailed Errors:**")
            for error in workflow['errors']:
                st.error(f"• {error.get('error', 'Unknown error')}")


def render_generation_metrics(workflow: Dict[str, Any]):
    """Render generation metrics and quality scores."""
    
    st.markdown("### 📊 Generation Metrics")
    
    metrics = workflow.get('metrics', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        execution_time = workflow.get('execution_time', 0)
        st.markdown(f"""
        <div class="metrics-card">
            <h3>⏱️</h3>
            <h2>{execution_time:.1f}s</h2>
            <p>Execution Time</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        quality_score = metrics.get('quality_score', 0)
        st.markdown(f"""
        <div class="metrics-card">
            <h3>🎯</h3>
            <h2>{quality_score}/100</h2>
            <p>Quality Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        word_count = workflow.get('content', {}).get('word_count', 0)
        st.markdown(f"""
        <div class="metrics-card">
            <h3>📝</h3>
            <h2>{word_count}</h2>
            <p>Word Count</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        token_count = metrics.get('total_tokens_used', 0)
        st.markdown(f"""
        <div class="metrics-card">
            <h3>🤖</h3>
            <h2>{token_count}</h2>
            <p>Tokens Used</p>
        </div>
        """, unsafe_allow_html=True)


def render_generated_content(content: Dict[str, Any]):
    """Render the generated content with formatting."""
    
    if not content:
        st.warning("No content generated")
        return
    
    st.markdown("### 📄 Generated Content")
    
    # Content preview with tabs
    tab1, tab2, tab3 = st.tabs(["📖 Preview", "📝 Raw Content", "🏷️ Metadata"])
    
    with tab1:
        # Formatted preview
        st.markdown(f"## {content.get('title', 'Untitled')}")
        
        if content.get('subtitle'):
            st.markdown(f"*{content['subtitle']}*")
        
        st.markdown("---")
        
        if content.get('introduction'):
            st.markdown("### Introduction")
            st.markdown(content['introduction'])
        
        if content.get('main_content'):
            st.markdown("### Main Content")
            st.markdown(content['main_content'])
        
        if content.get('key_points'):
            st.markdown("### Key Points")
            for point in content['key_points']:
                st.markdown(f"• {point}")
        
        if content.get('call_to_action'):
            st.markdown("### Call to Action")
            st.markdown(f"**{content['call_to_action']}**")
    
    with tab2:
        # Raw content
        st.code(str(content), language="json")
    
    with tab3:
        # Metadata
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Content Details:**")
            st.write(f"Word Count: {content.get('word_count', 'N/A')}")
            st.write(f"Read Time: {content.get('estimated_read_time', 'N/A')} min")
            st.write(f"Generated: {content.get('generation_timestamp', 'N/A')}")
        
        with col2:
            st.markdown("**Tags & Keywords:**")
            if content.get('tags'):
                for tag in content['tags']:
                    render_badge(tag)
            
            if content.get('meta_description'):
                st.markdown("**Meta Description:**")
                st.write(content['meta_description'])


def render_agent_insights(workflow: Dict[str, Any]):
    """Render insights from each agent."""
    
    st.markdown("### 🤖 AI Agent Insights")
    
    # Create tabs for each agent
    tab1, tab2, tab3, tab4 = st.tabs(["🧠 Persona", "🎯 Strategy", "✍️ Creative", "🔍 QA"])
    
    with tab1:
        persona_analysis = workflow.get('persona_analysis', {})
        if persona_analysis:
            st.markdown("**Key Insights:**")
            for insight in persona_analysis.get('key_insights', []):
                st.markdown(f"• {insight}")
            
            st.markdown("**Content Angles:**")
            for angle in persona_analysis.get('content_angles', []):
                st.markdown(f"• {angle}")
        else:
            st.info("No persona analysis available")
    
    with tab2:
        strategy_plan = workflow.get('strategy_plan', {})
        if strategy_plan:
            st.markdown(f"**Funnel Stage:** {strategy_plan.get('funnel_stage', 'N/A')}")
            st.markdown(f"**Recommended Angle:** {strategy_plan.get('recommended_angle', 'N/A')}")
            
            if strategy_plan.get('key_messages'):
                st.markdown("**Key Messages:**")
                for message in strategy_plan['key_messages']:
                    st.markdown(f"• {message}")
        else:
            st.info("No strategy analysis available")
    
    with tab3:
        content_info = workflow.get('content', {})
        if content_info:
            st.markdown("**Content Statistics:**")
            st.write(f"Model Used: {content_info.get('model_used', 'N/A')}")
            st.write(f"Tokens Used: {content_info.get('tokens_used', {}).get('total', 'N/A')}")
            
            if content_info.get('readability_notes'):
                st.markdown("**Readability Notes:**")
                st.write(content_info['readability_notes'])
        else:
            st.info("No creative analysis available")
    
    with tab4:
        qa_feedback = workflow.get('qa_feedback', {})
        if qa_feedback:
            st.markdown(f"**Quality Score:** {qa_feedback.get('quality_score', 'N/A')}/100")
            st.markdown(f"**Needs Improvement:** {qa_feedback.get('needs_improvement', 'N/A')}")
            
            if qa_feedback.get('strengths'):
                st.markdown("**Strengths:**")
                for strength in qa_feedback['strengths']:
                    st.markdown(f"• {strength}")
            
            if qa_feedback.get('improvement_suggestions'):
                st.markdown("**Suggestions:**")
                for suggestion in qa_feedback['improvement_suggestions']:
                    st.markdown(f"• {suggestion}")
        else:
            st.info("No QA analysis available")


def render_export_options(workflow: Dict[str, Any]):
    """Render content export options."""
    
    st.markdown("### 📤 Export Options")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📄 Copy Text", use_container_width=True):
            content = workflow.get('content', {})
            text_content = f"{content.get('title', '')}\n\n{content.get('introduction', '')}\n\n{content.get('main_content', '')}\n\n{content.get('call_to_action', '')}"
            st.text_area("Content to copy:", text_content, height=200)
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/Analytics.py")
    
    with col3:
        if st.button("💾 Save to History", use_container_width=True):
            st.success("Content saved to workflow history!")
    
    with col4:
        if st.button("🔄 Generate Variation", use_container_width=True):
            st.session_state.generation_status = 'generating'
            st.rerun()


def main():
    """Main content generation interface."""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="generation-header">
        <h1>🎯 Content Generation</h1>
        <p>Watch your multi-agent AI system create targeted content in real-time</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check prerequisites
    prerequisites_met = render_prerequisites_check()
    
    if not prerequisites_met:
        st.stop()
    
    # Render workflow progress
    current_stage = "idle"
    if st.session_state.generation_status == 'generating':
        current_stage = "persona_analysis"  # This would be dynamic in real implementation
    elif st.session_state.generation_status == 'completed':
        current_stage = "completed"
    elif st.session_state.generation_status == 'error':
        current_stage = "error"
    
    render_workflow_progress(current_stage)
    
    st.markdown("---")
    
    # Generation interface
    render_generation_interface()
    
    # Handle active generation
    if st.session_state.generation_status == 'generating':
        handle_content_generation()
    
    # Show results if available
    if st.session_state.generation_status in ['completed', 'error']:
        st.markdown("---")
        render_generation_results()


if __name__ == "__main__":
    main()
