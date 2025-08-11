"""Analytics and workflow history page for TargetScriptAI."""

import streamlit as st
import asyncio
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from frontend.utils.api_client import TargetScriptAIClient

# Configure page
st.set_page_config(
    page_title="Analytics Dashboard - TargetScriptAI",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for analytics interface
st.markdown("""
<style>
    .analytics-header {
        background: linear-gradient(135deg, #6f42c1 0%, #007bff 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin: 0.5rem;
        border-left: 4px solid #007bff;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #007bff;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: #6c757d;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .workflow-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .workflow-failed {
        border-left-color: #dc3545;
    }
    
    .insights-panel {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .export-section {
        background: linear-gradient(145deg, #e9ecef, #f8f9fa);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state for analytics."""
    
    if 'api_client' not in st.session_state:
        st.session_state.api_client = TargetScriptAIClient()
    
    if 'workflow_history' not in st.session_state:
        st.session_state.workflow_history = []


def calculate_metrics(workflow_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate comprehensive analytics metrics."""
    
    if not workflow_history:
        return {
            "total_workflows": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "success_rate": 0,
            "avg_quality_score": 0,
            "avg_execution_time": 0,
            "total_content_generated": 0,
            "avg_word_count": 0,
            "most_used_persona": "None",
            "most_used_content_type": "None"
        }
    
    total = len(workflow_history)
    successful = sum(1 for w in workflow_history if w.get('success', False))
    failed = total - successful
    success_rate = (successful / total * 100) if total > 0 else 0
    
    # Quality metrics
    quality_scores = [w.get('quality_score', 0) for w in workflow_history if w.get('quality_score')]
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    # Performance metrics
    execution_times = [w.get('execution_time', 0) for w in workflow_history if w.get('execution_time')]
    avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
    
    # Content metrics
    word_counts = [w.get('word_count', 0) for w in workflow_history if w.get('word_count')]
    avg_word_count = sum(word_counts) / len(word_counts) if word_counts else 0
    
    # Usage patterns
    personas = [w.get('persona', 'Unknown') for w in workflow_history]
    content_types = [w.get('content_type', 'Unknown') for w in workflow_history]
    
    most_used_persona = max(set(personas), key=personas.count) if personas else "None"
    most_used_content_type = max(set(content_types), key=content_types.count) if content_types else "None"
    
    return {
        "total_workflows": total,
        "successful_workflows": successful,
        "failed_workflows": failed,
        "success_rate": success_rate,
        "avg_quality_score": avg_quality,
        "avg_execution_time": avg_execution_time,
        "total_content_generated": successful,
        "avg_word_count": avg_word_count,
        "most_used_persona": most_used_persona,
        "most_used_content_type": most_used_content_type
    }


def render_key_metrics(metrics: Dict[str, Any]):
    """Render key performance metrics."""
    
    st.markdown("### 📈 Key Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['total_workflows']}</div>
            <div class="metric-label">Total Workflows</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['success_rate']:.1f}%</div>
            <div class="metric-label">Success Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['avg_quality_score']:.1f}</div>
            <div class="metric-label">Avg Quality Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['avg_execution_time']:.1f}s</div>
            <div class="metric-label">Avg Generation Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row of metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['total_content_generated']}</div>
            <div class="metric-label">Content Pieces</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['avg_word_count']:.0f}</div>
            <div class="metric-label">Avg Word Count</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['most_used_persona'][:15]}{'...' if len(metrics['most_used_persona']) > 15 else ''}</div>
            <div class="metric-label">Top Persona</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics['most_used_content_type'].replace('_', ' ').title()}</div>
            <div class="metric-label">Top Content Type</div>
        </div>
        """, unsafe_allow_html=True)


def render_charts(workflow_history: List[Dict[str, Any]]):
    """Render analytics charts and visualizations."""
    
    if not workflow_history:
        st.info("📊 Generate some content to see analytics charts!")
        return
    
    st.markdown("### 📊 Analytics Charts")
    
    # Create DataFrame for analysis
    df = pd.DataFrame(workflow_history)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Success/Failure pie chart
        success_counts = df['success'].value_counts()
        fig_success = px.pie(
            values=success_counts.values,
            names=['Success' if x else 'Failed' for x in success_counts.index],
            title="Workflow Success Rate",
            color_discrete_map={'Success': '#28a745', 'Failed': '#dc3545'}
        )
        fig_success.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_success, use_container_width=True)
    
    with col2:
        # Content type distribution
        if 'content_type' in df.columns:
            content_type_counts = df['content_type'].value_counts()
            fig_content = px.bar(
                x=content_type_counts.values,
                y=[ct.replace('_', ' ').title() for ct in content_type_counts.index],
                orientation='h',
                title="Content Types Generated",
                color=content_type_counts.values,
                color_continuous_scale='Blues'
            )
            fig_content.update_layout(showlegend=False)
            st.plotly_chart(fig_content, use_container_width=True)
    
    # Quality score trend over time
    if len(workflow_history) > 1:
        st.markdown("### 📈 Quality Score Trend")
        
        # Prepare data for time series
        df_quality = df[df['success'] == True].copy()
        if 'timestamp' in df_quality.columns and not df_quality.empty:
            df_quality['timestamp'] = pd.to_datetime(df_quality['timestamp'])
            df_quality = df_quality.sort_values('timestamp')
            
            if 'quality_score' in df_quality.columns:
                fig_trend = px.line(
                    df_quality,
                    x='timestamp',
                    y='quality_score',
                    title="Quality Score Over Time",
                    markers=True
                )
                fig_trend.update_traces(line_color='#007bff')
                fig_trend.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Quality Score",
                    yaxis=dict(range=[0, 100])
                )
                st.plotly_chart(fig_trend, use_container_width=True)


