"""Chat service for managing conversation sessions."""

from datetime import datetime
from typing import AsyncGenerator, Optional
from uuid import uuid4

from app.schemas.chat import (
    ChatSession,
    ChatMessage,
    MessageRole,
    UserProfile,
)
from app.services.llm_service import get_llm_service, LLMService
from app.services.data_fetcher import get_data_fetcher, DataFetcher
from app.services.metrics import get_metrics_calculator, MetricsCalculator


class ChatService:
    """
    Chat service managing conversation sessions and context.
    
    Note: In V1, sessions are stored in memory. 
    For production, use Redis or database.
    """
    
    def __init__(self):
        self._sessions: dict[str, ChatSession] = {}
        self._data_fetcher: DataFetcher = get_data_fetcher()
        self._metrics: MetricsCalculator = get_metrics_calculator()
        self._llm: Optional[LLMService] = get_llm_service()
    
    async def create_session(
        self,
        fund_code: str,
        user_profile: Optional[UserProfile] = None,
    ) -> ChatSession:
        """
        Create a new chat session for a fund.
        
        Args:
            fund_code: Fund code to analyze
            user_profile: Optional user investment profile
            
        Returns:
            New ChatSession with fund context loaded
        """
        # Get fund data
        fund_info = await self._data_fetcher.get_fund_info(fund_code)
        if not fund_info:
            raise ValueError(f"Fund not found: {fund_code}")
        
        # Get NAV history and calculate metrics
        nav_history = await self._data_fetcher.get_nav_history(fund_code, "3y")
        metrics = None
        if nav_history:
            metrics = self._metrics.calculate_metrics(nav_history)
        
        # Get holdings
        holdings = await self._data_fetcher.get_holdings(fund_code)
        
        # Build context
        fund_context = {
            "code": fund_code,
            "name": fund_info.name,
            "type": fund_info.type,
            "company": fund_info.company,
            "manager": fund_info.manager,
            "aum": fund_info.aum,
            "inception_date": str(fund_info.inception_date) if fund_info.inception_date else None,
            "nav": fund_info.nav,
            "management_fee": fund_info.management_fee,
            "custody_fee": fund_info.custody_fee,
        }
        
        if metrics:
            fund_context["metrics"] = {
                "return_1m": metrics.return_1m,
                "return_3m": metrics.return_3m,
                "return_6m": metrics.return_6m,
                "return_1y": metrics.return_1y,
                "return_3y": metrics.return_3y,
                "return_ytd": metrics.return_ytd,
                "return_inception": metrics.return_inception,
                "max_drawdown": metrics.max_drawdown,
                "volatility": metrics.volatility,
                "sharpe_ratio": metrics.sharpe_ratio,
            }
        
        if holdings and holdings.stock_holdings:
            fund_context["top_holdings"] = [
                {"name": h.name, "ratio": h.ratio}
                for h in holdings.stock_holdings[:10]
            ]
        
        # Create session
        session = ChatSession(
            fund_code=fund_code,
            fund_context=fund_context,
            user_profile=user_profile,
        )
        
        self._sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get existing session by ID."""
        return self._sessions.get(session_id)
    
    def update_user_profile(
        self,
        session_id: str,
        user_profile: UserProfile,
    ) -> bool:
        """Update user profile for a session."""
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        session.user_profile = user_profile
        return True
    
    async def send_message(
        self,
        session_id: str,
        message: str,
        user_profile: Optional[UserProfile] = None,
    ) -> str:
        """
        Send a message and get response.
        
        Args:
            session_id: Session ID
            message: User message
            user_profile: Optional user profile (updates session if provided)
            
        Returns:
            Assistant response
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        if not self._llm:
            raise ValueError("LLM service not available. Check API key configuration.")
        
        # Update profile if provided
        if user_profile:
            session.user_profile = user_profile
        
        # Add user message to history
        user_msg = ChatMessage(role=MessageRole.USER, content=message)
        session.messages.append(user_msg)
        
        # Prepare context messages (limit to last 10 for context window)
        context_messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in session.messages[-10:]
        ]
        
        # Get profile dict if available
        profile_dict = None
        if session.user_profile:
            profile_dict = {
                "risk_level": session.user_profile.risk_level.value,
                "purpose": session.user_profile.purpose.value,
                "horizon": session.user_profile.horizon.value,
            }
        
        # Generate response
        response = await self._llm.smart_chat(
            message=message,
            context_messages=context_messages[:-1],  # Exclude current message
            fund_context=session.fund_context,
            user_profile=profile_dict,
            stream=False,
        )
        
        # Add assistant message to history
        assistant_msg = ChatMessage(role=MessageRole.ASSISTANT, content=response)
        session.messages.append(assistant_msg)
        
        return response
    
    async def send_message_stream(
        self,
        session_id: str,
        message: str,
        user_profile: Optional[UserProfile] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Send a message and get streaming response.
        
        Yields:
            String chunks of the response
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        if not self._llm:
            raise ValueError("LLM service not available. Check API key configuration.")
        
        # Update profile if provided
        if user_profile:
            session.user_profile = user_profile
        
        # Add user message to history
        user_msg = ChatMessage(role=MessageRole.USER, content=message)
        session.messages.append(user_msg)
        
        # Prepare context messages
        context_messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in session.messages[-10:]
        ]
        
        # Get profile dict
        profile_dict = None
        if session.user_profile:
            profile_dict = {
                "risk_level": session.user_profile.risk_level.value,
                "purpose": session.user_profile.purpose.value,
                "horizon": session.user_profile.horizon.value,
            }
        
        # Generate streaming response
        full_response = ""
        async for chunk in await self._llm.smart_chat(
            message=message,
            context_messages=context_messages[:-1],
            fund_context=session.fund_context,
            user_profile=profile_dict,
            stream=True,
        ):
            full_response += chunk
            yield chunk
        
        # Add complete response to history
        assistant_msg = ChatMessage(role=MessageRole.ASSISTANT, content=full_response)
        session.messages.append(assistant_msg)
    
    def get_messages(self, session_id: str) -> list[ChatMessage]:
        """Get all messages for a session."""
        session = self._sessions.get(session_id)
        if not session:
            return []
        return session.messages
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False


# Singleton instance
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get singleton chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
