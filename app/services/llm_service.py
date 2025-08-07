"""LLM service for Groq integration - Fixed for langchain-groq 0.3.7."""

import asyncio
from typing import Dict, List, Optional, Any
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import get_settings, LoggerMixin
from app.utils.token_counter import count_tokens


class LLMService(LoggerMixin):
    """Service for LLM operations using LangChain-Groq wrapper."""
    
    def __init__(self):
        self.settings = get_settings()
        self._clients: Dict[str, ChatGroq] = {}
        self._model_names: Dict[str, str] = {}  # Store model names separately
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize Groq clients for different models."""
        try:
            # Store model names for reference
            self._model_names = {
                "smart": self.settings.llm.groq_model_smart,
                "fast": self.settings.llm.groq_model_fast,
                "creative": self.settings.llm.groq_model_creative
            }
            
            # Base configuration
            base_config = {
                "api_key": self.settings.llm.groq_api_key,
                "temperature": self.settings.llm.temperature,
                "max_tokens": self.settings.llm.max_tokens,
            }
            
            self._clients["smart"] = ChatGroq(
                model=self._model_names["smart"],
                **base_config
            )
            
            self._clients["fast"] = ChatGroq(
                model=self._model_names["fast"],
                **base_config
            )
            
            # Creative model with higher temperature
            creative_config = base_config.copy()
            creative_config["temperature"] = min(self.settings.llm.temperature + 0.2, 1.0)
            
            self._clients["creative"] = ChatGroq(
                model=self._model_names["creative"],
                **creative_config
            )
            
            self.log_event("LLM clients initialized", models=list(self._clients.keys()))
            
        except Exception as e:
            self.log_error(e, {"context": "LLM client initialization"})
            raise
    
    def get_client(self, model_type: str = "smart") -> ChatGroq:
        """Get LLM client for specified model type."""
        if model_type not in self._clients:
            raise ValueError(f"Unknown model type: {model_type}. Available: {list(self._clients.keys())}")
        return self._clients[model_type]
    
    def get_model_name(self, model_type: str) -> str:
        """Get model name for specified model type."""
        return self._model_names.get(model_type, self._model_names["smart"])
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model_type: str = "smart",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate response using specified model."""
        
        try:
            client = self.get_client(model_type)
            model_name = self.get_model_name(model_type)
            
            # Override parameters if provided
            if temperature is not None or max_tokens is not None:
                client = ChatGroq(
                    model=model_name,
                    api_key=self.settings.llm.groq_api_key,
                    temperature=temperature or client.temperature,
                    max_tokens=max_tokens or client.max_tokens,
                )
            
            # Convert to LangChain messages
            langchain_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
            
            input_tokens = sum(count_tokens(msg["content"]) for msg in messages)
            
            self.log_event(
                "Generating LLM response",
                model_type=model_type,
                model_name=model_name,
                input_tokens=input_tokens,
                message_count=len(messages)
            )
            
            # Use invoke method (standard in newer versions)
            response = await client.ainvoke(langchain_messages)
            content = response.content
            
            output_tokens = count_tokens(content)
            total_tokens = input_tokens + output_tokens
            
            result = {
                "content": content,
                "model_type": model_type,
                "model_name": model_name,  # Use stored model name
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": total_tokens
                },
                "success": True
            }
            
            self.log_event(
                "LLM response generated",
                model_type=model_type,
                model_name=model_name,
                output_tokens=output_tokens,
                total_tokens=total_tokens
            )
            
            return result
            
        except Exception as e:
            self.log_error(e, {
                "context": "LLM response generation",
                "model_type": model_type,
                "message_count": len(messages)
            })
            
            return {
                "content": "",
                "model_type": model_type,
                "error": str(e),
                "success": False
            }
    
    async def test_connection(self, model_type: str = "fast") -> Dict[str, Any]:
        """Test connection to LLM service."""
        
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello' to confirm you're working."}
        ]
        
        result = await self.generate_response(
            messages=test_messages,
            model_type=model_type,
            max_tokens=50
        )
        
        return {
            "model_type": model_type,
            "model_name": self.get_model_name(model_type),  # Use our method
            "connected": result.get("success", False),
            "response": result.get("content", ""),
            "error": result.get("error")
        }


# Global service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
