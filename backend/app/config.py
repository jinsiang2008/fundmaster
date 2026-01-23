"""Application configuration with LLM model routing."""

import os
from enum import Enum
from functools import lru_cache

from pydantic_settings import BaseSettings


class ModelType(Enum):
    """Model types for different task complexity."""
    FAST = "fast"      # Quick responses, simple tasks
    REASON = "reason"  # Deep reasoning, complex analysis


class LLMProvider(Enum):
    """Supported LLM providers."""
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    OPENAI = "openai"


# Task type to model mapping
TASK_MODEL_MAPPING: dict[str, ModelType] = {
    # Fast model tasks (deepseek-chat)
    "summarize": ModelType.FAST,
    "simple_qa": ModelType.FAST,
    "intent_detect": ModelType.FAST,
    "format_output": ModelType.FAST,
    
    # Reasoning model tasks (deepseek-reasoner)
    "deep_analysis": ModelType.REASON,
    "compare_funds": ModelType.REASON,
    "risk_assessment": ModelType.REASON,
    "investment_advice": ModelType.REASON,
    "profile_matching": ModelType.REASON,
}


# LLM configurations for each provider
LLM_CONFIGS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "models": {
            "fast": {"name": "deepseek-chat", "temperature": 0.7},
            "reason": {"name": "deepseek-reasoner", "temperature": 0.2},
        },
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": {
            "fast": {"name": "qwen-turbo", "temperature": 0.7},
            "reason": {"name": "qwen-plus", "temperature": 0.2},
        },
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "models": {
            "fast": {"name": "gpt-4o-mini", "temperature": 0.7},
            "reason": {"name": "gpt-4o", "temperature": 0.2},
        },
    },
}


class Settings(BaseSettings):
    """Application settings loaded from environment."""
    
    # LLM Configuration
    deepseek_api_key: str = ""
    qwen_api_key: str = ""
    openai_api_key: str = ""
    llm_provider: str = "deepseek"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def get_api_key(self, provider: str | None = None) -> str:
        """Get API key for the specified provider."""
        provider = provider or self.llm_provider
        key_map = {
            "deepseek": self.deepseek_api_key,
            "qwen": self.qwen_api_key,
            "openai": self.openai_api_key,
        }
        return key_map.get(provider, "")
    
    def get_llm_config(self, provider: str | None = None) -> dict:
        """Get LLM configuration for the specified provider."""
        provider = provider or self.llm_provider
        return LLM_CONFIGS.get(provider, LLM_CONFIGS["deepseek"])
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
