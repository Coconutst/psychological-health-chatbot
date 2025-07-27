"""心理健康聊天机器人的工具集合 - 基于LangChain Tools的独立实现"""

from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import logging
from app.core.factories import create_llm_instance
from app.core.vector_store import get_vector_store
from langchain_core.documents import Document
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)


class IntentAnalysisInput(BaseModel):
    """意图分析工具输入模型"""
    args: Dict[str, Any] = Field(description="包含user_input和chat_history的参数字典")


class SafetyCheckInput(BaseModel):
    """安全检查工具输入模型"""
    args: Dict[str, Any] = Field(description="包含user_input和chat_history的参数字典")


class DocumentRetrievalInput(BaseModel):
    """文档检索工具输入模型"""
    args: Dict[str, Any] = Field(description="包含user_input、intent和chat_history的参数字典")


class DocumentRerankInput(BaseModel):
    """文档重排序工具输入模型"""
    args: Dict[str, Any] = Field(description="包含user_input和documents的参数字典")


class AnswerGenerationInput(BaseModel):
    """答案生成工具输入模型"""
    args: Dict[str, Any] = Field(description="包含user_input、intent、documents、chat_history和safety_triggered的参数字典")


@tool(args_schema=IntentAnalysisInput)
def analyze_intent(args: Dict[str, Any]) -> Dict[str, Any]:
    """分析用户输入的意图和情绪状态"""
    try:
        user_input = args.get("user_input", "")
        chat_history = args.get("chat_history", [])
        
        logger.info(f"[IntentAnalysisTool] 开始意图分析: {user_input[:50]}...")
        
        # 简单的意图分析逻辑
        crisis_keywords = ["想死", "自杀", "结束生命", "不想活", "死了算了", "自残", "自伤"]
        consultation_keywords = ["焦虑", "抑郁", "压力", "困扰", "帮助", "难过", "痛苦"]
        knowledge_keywords = ["什么是", "如何", "为什么", "解释", "了解", "我是谁", "我是", "关于我", "个人信息", "我的", "介绍一下", "告诉我"]
        
        if any(keyword in user_input for keyword in crisis_keywords):
            intent = "crisis"
            confidence = 0.9
        elif any(keyword in user_input for keyword in consultation_keywords):
            intent = "consultation"
            confidence = 0.8
        elif any(keyword in user_input for keyword in knowledge_keywords):
            intent = "knowledge"
            confidence = 0.7
        else:
            intent = "chat"
            confidence = 0.6
        
        result = {
            "intent": intent,
            "confidence": confidence,
            "reasoning": f"基于关键词分析确定意图为{intent}",
            "next_step": "safety_check" if intent == "crisis" else "document_retrieval",
            "user_input": user_input,
            "chat_history": chat_history or []
        }
        
        logger.info(f"[IntentAnalysisTool] 意图分析完成: {intent}, 置信度: {confidence}")
        return result
        
    except Exception as e:
        logger.error(f"[IntentAnalysisTool] 意图分析失败: {e}")
        return {
            "intent": "consultation",
            "confidence": 0.5,
            "reasoning": f"意图分析失败，默认为咨询意图。错误：{str(e)}",
            "next_step": "document_retrieval",
            "user_input": user_input,
            "chat_history": chat_history or []
        }


