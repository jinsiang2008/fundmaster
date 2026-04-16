"""Chat API endpoints for personalized conversation."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.chat import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    UserProfile,
)
from app.services.chat_service import get_chat_service

router = APIRouter()


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_chat_session(request: CreateSessionRequest):
    """
    创建新的对话会话。

    会自动加载基金数据作为对话上下文。
    """
    service = get_chat_service()

    try:
        session = await service.create_session(request.fund_code)

        return CreateSessionResponse(
            session_id=session.session_id,
            fund_code=session.fund_code,
            fund_name=session.fund_context.get("name", ""),
            created_at=session.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"建立会话失败: {type(e).__name__}: {e}",
        ) from e


@router.post("/messages", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    发送消息并获取回复。

    如果没有提供 session_id，会自动创建新会话。
    """
    service = get_chat_service()

    # Create session if needed
    session_id = request.session_id
    if not session_id:
        if not request.fund_code:
            raise HTTPException(status_code=400, detail="首次对话必须提供 fund_code")
        try:
            session = await service.create_session(
                request.fund_code,
                request.user_profile,
            )
            session_id = session.session_id
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"建立会话失败: {type(e).__name__}: {e}",
            ) from e

    # Send message
    try:
        response = await service.send_message(
            session_id=session_id,
            message=request.message,
            user_profile=request.user_profile,
        )

        return ChatResponse(
            session_id=session_id,
            message=response,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/messages/stream")
async def send_message_stream(request: ChatRequest):
    """
    发送消息并获取流式回复（SSE）。

    用于实现打字机效果。
    """
    service = get_chat_service()

    # Create session if needed
    session_id = request.session_id
    if not session_id:
        if not request.fund_code:
            raise HTTPException(status_code=400, detail="首次对话必须提供 fund_code")
        try:
            session = await service.create_session(
                request.fund_code,
                request.user_profile,
            )
            session_id = session.session_id
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except Exception as e:
            # 网络/解析等异常不再变成无信息的 500
            raise HTTPException(
                status_code=502,
                detail=f"建立对话会话失败（基金数据或网络异常）: {type(e).__name__}: {e}",
            ) from e

    async def generate():
        try:
            async for chunk in service.send_message_stream(
                session_id=session_id,
                message=request.message,
                user_profile=request.user_profile,
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except ValueError as e:
            yield f"data: [ERROR] {str(e)}\n\n"
        except Exception as e:
            # LLM 网络错误、鉴权失败等
            yield f"data: [ERROR] {type(e).__name__}: {str(e)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Session-ID": session_id,
        },
    )


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessage])
async def get_session_messages(session_id: str):
    """
    获取会话的历史消息。
    """
    service = get_chat_service()
    messages = service.get_messages(session_id)

    if not messages:
        # Check if session exists
        session = service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")

    return messages


@router.put("/sessions/{session_id}/profile")
async def update_user_profile(session_id: str, profile: UserProfile):
    """
    更新会话的用户画像。
    """
    service = get_chat_service()
    success = service.update_user_profile(session_id, profile)

    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")

    return {"status": "updated"}


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    删除会话。
    """
    service = get_chat_service()
    success = service.delete_session(session_id)

    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")

    return {"status": "deleted"}