def render_workflow_history(workflow_history: List[Dict[str, Any]]):
    """Render detailed workflow history."""
    
    st.markdown("### 📝 Workflow History")
    
    if not workflow_history:
        st.info("🚀 No workflows yet. Start generating content to build your history!")
        return
    
    # Filter and search options
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input(
            "🔍 Search workflows",
            placeholder="Search by topic, persona, or content type...",
            help="Filter workflows by keywords"
        )
    
    with col2:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "Successful", "Failed"]
        )
    
    with col3:
        sort_order = st.selectbox(
            "Sort by",
            ["Newest First", "Oldest First", "Highest Quality", "Lowest Quality"]
        )
    
    # Apply filters
    filtered_history = workflow_history.copy()
    
    if search_term:
        search_lower = search_term.lower()
        filtered_history = [
            w for w in filtered_history
            if search_lower in w.get('topic', '').lower()
            or search_lower in w.get('persona', '').lower()
            or search_lower in w.get('content_type', '').lower()
        ]
    
    if status_filter == "Successful":
        filtered_history = [w for w in filtered_history if w.get('success', False)]
    elif status_filter == "Failed":
        filtered_history = [w for w in filtered_history if not w.get('success', False)]
    
    # Apply sorting
    if sort_order == "Newest First":
        filtered_history = sorted(filtered_history, key=lambda x: x.get('timestamp', ''), reverse=True)
    elif sort_order == "Oldest First":
        filtered_history = sorted(filtered_history, key=lambda x: x.get('timestamp', ''))
    elif sort_order == "Highest Quality":
        filtered_history = sorted(filtered_history, key=lambda x: x.get('quality_score', 0), reverse=True)
    elif sort_order == "Lowest Quality":
        filtered_history = sorted(filtered_history, key=lambda x: x.get('quality_score', 0))
    
    # Display results
    if not filtered_history:
        st.info("🔍 No workflows match your search criteria.")
        return
    
    st.markdown(f"**Showing {len(filtered_history)} of {len(workflow_history)} workflows**")
    
    # Display workflows
    for i, workflow in enumerate(filtered_history[:20]):  # Limit to 20 for performance
        
        status_class = "workflow-card" if workflow.get('success', False) else "workflow-card workflow-failed"
        status_emoji = "✅" if workflow.get('success', False) else "❌"
        
        with st.expander(f"{status_emoji} {workflow.get('topic', 'Untitled')} - {workflow.get('timestamp', 'Unknown time')}", expanded=False):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📋 Workflow Details:**")
                st.write(f"**Topic:** {workflow.get('topic', 'N/A')}")
                st.write(f"**Persona:** {workflow.get('persona', 'N/A')}")
                st.write(f"**Content Type:** {workflow.get('content_type', 'N/A').replace('_', ' ').title()}")
                st.write(f"**Status:** {'Success' if workflow.get('success', False) else 'Failed'}")
            
            with col2:
                st.markdown("**⚡ Performance Metrics:**")
                st.write(f"**Quality Score:** {workflow.get('quality_score', 'N/A')}/100")
                st.write(f"**Execution Time:** {workflow.get('execution_time', 'N/A')}s")
                st.write(f"**Word Count:** {workflow.get('word_count', 'N/A')}")
                st.write(f"**Workflow ID:** {workflow.get('workflow_id', 'N/A')}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"🔄 Regenerate Similar", key=f"regen_{i}"):
                    st.info("Feature coming soon: Regenerate similar content")
            
            with col2:
                if st.button(f"📋 Copy Content", key=f"copy_{i}"):
                    st.info("Feature coming soon: Copy generated content")
            
            with col3:
                if st.button(f"📊 View Details", key=f"details_{i}"):
                    st.info("Feature coming soon: Detailed workflow analysis")


def render_insights_panel(metrics: Dict[str, Any], workflow_history: List[Dict[str, Any]]):
    """Render AI-powered insights and recommendations."""
    
    st.markdown("### 🧠 AI Insights & Recommendations")
    
    insights = []
    
    # Generate insights based on data
    if metrics['total_workflows'] == 0:
        insights.append("🚀 **Get Started**: Generate your first content to start building analytics!")
    
    elif metrics['success_rate'] < 50:
        insights.append("⚠️ **Low Success Rate**: Consider reviewing your persona selections and content configurations.")
    
    elif metrics['avg_quality_score'] < 70:
        insights.append("📈 **Quality Improvement**: Try providing more specific context and keywords to improve content quality.")
    
    elif metrics['total_workflows'] >= 5:
        insights.append(f"🎯 **Trending**: Your most successful persona is '{metrics['most_used_persona']}' - consider expanding content for this audience.")
    
    if metrics['avg_execution_time'] > 45:
        insights.append("⏱️ **Performance**: Generation times are higher than average. This may indicate complex content requirements.")
    
    # Content diversity insights
    if workflow_history:
        content_types = [w.get('content_type', '') for w in workflow_history]
        unique_types = len(set(content_types))
        if unique_types < 3:
            insights.append(f"🎨 **Diversify**: You've used {unique_types} content types. Try exploring different formats like case studies or whitepapers.")
    
    # Default insights for good performance
    if not insights:
        insights.append("✨ **Excellent Performance**: Your content generation is performing well across all metrics!")
        insights.append("🚀 **Keep Growing**: Consider experimenting with new personas and content types to expand your reach.")
    
    # Display insights
    st.markdown("""
    <div class="insights-panel">
        <h4>💡 Personalized Recommendations</h4>
    </div>
    """, unsafe_allow_html=True)
    
    for insight in insights:
        st.markdown(f"• {insight}")


def render_export_options(workflow_history: List[Dict[str, Any]]):
    """Render data export options."""
    
    st.markdown("### 📤 Export & Actions")
    
    st.markdown("""
    <div class="export-section">
        <h4>📊 Export Your Data</h4>
        <p>Export your workflow history and analytics for external analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Export CSV", use_container_width=True):
            if workflow_history:
                df = pd.DataFrame(workflow_history)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"targetscriptai_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No data to export")
    
    with col2:
        if st.button("📄 Export JSON", use_container_width=True):
            if workflow_history:
                import json
                json_data = json.dumps(workflow_history, indent=2)
                st.download_button(
                    label="⬇️ Download JSON",
                    data=json_data,
                    file_name=f"targetscriptai_workflows_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            else:
                st.warning("No data to export")
    
    with col3:
        if st.button("🗑️ Clear History", use_container_width=True):
            if st.button("⚠️ Confirm Clear", type="secondary"):
                st.session_state.workflow_history = []
                st.success("Workflow history cleared!")
                st.rerun()
    
    with col4:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.success("Data refreshed!")
            st.rerun()


def main():
    """Main analytics dashboard interface."""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="analytics-header">
        <h1>📊 Analytics Dashboard</h1>
        <p>Comprehensive insights into your content generation performance and usage patterns</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get workflow history
    workflow_history = st.session_state.workflow_history
    
    # Calculate metrics
    metrics = calculate_metrics(workflow_history)
    
    # Render key metrics
    render_key_metrics(metrics)
    
    st.markdown("---")
    
    # Render charts
    render_charts(workflow_history)
    
    st.markdown("---")
    
    # Render insights
    render_insights_panel(metrics, workflow_history)
    
    st.markdown("---")
    
    # Render workflow history
    render_workflow_history(workflow_history)
    
    st.markdown("---")
    
    # Render export options
    render_export_options(workflow_history)
    
    # Navigation
    st.markdown("---")
    st.markdown("### 🧭 Quick Navigation")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("app.py")
    
    with col2:
        if st.button("🧠 Personas", use_container_width=True):
            st.switch_page("pages/Persona_Selection.py")
    
    with col3:
        if st.button("⚙️ Configuration", use_container_width=True):
            st.switch_page("pages/Content_Config.py")
    
    with col4:
        if st.button("🎯 Generation", use_container_width=True):
            st.switch_page("pages/Generation.py")


if __name__ == "__main__":
    main()
