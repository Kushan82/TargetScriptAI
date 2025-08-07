import tiktoken
from typing import Optional


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count tokens in text for the specified model."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback: rough estimation (1 token ≈ 0.75 words)
        words = len(text.split())
        return int(words / 0.75)


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model_type: str = "smart"
) -> float:
    """Estimate cost for token usage (placeholder pricing)."""
    
    # Rough cost estimates (adjust based on actual Groq pricing)
    pricing = {
        "smart": {"input": 0.0001, "output": 0.0002},  # Per token
        "fast": {"input": 0.00005, "output": 0.0001},
        "creative": {"input": 0.00008, "output": 0.00015}
    }
    
    rates = pricing.get(model_type, pricing["smart"])
    
    input_cost = input_tokens * rates["input"]
    output_cost = output_tokens * rates["output"]
    
    return input_cost + output_cost
