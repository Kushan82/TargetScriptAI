"""Test the FastAPI endpoints."""

import asyncio
import httpx
import json


async def test_api_endpoints():
    """Test all API endpoints."""
    
    print("🚀 Testing TargetScriptAI API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # Test root endpoint
        print("\n🏠 Testing Root Endpoint...")
        try:
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                data = response.json()
                print("✅ Root endpoint working")
                print(f"   Service: {data['service']}")
                print(f"   Version: {data['version']}")
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
        
        # Test health check
        print("\n🏥 Testing Health Check...")
        try:
            response = await client.get(f"{base_url}/api/v1/health/")
            if response.status_code == 200:
                health = response.json()
                print("✅ Health check working")
                print(f"   Status: {health['status']}")
                print(f"   Components: {list(health['components'].keys())}")
                print(f"   LLM Service: {health['components'].get('llm_service', 'unknown')}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # Test personas endpoint
        print("\n👤 Testing Personas Endpoint...")
        try:
            response = await client.get(f"{base_url}/api/v1/personas/")
            if response.status_code == 200:
                personas = response.json()
                print("✅ Personas endpoint working")
                print(f"   Found {len(personas)} personas")
                for persona in personas[:2]:  # Show first 2
                    print(f"   - {persona['name']} ({persona['id']})")
            else:
                print(f"❌ Personas endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Personas endpoint error: {e}")
        
        # Test content types endpoint
        print("\n📄 Testing Content Types Endpoint...")
        try:
            response = await client.get(f"{base_url}/api/v1/generate/content-types")
            if response.status_code == 200:
                content_types = response.json()
                print("✅ Content types endpoint working")
                print(f"   Supported types: {content_types['count']}")
                for ct in content_types['content_types'][:3]:
                    print(f"   - {ct['name']}: {ct['type']}")
            else:
                print(f"❌ Content types endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Content types endpoint error: {e}")
        
        # Test content generation endpoint
        print("\n✍️ Testing Content Generation Endpoint...")
        try:
            request_data = {
                "persona_id": "startup_founder_tech",
                "topic": "5 Quick MVP Validation Tips",
                "content_config": {
                    "content_type": "blog_post",
                    "tone": "professional",
                    "length": "short",
                    "platform": "blog",
                    "include_cta": True,
                    "keywords": ["MVP", "validation", "startup"]
                },
                "context": "Focus on actionable, quick tips"
            }
            
            print("   Generating content (this may take 15-30 seconds)...")
            response = await client.post(
                f"{base_url}/api/v1/generate/",
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Content generation working")
                print(f"   Success: {result['success']}")
                print(f"   Workflow ID: {result['workflow_id']}")
                print(f"   Execution Time: {result['execution_time']:.2f}s")
                print(f"   Stage: {result['current_stage']}")
                
                if result['success'] and result.get('content'):
                    content = result['content']
                    print(f"   Title: {content.get('title', 'No title')[:50]}...")
                    print(f"   Word Count: {content.get('word_count', 0)}")
                    print(f"   Quality Score: {result.get('metrics', {}).get('quality_score', 'N/A')}")
                else:
                    print(f"   Error: {result.get('error', 'Unknown error')}")
                    
            else:
                print(f"❌ Content generation failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Raw error: {response.text}")
                    
        except Exception as e:
            print(f"❌ Content generation error: {e}")
        
        print(f"\n🎯 API Test Summary:")
        print(f"   Base URL: {base_url}")
        print(f"   API Docs: {base_url}/docs")
        print(f"   Health: {base_url}/api/v1/health")


if __name__ == "__main__":
    print("🚀 TargetScriptAI API Test Suite")
    print("Make sure to start the server first:")
    print("python -m uvicorn app.main:app --reload")
    print("\nThen run this test in another terminal.")
    
    asyncio.run(test_api_endpoints())
