from typing import Optional, List, Dict
from pydantic import Field, field_validator, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum

import os
from dotenv import load_dotenv

load_dotenv()

class ModelType(str, Enum):
    """Available model types for different use cases."""
    SMART = "smart"      # Complex reasoning, strategy planning
    FAST = "fast"        # Quick operations, validation
    CREATIVE = "creative" # Content generation, creativity

class AppSettings(BaseModel):
    '''Applications specific settings'''
    environment: str = Field(default="development", description="Application environment")
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:8080"], description="CORS origins")
    allowed_hosts: List[str] = Field(default=["*"], description="Allowed hosts")

class LLMSettings(BaseSettings):
    groq_api_key: str = Field(..., description="Groq API key")
    groq_model_smart: str = Field("llama-3.1-70b-versatile", description="Smart model for reasoning")
    groq_model_fast: str = Field("llama-3.1-8b-instant", description="Fast model for quick tasks")
    groq_model_creative: str = Field("mixtral-8x7b-32768", description="Creative model for content")

    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: int = Field(4096, ge=1, le=8192, description="Maximum tokens")
    top_p: float = Field(1.0, ge=0.0, le=1.0, description="Top-p sampling")

    @property
    def model_mapping(self) -> Dict[ModelType, str]:
        """Get mapping of model types to actual model names."""
        return {
            ModelType.SMART: self.groq_model_smart,
            ModelType.FAST: self.groq_model_fast,
            ModelType.CREATIVE: self.groq_model_creative,
        }
    def get_model_for_agent(self, agent_type: str) -> str:
        """Get the appropriate model for a specific agent type."""
        model_assignment = {
            "persona": ModelType.SMART,     # Needs deep understanding
            "strategy": ModelType.SMART,    # Requires complex reasoning
            "creative": ModelType.CREATIVE, # Benefits from creativity
            "qa": ModelType.FAST,          # Quick validation tasks
        }
        
        model_type = model_assignment.get(agent_type.lower(), ModelType.SMART)
        return self.model_mapping[model_type]

class APISettings(BaseSettings):
    host: str = Field("0.0.0.0", description="API host")
    port: int = Field(8000, ge=1, le=65535, description="API port")
    reload: bool = Field(True, description="Auto-reload on changes")
    log_level: str = Field("info", description="Uvicorn log level")

    cors_origins: List[str] = Field(
        ["http://localhost:8501", "http://127.0.0.1:8501"],
        description="CORS allowed origins"
    )
    
    model_config = SettingsConfigDict(env_prefix="API_")

class StreamlitSettings(BaseSettings):
    
    
    host: str = Field("0.0.0.0", description="Streamlit host")
    port: int = Field(8501, ge=1, le=65535, description="Streamlit port")
    
    model_config = SettingsConfigDict(env_prefix="STREAMLIT_")


class DatabaseSettings(BaseSettings):
    
    
    url: str = Field("sqlite:///./targetscriptai.db", description="Database URL")
    echo: bool = Field(False, description="SQLAlchemy echo")
    
    model_config = SettingsConfigDict(env_prefix="DATABASE_")

class SecuritySettings(BaseSettings):
   
    
    secret_key: str = Field(..., description="JWT secret key")
    algorithm: str = Field("HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(30, description="Token expiry")
    
    model_config = SettingsConfigDict(env_file= ".env",
        env_file_encoding="utf-8",
        case_sensitive= False,
        extra= "ignore"
    )

class ObservabilitySettings(BaseSettings):
    
    
    enable_metrics: bool = Field(True, description="Enable Prometheus metrics")
    enable_tracing: bool = Field(False, description="Enable tracing")
    log_level: str = Field("INFO", description="Application log level")
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v:str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    model_config = SettingsConfigDict(env_prefix="")

class RateLimitSettings(BaseSettings):
    
    
    enabled: bool = Field(True, description="Enable rate limiting")
    requests: int = Field(100, description="Requests per window")
    window: int = Field(3600, description="Time window in seconds")
    
    model_config = SettingsConfigDict(env_prefix="RATE_LIMIT_")

class Settings(BaseSettings):
    
    
    # Environment
    environment: str = Field("development", description="Environment name")
    debug: bool = Field(True, description="Debug mode")
    
    app: AppSettings = Field(default_factory=AppSettings)
    # Component settings
    llm: LLMSettings = Field(default_factory=LLMSettings)
    api: APISettings = Field(default_factory=APISettings)
    streamlit: StreamlitSettings = Field(default_factory=StreamlitSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    rate_limit: RateLimitSettings = Field(default_factory=RateLimitSettings)

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v:str) -> str:
        valid_envs = ["development", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}")
        return v
    
    @property
    def model_info(self) -> Dict[str, Dict[str, str]]:
        
        return {
            "smart": {
                "model": self.llm.groq_model_smart,
                "use_case": "Complex reasoning, strategy planning, deep analysis",
                "speed": "Slow but thorough"
            },
            "fast": {
                "model": self.llm.groq_model_fast,
                "use_case": "Quick validation, simple tasks, rapid responses",
                "speed": "Very fast"
            },
            "creative": {
                "model": self.llm.groq_model_creative,
                "use_case": "Creative content generation, storytelling, copywriting",
                "speed": "Moderate with high creativity"
            }
        }
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    global settings
    if settings is None:
        settings = Settings()

    return settings

settings = get_settings()