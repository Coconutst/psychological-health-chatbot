# feedback_api.py   用户反馈模块示例接口
# @app.post("/api/message/feedback")
# async def save_feedback(item: FeedbackIn, user=Depends(get_current_user)):
#     """
#     保存单条消息的用户反馈
#     item.feedback: 1=👍  -1=👎  2=举报
#     """
#     db.query(Message).filter(
#         Message.message_id == item.message_id,
#         Message.conversation.has(user_id=user.user_id)
#     ).update({"feedback": item.feedback})
#     db.commit()
#     return {"code": 0, "msg": "反馈已记录"}

# # 文件位置：api/feedback.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from models.feedback import Feedback
# from schemas.feedback import FeedbackCreate
# from database import get_db
#
# router = APIRouter()
#
# # 用户提交反馈
# @router.post("/feedback/")
# async def create_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
#     """
#     用户提交反馈
#     :param feedback: 反馈内容
#     :param db: 数据库会话
#     :return: 反馈结果
#     """
#     db_feedback = Feedback(**feedback.dict())
#     db.add(db_feedback)
#     db.commit()
#     db.refresh(db_feedback)
#     return {"message": "反馈已提交", "feedback_id": db_feedback.id}
#
# # 获取用户反馈列表
# @router.get("/feedback/")
# async def get_feedbacks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     """
#     获取用户反馈列表
#     :param skip: 跳过数量
#     :param limit: 限制数量
#     :param db: 数据库会话
#     :return: 反馈列表
#     """
#     feedbacks = db.query(Feedback).offset(skip).limit(limit).all()
#     return feedbacks