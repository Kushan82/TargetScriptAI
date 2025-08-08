"""Test the LangGraph orchestrator."""

import asyncio
from app.agents.orchestrator import get_content_orchestrator


async def test_orchestrator_workflow():
    """Test the complete orchestrator workflow."""
    
    print("🚀 Testing LangGraph Orchestrator")
    print("=" * 50)
    
    try:
        # Get orchestrator
        orchestrator = get_content_orchestrator()
        print("✅ Orchestrator initialized")
        
        # Test content generation
        print(f"\n🎯 Generating content...")
        
        result = await orchestrator.generate_content(
            persona_id="startup_founder_tech",
            topic="How to validate your MVP with real customers",
            content_config={
                "content_type": "blog_post",
                "tone": "professional", 
                "length": "medium",
                "platform": "blog",
                "include_cta": True,
                "keywords": ["MVP", "validation", "customer feedback", "startup"]
            },
            context="Focus on practical, actionable steps that can be implemented quickly"
        )
        
        # Display results
        print(f"\n📊 Orchestrator Results:")
        print(f"✅ Success: {result['success']}")
        print(f"✅ Workflow ID: {result['workflow_id']}")
        print(f"✅ Execution Time: {result['execution_time']:.2f}s")
        print(f"✅ Current Stage: {result['current_stage']}")
        
        if result["success"]:
            content = result.get("content", {})
            metrics = result.get("metrics", {})
            
            print(f"\n📝 Generated Content:")
            print(f"   Title: {content.get('title', 'No title')}")
            print(f"   Word Count: {content.get('word_count', 0)}")
            print(f"   Read Time: {content.get('estimated_read_time', 0)} min")
            print(f"   CTA: {content.get('call_to_action', 'No CTA')[:50]}...")
            
            print(f"\n📈 Metrics:")
            print(f"   Total Tokens: {metrics.get('total_tokens_used', 0)}")
            print(f"   Quality Score: {metrics.get('quality_score', 0)}/100")
            print(f"   Estimated Cost: ${metrics.get('estimated_cost', 0):.4f}")
            print(f"   Agent Count: {metrics.get('agent_count', 0)}")
            print(f"   Errors: {metrics.get('errors_count', 0)}")
            print(f"   Warnings: {metrics.get('warnings_count', 0)}")
            
            print(f"\n🔍 Agent Execution Summary:")
            agent_logs = result.get("agent_logs", [])
            for log in agent_logs:
                print(f"   {log.get('agent', 'Unknown')}: {log.get('action', 'Unknown')} "
                      f"({log.get('duration', 0):.1f}s)")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
        return result["success"]
        
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_content_types():
    """Test different content types."""
    
    print(f"\n🧪 Testing Different Content Types")
    print("=" * 40)
    
    orchestrator = get_content_orchestrator()
    
    # Test different content types
    content_types = [
        {"type": "social_media", "length": "short"},
        {"type": "email_campaign", "length": "medium"},
    ]
    
    for config in content_types:
        print(f"\n📝 Testing {config['type']}...")
        
        try:
            result = await orchestrator.generate_content(
                persona_id="startup_founder_tech",
                topic="5 Quick MVP Validation Tips",
                content_config={
                    "content_type": config["type"],
                    "tone": "conversational",
                    "length": config["length"],
                    "include_cta": True
                }
            )
            
            if result["success"]:
                content = result.get("content", {})
                print(f"   ✅ {config['type']}: {content.get('word_count', 0)} words")
            else:
                print(f"   ❌ {config['type']}: Failed")
                
        except Exception as e:
            print(f"   ❌ {config['type']}: Error - {e}")


async def main():
    """Run orchestrator tests."""
    
    workflow_success = await test_orchestrator_workflow()
    
    if workflow_success:
        await test_content_types()
    
    print(f"\n🎯 Final Result: {'✅ SUCCESS' if workflow_success else '❌ FAILED'}")
    
    if workflow_success:
        print("\n🚀 Orchestrator working perfectly! Ready for API endpoints.")
    else:
        print("\n⚠️ Orchestrator needs debugging.")


if __name__ == "__main__":
    asyncio.run(main())
