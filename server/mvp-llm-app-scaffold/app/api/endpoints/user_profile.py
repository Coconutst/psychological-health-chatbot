# 用户画像API端点
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.configs.database import get_db
from app.models.user import User
from app.services.conversation_service import ConversationService
from app.api.endpoints.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/emotion-profile")
async def get_user_emotion_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取当前用户的情绪画像"""
    try:
        logger.info(f"[UserProfile] 获取用户情绪画像: user_id={current_user.user_id}")
        
        conversation_service = ConversationService(db)
        emotion_profile = conversation_service.get_user_emotion_profile(str(current_user.user_id))
        
        if not emotion_profile:
            return {
                "user_id": str(current_user.user_id),
                "current_emotion": None,
                "emotion_updated_at": None,
                "emotion_history": [],
                "emotion_history_count": 0,
                "message": "用户情绪画像暂无数据"
            }
        
        logger.info(f"[UserProfile] 情绪画像获取成功: user_id={current_user.user_id}, current_emotion={emotion_profile.get('current_emotion')}")
        return emotion_profile
        
    except Exception as e:
        logger.error(f"[UserProfile] 获取用户情绪画像失败: user_id={current_user.user_id}, error={e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取用户情绪画像失败: {str(e)}"
        )

@router.get("/emotion-stats")
async def get_user_emotion_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取用户情绪统计信息"""
    try:
        logger.info(f"[UserProfile] 获取用户情绪统计: user_id={current_user.user_id}")
        
        conversation_service = ConversationService(db)
        emotion_profile = conversation_service.get_user_emotion_profile(str(current_user.user_id))
        
        if not emotion_profile or not emotion_profile.get('emotion_history'):
            return {
                "user_id": str(current_user.user_id),
                "total_records": 0,
                "emotion_distribution": {},
                "recent_emotions": [],
                "message": "暂无情绪数据"
            }
        
        emotion_history = emotion_profile['emotion_history']
        
        # 统计情绪分布
        emotion_distribution = {}
        for record in emotion_history:
            emotion = record.get('emotion', 'unknown')
            emotion_distribution[emotion] = emotion_distribution.get(emotion, 0) + 1
        
        # 获取最近10条情绪记录
        recent_emotions = emotion_history[-10:] if len(emotion_history) > 10 else emotion_history
        
        stats = {
            "user_id": str(current_user.user_id),
            "total_records": len(emotion_history),
            "emotion_distribution": emotion_distribution,
            "recent_emotions": recent_emotions,
            "current_emotion": emotion_profile.get('current_emotion'),
            "last_updated": emotion_profile.get('emotion_updated_at')
        }
        
        logger.info(f"[UserProfile] 情绪统计获取成功: user_id={current_user.user_id}, total_records={len(emotion_history)}")
        return stats
        
    except Exception as e:
        logger.error(f"[UserProfile] 获取用户情绪统计失败: user_id={current_user.user_id}, error={e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取用户情绪统计失败: {str(e)}"
        )

@router.delete("/emotion-profile")
async def clear_user_emotion_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """清空用户情绪画像数据"""
    try:
        logger.info(f"[UserProfile] 清空用户情绪画像: user_id={current_user.user_id}")
        
        # 直接更新用户的情绪相关字段
        user = db.query(User).filter(User.user_id == str(current_user.user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        user.current_emotion = None
        user.emotion_history = None
        user.emotion_updated_at = None
        
        db.commit()
        
        logger.info(f"[UserProfile] 用户情绪画像清空成功: user_id={current_user.user_id}")
        return {
            "message": "用户情绪画像已清空",
            "user_id": str(current_user.user_id)
        }
        
    except Exception as e:
        logger.error(f"[UserProfile] 清空用户情绪画像失败: user_id={current_user.user_id}, error={e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"清空用户情绪画像失败: {str(e)}"
        )