"""Main Streamlit application for TargetScriptAI."""

import streamlit as st
import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from frontend.utils.api_client import TargetScriptAIClient

# Configure page
st.set_page_config(
    page_title="TargetScriptAI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        transition: transform 0.2s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }
    
    .metric-card {
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .status-card {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    
    .status-success {
        background: #d4edda;
        color: #155724;
        border-color: #28a745;
    }
    
    .status-warning {
        background: #fff3cd;
        color: #856404;
        border-color: #ffc107;
    }
    
    .status-error {
        background: #f8d7da;
        color: #721c24;
        border-color: #dc3545;
    }
    
    .workflow-step {
        display: flex;
        align-items: center;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }
    
    .step-number {
        background: #007bff;
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    
    # API Client
    if 'api_client' not in st.session_state:
        st.session_state.api_client = TargetScriptAIClient()
    
    # User selections
    if 'selected_persona' not in st.session_state:
        st.session_state.selected_persona = None
    
    if 'content_config' not in st.session_state:
        st.session_state.content_config = {}
    
    # Generated content and workflow
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = None
    
    if 'current_workflow' not in st.session_state:
        st.session_state.current_workflow = None
    
    if 'workflow_history' not in st.session_state:
        st.session_state.workflow_history = []
    
    # Cache for API data
    if 'personas_cache' not in st.session_state:
        st.session_state.personas_cache = None
    
    if 'content_types_cache' not in st.session_state:
        st.session_state.content_types_cache = None


async def check_api_connection():
    """Check API connection and return health status."""
    
    client = st.session_state.api_client
    
    # Try multiple connection attempts
    for attempt in range(3):
        try:
            print(f"🔄 Attempt {attempt + 1}: Connecting to {client.base_url}")
            health_status = await client.check_health()
            print(f"✅ Connection successful: {health_status.get('status')}")
            return health_status
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {str(e)}")
            if attempt < 2:  # Don't wait on last attempt
                await asyncio.sleep(1)
            continue
    
    # All attempts failed
    return {
        "status": "error", 
        "error": "Cannot connect to backend after 3 attempts",
        "troubleshooting": {
            "backend_url": client.base_url,
            "suggestions": [
                "Ensure FastAPI server is running",
                "Check if port 8000 is blocked",
                "Try restarting both servers",
                "Check firewall settings"
            ]
        }
    }
def render_api_status(health_status):
    """Render API connection status with detailed troubleshooting."""
    
    if health_status.get('status') == 'healthy':
        st.success("✅ **API Connected** - All systems operational")
        return True
    else:
        st.error("❌ **API Connection Failed** - Unable to connect to backend")
        
        # Show detailed error information
        error_msg = health_status.get('error', 'Unknown connection error')
        st.code(f"Error: {error_msg}")
        
        # Troubleshooting section
        with st.expander("🔧 **Detailed Troubleshooting**", expanded=True):
            
            # Step 1: Check if backend is running
            st.markdown("**Step 1: Verify FastAPI Backend**")
            st.code("""
# In your terminal, ensure FastAPI is running:
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# You should see:
INFO:     Uvicorn running on http://0.0.0.0:8000
            """)
            
            # Step 2: Test manual connection
            st.markdown("**Step 2: Test Manual Connection**")
            st.markdown("Try opening these URLs in your browser:")
            
            test_urls = [
                "http://localhost:8000",
                "http://127.0.0.1:8000", 
                "http://0.0.0.0:8000"
            ]
            
            for url in test_urls:
                st.markdown(f"- [{url}]({url})")
            
            # Step 3: Connection test button
            st.markdown("**Step 3: Test Connection**")
            if st.button("🔍 Test Backend Connection"):
                working_url = test_backend_connection()
                if working_url:
                    st.success(f"Found working backend at: {working_url}")
                    # Update the client
                    st.session_state.api_client = TargetScriptAIClient(working_url)
                    st.rerun()
            
            # Step 4: Common solutions
            st.markdown("**Step 4: Common Solutions**")
            st.markdown("""
            - **Port conflict**: Another service might be using port 8000
            - **Firewall**: Windows Defender might be blocking the connection
            - **Host binding**: Try starting FastAPI with `--host 127.0.0.1` instead
            - **Restart**: Stop both servers and restart FastAPI first, then Streamlit
            """)
        
        return False

def render_workflow_steps():
    """Render the 4-step workflow."""
    
    st.markdown("## 🚀 AI-Powered Content Generation Workflow")
    
    steps = [
        {
            "number": "1",
            "title": "🧠 Persona Analysis",
            "description": "AI analyzes your target audience's needs, pain points, and motivations to understand who you're creating content for.",
            "icon": "🧠"
        },
        {
            "number": "2", 
            "title": "🎯 Strategy Planning",
            "description": "Develops comprehensive content strategy, positioning, and funnel optimization based on persona insights.",
            "icon": "🎯"
        },
        {
            "number": "3",
            "title": "✍️ Creative Generation", 
            "description": "Creates engaging, targeted content that resonates with your audience using advanced AI creativity.",
            "icon": "✍️"
        },
        {
            "number": "4",
            "title": "🔍 Quality Assurance",
            "description": "Reviews and improves content quality, ensuring maximum impact and engagement for your audience.",
            "icon": "🔍"
        }
    ]
    
    for step in steps:
        st.markdown(f"""
        <div class="workflow-step">
            <div class="step-number">{step['number']}</div>
            <div>
                <h4>{step['title']}</h4>
                <p>{step['description']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_feature_overview():
    """Render feature overview cards."""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🎯 Smart Targeting</h3>
            <p>AI-powered persona analysis ensures your content resonates with the right audience</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>⚡ Fast Generation</h3>
            <p>Generate high-quality content in seconds, not hours, with our optimized AI workflow</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Quality Assured</h3>
            <p>Built-in QA agent reviews and improves content for maximum engagement and impact</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <h3>🔄 Multi-Format</h3>
            <p>Support for blogs, social media, emails, ads, and more - all optimized for each platform</p>
        </div>
        """, unsafe_allow_html=True)


def render_system_metrics(health_status):
    """Render system status metrics."""
    
    if health_status.get('status') != 'healthy':
        return
    
    st.markdown("## 📊 System Status")
    
    components = health_status.get('components', {})
    models = health_status.get('models', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🤖 AI Models</h3>
            <h2>3</h2>
            <p><strong>Smart:</strong> Strategy & Analysis<br>
            <strong>Creative:</strong> Content Generation<br>
            <strong>Fast:</strong> Quality Assurance</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        healthy_components = sum(1 for status in components.values() if status == 'healthy')
        total_components = len([k for k in components.keys() if not k.endswith('_count')])
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>🏥 Components</h3>
            <h2>{healthy_components}/{total_components}</h2>
            <p>Services Online</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        persona_count = components.get('persona_count', 0)
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>👤 Personas</h3>
            <h2>{persona_count}</h2>
            <p>Target Audiences Available</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        content_types = components.get('content_types_count', 8)
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>📄 Content Types</h3>
            <h2>{content_types}</h2>
            <p>Supported Formats</p>
        </div>
        """, unsafe_allow_html=True)


def render_quick_start():
    """Render quick start guide."""
    
    st.markdown("## 🚀 Quick Start Guide")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Ready to create amazing content? Follow these simple steps:
        
        **Step 1: Select Your Target Persona**
        - Choose from pre-built personas or create your own
        - Define your audience's goals, pain points, and preferences
        
        **Step 2: Configure Your Content**
        - Set content type (blog post, social media, email, etc.)
        - Choose tone, length, and platform requirements
        - Add keywords and specific context
        
        **Step 3: Generate with AI**
        - Watch our multi-agent system work its magic
        - Persona analysis → Strategy → Creative → QA
        - Get results in 15-30 seconds
        
        **Step 4: Review and Export**
        - Review quality scores and improvements
        - Export to DOCX, PDF, or HTML formats
        - Track performance in analytics dashboard
        """)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>💡 Pro Tips</h3>
            <ul>
                <li><strong>Be Specific:</strong> The more details you provide about your audience, the better the results</li>
                <li><strong>Try Different Tones:</strong> Experiment with various tones for different audiences</li>
                <li><strong>Use Context:</strong> Add specific context for more targeted content</li>
                <li><strong>Review QA Feedback:</strong> Check quality scores to improve your prompts</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def test_backend_connection():
    """Test backend connection with detailed diagnostics."""
    
    st.markdown("### 🔧 Connection Diagnostics")
    
    # Test different URLs
    test_urls = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://0.0.0.0:8000"
    ]
    
    for url in test_urls:
        try:
            import httpx
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{url}/api/v1/health/")
                if response.status_code == 200:
                    st.success(f"✅ **{url}** - Connected successfully")
                    st.json(response.json())
                    return url
                else:
                    st.error(f"❌ **{url}** - HTTP {response.status_code}")
        except Exception as e:
            st.error(f"❌ **{url}** - {str(e)}")
    
    return None

def main():
    """Main application function."""
    
    # Initialize session state
    initialize_session_state()
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 TargetScriptAI</h1>
        <h3>Multi-Agent AI Content Generation System</h3>
        <p>Transform your content strategy with AI-powered persona targeting, strategic planning, creative generation, and quality assurance.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check API connection
    with st.spinner("🔌 Connecting to TargetScriptAI API..."):
        health_status = asyncio.run(check_api_connection())
    
    # Render API status
    api_connected = render_api_status(health_status)
    
    if api_connected:
        # Render system metrics
        render_system_metrics(health_status)
        
        # Render feature overview
        st.markdown("---")
        render_feature_overview()
        
        # Render workflow steps
        st.markdown("---")
        render_workflow_steps()
        
        # Navigation call-to-action
        st.markdown("---")
        st.markdown("## 🎯 Ready to Get Started?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧠 Select Persona", type="primary", use_container_width=True):
                st.switch_page("pages/Persona_Selection.py")
        
        with col2:
            if st.button("⚙️ Configure Content", use_container_width=True):
                st.switch_page("pages/Content_Config.py")
        
        with col3:
            if st.button("🎯 Generate Content", use_container_width=True):
                st.switch_page("pages/Generation.py")
        
        # Quick start guide
        st.markdown("---")
        render_quick_start()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem;">
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
