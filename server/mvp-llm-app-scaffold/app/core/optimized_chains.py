"""优化的心理咨询链 - 解决性能问题和模拟数据问题"""

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory
from pydantic import BaseModel, Field
import logging
import time

from app.core.factories import create_llm_instance, create_vector_store_instance

logger = logging.getLogger(__name__)


class OptimizedPsychologicalResponse(BaseModel):
    """优化的心理咨询回复模型 - 合并情绪分析和回复生成"""
    final_response: str = Field(description="最终回复内容")
    primary_emotion: str = Field(description="识别的主要情绪")
    emotion_intensity: float = Field(description="情绪强度 (0-1)", ge=0.0, le=1.0)
    confidence: float = Field(description="回复质量置信度 (0-1)", ge=0.0, le=1.0)
    response_type: str = Field(description="回复类型：empathetic, supportive, informative, crisis")


def create_optimized_psychological_chain(vector_store=None):
    """创建优化的心理咨询链 - 单次LLM调用，快速响应"""
    
    # 创建LLM实例，优化配置
    llm = create_llm_instance({
        "temperature": 0.7,
        "max_tokens": 800,  # 增加token限制以获得更完整的回复
        "timeout": 30,     # 减少单次调用超时
        "max_retries": 2   # 减少重试次数
    })
    
    # 创建结构化输出LLM
    structured_llm = llm.with_structured_output(OptimizedPsychologicalResponse)
    
    # 创建优化的提示词模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
你是一位专业、温暖、富有同理心的心理健康顾问。请在一次回复中完成以下任务：

1. **情绪识别**：分析用户的主要情绪（焦虑、抑郁、愤怒、恐惧、内疚、困惑、孤独、积极、中性）
2. **情绪强度评估**：评估情绪强度（0-1）
3. **生成专业回复**：提供温暖、专业、有帮助的回复

**回复原则**：
- 首先承认和验证用户的感受
- 提供情感支持和理解
- 给出实用的建议或应对策略
- 保持专业界限，不提供医疗诊断
- 如果情况严重，建议寻求专业帮助

**回复结构**：
1. 情感确认和共情
2. 理解和支持
3. 实用建议或应对策略
4. 鼓励和希望
5. 必要时提供专业资源信息

请根据用户输入生成一个完整的回复，同时识别情绪状态。
"""),
        ("human", """
用户输入：{user_input}

{context_info}

{chat_history}

