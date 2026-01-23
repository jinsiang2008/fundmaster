"""Chat-related Pydantic models."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """User risk tolerance level."""
    CONSERVATIVE = "conservative"  # 保守型
    STABLE = "stable"              # 稳健型
    BALANCED = "balanced"          # 平衡型
    AGGRESSIVE = "aggressive"      # 进取型
    RADICAL = "radical"            # 激进型


class InvestmentPurpose(str, Enum):
    """Investment purpose."""
    SAVINGS = "savings"        # 闲钱理财
    RETIREMENT = "retirement"  # 养老储备
    GROWTH = "growth"          # 资产增值
    EDUCATION = "education"    # 教育金
    OTHER = "other"            # 其他


class InvestmentHorizon(str, Enum):
    """Investment time horizon."""
    SHORT = "short"    # 短期 (<1年)
    MEDIUM = "medium"  # 中期 (1-3年)
    LONG = "long"      # 长期 (>3年)


class UserProfile(BaseModel):
    """User investment profile."""
    risk_level: RiskLevel = Field(default=RiskLevel.BALANCED, description="风险偏好")
    purpose: InvestmentPurpose = Field(default=InvestmentPurpose.GROWTH, description="投资目的")
    horizon: InvestmentHorizon = Field(default=InvestmentHorizon.MEDIUM, description="投资期限")
    
    class Config:
        json_schema_extra = {
            "example": {
                "risk_level": "stable",
                "purpose": "savings",
                "horizon": "short"
            }
        }


class MessageRole(str, Enum):
    """Chat message role."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Single chat message."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatSession(BaseModel):
    """Chat session with context."""
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    fund_code: str = Field(..., description="当前分析的基金代码")
    fund_context: dict = Field(default_factory=dict, description="基金数据上下文")
    user_profile: Optional[UserProfile] = Field(default=None, description="用户画像")
    messages: list[ChatMessage] = Field(default_factory=list, description="对话历史")
    created_at: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Chat request model."""
    session_id: Optional[str] = Field(default=None, description="会话ID，首次对话可不传")
    fund_code: Optional[str] = Field(default=None, description="基金代码，创建新会话时必传")
    message: str = Field(..., min_length=1, description="用户消息")
    user_profile: Optional[UserProfile] = Field(default=None, description="用户画像")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fund_code": "110011",
                "message": "我是稳健型投资者，这只基金适合我吗？",
                "user_profile": {
                    "risk_level": "stable",
                    "purpose": "savings",
                    "horizon": "medium"
                }
            }
        }


class ChatResponse(BaseModel):
    """Chat response model."""
    session_id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)


class CreateSessionRequest(BaseModel):
    """Request to create a new chat session."""
    fund_code: str = Field(..., description="基金代码")


class CreateSessionResponse(BaseModel):
    """Response for session creation."""
    session_id: str
    fund_code: str
    fund_name: str
    created_at: datetime
