"""心理咨询API端点 - 基于LangChain Tools架构"""

import asyncio
import json
import requests
import traceback
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# 导入核心模块
from app.core.tools.psychological_controller import psychological_controller
from app.core.memory.memory_manager import get_session_history, get_session_history_database, get_conversation_buffer_memory, _buffer_memories
from app.configs.database import get_db
from app.services.conversation_service import ConversationService
from app.services.streaming_service import StreamingService
from app.api.endpoints.auth import get_current_user_optional, get_current_user
from app.models.user import User
from app.configs.settings import api_settings
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建API路由器
router = APIRouter()

# 请求模型
class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息")  
    conversation_id: Optional[str] = Field(None, description="会话ID")
    model: str = Field("deepseek-chat", description="模型名称")
    stream: bool = Field(True, description="是否流式响应")

# 非流式响应处理函数
async def handle_non_stream_response(
    request: ChatRequest,
    db: Session,
    current_user: Optional[Any],
    conversation_id: str
) -> Dict[str, Any]:
    """处理非流式响应"""
    try:
        logger.info(f"[API] 处理非流式响应，会话ID: {conversation_id}")
        
        # 使用ConversationBufferMemory获取包含历史上下文的对话记忆
        user_id = getattr(current_user, 'user_id', None) if current_user and not getattr(current_user, 'is_anonymous', False) else None
        
        # 获取ConversationBufferMemory（自动加载历史上下文）
        buffer_memory = get_conversation_buffer_memory(
            session_id=conversation_id, 
            user_id=user_id, 
            load_historical_context=True
        )
        
        # 从ConversationBufferMemory获取格式化的对话历史
        memory_variables = buffer_memory.load_memory_variables({})
        chat_history = memory_variables.get('chat_history', [])
        
        # 将LangChain消息格式转换为API格式
        formatted_history = []
        for message in chat_history:
            if hasattr(message, 'type'):
                role = "human" if message.type == "human" else "assistant"
            else:
                role = "human" if message.__class__.__name__ == "HumanMessage" else "assistant"
            
            formatted_history.append({
                "role": role,
                "content": message.content
            })
        
        logger.info(f"[API] ConversationBufferMemory加载了 {len(formatted_history)} 条消息（包含历史上下文）")
        
        # 添加内置系统角色
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的心理健康咨询师AI助手。你具备丰富的心理学知识和咨询经验，能够为用户提供专业、温暖、有效的心理支持和建议。请以同理心、专业性和关怀的态度回应用户的问题。"
            }
        ]
        
        # 添加历史对话
        messages.extend(formatted_history)
        
        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # 使用心理咨询控制器处理消息（formatted_history已包含历史上下文）
        result = await psychological_controller.process_message(
            user_input=request.message,
            chat_history=formatted_history,
            timeout=30
        )
        
        # 获取响应内容
        response_content = result.get("response")
        if not response_content:
            raise ValueError("No response generated from controller")
        
        # 保存对话到数据库（如果用户已登录）
        if current_user and hasattr(current_user, 'user_id') and not getattr(current_user, 'is_anonymous', False):
            try:
                conversation_service = ConversationService(db)
                
                # 确保对话记录存在
                conversation = conversation_service.get_conversation(conversation_id)
                if not conversation:
                    conversation = conversation_service.create_conversation(
                        conversation_id=conversation_id,
                        user_id=str(current_user.user_id),
                        title=request.message[:30] + ('...' if len(request.message) > 30 else '')
                    )
                
                # 保存用户消息和AI回复
                conversation_service.add_message(
                    conversation_id=conversation_id,
                    role="human",
                    content=request.message
                )
                conversation_service.add_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=response_content,
                    metadata=result.get("metadata", {})
                )
                
                # 更新ConversationBufferMemory缓存
                try:
                    cache_key = f"{conversation_id}_{current_user.user_id or 'anonymous'}"
                    if cache_key in _buffer_memories:
                        buffer_memory = _buffer_memories[cache_key]
                        buffer_memory.chat_memory.add_user_message(request.message)
                        buffer_memory.chat_memory.add_ai_message(result["output"])
                        logger.debug(f"[NonStream] ConversationBufferMemory缓存已更新")
                except Exception as e:
                    logger.error(f"[NonStream] 更新ConversationBufferMemory缓存失败: {e}")
                
                # 更新用户情绪画像
                emotion = result.get("emotion")
                if emotion and emotion != "unknown":
                    conversation_service.update_user_emotion_profile(
                        user_id=str(current_user.user_id),
                        emotion=emotion,
                        confidence=result.get("confidence", 0.5),
                        emotion_context={
                            "conversation_id": conversation_id,
                            "message_content": request.message[:100]
                        }
                    )
                    
            except Exception as e:
                logger.error(f"[API] 保存对话失败: {e}")
        
        # 返回类似 DeepSeek API 的响应格式
        return {
            "id": f"chatcmpl-{conversation_id}",
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(request.message.split()),
                "completion_tokens": len(response_content.split()),
                "total_tokens": len(request.message.split()) + len(response_content.split())
            },
            "system_fingerprint": "psychological-health-chatbot",
            "metadata": {
                "conversation_id": conversation_id,
                "intent": result.get("intent", "unknown"),
                "emotion": result.get("emotion", "neutral"),
                "confidence": result.get("confidence", 0.5),
                "execution_time": result.get("execution_time", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"[API] 非流式响应处理异常: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"处理请求失败: {str(e)}"
        )

class SystemStatusResponse(BaseModel):
    """系统状态响应模型"""
    tools_active: bool = Field(True, description="LangChain Tools状态")
    controller_active: bool = Field(True, description="心理咨询控制器状态")
    database_active: bool = Field(True, description="数据库状态")
    vector_store_active: bool = Field(True, description="向量存储状态")
    system_status: str = Field("healthy", description="系统状态")

class AnalysisResponse(BaseModel):
    """消息分析响应模型"""
    intent: str = Field(..., description="意图识别")
    confidence: float = Field(..., description="置信度")
    explanation: str = Field(..., description="分析说明")
    crisis_level: str = Field(..., description="危机等级")
    crisis_confidence: float = Field(..., description="危机检测置信度")
    crisis_explanation: str = Field(..., description="危机分析说明")
    requires_intervention: bool = Field(..., description="是否需要干预")
    timestamp: str = Field(..., description="时间戳")

@router.post("/chat")
async def psychological_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[Any] = Depends(get_current_user_optional)
):
    """心理咨询聊天接口 - 基于LangChain Tools，支持流式和非流式响应"""
    
    logger.info(f"[API] 收到聊天请求: {request.message[:50]}...")
    logger.info(f"[API] 请求参数 - model: {request.model}, stream: {request.stream}")
    
    # 生成会话ID
    user_id = getattr(current_user, 'user_id', 'anonymous')
    conversation_id = request.conversation_id or f"user_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 如果不是流式响应，直接处理并返回JSON
    if not request.stream:
        return await handle_non_stream_response(request, db, current_user, conversation_id)
    
    async def generate_stream():
        try:
            logger.info(f"[API] 开始流式响应生成，会话ID: {conversation_id}")
            
            # 发送处理状态
            yield f"data: {{\"type\": \"status\", \"message\": \"Processing your message...\"}}"
            
            # 使用基于LangChain Tools的心理咨询控制器
            logger.info(f"[API] 开始心理咨询控制器处理")
            
            response_content = ""
            error_occurred = False
            emotion = "unknown"
            confidence = 0.5
            execution_time = 0
            success = True
            result = {}
            
            try:
                # 使用ConversationBufferMemory获取包含历史上下文的对话记忆
                user_id = getattr(current_user, 'user_id', None) if current_user and not getattr(current_user, 'is_anonymous', False) else None
                
                # 获取ConversationBufferMemory（自动加载历史上下文）
                buffer_memory = get_conversation_buffer_memory(
                    session_id=conversation_id, 
                    user_id=user_id, 
                    load_historical_context=True
                )
                
                # 从ConversationBufferMemory获取格式化的对话历史
                memory_variables = buffer_memory.load_memory_variables({})
                chat_history = memory_variables.get('chat_history', [])
                
                # 将LangChain消息格式转换为API格式
                formatted_history = []
                for message in chat_history:
                    if hasattr(message, 'type'):
                        role = "human" if message.type == "human" else "assistant"
                    else:
                        role = "human" if message.__class__.__name__ == "HumanMessage" else "assistant"
                    
                    formatted_history.append({
                        "role": role,
                        "content": message.content
                    })
                
                logger.info(f"[Tools] ConversationBufferMemory加载了 {len(formatted_history)} 条消息（包含历史上下文）")
                
                # 发送工具处理状态
                tools_status = {
                    "type": "tools_status",
                    "message": "启动LangChain Tools处理流程...",
                    "tools": ["意图分析", "安全检查", "文档检索", "文档重排序", "答案生成"],
                    "status": "processing"
                }
                yield f"data: {json.dumps(tools_status, ensure_ascii=False)}"
                
                # 使用基于LangChain Tools的控制器处理消息
                logger.info(f"[Tools] 使用Tools控制器处理消息: {request.message[:50]}...")
                
                result = await psychological_controller.process_message(
                    user_input=request.message,
                    chat_history=formatted_history,  # formatted_history已包含历史上下文
                    timeout=30
                )
                logger.info(f"[Tools] Tools控制器执行完成")
                
                # 记录详细的执行结果
                logger.info(f"[MultiAgent] 执行结果详情:")
                logger.info(f"  - 意图: {result.get('intent', 'unknown')}")
                logger.info(f"  - 置信度: {result.get('confidence', 0)}")
                logger.info(f"  - 情绪: {result.get('emotion', 'unknown')}")
                logger.info(f"  - 危机等级: {result.get('crisis_level', 'unknown')}")
                logger.info(f"  - 安全触发: {result.get('safety_triggered', False)}")
                logger.info(f"  - 检索文档数: {result.get('documents_count', 0)}")
                logger.info(f"  - 重排序文档数: {result.get('documents_count', 0)}")
                logger.info(f"  - 执行时间: {result.get('execution_time', 0):.2f}秒")
                
                # 获取响应内容和元数据
                response_content = result.get("response")
                if not response_content:
                    raise ValueError("No response generated from controller")
                emotion = result.get("emotion", "unknown")
                confidence = result.get("confidence", 0.5)
                execution_time = result.get("execution_time", 0)
                success = not result.get("error")
                
                logger.info(f"[MultiAgent] 最终响应长度: {len(response_content)} 字符")
                logger.info(f"[MultiAgent] 执行成功: {success}")
                
                # 发送思考过程
                thinking_steps = [
                    "🤔 正在分析您的问题...",
                    "📚 检索相关的心理健康知识...",
                    "🧠 整合信息并组织回复...",
                    "💡 准备为您提供专业建议..."
                ]
                
                for step in thinking_steps:
                    thinking_data = {
                        "type": "thinking",
                        "content": step,
                        "conversation_id": conversation_id,
                        "timestamp": datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(thinking_data, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.5)  # 思考过程稍慢一些
                
                # 发送回复开始标记
                start_response_data = {
                    "type": "response_start",
                    "message": "💬 AI心理助手回复：",
                    "conversation_id": conversation_id,
                    "metadata": {
                        "intent": result.get("intent", "unknown"),
                        "emotion": result.get("emotion", "neutral"),
                        "confidence": result.get("confidence", 0.5),
                        "documents_used": result.get("retrieved_docs_count", 0),
                        "processing_time": f"{result.get('execution_time', 0):.2f}秒"
                    },
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(start_response_data, ensure_ascii=False)}\n\n"
                
                # 流式返回响应内容（美化格式）
                formatted_response = f"\n{response_content}\n\n---\n\n📊 **分析结果**\n" \
                                   f"• 意图识别: {result.get('intent', 'unknown')}\n" \
                                   f"• 情绪状态: {result.get('emotion', 'neutral')}\n" \
                                   f"• 置信度: {result.get('confidence', 0.5):.1%}\n" \
                                   f"• 参考文档: {result.get('documents_count', 0)}篇\n" \
                                   f"• 处理时间: {result.get('execution_time', 0):.2f}秒"
                
                for char in formatted_response:
                    char_data = {
                        "type": "content",
                        "content": char,
                        "conversation_id": conversation_id,
                        "timestamp": datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(char_data, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.01)
                    
            except Exception as e:
                logger.error(f"[MultiAgent] 心理咨询控制器调用错误: {e}")
                import traceback
                logger.error(f"[MultiAgent] 完整错误堆栈: {traceback.format_exc()}")
                # 直接抛出异常，不使用备用响应
                raise
                
            # 设置默认的元数据值（如果没有从控制器获取到）
            if 'emotion' not in locals():
                emotion = "unknown"
            if 'confidence' not in locals():
                confidence = 0.5
            if 'execution_time' not in locals():
                execution_time = 0
            if 'success' not in locals():
                success = True
            
            # 检查响应内容是否生成成功
            if 'response_content' not in locals() or not response_content:
                raise ValueError("Failed to generate response")
            
            result = {
                "output": response_content,
                "metadata": {
                    "multi_agent": True,
                    "emotion": emotion,
                    "confidence": confidence,
                    "execution_time": execution_time,
                    "success": success,
                    "agent_details": {
                        "intent": locals().get('result', {}).get('intent'),
                        "crisis_level": locals().get('result', {}).get('crisis_level'),
                        "safety_triggered": locals().get('result', {}).get('safety_triggered', False),
                        "retrieved_docs_count": locals().get('result', {}).get('documents_count', 0),
                        "reranked_docs_count": locals().get('result', {}).get('documents_count', 0),
                        "supervisor_completed": locals().get('result', {}).get('supervisor_completed', False),
                        "safety_completed": locals().get('result', {}).get('safety_completed', False)
                    }
                }
            }
            
            logger.info(f"[MultiAgent] 准备保存对话结果，元数据: {result['metadata']}")
            
            # 保存对话到数据库
            logger.info(f"[MultiAgent] 开始保存对话到数据库")
            logger.debug(f"[MultiAgent] 当前用户: {current_user}, 类型: {type(current_user)}")
            logger.debug(f"[MultiAgent] 对话ID: {conversation_id}")
            logger.debug(f"[MultiAgent] 用户消息: {request.message[:100]}...")
            logger.debug(f"[MultiAgent] AI回复: {result['output'][:100]}...")  # 只打印前100个字符
            
            if current_user and hasattr(current_user, 'user_id') and not getattr(current_user, 'is_anonymous', False):
                try:
                    conversation_service = ConversationService(db)
                    logger.debug(f"[MultiAgent] ConversationService实例创建成功")
                    
                    # 确保对话记录存在
                    conversation = conversation_service.get_conversation(conversation_id)
                    if not conversation:
                        logger.info(f"[MultiAgent] 创建新对话: {conversation_id}")
                        conversation = conversation_service.create_conversation(
                            conversation_id=conversation_id,
                            user_id=str(current_user.user_id),
                            title=request.message[:30] + ('...' if len(request.message) > 30 else '')
                        )
                        logger.info(f"[MultiAgent] 对话创建成功: {conversation.conversation_id}")
                    else:
                        logger.debug(f"[MultiAgent] 使用现有对话: {conversation_id}")
                    
                    # 保存用户消息
                    logger.debug(f"[MultiAgent] 保存用户消息到对话: {conversation_id}")
                    conversation_service.add_message(
                        conversation_id=conversation_id,
                        role="human",
                        content=request.message
                    )
                    logger.debug(f"[MultiAgent] 用户消息保存成功")
                    
                    # 保存AI回复
                    logger.debug(f"[MultiAgent] 保存AI回复到对话: {conversation_id}")
                    conversation_service.add_message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=result["output"],
                        metadata=result.get("metadata", {})
                    )
                    logger.info(f"[MultiAgent] 对话消息保存完成")
                    
                    # 更新ConversationBufferMemory缓存
                    try:
                        cache_key = f"{conversation_id}_{current_user.user_id or 'anonymous'}"
                        if cache_key in _buffer_memories:
                            buffer_memory = _buffer_memories[cache_key]
                            buffer_memory.chat_memory.add_user_message(request.message)
                            buffer_memory.chat_memory.add_ai_message(result["output"])
                            logger.debug(f"[MultiAgent] ConversationBufferMemory缓存已更新")
                    except Exception as e:
                        logger.error(f"[MultiAgent] 更新ConversationBufferMemory缓存失败: {e}")
                    
                    # 更新用户情绪画像
                    if emotion and emotion != "unknown":
                        logger.debug(f"[MultiAgent] 开始更新用户情绪画像: emotion={emotion}, confidence={confidence}")
                        emotion_context = {
                            "conversation_id": conversation_id,
                            "message_content": request.message[:100],  # 只保存前100个字符
                            "agent_details": result.get("metadata", {}).get("agent_details", {})
                        }
                        
                        emotion_updated = conversation_service.update_user_emotion_profile(
                            user_id=str(current_user.user_id),
                            emotion=emotion,
                            confidence=confidence,
                            emotion_context=emotion_context
                        )
                        
                        if emotion_updated:
                            logger.info(f"[MultiAgent] 用户情绪画像更新成功: user_id={current_user.user_id}, emotion={emotion}")
                        else:
                            logger.warning(f"[MultiAgent] 用户情绪画像更新失败: user_id={current_user.user_id}")
                    else:
                        logger.debug(f"[MultiAgent] 跳过情绪画像更新，情绪状态为: {emotion}")
                    
                except Exception as e:
                    logger.error(f"[MultiAgent] 保存对话失败: {e}")
                    logger.error(f"[MultiAgent] 错误详情: {traceback.format_exc()}")
                    # 不影响响应返回，只记录错误
                    pass
            else:
                logger.warning(f"[MultiAgent] 用户未登录或为匿名用户，跳过对话保存")
            
            # 最终响应已在上面的逐字输出中发送，这里不需要再发送
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"[API] 流式响应生成异常: {e}")
            # 直接抛出异常，不返回错误响应
            raise
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Conversation-ID": conversation_id  # 添加对话ID到响应头
        }
    )

