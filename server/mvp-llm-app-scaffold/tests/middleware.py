from fastapi import Request, Depends, HTTPException
from jose import JWTError


async def session_middleware(
        request: Request,
        session_manager: SessionManager = Depends(SessionManager)
):
    """会话验证中间件"""
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="未找到会话")

    session_data = session_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="会话已过期")

    # 更新最后活跃时间
    session_manager.update_session(session_id)

    request.state.session = session_data
    return session_data