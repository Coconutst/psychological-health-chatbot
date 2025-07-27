"""基于LangChain Tools的心理健康聊天控制器"""

from typing import Dict, Any, List, Optional, AsyncGenerator
import logging
import asyncio
from datetime import datetime

from app.core.tools.psychological_tools import (
    analyze_intent,
    check_safety,
    retrieve_documents,
    rerank_documents,
    generate_answer
)

logger = logging.getLogger(__name__)


class PsychologicalChatController:
    """心理健康聊天控制器 - 基于LangChain Tools实现"""
    
    def __init__(self):
        """初始化控制器"""
        logger.info("[PsychologicalChatController] 控制器初始化完成")
    
    async def process_message(
        self, 
        user_input: str, 
        chat_history: Optional[List[Dict[str, Any]]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """处理用户消息的主要方法"""
        start_time = datetime.now()
        chat_history = chat_history or []
        
        try:
            logger.info(f"[PsychologicalChatController] 开始处理消息: {user_input[:100]}...")
            
            # 步骤1: 意图分析
            logger.info("[PsychologicalChatController] 步骤1: 执行意图分析")
            intent_result = await asyncio.wait_for(
                asyncio.to_thread(analyze_intent, {"args": {"user_input": user_input, "chat_history": chat_history}}),
                timeout=timeout
            )
            
            intent = intent_result.get('intent', 'consultation')
            confidence = intent_result.get('confidence', 0.5)
            
            # 步骤2: 安全检查
            logger.info("[PsychologicalChatController] 步骤2: 执行安全检查")
            safety_result = await asyncio.wait_for(
                asyncio.to_thread(check_safety, {"args": {"user_input": user_input, "chat_history": chat_history}}),
                timeout=timeout
            )
            
            risk_level = safety_result.get('risk_level', 'none')
            safety_triggered = risk_level in ['high', 'medium'] or safety_result.get('immediate_action_required', False)
            
            # 如果触发安全机制，直接返回安全回复
            if safety_triggered:
                logger.warning(f"[PsychologicalChatController] 触发安全机制: 风险等级={risk_level}")
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return {
                    "response": safety_result.get('response', ''),
                    "emotion": "concerned",
                    "intent": intent,
                    "confidence": confidence,
                    "crisis_level": risk_level,
                    "safety_triggered": True,
                    "documents_count": 0,
                    "execution_time": execution_time,
                    "metadata": {
                        "intent_analysis": intent_result,
                        "safety_check": safety_result,
                        "workflow_path": "intent -> safety -> end"
                    }
                }
            
            # 步骤3: 文档检索（默认开启知识库检索增强）
            documents = []
            logger.info("[PsychologicalChatController] 步骤3: 执行文档检索（默认开启）")
            retrieval_result = await asyncio.wait_for(
                asyncio.to_thread(retrieve_documents, {"args": {"user_input": user_input, "intent": intent, "chat_history": chat_history}}),
                timeout=timeout
            )
            documents = retrieval_result.get('retrieved_documents', [])
            
            # 步骤4: 文档重排序（如果有文档）
            if documents:
                logger.info(f"[PsychologicalChatController] 步骤4: 执行文档重排序，文档数量: {len(documents)}")
                rerank_result = await asyncio.wait_for(
                    asyncio.to_thread(rerank_documents, {"args": {"user_input": user_input, "documents": documents}}),
                    timeout=timeout
                )
                documents = rerank_result.get('reranked_documents', documents)
            
            # 步骤5: 生成最终回复
            logger.info("[PsychologicalChatController] 步骤5: 生成最终回复")
            answer_result = await asyncio.wait_for(
                asyncio.to_thread(
                    generate_answer,
                    {
                        "args": {
                            "user_input": user_input,
                            "intent": intent,
                            "documents": documents,
                            "chat_history": chat_history,
                            "safety_triggered": safety_triggered
                        }
                    }
                ),
                timeout=timeout
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # 构建最终结果
            result = {
                "response": answer_result.get('final_response', ''),
                "emotion": answer_result.get('emotion', 'neutral'),
                "intent": intent,
                "confidence": confidence,
                "crisis_level": risk_level,
                "safety_triggered": safety_triggered,
                "documents_count": len(documents),
                "execution_time": execution_time,
                "metadata": {
                    "intent_analysis": intent_result,
                    "safety_check": safety_result,
                    "document_retrieval": retrieval_result if 'retrieval_result' in locals() else None,
                    "document_rerank": rerank_result if 'rerank_result' in locals() else None,
                    "answer_generation": answer_result,
                    "workflow_path": self._get_workflow_path(intent, len(documents), safety_triggered)
                }
            }
            
            logger.info(f"[PsychologicalChatController] 消息处理完成，耗时: {execution_time:.2f}秒")
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"[PsychologicalChatController] 处理超时 ({timeout}秒)")
            raise
        except Exception as e:
            logger.error(f"[PsychologicalChatController] 处理失败: {e}")
            logger.error(f"[PsychologicalChatController] 错误详情: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"[PsychologicalChatController] 错误堆栈: {traceback.format_exc()}")
            raise
    
    async def process_message_stream(
        self, 
        user_input: str, 
        chat_history: Optional[List[Dict[str, Any]]] = None,
        timeout: int = 30
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式处理用户消息"""
        start_time = datetime.now()
        chat_history = chat_history or []
        
        try:
            logger.info(f"[PsychologicalChatController] 开始流式处理消息: {user_input[:100]}...")
            
            # 发送开始信号
            yield {
                "type": "start",
                "message": "开始处理您的消息...",
                "timestamp": start_time.isoformat()
            }
            
            # 步骤1: 意图分析
            yield {
                "type": "progress",
                "step": "intent_analysis",
                "message": "正在分析您的意图..."
            }
            
            intent_result = await asyncio.wait_for(
                asyncio.to_thread(analyze_intent, {"args": {"user_input": user_input, "chat_history": chat_history}}),
                timeout=timeout
            )
            
            intent = intent_result.get('intent', 'consultation')
            confidence = intent_result.get('confidence', 0.5)
            
            yield {
                "type": "progress",
                "step": "intent_analysis_complete",
                "message": f"意图分析完成: {intent} (置信度: {confidence:.2f})",
                "data": {"intent": intent, "confidence": confidence}
            }
            
            # 步骤2: 安全检查
            yield {
                "type": "progress",
                "step": "safety_check",
                "message": "正在进行安全检查..."
            }
            
            safety_result = await asyncio.wait_for(
                asyncio.to_thread(check_safety, {"args": {"user_input": user_input, "chat_history": chat_history}}),
                timeout=timeout
            )
            
            risk_level = safety_result.get('risk_level', 'none')
            safety_triggered = risk_level in ['high', 'medium'] or safety_result.get('immediate_action_required', False)
            
            yield {
                "type": "progress",
                "step": "safety_check_complete",
                "message": f"安全检查完成: 风险等级={risk_level}",
                "data": {"risk_level": risk_level, "safety_triggered": safety_triggered}
            }
            
            # 如果触发安全机制，直接返回安全回复
            if safety_triggered:
                logger.warning(f"[PsychologicalChatController] 触发安全机制: 风险等级={risk_level}")
                execution_time = (datetime.now() - start_time).total_seconds()
                
                yield {
                    "type": "final_response",
                    "response": safety_result.get('response', ''),
                    "emotion": "concerned",
                    "intent": intent,
                    "confidence": confidence,
                    "crisis_level": risk_level,
                    "safety_triggered": True,
                    "documents_count": 0,
                    "execution_time": execution_time
                }
                return
            
            # 步骤3: 文档检索（默认开启知识库检索增强）
            documents = []
            yield {
                "type": "progress",
                "step": "document_retrieval",
                "message": "正在检索相关文档..."
            }
            
            retrieval_result = await asyncio.wait_for(
                asyncio.to_thread(retrieve_documents, {"args": {"user_input": user_input, "intent": intent, "chat_history": chat_history}}),
                timeout=timeout
            )
            documents = retrieval_result.get('retrieved_documents', [])
            
            yield {
                "type": "progress",
                "step": "document_retrieval_complete",
                "message": f"文档检索完成: 找到{len(documents)}个相关文档",
                "data": {"documents_count": len(documents)}
            }
            
            # 步骤4: 文档重排序（如果有文档）
            if documents:
                yield {
                    "type": "progress",
                    "step": "document_rerank",
                    "message": "正在优化文档相关性..."
                }
                
                rerank_result = await asyncio.wait_for(
                    asyncio.to_thread(rerank_documents, {"args": {"user_input": user_input, "documents": documents}}),
                    timeout=timeout
                )
                documents = rerank_result.get('reranked_documents', documents)
                
                yield {
                    "type": "progress",
                    "step": "document_rerank_complete",
                    "message": "文档优化完成"
                }
            
            # 步骤5: 生成最终回复
            yield {
                "type": "progress",
                "step": "answer_generation",
                "message": "正在生成回复..."
            }
            
            answer_result = await asyncio.wait_for(
                asyncio.to_thread(
                    generate_answer,
                    {
                        "args": {
                            "user_input": user_input,
                            "intent": intent,
                            "documents": documents,
                            "chat_history": chat_history,
                            "safety_triggered": safety_triggered
                        }
                    }
                ),
                timeout=timeout
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # 发送最终结果
            yield {
                "type": "final_response",
                "response": answer_result.get('final_response', ''),
                "emotion": answer_result.get('emotion', 'neutral'),
                "intent": intent,
                "confidence": confidence,
                "crisis_level": risk_level,
                "safety_triggered": safety_triggered,
                "documents_count": len(documents),
                "execution_time": execution_time
            }
            
            logger.info(f"[PsychologicalChatController] 流式处理完成，耗时: {execution_time:.2f}秒")
            
        except asyncio.TimeoutError:
            logger.error(f"[PsychologicalChatController] 流式处理超时 ({timeout}秒)")
            raise  # Remove friendly response, raise exception
        except Exception as e:
            logger.error(f"[PsychologicalChatController] 流式处理失败: {e}")
            logger.error(f"[PsychologicalChatController] 流式处理错误详情: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"[PsychologicalChatController] 流式处理错误堆栈: {traceback.format_exc()}")
            raise  # Remove friendly response, raise exception
    
    def _get_workflow_path(self, intent: str, doc_count: int, safety_triggered: bool) -> str:
        """获取工作流路径描述"""
        if safety_triggered:
            return "intent -> safety -> end"
        elif doc_count > 0:
            return "intent -> safety -> retrieval -> rerank -> answer"
        else:
            return "intent -> safety -> retrieval -> answer"


# 创建全局控制器实例
psychological_controller = PsychologicalChatController()