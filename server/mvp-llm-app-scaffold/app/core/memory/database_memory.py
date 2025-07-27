# 基于数据库的聊天消息历史管理
from typing import List, Optional
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from sqlalchemy.orm import Session
from app.models.conversation import Conversation, Message
from app.services.conversation_service import ConversationService
from app.configs.database import SessionLocal
import json

class DatabaseChatMessageHistory(BaseChatMessageHistory):
    """基于数据库的聊天消息历史类"""
    
    def __init__(self, conversation_id: str, user_id: str = None):
        self.conversation_id = conversation_id
        self.user_id = user_id
        self._db: Optional[Session] = None
        self._service: Optional[ConversationService] = None
        self._ensure_conversation_exists()
    
    @property
    def db(self) -> Session:
        """获取数据库会话"""
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    @property
    def service(self) -> ConversationService:
        """获取对话服务"""
        if self._service is None:
            self._service = ConversationService(self.db)
        return self._service
    
    def _ensure_conversation_exists(self):
        """确保对话存在"""
        try:
            # 延迟初始化，确保数据库连接可用
            if self._db is None:
                self._db = SessionLocal()
            if self._service is None:
                self._service = ConversationService(self._db)
                
            conversation = self.service.get_conversation(self.conversation_id)
            if not conversation:
                # 创建新对话
                print(f"创建新对话: {self.conversation_id}, 用户ID: {self.user_id}")
                self.service.create_conversation(
                    user_id=self.user_id,
                    conversation_id=self.conversation_id
                )
                print(f"对话创建成功: {self.conversation_id}")
            else:
                print(f"对话已存在: {self.conversation_id}")
        except Exception as e:
            print(f"创建对话时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _message_to_langchain(self, message: Message) -> BaseMessage:
        """将数据库消息转换为LangChain消息"""
        if message.role == "user":
            return HumanMessage(content=message.content)
        elif message.role == "assistant":
            return AIMessage(content=message.content)
        elif message.role == "system":
            return SystemMessage(content=message.content)
        else:
            # 默认作为人类消息处理
            return HumanMessage(content=message.content)
    
    def _langchain_to_message_data(self, message: BaseMessage) -> dict:
        """将LangChain消息转换为数据库消息数据"""
        if isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, AIMessage):
            role = "assistant"
        elif isinstance(message, SystemMessage):
            role = "system"
        else:
            role = "user"  # 默认角色
        
        return {
            "role": role,
            "content": message.content
        }
    
    @property
    def messages(self) -> List[BaseMessage]:
        """获取所有消息"""
        try:
            db_messages = self.service.get_conversation_messages(self.conversation_id)
            return [self._message_to_langchain(msg) for msg in db_messages]
        except Exception as e:
            print(f"获取消息时出错: {e}")
            return []
    
    def add_message(self, message: BaseMessage) -> None:
        """添加消息"""
        try:
            message_data = self._langchain_to_message_data(message)
            self.service.add_message(
                conversation_id=self.conversation_id,
                role=message_data["role"],
                content=message_data["content"]
            )
        except Exception as e:
            print(f"添加消息时出错: {e}")
    
    def clear(self) -> None:
        """清空消息历史（软删除对话）"""
        try:
            self.service.delete_conversation(self.conversation_id)
        except Exception as e:
            print(f"清空消息时出错: {e}")
    
    def __del__(self):
        """析构函数，关闭数据库连接"""
        if self._db:
            self._db.close()

# 全局会话存储（用于缓存）
_database_sessions = {}

def get_database_session_history(session_id: str, user_id: str = None) -> DatabaseChatMessageHistory:
    """获取基于数据库的会话历史"""
    cache_key = f"{session_id}_{user_id or 'anonymous'}"
    
    if cache_key not in _database_sessions:
        _database_sessions[cache_key] = DatabaseChatMessageHistory(
            conversation_id=session_id,
            user_id=user_id
        )
        print(f"--- 创建新的数据库会话: {session_id} ---")
    else:
        print(f"--- 加载已存在的数据库会话: {session_id} ---")
    
    return _database_sessions[cache_key]

def clear_session_cache():
    """清空会话缓存"""
    global _database_sessions
    for session in _database_sessions.values():
        if hasattr(session, '__del__'):
            session.__del__()
    _database_sessions.clear()