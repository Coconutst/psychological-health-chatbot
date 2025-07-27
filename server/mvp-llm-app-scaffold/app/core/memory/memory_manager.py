from typing import Dict
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage

# 内存会话存储
_sessions: Dict[str, BaseChatMessageHistory] = {}
# ConversationBufferMemory 缓存
_buffer_memories: Dict[str, ConversationBufferMemory] = {}

# 导入文件聊天消息历史类
from langchain_community.chat_message_histories import FileChatMessageHistory  # 导入FileChatMessageHistory，用于文件-based会话历史持久化
# 导入路径处理模块
from pathlib import Path  # 导入Path类，用于处理文件路径
# 导入应用根目录
from app.configs.settings import ROOT  # 导入项目根目录路径
# 导入数据库内存管理
from app.core.memory.database_memory import get_database_session_history

# 设置聊天历史存储目录（移到前面）
history_dir = ROOT / "chat_histories"  # 设置聊天历史存储目录为根目录下的chat_histories
history_dir.mkdir(exist_ok=True)  # 如果目录不存在，则创建它


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """获取基于文件的会话历史（持久化存储）"""
    file_path = str(history_dir / f"{session_id}.json")
    if Path(file_path).exists():
        print(f"--- Loaded existing session from file: {session_id} ---")
    else:
        print(f"--- New session created: {session_id} ---")
    return FileChatMessageHistory(file_path=file_path)


def get_session_history_memory_only(session_id: str) -> BaseChatMessageHistory:
    """获取仅内存存储的会话历史（无持久化）"""
    if session_id not in _sessions:
        _sessions[session_id] = ChatMessageHistory()
        print(f"--- New memory session created: {session_id} ---")
    else:
        print(f"--- Loaded existing memory session: {session_id} ---")
    return _sessions[session_id]


def get_session_history_database(session_id: str, user_id: str | None = None) -> BaseChatMessageHistory:
    """获取基于数据库的会话历史（MySQL持久化存储）"""
    try:
        # 直接传递 user_id，包括 None 值
        return get_database_session_history(session_id, user_id)
    except Exception as e:
        print(f"--- 数据库会话创建失败，回退到文件存储: {e} ---")
        return get_session_history(session_id)

def get_session_history_with_options(session_id: str, use_memory_only: bool = False, 
                                   use_database: bool = True, user_id: str | None = None,
                                   db_session = None) -> BaseChatMessageHistory:
    """根据选项获取会话历史"""
    if use_memory_only:
        return get_session_history_memory_only(session_id)
    elif use_database:
        return get_session_history_database(session_id, user_id)
    else:
        return get_session_history(session_id)


def get_conversation_buffer_memory(session_id: str, user_id: str = None, 
                                 load_historical_context: bool = True) -> ConversationBufferMemory:
    """获取ConversationBufferMemory，包含历史上下文"""
    cache_key = f"{session_id}_{user_id or 'anonymous'}"
    
    if cache_key not in _buffer_memories:
        # 创建新的ConversationBufferMemory
        memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
        
        # 如果需要加载历史上下文
        if load_historical_context and user_id:
            try:
                from app.services.conversation_service import ConversationService
                from app.configs.database import SessionLocal
                
                # 获取数据库会话
                db = SessionLocal()
                conversation_service = ConversationService(db)
                
                # 获取用户的历史消息（最近10条，排除当前对话）
                historical_messages = conversation_service.get_user_historical_messages(
                    user_id=user_id,
                    limit=10,
                    exclude_conversation_id=session_id
                )
                
                # 将历史消息添加到memory中
                for msg in reversed(historical_messages):  # 按时间正序
                    if msg.role == "human":
                        memory.chat_memory.add_user_message(msg.content)
                    elif msg.role == "assistant":
                        memory.chat_memory.add_ai_message(msg.content)
                
                print(f"--- 加载了 {len(historical_messages)} 条历史上下文消息到ConversationBufferMemory ---")
                db.close()
                
            except Exception as e:
                print(f"--- 加载历史上下文失败: {e} ---")
        
        # 加载当前对话的消息
        try:
            current_history = get_session_history_database(session_id, user_id)
            for message in current_history.messages:
                if isinstance(message, HumanMessage):
                    memory.chat_memory.add_user_message(message.content)
                elif isinstance(message, AIMessage):
                    memory.chat_memory.add_ai_message(message.content)
            
            print(f"--- 加载了当前对话的 {len(current_history.messages)} 条消息到ConversationBufferMemory ---")
        except Exception as e:
            print(f"--- 加载当前对话消息失败: {e} ---")
        
        _buffer_memories[cache_key] = memory
        print(f"--- 创建新的ConversationBufferMemory: {session_id} ---")
    else:
        print(f"--- 使用缓存的ConversationBufferMemory: {session_id} ---")
    
    return _buffer_memories[cache_key]


def clear_buffer_memory_cache():
    """清空ConversationBufferMemory缓存"""
    global _buffer_memories
    _buffer_memories.clear()
    print("--- ConversationBufferMemory缓存已清空 ---")

# history_dir 已在文件开头定义
