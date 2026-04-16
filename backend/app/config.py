"""Application configuration with LLM model routing."""

from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 始终读取 backend/.env，避免从错误工作目录启动时读到空配置或其它目录的 .env
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_ENV_FILE = _BACKEND_ROOT / ".env"


class ModelType(Enum):
    """Model types for different task complexity."""

    FAST = "fast"  # Quick responses, simple tasks
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
    # Reasoning model tasks (deepseek-reasoner) — 较慢，仅适合单基金长文分析
    "deep_analysis": ModelType.REASON,
    # 多基对比：输入已为结构化指标，用 fast 即可，避免 reasoner 耗时过长
    "compare_funds": ModelType.FAST,
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

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

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
        return (key_map.get(provider, "") or "").strip()

    def get_llm_config(self, provider: str | None = None) -> dict:
        """Get LLM configuration for the specified provider."""
        provider = provider or self.llm_provider
        return LLM_CONFIGS.get(provider, LLM_CONFIGS["deepseek"])


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def warn_if_deepseek_key_env_overrides_dotenv() -> None:
    """
    若 shell/IDE 里设置了 DEEPSEEK_API_KEY，会覆盖 backend/.env（Pydantic 默认优先级）。
    易导致「.env 已换新 Key 但仍 401」。
    """
    import os

    from dotenv import dotenv_values

    if not _ENV_FILE.is_file():
        return
    file_key = (dotenv_values(_ENV_FILE).get("DEEPSEEK_API_KEY") or "").strip()
    env_key = (os.environ.get("DEEPSEEK_API_KEY") or "").strip()
    if file_key and env_key and file_key != env_key:
        print(
            "⚠️  DEEPSEEK_API_KEY：当前进程将使用「环境变量」中的值，与 backend/.env 不一致。\n"
            "   若你刚更新了 .env 但仍报 401，请在终端执行: unset DEEPSEEK_API_KEY\n"
            "   然后重启后端，或从 IDE/Cursor 的运行配置里删掉该环境变量。"
        )