@tool(args_schema=SafetyCheckInput)
def check_safety(args: Dict[str, Any]) -> Dict[str, Any]:
    """检查用户输入是否包含自伤、自杀或其他危险内容"""
    try:
        user_input = args.get("user_input", "")
        chat_history = args.get("chat_history", [])
        
        logger.info(f"[SafetyCheckTool] 开始安全检查: {user_input[:50]}...")
        
        crisis_resources = {
            "hotlines": [
                "全国心理危机干预热线：400-161-9995",
                "北京危机干预热线：400-161-9995",
                "上海心理援助热线：021-34289888",
                "广州心理危机干预热线：020-81899120"
            ],
            "emergency": "如果情况紧急，请立即拨打120急救电话或前往最近的医院急诊科"
        }
        
        # 高风险关键词检测
        high_risk_keywords = ["自杀", "想死", "结束生命", "不想活", "死了算了", "自残", "自伤", "割腕", "跳楼"]
        medium_risk_keywords = ["绝望", "无助", "没有意义", "活着没意思", "痛苦", "折磨"]
        
        high_risk_count = sum(1 for keyword in high_risk_keywords if keyword in user_input)
        medium_risk_count = sum(1 for keyword in medium_risk_keywords if keyword in user_input)
        
        if high_risk_count > 0:
            risk_level = "high"
            immediate_action = True
            confidence = 0.9
            response = f"我非常关心您的安全。请立即联系专业帮助：\n\n{crisis_resources['emergency']}\n\n心理危机干预热线：\n" + "\n".join(crisis_resources['hotlines'])
        elif medium_risk_count > 0:
            risk_level = "medium"
            immediate_action = True
            confidence = 0.7
            response = "我注意到您可能正在经历困难时期。建议您寻求专业心理健康支持。如需紧急帮助，请联系心理危机干预热线：400-161-9995"
        else:
            risk_level = "low"
            immediate_action = False
            confidence = 0.8
            response = None
        
        result = {
            "risk_level": risk_level,
            "risk_factors": high_risk_keywords + medium_risk_keywords if high_risk_count + medium_risk_count > 0 else [],
            "immediate_action_required": immediate_action,
            "confidence": confidence,
            "reasoning": f"检测到{high_risk_count}个高风险关键词，{medium_risk_count}个中风险关键词",
            "response": response,
            "requires_human_intervention": immediate_action,
            "next_step": "end" if immediate_action else "document_retrieval"
        }
        
        logger.info(f"[SafetyCheckTool] 安全检查完成: 风险等级={risk_level}, 需要干预={immediate_action}")
        return result
        
    except Exception as e:
        logger.error(f"[SafetyCheckTool] 安全检查失败: {e}")
        return {
            "risk_level": "medium",
            "risk_factors": ["安全检查系统异常"],
            "immediate_action_required": True,
            "confidence": 0.5,
            "reasoning": f"安全检查失败，出于安全考虑标记为中等风险。错误：{str(e)}",
            "response": "我检测到可能存在安全风险，建议您联系专业的心理健康服务。如果情况紧急，请拨打心理危机干预热线：400-161-9995",
            "requires_human_intervention": True,
            "next_agent": "end"
        }


@tool(args_schema=DocumentRetrievalInput)
def retrieve_documents(args: Dict[str, Any]) -> Dict[str, Any]:
    """根据用户输入和意图检索相关的心理健康知识文档"""
    try:
        user_input = args.get("user_input", "")
        intent = args.get("intent", "consultation")
        chat_history = args.get("chat_history", [])
        
        logger.info(f"[DocumentRetrievalTool] 开始文档检索: 意图={intent}, 查询={user_input[:50]}...")
        
        vector_store = get_vector_store()
        
        # 根据意图调整检索策略
        if intent == "crisis":
            k = 3  # 危机情况下检索较少文档，快速响应
        elif intent == "knowledge":
            k = 8  # 知识查询需要更多相关文档
        else:
            k = 5  # 默认检索数量
        
        # 执行向量检索
        docs = vector_store.similarity_search(user_input, k=k)
        
        # 转换为字典格式
        retrieved_documents = []
        for i, doc in enumerate(docs):
            retrieved_documents.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": getattr(doc, "score", 0.0),
                "rank": i + 1,
                "source": "vector_search"
            })
        
        result = {
            "retrieved_documents": retrieved_documents,
            "next_step": "document_rerank" if len(retrieved_documents) > 3 else "answer_generation",
            "retrieval_method": "vector_search",
            "document_count": len(retrieved_documents)
        }
        
        logger.info(f"[DocumentRetrievalTool] 文档检索完成: 检索到{len(retrieved_documents)}个文档")
        return result
        
    except Exception as e:
        logger.error(f"[DocumentRetrievalTool] 文档检索失败: {e}")
        return {
            "retrieved_documents": [],
            "next_step": "answer_generation",
            "error": f"文档检索失败：{str(e)}",
            "document_count": 0
        }


