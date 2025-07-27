# 对话服务层
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.configs.database import get_db
from datetime import datetime
import json
import uuid
import logging

logger = logging.getLogger(__name__)

class ConversationService:
    """对话服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_user(self, user_id: Optional[str], username: Optional[str] = None, email: Optional[str] = None) -> User:
        """获取或创建用户"""
        if user_id:
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if user:
                return user
        
        # 创建新用户
        user = User(
            user_id=user_id or str(uuid.uuid4()),
            username=username,
            email=email
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def create_conversation(self, user_id: Optional[str] = None, title: Optional[str] = None, conversation_id: Optional[str] = None) -> Conversation:
        """创建新对话"""
        print(f"[ConversationService] create_conversation 被调用，参数: user_id={user_id}, title={title}, conversation_id={conversation_id}")
        
        if user_id:
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if not user:
                print(f"[ConversationService] 错误：用户ID {user_id} 不存在")
                raise ValueError(f"用户ID {user_id} 不存在")
            print(f"[ConversationService] 找到用户: id={user.id}, user_id={user.user_id}, username={user.username}")
            conversation_user_id = user.user_id  # 使用字符串 user_id
        else:
            print(f"[ConversationService] 警告：user_id 为 None，将创建匿名对话")
            conversation_user_id = None
        
        conversation = Conversation(
            conversation_id=conversation_id or str(uuid.uuid4()),
            user_id=conversation_user_id,
            title=title or "新对话"
        )
        print(f"[ConversationService] 创建对话对象: conversation_id={conversation.conversation_id}, user_id={conversation.user_id}, title={conversation.title}")
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        print(f"[ConversationService] 对话已保存到数据库: id={conversation.id}, user_id={conversation.user_id}")
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """根据conversation_id获取对话"""
        return self.db.query(Conversation).filter(
            Conversation.conversation_id == conversation_id,
            Conversation.is_active == "true"
        ).first()
    
    def get_conversation_with_messages(self, conversation_id: str) -> Optional[Conversation]:
        """获取对话及其所有消息"""
        return self.db.query(Conversation).filter(
            Conversation.conversation_id == conversation_id,
            Conversation.is_active == "true"
        ).first()
    
    def add_message(self, conversation_id: str, role: str, content: str, 
                   model_name: Optional[str] = None, temperature: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> Message:
        """添加消息到对话"""
        print(f"[ConversationService] add_message 被调用，conversation_id={conversation_id}, role={role}")
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            print(f"[ConversationService] 错误：对话 {conversation_id} 不存在")
            raise ValueError(f"对话 {conversation_id} 不存在")
        
        print(f"[ConversationService] 找到对话: id={conversation.id}, conversation_id={conversation.conversation_id}")
        
        message = Message(
            message_id=str(uuid.uuid4()),
            conversation_id=conversation.conversation_id,  # 使用字符串conversation_id
            role=role,
            content=content,
            model_name=model_name,
            temperature=temperature,
            metadata=json.dumps(metadata) if metadata else None
        )
        
        print(f"[ConversationService] 创建消息对象: message_id={message.message_id}, conversation_id={message.conversation_id}")
        
        self.db.add(message)
        
        # 更新对话的消息计数和最后消息时间
        # 使用 or 运算符获取当前消息计数，如果为 None 则默认为 0，然后加 1
        current_count = conversation.message_count if conversation.message_count is not None else 0
        # 使用 setattr 来避免类型检查器的警告
        setattr(conversation, 'message_count', current_count + 1)
        setattr(conversation, 'last_message_at', datetime.now())
        
        # 如果是第一条用户消息且没有标题，使用消息内容作为标题
        if role == "user" and conversation.message_count == 1 and (not conversation.title or conversation.title == "新对话"):
            setattr(conversation, 'title', content[:50] + "..." if len(content) > 50 else content)
        
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_conversation_messages(self, conversation_id: str, limit: int = 50, offset: int = 0) -> List[Message]:
        """获取对话的消息列表"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        return self.db.query(Message).filter(
            Message.conversation_id == conversation.conversation_id
        ).order_by(Message.created_at).offset(offset).limit(limit).all()
    
    def get_user_conversations(self, user_id: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[Conversation]:
        """获取用户的对话列表"""
        if user_id is None:
            # 查询user_id为None的对话（匿名用户对话）
            return self.db.query(Conversation).filter(
                Conversation.user_id == None,
                Conversation.is_active == "true"
            ).order_by(desc(Conversation.last_message_at)).offset(offset).limit(limit).all()
        
        # 直接使用传入的user_id（字符串类型）
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.is_active == "true"
        ).order_by(desc(Conversation.last_message_at)).offset(offset).limit(limit).all()
    
    def get_all_conversations(self, limit: int = 20, offset: int = 0) -> List[Conversation]:
        """获取所有对话列表（用于匿名用户）"""
        return self.db.query(Conversation).filter(
            Conversation.is_active == "true"
        ).order_by(desc(Conversation.last_message_at)).offset(offset).limit(limit).all()
    
    def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """更新对话标题"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        setattr(conversation, 'title', title)
        setattr(conversation, 'updated_at', datetime.now())
        self.db.commit()
        return True
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """删除对话（软删除）"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        setattr(conversation, 'is_active', "false")
        setattr(conversation, 'updated_at', datetime.now())
        self.db.commit()
        return True
    
    def get_conversation_stats(self, conversation_id: str) -> Dict[str, Any]:
        """获取对话统计信息"""
        conversation = self.get_conversation_with_messages(conversation_id)
        if not conversation:
            return {}
        
        total_messages = len(conversation.messages)
        user_messages = len([m for m in conversation.messages if m.role == "user"])
        assistant_messages = len([m for m in conversation.messages if m.role == "assistant"])
        
        return {
            "conversation_id": str(conversation.conversation_id),
            "title": str(conversation.title) if conversation.title else None,
            "total_messages": total_messages,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "last_message_at": conversation.last_message_at.isoformat() if conversation.last_message_at else None
        }
    
    def update_user_emotion_profile(self, user_id: str, emotion: str, confidence: float = 0.5, 
                                   emotion_context: Optional[Dict[str, Any]] = None) -> bool:
        """更新用户情绪画像"""
        try:
            logger.info(f"[ConversationService] 开始更新用户情绪画像: user_id={user_id}, emotion={emotion}, confidence={confidence}")
            
            # 获取用户
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if not user:
                logger.warning(f"[ConversationService] 用户不存在: {user_id}")
                return False
            
            # 更新当前情绪状态
            user.current_emotion = emotion
            user.emotion_updated_at = datetime.now()
            
            # 更新情绪历史记录
            emotion_record = {
                "emotion": emotion,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "context": emotion_context or {}
            }
            
            # 解析现有的情绪历史
            try:
                if user.emotion_history:
                    emotion_history = json.loads(user.emotion_history)
                    if not isinstance(emotion_history, list):
                        emotion_history = []
                else:
                    emotion_history = []
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"[ConversationService] 用户 {user_id} 的情绪历史数据格式错误，重新初始化")
                emotion_history = []
            
            # 添加新的情绪记录
            emotion_history.append(emotion_record)
            
            # 保持最近50条记录
            if len(emotion_history) > 50:
                emotion_history = emotion_history[-50:]
            
            # 更新情绪历史
            user.emotion_history = json.dumps(emotion_history, ensure_ascii=False)
            
            # 提交更改
            self.db.commit()
            
            logger.info(f"[ConversationService] 用户情绪画像更新成功: user_id={user_id}, current_emotion={emotion}")
            return True
            
        except Exception as e:
            logger.error(f"[ConversationService] 更新用户情绪画像失败: user_id={user_id}, error={e}")
            self.db.rollback()
            return False
    
    def get_user_emotion_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户情绪画像"""
        try:
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return None
            
            # 解析情绪历史
            emotion_history = []
            if user.emotion_history:
                try:
                    emotion_history = json.loads(user.emotion_history)
                    if not isinstance(emotion_history, list):
                        emotion_history = []
                except (json.JSONDecodeError, TypeError):
                    emotion_history = []
            
            return {
                "user_id": user.user_id,
                "current_emotion": user.current_emotion,
                "emotion_updated_at": user.emotion_updated_at.isoformat() if user.emotion_updated_at else None,
                "emotion_history": emotion_history,
                "emotion_history_count": len(emotion_history)
            }
            
        except Exception as e:
            logger.error(f"[ConversationService] 获取用户情绪画像失败: user_id={user_id}, error={e}")
            return None
    
    def get_user_historical_messages(self, user_id: str, limit: int = 20, exclude_conversation_id: Optional[str] = None) -> List[Message]:
        """获取用户的历史消息，用于跨对话上下文记忆
        
        Args:
            user_id: 用户ID
            limit: 返回消息数量限制
            exclude_conversation_id: 排除的对话ID（通常是当前对话）
        
        Returns:
            按时间倒序排列的历史消息列表
        """
        try:
            logger.info(f"[ConversationService] 获取用户历史消息: user_id={user_id}, limit={limit}, exclude_conversation_id={exclude_conversation_id}")
            
            # 构建查询
            query = self.db.query(Message).join(Conversation).filter(
                Conversation.user_id == user_id,
                Conversation.is_active == "true"
            )
            
            # 排除当前对话
            if exclude_conversation_id:
                query = query.filter(Message.conversation_id != exclude_conversation_id)
            
            # 按时间倒序排列，获取最近的消息
            messages = query.order_by(desc(Message.created_at)).limit(limit).all()
            
            logger.info(f"[ConversationService] 获取到 {len(messages)} 条历史消息")
            return messages
            
        except Exception as e:
            logger.error(f"[ConversationService] 获取用户历史消息失败: user_id={user_id}, error={e}")
            return []

# 便捷函数
def get_conversation_service(db: Session = None) -> ConversationService:
    """获取对话服务实例"""
    if db is None:
        db = next(get_db())
    return ConversationService(db)