"""聊天服务模块"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, AsyncGenerator
from sqlalchemy.orm import Session

from ..models import User, Conversation, Message
from ..core.database import get_db
from .langchain_service import langchain_service
from ..utils.datetime_utils import beijing_now_naive

logger = logging.getLogger(__name__)


class ChatService:
    """聊天服务类"""
    
    def __init__(self):
        self.active_sessions: Dict[str, dict] = {}
    
    async def start_chat_session(self, user_id: int, db: Session) -> str:
        """开始聊天会话"""
        try:
            # 创建新的对话记录
            conversation = Conversation(
                user_id=user_id,
                title="新的心理咨询对话",
                created_at=beijing_now_naive()
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            
            # 生成会话ID
            session_id = str(uuid.uuid4())
            
            # 存储会话信息
            self.active_sessions[session_id] = {
                "user_id": user_id,
                "conversation_id": conversation.conversation_id,  # 使用字符串conversation_id
                "created_at": beijing_now_naive(),
                "message_count": 0
            }
            
            logger.info(f"用户 {user_id} 开始新的聊天会话: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"开始聊天会话错误: {e}")
            db.rollback()
            raise
    
    async def send_message_stream(
        self, 
        session_id: str, 
        message: str, 
        db: Session
    ) -> AsyncGenerator[str, None]:
        """发送消息并流式返回响应"""
        try:
            # 验证会话
            if session_id not in self.active_sessions:
                yield "错误：无效的会话ID"
                return
            
            session_info = self.active_sessions[session_id]
            user_id = session_info["user_id"]
            conversation_id = session_info["conversation_id"]
            
            # 保存用户消息
            user_message = Message(
                conversation_id=conversation_id,
                content=message,
                role="user",
                created_at=beijing_now_naive()
            )
            db.add(user_message)
            db.commit()
            
            # 流式获取AI响应
            ai_response = ""
            async for chunk in langchain_service.chat_stream(message, str(user_id)):
                ai_response += chunk
                yield chunk
            
            # 保存AI响应
            ai_message = Message(
                conversation_id=conversation_id,
                content=ai_response,
                role="assistant",
                created_at=beijing_now_naive()
            )
            db.add(ai_message)
            
            # 更新对话标题（如果是第一条消息）
            if session_info["message_count"] == 0:
                conversation = db.query(Conversation).filter(
                    Conversation.conversation_id == conversation_id
                ).first()
                if conversation:
                    conversation.title = message[:50] + "..." if len(message) > 50 else message
            
            # 更新会话信息
            session_info["message_count"] += 2  # 用户消息 + AI响应
            session_info["last_activity"] = beijing_now_naive()
            
            db.commit()
            
        except Exception as e:
            logger.error(f"发送消息错误: {e}")
            db.rollback()
            yield f"错误：{str(e)}"
    
    async def send_message(
        self, 
        session_id: str, 
        message: str, 
        db: Session
    ) -> Dict[str, any]:
        """发送消息并返回完整响应"""
        try:
            # 验证会话
            if session_id not in self.active_sessions:
                return {"error": "无效的会话ID"}
            
            session_info = self.active_sessions[session_id]
            user_id = session_info["user_id"]
            conversation_id = session_info["conversation_id"]
            
            # 保存用户消息
            user_message = Message(
                conversation_id=conversation_id,
                content=message,
                role="user",
                created_at=beijing_now_naive()
            )
            db.add(user_message)
            db.commit()
            db.refresh(user_message)
            
            # 获取AI响应
            ai_response = await langchain_service.chat(message, str(user_id))
            
            # 保存AI响应
            ai_message = Message(
                conversation_id=conversation_id,
                content=ai_response,
                role="assistant",
                created_at=beijing_now_naive()
            )
            db.add(ai_message)
            db.commit()
            db.refresh(ai_message)
            
            # 更新对话标题（如果是第一条消息）
            if session_info["message_count"] == 0:
                conversation = db.query(Conversation).filter(
                    Conversation.conversation_id == conversation_id
                ).first()
                if conversation:
                    conversation.title = message[:50] + "..." if len(message) > 50 else message
                    db.commit()
            
            # 更新会话信息
            session_info["message_count"] += 2
            session_info["last_activity"] = beijing_now_naive()
            
            return {
                "session_id": session_id,
                "user_message": {
                    "id": user_message.id,
                    "content": user_message.content,
                    "role": user_message.role,
                    "created_at": user_message.created_at.isoformat()
                },
                "ai_message": {
                    "id": ai_message.id,
                    "content": ai_message.content,
                    "role": ai_message.role,
                    "created_at": ai_message.created_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"发送消息错误: {e}")
            db.rollback()
            return {"error": str(e)}
    
    def get_conversation_history(
        self, 
        session_id: str, 
        db: Session,
        limit: int = 50
    ) -> Dict[str, any]:
        """获取对话历史"""
        try:
            if session_id not in self.active_sessions:
                return {"error": "无效的会话ID"}
            
            session_info = self.active_sessions[session_id]
            conversation_id = session_info["conversation_id"]
            
            # 查询消息历史
            messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.desc()).limit(limit).all()
            
            # 反转消息顺序（最新的在后面）
            messages.reverse()
            
            return {
                "session_id": session_id,
                "conversation_id": conversation_id,
                "messages": [
                    {
                        "id": msg.id,
                        "content": msg.content,
                        "role": msg.role,
                        "created_at": msg.created_at.isoformat()
                    }
                    for msg in messages
                ]
            }
            
        except Exception as e:
            logger.error(f"获取对话历史错误: {e}")
            return {"error": str(e)}
    
    def end_chat_session(self, session_id: str) -> bool:
        """结束聊天会话"""
        try:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                logger.info(f"聊天会话已结束: {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"结束聊天会话错误: {e}")
            return False
    
    def get_user_conversations(
        self, 
        user_id: int, 
        db: Session,
        limit: int = 20
    ) -> List[Dict[str, any]]:
        """获取用户的对话列表"""
        try:
            conversations = db.query(Conversation).filter(
                Conversation.user_id == user_id
            ).order_by(Conversation.created_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat() if conv.updated_at else None
                }
                for conv in conversations
            ]
            
        except Exception as e:
            logger.error(f"获取用户对话列表错误: {e}")
            return []
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, any]]:
        """获取会话信息"""
        return self.active_sessions.get(session_id)
    
    def cleanup_inactive_sessions(self, max_inactive_hours: int = 24):
        """清理不活跃的会话"""
        try:
            current_time = beijing_now_naive()
            inactive_sessions = []
            
            for session_id, session_info in self.active_sessions.items():
                last_activity = session_info.get("last_activity", session_info["created_at"])
                inactive_hours = (current_time - last_activity).total_seconds() / 3600
                
                if inactive_hours > max_inactive_hours:
                    inactive_sessions.append(session_id)
            
            for session_id in inactive_sessions:
                del self.active_sessions[session_id]
                logger.info(f"清理不活跃会话: {session_id}")
            
            return len(inactive_sessions)
            
        except Exception as e:
            logger.error(f"清理不活跃会话错误: {e}")
            return 0


# 全局聊天服务实例
chat_service = ChatService()