@tool(args_schema=DocumentRerankInput)
def rerank_documents(args: Dict[str, Any]) -> Dict[str, Any]:
    """对检索到的文档进行重排序，提高相关性"""
    try:
        user_input = args.get("user_input", "")
        documents = args.get("documents", [])
        
        logger.info(f"[DocumentRerankTool] 开始文档重排序: {len(documents)}个文档")
        
        if not documents:
            return {
                 "reranked_documents": [],
                 "next_step": "answer_generation",
                 "rerank_method": "none"
             }
        
        tfidf_vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        
        # 预处理查询和文档
        query_tokens = list(jieba.cut(user_input))
        query_text = " ".join(query_tokens)
        
        doc_texts = []
        for doc in documents:
            content = doc.get("content", "")
            tokens = list(jieba.cut(content))
            doc_texts.append(" ".join(tokens))
        
        # 使用TF-IDF计算相似度
        all_texts = [query_text] + doc_texts
        tfidf_matrix = tfidf_vectorizer.fit_transform(all_texts)
        
        query_vector = tfidf_matrix[0:1]
        doc_vectors = tfidf_matrix[1:]
        similarities = cosine_similarity(query_vector, doc_vectors)[0]
        
        # 重新排序文档
        scored_docs = []
        for i, (doc, score) in enumerate(zip(documents, similarities)):
            scored_docs.append({
                **doc,
                "relevance_score": float(score),
                "original_rank": doc.get("rank", i + 1),
                "rerank_score": float(score)
            })
        
        # 按相关性分数排序
        scored_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # 更新排名
        for i, doc in enumerate(scored_docs):
            doc["rank"] = i + 1
        
        result = {
             "reranked_documents": scored_docs[:5],  # 返回前5个最相关的文档
             "next_step": "answer_generation",
             "rerank_method": "tfidf_cosine",
             "original_count": len(documents),
             "reranked_count": len(scored_docs[:5])
         }
        
        logger.info(f"[DocumentRerankTool] 文档重排序完成: {len(scored_docs[:5])}个文档")
        return result
        
    except Exception as e:
        logger.error(f"[DocumentRerankTool] 文档重排序失败: {e}")
        return {
             "reranked_documents": documents[:5],  # 如果重排序失败，返回前5个原始文档
             "next_step": "answer_generation",
             "error": f"文档重排序失败：{str(e)}",
             "rerank_method": "fallback"
         }


@tool(args_schema=AnswerGenerationInput)
def generate_answer(args: Dict[str, Any]) -> Dict[str, Any]:
    """基于用户输入、意图和相关文档生成最终回复"""
    try:
        user_input = args.get("user_input", "")
        intent = args.get("intent", "consultation")
        documents = args.get("documents", [])
        chat_history = args.get("chat_history", [])
        safety_triggered = args.get("safety_triggered", False)
        
        logger.info(f"[AnswerGenerationTool] 开始生成答案: 意图={intent}, 文档数={len(documents or [])}, 安全触发={safety_triggered}")
        
        # 如果安全机制已触发，直接返回安全回复
        if safety_triggered:
            return {
                 "final_response": "我非常关心您的安全和福祉。请考虑联系专业的心理健康服务或危机干预热线。您的生命很宝贵，总有人愿意帮助您。",
                 "response_type": "safety_intervention",
                 "confidence": 1.0,
                 "next_step": "end"
             }
        
        llm = create_llm_instance()
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位专业、温暖、有同理心的AI心理健康助手。请根据用户的输入、意图和相关文档生成一个包含思考过程的专业回复。

回复结构要求：
1. 首先表达对用户的理解和共情
2. 简要分析用户的情况（基于意图和情绪）
3. 提供专业的建议或支持
4. 如果有相关文档，要自然地融入回复中
5. 以鼓励和支持的话语结束

回复原则：
• 保持专业性和同理心
• 根据用户意图调整回复风格
• 避免诊断或提供医疗建议
• 鼓励用户寻求专业帮助
• 保持温暖、支持性的语调
• 体现AI的分析思路和专业判断