请分析用户情绪并生成专业的心理咨询回复。
""")
    ])
    
    # 创建链
    chain = prompt | structured_llm
    
    # 创建记忆
    memory = ConversationBufferWindowMemory(
        k=6,  # 保留最近3轮对话
        return_messages=True,
        memory_key="chat_history"
    )
    
    def format_context_info(retrieved_docs: List[Document] = None) -> str:
        """格式化上下文信息"""
        if not retrieved_docs:
            return "相关知识：基于专业心理健康知识库提供支持。"
        
        context = "相关专业知识：\n"
        for i, doc in enumerate(retrieved_docs[:2], 1):  # 最多使用2个文档
            context += f"{i}. {doc.page_content[:200]}...\n"
        return context
    
    def format_chat_history(history: List[Dict[str, str]] = None) -> str:
        """格式化对话历史"""
        if not history:
            return "对话历史：这是对话的开始。"
        
        formatted = "最近对话：\n"
        recent = history[-4:] if len(history) > 4 else history  # 最近2轮对话
        
        for i in range(0, len(recent), 2):
            if i + 1 < len(recent):
                user_msg = recent[i].get('content', '')[:100]
                ai_msg = recent[i + 1].get('content', '')[:100]
                formatted += f"用户：{user_msg}...\nAI：{ai_msg}...\n\n"
        
        return formatted
    
    async def optimized_invoke(user_input: str, conversation_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """优化的调用函数 - 快速响应"""
        start_time = time.time()
        
        try:
            logger.info(f"开始处理用户输入: {user_input[:50]}...")
            
            # 简单的关键词检索（如果有向量存储）
            retrieved_docs = []
            if vector_store:
                try:
                    # 快速检索，限制结果数量
                    retrieved_docs = vector_store.similarity_search(user_input, k=2)
                    logger.info(f"检索到 {len(retrieved_docs)} 个相关文档")
                except Exception as e:
                    logger.warning(f"向量检索失败，继续处理: {e}")
            
            # 格式化输入
            context_info = format_context_info(retrieved_docs)
            chat_history_str = format_chat_history(conversation_history)
            
            # 单次LLM调用生成回复
            logger.info("调用LLM生成回复...")
            result = chain.invoke({
                "user_input": user_input,
                "context_info": context_info,
                "chat_history": chat_history_str
            })
            
            execution_time = time.time() - start_time
            logger.info(f"回复生成完成，耗时: {execution_time:.2f}秒")
            
            # 增强回复内容
            enhanced_response = enhance_response_with_resources(
                result.final_response, 
                result.primary_emotion, 
                result.emotion_intensity
            )
            
            return {
                "response": enhanced_response,
                "emotion": result.primary_emotion,
                "emotion_intensity": result.emotion_intensity,
                "confidence": result.confidence,
                "response_type": result.response_type,
                "execution_time": execution_time,
                "retrieved_docs_count": len(retrieved_docs),
                "success": True
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"优化链执行失败: {e}，耗时: {execution_time:.2f}秒")
            raise  # 抛出真实异常以便调试
            # 返回友好的错误回复，而不是预定义的模拟数据
            return {
                "response": generate_fallback_response(user_input),
                "emotion": "unknown",
                "emotion_intensity": 0.5,
                "confidence": 0.3,
                "response_type": "fallback",
                "execution_time": execution_time,
                "retrieved_docs_count": 0,
                "success": False,
                "error": str(e)
            }
    
    return optimized_invoke


def enhance_response_with_resources(response: str, emotion: str, intensity: float) -> str:
    """根据情绪状态增强回复内容"""
    enhanced = response
    
    # 根据情绪强度和类型添加资源
    if intensity > 0.7:  # 高强度情绪
        if emotion in ["焦虑", "恐惧"]:
            enhanced += "\n\n💡 **即时缓解技巧**：\n• 尝试4-7-8呼吸法：吸气4秒，屏息7秒，呼气8秒\n• 进行5-4-3-2-1感官练习：说出5样看到的、4样听到的、3样摸到的、2样闻到的、1样尝到的"
        elif emotion in ["抑郁", "孤独"]:
            enhanced += "\n\n🌟 **情绪支持**：\n• 记住：你的感受是有效的，你不是一个人\n• 尝试每天做一件小事来照顾自己\n• 考虑联系信任的朋友或家人"
        elif emotion == "愤怒":
            enhanced += "\n\n🔥 **情绪管理**：\n• 暂停并深呼吸10次\n• 进行体育活动来释放能量\n• 用'我感到...'的方式表达感受"
    
    # 高强度情绪时提供专业资源
    if intensity > 0.8:
        enhanced += "\n\n📞 **专业支持**：\n• 心理咨询热线：400-161-9995\n• 如果感到无法应对，请考虑寻求专业心理咨询师的帮助"
    
    return enhanced


def generate_fallback_response(user_input: str) -> str:
    """生成友好的回退回复，避免使用预定义的模拟数据"""
    return f"""你好，我是你的心理健康助手。我注意到你提到了"{user_input[:20]}..."，我很想为你提供帮助。

虽然我现在遇到了一些技术问题，但我想让你知道：

🤗 **你的感受很重要**：无论你现在经历什么，你的感受都是有效的。

💪 **你并不孤单**：很多人都会面临各种心理健康挑战，寻求帮助是勇敢的表现。

🌱 **希望总是存在**：即使在最困难的时候，情况是可以改善的。

如果你需要立即的支持，请考虑：
• 联系心理咨询热线：400-161-9995
• 与信任的朋友或家人交谈
• 寻求专业心理咨询师的帮助

请稍后再试，我会努力为你提供更好的支持。"""


def get_optimized_psychological_chain(vector_store=None):
    """获取优化的心理咨询链"""
    if vector_store is None:
        try:
            vector_store = create_vector_store_instance()
        except Exception as e:
            logger.warning(f"无法创建向量存储，将在没有检索的情况下运行: {e}")
            vector_store = None
    
    return create_optimized_psychological_chain(vector_store)