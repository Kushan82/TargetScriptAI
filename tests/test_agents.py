"""Test complete agent system functionality."""

import asyncio
from app.agents.base import create_agent_state
from app.agents.persona_agent import PersonaAgent
from app.agents.strategy_agent import StrategyAgent
from app.agents.creative_agent import CreativeAgent
from app.agents.qa_agent import QAAgent


async def test_complete_workflow():
    """Test the complete four-agent workflow."""
    
    print("🚀 Testing Complete Agent Workflow")
    print("=" * 50)
    
    try:
        # Create initial state with proper parameters - ✅ FIXED
        state = create_agent_state(
            request_data={
                "persona_id": "startup_founder_tech",
                "topic": "How to build your first MVP in 30 days",
                "context": "Focus on lean development, rapid iteration, and customer feedback"
            },
            content_config={
                "content_type": "blog_post",
                "tone": "professional",
                "length": "long",
                "platform": "blog",
                "include_cta": True,
                "keywords": ["MVP", "startup", "product development", "lean startup"]
            }
        )
        
        print(f"📝 Topic: {state['request_data']['topic']}")
        print(f"🎯 Target: {state['request_data']['persona_id']}")
        print(f"📄 Content Type: {state['content_config']['content_type']}")
        
        # Execute Persona Agent
        print(f"\n🧠 Step 1: Persona Analysis...")
        persona_agent = PersonaAgent()
        persona_updates = await persona_agent.execute(state)
        
        # Apply updates to state
        for key, value in persona_updates.items():
            state[key] = value
        
        if state["errors"]:
            print(f"❌ Persona agent failed: {state['errors']}")
            return False
        
        print(f"✅ Persona loaded: {state['persona_data'].get('name')}")
        print(f"✅ Key insights: {len(state['persona_analysis'].get('key_insights', []))}")
        
        # Execute Strategy Agent
        print(f"\n🎯 Step 2: Strategy Planning...")
        strategy_agent = StrategyAgent()
        strategy_updates = await strategy_agent.execute(state)
        
        # Apply updates to state
        for key, value in strategy_updates.items():
            state[key] = value
        
        if state["errors"]:
            print(f"❌ Strategy agent failed: {state['errors']}")
            return False
        
        strategy = state["strategy_plan"]
        print(f"✅ Funnel stage: {strategy.get('funnel_stage')}")
        print(f"✅ Content angle: {strategy.get('recommended_angle')}")
        print(f"✅ CTA type: {strategy.get('cta_strategy', {}).get('type')}")
        
        # Execute Creative Agent
        print(f"\n✍️ Step 3: Content Generation...")
        creative_agent = CreativeAgent()
        creative_updates = await creative_agent.execute(state)
        
        # Apply updates to state
        for key, value in creative_updates.items():
            state[key] = value
        
        if state["errors"]:
            print(f"❌ Creative agent failed: {state['errors']}")
            return False
        
        content = state["generated_content"]
        print(f"✅ Title: {content.get('title', 'No title')[:50]}...")
        print(f"✅ Word count: {content.get('word_count', 0)}")
        print(f"✅ Read time: {content.get('estimated_read_time', 0)} min")
        
        # Execute QA Agent
        print(f"\n🔍 Step 4: Quality Assurance...")
        qa_agent = QAAgent()
        qa_updates = await qa_agent.execute(state)
        
        # Apply updates to state
        for key, value in qa_updates.items():
            state[key] = value
        
        if state["errors"]:
            print(f"❌ QA agent failed: {state['errors']}")
            return False
        
        qa_feedback = state["qa_feedback"]
        print(f"✅ Quality score: {qa_feedback.get('quality_score', 0)}/100")
        print(f"✅ Needs improvement: {qa_feedback.get('needs_improvement', False)}")
        print(f"✅ Strengths: {len(qa_feedback.get('strengths', []))}")
        
        # Final results
        print(f"\n📊 Workflow Summary:")
        print(f"   Current stage: {state['current_stage']}")
        print(f"   Total agents executed: {len(state['agent_logs'])}")
        print(f"   Total tokens used: {state['total_tokens_used']}")
        print(f"   Warnings: {len(state['warnings'])}")
        print(f"   Errors: {len(state['errors'])}")
        
        print(f"\n🎉 Complete workflow executed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False



async def test_individual_agents():
    """Test creative and QA agents individually."""
    
    print("🧪 Testing Individual Agents")
    print("=" * 30)
    
    # Test Creative Agent
    print("\n✍️ Testing Creative Agent...")
    try:
        state = create_agent_state()
        request_data = {"topic": "MVP Development"}
        content_config = {"content_type": "blog_post", "length": "medium", "tone": "professional"}
        state["persona_data"] = {"name": "Tech Founder", "primary_goals": ["Launch quickly"]}
        state["persona_analysis"] = {
            "key_insights": ["Values speed", "Limited resources"],
            "content_angles": ["practical steps", "quick wins"]
        }
        state["strategy_plan"] = {
            "funnel_stage": "awareness",
            "recommended_angle": "step-by-step guide",
            "key_messages": ["Start small", "Iterate quickly"],
            "cta_strategy": {"type": "learn_more", "message": "Get started today"}
        }
        
        creative_agent = CreativeAgent()
        creative_updates = await creative_agent.execute(state)
        for key, value in creative_updates.items():
            state[key] = value

        if state["generated_content"] and not state["errors"]:
            print("✅ Creative agent working!")
        else:
            print(f"❌ Creative agent failed: {state['errors']}")
            
    except Exception as e:
        print(f"❌ Creative agent test failed: {e}")
    
    # Test QA Agent
    print("\n🔍 Testing QA Agent...")
    try:
        # Use state from creative agent test with generated content
        if state["generated_content"]:
            qa_agent = QAAgent()
            qa_updates = await qa_agent.execute(state)
            for key, value in qa_updates.items():
                state[key] = value

            if state["qa_feedback"] and not state["errors"]:
                print("✅ QA agent working!")
                print(f"   Quality score: {state['qa_feedback'].get('quality_score', 0)}")
            else:
                print(f"❌ QA agent failed: {state['errors']}")
        else:
            print("⚠️ Skipping QA test - no content to analyze")
            
    except Exception as e:
        print(f"❌ QA agent test failed: {e}")


async def main():
    """Run all agent tests."""
    
    # Test individual agents first
    await test_individual_agents()
    
    print("\n" + "=" * 60 + "\n")
    
    # Test complete workflow
    workflow_success = await test_complete_workflow()
    
    print(f"\n🎯 Final Result: {'✅ SUCCESS' if workflow_success else '❌ FAILED'}")
    
    if workflow_success:
        print("\n🚀 All agents working perfectly! Ready for LangGraph orchestrator.")
    else:
        print("\n⚠️ Some issues found. Check the logs above.")


if __name__ == "__main__":
    asyncio.run(main())