当前分析：
- 用户意图：{intent}
- 情绪状态：需要从用户输入中识别
- 相关文档：{documents}
- 对话历史：{chat_history}
- 安全状态：{safety_triggered}

请生成一个既专业又温暖的回复，让用户感受到被理解和支持。"""),
            ("human", "用户输入：{user_input}")
        ])
        
        # 准备文档内容
        doc_content = ""
        if documents:
            doc_content = "\n\n".join([doc.get("content", "")[:500] for doc in documents[:3]])
        
        # 准备对话历史
        history_text = ""
        if chat_history:
            recent_history = chat_history[-3:]  # 只使用最近3轮对话
            history_text = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in recent_history])
        
        # 生成回复
        logger.info(f"[AnswerGenerationTool] 准备调用LLM，用户输入: {user_input[:100]}...")
        logger.info(f"[AnswerGenerationTool] 文档内容长度: {len(doc_content)}")
        
        try:
            formatted_messages = prompt.format_messages(
                user_input=user_input,
                intent=intent,
                documents=doc_content or "无相关文档",
                chat_history=history_text or "无对话历史",
                safety_triggered=safety_triggered
            )
            logger.info(f"[AnswerGenerationTool] 消息格式化完成，开始调用LLM")
            
            response = llm.invoke(formatted_messages)
            logger.info(f"[AnswerGenerationTool] LLM调用成功，响应类型: {type(response)}")
            
            final_response = response.content if hasattr(response, 'content') else str(response)
            logger.info(f"[AnswerGenerationTool] 最终回复长度: {len(final_response)}")
            
        except Exception as llm_error:
            logger.error(f"[AnswerGenerationTool] LLM调用失败: {llm_error}")
            logger.error(f"[AnswerGenerationTool] LLM错误详情: {type(llm_error).__name__}: {str(llm_error)}")
            import traceback
            logger.error(f"[AnswerGenerationTool] LLM错误堆栈: {traceback.format_exc()}")
            
            # LLM调用失败时的备用回复
            final_response = "抱歉，我现在无法为您提供详细的回复。建议您稍后再试，或直接联系专业的心理健康服务。"
            logger.warning(f"[AnswerGenerationTool] 使用备用回复")
        
        # 分析用户情绪
        emotion = "neutral"
        emotion_keywords = {
            "anxious": ["焦虑", "担心", "紧张", "不安", "恐惧"],
            "sad": ["难过", "伤心", "沮丧", "失落", "痛苦", "绝望"],
            "angry": ["愤怒", "生气", "恼火", "烦躁", "愤恨"],
            "confused": ["困惑", "迷茫", "不知道", "不明白", "疑惑"],
            "hopeful": ["希望", "期待", "乐观", "积极", "向上"]
        }
        
        for emotion_type, keywords in emotion_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                emotion = emotion_type
                break
        
        # 根据意图和情绪添加适当的结尾
        if intent == "consultation":
            if emotion in ["sad", "anxious"]:
                final_response += "\n\n💙 请记住，您并不孤单。如果需要更专业的帮助，建议咨询专业的心理健康专家。"
            else:
                final_response += "\n\n如果您需要更专业的帮助，建议咨询专业的心理健康专家。"
        elif intent == "knowledge":
            final_response += "\n\n📚 希望这些信息对您有帮助。如有更多疑问，欢迎继续询问。"
        elif intent == "crisis":
            final_response += "\n\n🆘 您的安全是最重要的。请立即寻求专业帮助或联系危机干预热线。"
        
        result = {
             "final_response": final_response,
             "response_type": intent,
             "emotion": emotion,
             "confidence": 0.8,
             "used_documents": len(documents or []),
             "next_step": "end"
         }
        
        logger.info(f"[AnswerGenerationTool] 答案生成完成: 回复长度={len(final_response)}")
        return result
        
    except Exception as e:
        logger.error(f"[AnswerGenerationTool] 答案生成失败: {e}")
        return {
             "final_response": "抱歉，我现在无法为您提供回复。建议您稍后再试，或直接联系专业的心理健康服务。",
             "response_type": "error",
             "confidence": 0.0,
             "error": str(e),
             "next_step": "end"
         }