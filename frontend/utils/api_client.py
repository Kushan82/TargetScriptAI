"""API client for communicating with TargetScriptAI backend."""

import httpx
import asyncio
from typing import Dict, List, Any, Optional
import streamlit as st


class TargetScriptAIClient:
    """Client for TargetScriptAI API with comprehensive error handling."""
    
    def __init__(self, base_url: str = None):
        # Try multiple potential backend URLs
        if base_url is None:
            possible_urls = [
                "http://127.0.0.1:8000",
                "http://localhost:8000", 
                "http://0.0.0.0:8000"
            ]
            
            # Test which URL works
            for url in possible_urls:
                try:
                    import httpx
                    with httpx.Client(timeout=5.0) as client:
                        response = client.get(f"{url}/api/v1/health/")
                        if response.status_code == 200:
                            base_url = url
                            break
                except:
                    continue
            
            # Fallback to default
            base_url = base_url or "http://127.0.0.1:8000"
        
        self.base_url = base_url
        self.timeout = httpx.Timeout(5.0, read=30.0)  # Shorter initial timeout
        print(f"🔌 API Client connecting to: {self.base_url}")  # Debug log
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling."""
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, f"{self.base_url}{endpoint}", **kwargs)
                
                if response.status_code >= 200 and response.status_code < 300:
                    return response.json() if response.content else {}
                else:
                    error_detail = "Unknown error"
                    try:
                        error_data = response.json()
                        error_detail = error_data.get('detail', f"HTTP {response.status_code}")
                    except:
                        error_detail = f"HTTP {response.status_code}: {response.text}"
                    
                    raise Exception(f"API Error: {error_detail}")
                    
        except httpx.TimeoutException:
            raise Exception("Request timed out. Please try again.")
        except httpx.ConnectError:
            raise Exception("Cannot connect to API. Please ensure the server is running.")
        except Exception as e:
            if "API Error:" in str(e):
                raise e
            else:
                raise Exception(f"Request failed: {str(e)}")
    
    async def check_health(self) -> Dict[str, Any]:
        """Check API health status."""
        return await self._make_request("GET", "/api/v1/health/")
    
    async def get_personas(self) -> List[Dict[str, Any]]:
        """Get all available personas."""
        return await self._make_request("GET", "/api/v1/personas/")
    
    async def get_persona(self, persona_id: str) -> Dict[str, Any]:
        """Get specific persona by ID."""
        return await self._make_request("GET", f"/api/v1/personas/{persona_id}")
    
    async def create_persona(self, persona_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new persona."""
        return await self._make_request("POST", "/api/v1/personas/", json=persona_data)
    
    async def update_persona(self, persona_id: str, persona_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing persona."""
        return await self._make_request("PUT", f"/api/v1/personas/{persona_id}", json=persona_data)
    
    async def delete_persona(self, persona_id: str) -> bool:
        """Delete a persona."""
        try:
            await self._make_request("DELETE", f"/api/v1/personas/{persona_id}")
            return True
        except:
            return False
    
    async def search_personas(self, search_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search personas by criteria."""
        return await self._make_request("POST", "/api/v1/personas/search", json=search_request)
    
    async def get_content_types(self) -> Dict[str, Any]:
        """Get supported content types."""
        return await self._make_request("GET", "/api/v1/generate/content-types")
    
    async def generate_content(
        self,
        persona_id: str,
        topic: str,
        content_config: Dict[str, Any],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate content using the multi-agent workflow."""
        
        # Extend timeout for content generation
        original_timeout = self.timeout
        self.timeout = httpx.Timeout(10.0, read=120.0)  # 2 minute read timeout
        
        try:
            request_data = {
                "persona_id": persona_id,
                "topic": topic,
                "content_config": content_config,
                "context": context
            }
            
            result = await self._make_request("POST", "/api/v1/generate/", json=request_data)
            return result
            
        finally:
            # Restore original timeout
            self.timeout = original_timeout
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status."""
        return await self._make_request("GET", f"/api/v1/generate/status/{workflow_id}")
    
    async def generate_batch_content(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate multiple content pieces in batch."""
        return await self._make_request("POST", "/api/v1/generate/batch", json=requests)


# Utility functions for Streamlit integration
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_personas_cached() -> List[Dict[str, Any]]:
    """Load personas with caching."""
    client = TargetScriptAIClient()
    return asyncio.run(client.get_personas())


@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_content_types_cached() -> Dict[str, Any]:
    """Load content types with caching."""
    client = TargetScriptAIClient()
    return asyncio.run(client.get_content_types())


def clear_cache():
    """Clear all cached data."""
    st.cache_data.clear()