@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """获取系统状态"""
    try:
        # 这里可以添加实际的健康检查逻辑
        # 例如检查LangChain Tools是否正常工作
        
        return SystemStatusResponse(
            tools_active=True,
            controller_active=True,
            database_active=True,
            vector_store_active=True,
            system_status="healthy"
        )
        
    except Exception as e:
        return SystemStatusResponse(
            tools_active=False,
            controller_active=False,
            database_active=False,
            vector_store_active=False,
            system_status=f"error: {str(e)}"
        )

@router.post("/analyze")
async def analyze_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """分析消息（仅分析，不生成回复）"""
    try:
        # 使用基于LangChain Tools的心理咨询控制器进行分析
        # 具体实现请参考 app/core/tools/psychological_controller.py
        
        # 这里可以添加仅分析的逻辑
        # 例如只运行意图分析和安全检测
        
        # 临时返回模拟数据，实际应使用 psychological_controller
        route_result = {
            "intent": "general_consultation",
            "confidence": 0.8,
            "explanation": "用户寻求一般心理咨询"
        }
        
        crisis_assessment = {
            "risk_level": "low",
            "confidence": 0.9,
            "explanation": "未检测到明显风险"
        }
        
        return {
            "intent": route_result["intent"],
            "confidence": route_result["confidence"],
            "explanation": route_result["explanation"],
            "crisis_level": crisis_assessment["risk_level"],
            "crisis_confidence": crisis_assessment["confidence"],
            "crisis_explanation": crisis_assessment["explanation"],
            "requires_intervention": crisis_assessment["risk_level"] in ["high", "medium"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"消息分析失败: {str(e)}"
        )

@router.get("/agents/info")
async def get_agents_info():
    """获取LangChain Tools信息（保持向后兼容的路径）"""
    return {
        "tools": [
            {
                "name": "Intent Analysis Tool",
                "description": "分析用户输入意图并确定处理策略",
                "capabilities": ["意图识别", "置信度评估", "路由决策"]
            },
            {
                "name": "Safety Check Tool",
                "description": "识别自伤、自杀等高风险内容，调用安全流程",
                "capabilities": ["危机检测", "风险评估", "安全干预"]
            },
            {
                "name": "Document Retrieval Tool",
                "description": "负责向ChromaDB执行向量检索与关键词检索",
                "capabilities": ["向量检索", "关键词检索", "RRF融合"]
            },
            {
                "name": "Document Reranking Tool",
                "description": "对检索结果进行Cross-Encoder精排",
                "capabilities": ["文档重排序", "相关性评分", "结果优化"]
            },
            {
                "name": "Answer Generation Tool",
                "description": "基于检索结果和用户情绪生成最终回复",
                "capabilities": ["情绪分析", "回复生成", "情绪支持"]
            }
        ],
        "workflow": {
            "description": "用户输入 → 意图分析 → 安全检测 → 文档检索 → 文档重排序 → 答案生成",
            "features": ["LangChain Tools架构", "安全检测", "知识检索", "情绪支持", "个性化回复"]
        }
    }