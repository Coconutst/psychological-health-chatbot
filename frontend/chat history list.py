# 后端 FastAPI 片段：历史对话列表模块
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from database import get_db
# from models import Conversation, User
#
# router = APIRouter(prefix="/api/conversations")
#
# @router.get("/")
# def list_conversations(
#     limit: int = 20,
#     keyword: str = None,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """按时间倒序返回当前用户的会话列表，支持关键词过滤"""
#     q = db.query(Conversation)\
#           .filter(Conversation.user_id == current_user.id, Conversation.is_active == True)
#     if keyword:
#         q = q.filter(Conversation.title.contains(keyword))
#     return q.order_by(Conversation.updated_at.desc()).limit(limit).all()
#
# @router.delete("/{conversation_id}")
# def delete_conversation(
#     conversation_id: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """软删除指定会话"""
#     c = db.query(Conversation)\
#           .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)\
#           .first()
#     if not c:
#         raise HTTPException(404, "会话不存在")
#     c.is_active = False
#     db.commit()
#     return {"msg": "已删除"}

# ↓ 追加缓存：将结果写入 Redis，10 分钟内有效
#await redis.setex(f"conv:user:{user_id}", 600, json.dumps([c.to_dict() for c in conversations]))

#补充
# def search_conversations(user_id: str, keyword: str, limit: int = 20):
#     """根据关键词模糊搜索会话标题"""
#     return db.query(Conversation)\
#         .filter(Conversation.user_id == user_id,
#                 Conversation.title.contains(keyword),
#                 Conversation.is_active == True)\
#         .order_by(Conversation.last_message_at.desc())\
#         .limit(limit)\
#         .all()