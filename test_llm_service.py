"""Test LLM service integration."""

import asyncio

async def test_llm_service():
    """Test LLM service functionality."""
    
    try:
        from app.services.llm_service import get_llm_service
        
        print("🔍 Testing LLM Service...")
        
        llm_service = get_llm_service()
        print("✅ LLM service initialized")
        
        # Test connection
        connection_test = await llm_service.test_connection("fast")
        print(f"✅ Connection test: {connection_test}")
        
        if connection_test["connected"]:
            print("🎉 LLM service working perfectly!")
            
            # Test different models
            for model_type in ["smart", "fast", "creative"]:
                print(f"\n🧪 Testing {model_type} model...")
                result = await llm_service.test_connection(model_type)
                print(f"   Model: {result['model_name']}")
                print(f"   Connected: {result['connected']}")
                print(f"   Response: {result['response'][:50]}...")
        else:
            print(f"❌ Connection failed: {connection_test.get('error', 'Unknown error')}")
            
        return True
        
    except Exception as e:
        print(f"❌ LLM service test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_llm_service())
