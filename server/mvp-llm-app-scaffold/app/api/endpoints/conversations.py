# 导入必要的模块
import os
import json
from typing import List, Optional
from datetime import datetime
from pathlib import Path

# 导入FastAPI相关模块
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# 导入会话历史管理模块
from app.core.memory.memory_manager import get_session_history
from app.configs.settings import get_settings
# 导入数据库相关模块
from app.configs.database import get_db
from app.services.conversation_service import ConversationService
# 导入认证相关模块
from app.api.endpoints.auth import get_current_user
from app.models.user import User
from app.models.conversation import Conversation, Message

# 创建API路由器实例
router = APIRouter()

# 获取设置
settings = get_settings()

# 会话历史文件目录
history_dir = Path("./data/chat_history")
history_dir.mkdir(parents=True, exist_ok=True)

# 定义会话信息模型
class ConversationInfo(BaseModel):
    id: int  # 对话的主键ID
    conversation_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int

# 定义更新会话标题请求模型
class UpdateTitleRequest(BaseModel):
    title: str

# 定义消息响应模型
class MessageInfo(BaseModel):
    id: int
    message_id: str
    role: str
    content: str
    created_at: str
    token_count: Optional[int] = None
    model_name: Optional[str] = None
    temperature: Optional[str] = None
    feedback: Optional[int] = None

# 定义反馈更新请求模型
class FeedbackUpdateRequest(BaseModel):
    feedback: int = Field(..., ge=-1, le=1, description="反馈值：-1(不好)，0(默认)，1(很好)")

def get_conversation_metadata(conversation_id: str) -> Optional[dict]:
    """获取会话元数据"""
    file_path = history_dir / f"{conversation_id}.json"
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 计算消息数量
        message_count = len(data.get('messages', []))
        
        # 获取创建和更新时间
        created_at = data.get('created_at', datetime.now().isoformat())
        updated_at = data.get('updated_at', datetime.now().isoformat())
        
        # 生成标题（使用第一条用户消息的前30个字符）
        title = "新对话"
        messages = data.get('messages', [])
        for msg in messages:
            if msg.get('type') == 'human':
                content = msg.get('data', {}).get('content', '')
                if content:
                    title = content[:30] + ('...' if len(content) > 30 else '')
                    break
        
        return {
            'id': -1,  # 文件系统数据没有主键ID，使用-1表示
            'conversation_id': conversation_id,
            'title': title,
            'created_at': created_at,
            'updated_at': updated_at,
            'message_count': message_count
        }
    except Exception as e:
        print(f"Error reading conversation metadata for {conversation_id}: {e}")
        return None

@router.get("/", response_model=List[ConversationInfo])
def get_conversations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取当前用户的会话列表"""
    try:
        # 从数据库获取当前用户的对话
        service = ConversationService(db)
        conversations = service.get_user_conversations(str(current_user.user_id))

        
        if conversations:
            return [
                ConversationInfo(
                    id=conv.id,  # 添加主键ID
                    conversation_id=str(conv.conversation_id),
                    title=str(conv.title),
                    created_at=conv.created_at.isoformat(),
                    updated_at=conv.updated_at.isoformat(),
                    message_count=len(conv.messages)
                )
                for conv in conversations
            ]
        else:
            # 回退到文件系统
            conversations = []
            
            # 遍历历史文件目录
            for file_path in history_dir.glob("*.json"):
                conversation_id = file_path.stem
                metadata = get_conversation_metadata(conversation_id)
                if metadata:
                    conversations.append(ConversationInfo(**metadata))
            
            # 按更新时间倒序排列
            conversations.sort(key=lambda x: x.updated_at, reverse=True)
            return conversations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话列表失败: {str(e)}")

@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """删除指定会话"""
    try:
        # 验证对话是否属于当前用户
        service = ConversationService(db)
        conversation = service.get_conversation(conversation_id)
        if conversation is not None and str(conversation.user_id) != str(current_user.user_id):
            raise HTTPException(status_code=403, detail="无权限删除此对话")
        
        # 删除对话
        success = service.delete_conversation(conversation_id)
        
        if success:
            return {"message": "会话删除成功", "conversation_id": conversation_id}
        else:
            # 回退到文件删除
            file_path = history_dir / f"{conversation_id}.json"
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="会话不存在")
            
            file_path.unlink()  # 删除文件
            return {"message": "会话删除成功", "conversation_id": conversation_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除会话失败: {str(e)}")

@router.patch("/{conversation_id}")
def update_conversation_title(conversation_id: str, request: UpdateTitleRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """更新会话标题"""
    try:
        # 验证对话是否属于当前用户
        service = ConversationService(db)
        conversation = service.get_conversation(conversation_id)
        if conversation is not None and str(conversation.user_id) != str(current_user.user_id):
            raise HTTPException(status_code=403, detail="无权限修改此对话")
        
        # 更新对话标题
        success = service.update_conversation_title(conversation_id, request.title)
        
        if success:
            return {
                "message": "标题更新成功",
                "conversation_id": conversation_id,
                "title": request.title
            }
        else:
            # 回退到文件更新
            file_path = history_dir / f"{conversation_id}.json"
            
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="会话不存在")
            
            # 读取现有数据
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 更新标题和时间戳
            data['title'] = request.title
            data['updated_at'] = datetime.now().isoformat()
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return {
                "message": "标题更新成功",
                "conversation_id": conversation_id,
                "title": request.title
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新标题失败: {str(e)}")

@router.get("/{conversation_id}/messages", response_model=List[MessageInfo])
def get_conversation_messages(conversation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """根据会话conversation_id获取消息列表"""
    try:
        service = ConversationService(db)
        
        # 根据conversation_id UUID获取对话
        conversation = db.query(Conversation).filter(Conversation.conversation_id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 验证对话是否属于当前用户
        if str(conversation.user_id) != str(current_user.user_id):
            raise HTTPException(status_code=403, detail="无权限访问此对话")
        
        # 获取消息列表
        messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
        
        return [
            MessageInfo(
                id=msg.id,
                message_id=msg.message_id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at.isoformat(),
                token_count=getattr(msg, 'token_count', None),
                model_name=msg.model_name,
                temperature=msg.temperature,
                feedback=getattr(msg, 'feedback', 0)
            )
            for msg in messages
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消息列表失败: {str(e)}")

@router.patch("/messages/{message_id}/feedback")
def update_message_feedback(message_id: str, request: FeedbackUpdateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """更新消息反馈"""
    try:
        # 根据message_id查找消息
        message = db.query(Message).filter(Message.message_id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="消息不存在")
        
        # 验证消息所属的对话是否属于当前用户
        conversation = db.query(Conversation).filter(Conversation.conversation_id == message.conversation_id).first()
        if not conversation or str(conversation.user_id) != str(current_user.user_id):
            raise HTTPException(status_code=403, detail="无权限修改此消息的反馈")
        
        # 更新反馈值
        message.feedback = request.feedback
        db.commit()
        
        return {
            "message": "反馈更新成功",
            "message_id": message_id,
            "feedback": request.feedback
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新反馈失败: {str(e)}")