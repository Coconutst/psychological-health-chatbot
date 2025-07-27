"""知识检索工具 - 从向量数据库检索相关心理健康知识"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


class KnowledgeRetrievalInput(BaseModel):
    """知识检索输入参数"""
    query: str = Field(description="检索查询内容")
    user_id: str = Field(description="用户ID")
    emotion_context: Optional[Dict[str, Any]] = Field(default=None, description="情绪上下文")
    conversation_context: Optional[List[Dict[str, str]]] = Field(default=None, description="对话上下文")
    max_results: int = Field(default=5, description="最大返回结果数")
    similarity_threshold: float = Field(default=0.7, description="相似度阈值")


class KnowledgeCategory:
    """知识分类定义"""
    COPING_STRATEGIES = "coping_strategies"       # 应对策略
    EMOTIONAL_REGULATION = "emotional_regulation" # 情绪调节
    STRESS_MANAGEMENT = "stress_management"       # 压力管理
    ANXIETY_HELP = "anxiety_help"                 # 焦虑帮助
    DEPRESSION_SUPPORT = "depression_support"     # 抑郁支持
    RELATIONSHIP_ADVICE = "relationship_advice"   # 关系建议
    SELF_CARE = "self_care"                       # 自我关怀
    MINDFULNESS = "mindfulness"                   # 正念冥想
    CRISIS_INTERVENTION = "crisis_intervention"   # 危机干预
    PROFESSIONAL_HELP = "professional_help"       # 专业帮助
    GENERAL_WELLNESS = "general_wellness"         # 一般健康


# 情绪到知识分类的映射
EMOTION_TO_KNOWLEDGE_MAP = {
    "anxiety": [KnowledgeCategory.ANXIETY_HELP, KnowledgeCategory.STRESS_MANAGEMENT, KnowledgeCategory.EMOTIONAL_REGULATION],
    "depression": [KnowledgeCategory.DEPRESSION_SUPPORT, KnowledgeCategory.SELF_CARE, KnowledgeCategory.PROFESSIONAL_HELP],
    "stress": [KnowledgeCategory.STRESS_MANAGEMENT, KnowledgeCategory.COPING_STRATEGIES, KnowledgeCategory.MINDFULNESS],
    "anger": [KnowledgeCategory.EMOTIONAL_REGULATION, KnowledgeCategory.COPING_STRATEGIES, KnowledgeCategory.MINDFULNESS],
    "sadness": [KnowledgeCategory.EMOTIONAL_REGULATION, KnowledgeCategory.SELF_CARE, KnowledgeCategory.COPING_STRATEGIES],
    "loneliness": [KnowledgeCategory.RELATIONSHIP_ADVICE, KnowledgeCategory.SELF_CARE, KnowledgeCategory.COPING_STRATEGIES],
    "fear": [KnowledgeCategory.ANXIETY_HELP, KnowledgeCategory.COPING_STRATEGIES, KnowledgeCategory.EMOTIONAL_REGULATION],
    "joy": [KnowledgeCategory.GENERAL_WELLNESS, KnowledgeCategory.SELF_CARE, KnowledgeCategory.MINDFULNESS]
}


# 查询增强关键词
QUERY_ENHANCEMENT_KEYWORDS = {
    KnowledgeCategory.ANXIETY_HELP: ["焦虑", "担心", "紧张", "不安", "恐慌", "anxiety", "worry", "nervous"],
    KnowledgeCategory.DEPRESSION_SUPPORT: ["抑郁", "沮丧", "绝望", "无助", "低落", "depression", "hopeless", "sad"],
    KnowledgeCategory.STRESS_MANAGEMENT: ["压力", "紧张", "疲劳", "负担", "overwhelmed", "stress", "pressure"],
    KnowledgeCategory.EMOTIONAL_REGULATION: ["情绪", "感受", "调节", "控制", "管理", "emotion", "feeling", "regulation"],
    KnowledgeCategory.COPING_STRATEGIES: ["应对", "处理", "解决", "策略", "方法", "coping", "strategy", "handle"],
    KnowledgeCategory.MINDFULNESS: ["正念", "冥想", "专注", "当下", "觉察", "mindfulness", "meditation", "awareness"],
    KnowledgeCategory.SELF_CARE: ["自我关怀", "照顾自己", "休息", "放松", "self-care", "wellness", "relax"]
}


def _enhance_query_with_emotion(query: str, emotion_context: Optional[Dict[str, Any]]) -> str:
    """基于情绪上下文增强查询"""
    if not emotion_context:
        return query
    
    dominant_emotion = emotion_context.get("dominant_emotion", "")
    
    # 根据主导情绪添加相关关键词
    if dominant_emotion in EMOTION_TO_KNOWLEDGE_MAP:
        relevant_categories = EMOTION_TO_KNOWLEDGE_MAP[dominant_emotion]
        enhancement_keywords = []
        
        for category in relevant_categories[:2]:  # 只取前两个最相关的分类
            if category in QUERY_ENHANCEMENT_KEYWORDS:
                enhancement_keywords.extend(QUERY_ENHANCEMENT_KEYWORDS[category][:3])
        
        if enhancement_keywords:
            enhanced_query = f"{query} {' '.join(enhancement_keywords[:5])}"
            return enhanced_query
    
    return query


def _extract_conversation_keywords(conversation_context: Optional[List[Dict[str, str]]]) -> List[str]:
    """从对话上下文中提取关键词"""
    if not conversation_context:
        return []
    
    # 获取最近的几条消息
    recent_messages = conversation_context[-3:] if len(conversation_context) > 3 else conversation_context
    
    keywords = []
    for message in recent_messages:
        content = message.get("content", "")
        
        # 简单的关键词提取（实际应用中可以使用更复杂的NLP技术）
        important_words = [
            "工作", "家庭", "朋友", "学习", "健康", "睡眠", "关系", "未来",
            "压力", "焦虑", "抑郁", "愤怒", "悲伤", "孤独", "恐惧",
            "work", "family", "friend", "study", "health", "sleep", "relationship"
        ]
        
        for word in important_words:
            if word in content and word not in keywords:
                keywords.append(word)
    
    return keywords[:10]  # 限制关键词数量


def _simulate_vector_search(enhanced_query: str, max_results: int, similarity_threshold: float) -> List[Dict[str, Any]]:
    """模拟向量数据库搜索（实际应用中应该连接真实的向量数据库）"""
    
    # 模拟知识库数据
    mock_knowledge_base = [
        {
            "id": "kb_001",
            "title": "焦虑情绪的应对策略",
            "content": "当感到焦虑时，可以尝试深呼吸练习、渐进性肌肉放松、正念冥想等技巧。重要的是要接受焦虑是正常的情绪反应。",
            "category": KnowledgeCategory.ANXIETY_HELP,
            "tags": ["焦虑", "应对", "放松", "正念"],
            "similarity_score": 0.85
        },
        {
            "id": "kb_002",
            "title": "压力管理的有效方法",
            "content": "有效的压力管理包括：时间管理、设定优先级、适当休息、运动锻炼、寻求社会支持等。",
            "category": KnowledgeCategory.STRESS_MANAGEMENT,
            "tags": ["压力", "管理", "时间", "运动"],
            "similarity_score": 0.82
        },
        {
            "id": "kb_003",
            "title": "情绪调节技巧",
            "content": "情绪调节的关键是认识和接受自己的情绪，然后选择合适的应对方式。可以尝试情绪标记、重新评估、分散注意力等技巧。",
            "category": KnowledgeCategory.EMOTIONAL_REGULATION,
            "tags": ["情绪", "调节", "认识", "接受"],
            "similarity_score": 0.78
        },
        {
            "id": "kb_004",
            "title": "抑郁情绪的自我关怀",
            "content": "面对抑郁情绪时，自我关怀非常重要。包括保持规律作息、适度运动、营养均衡、寻求专业帮助等。",
            "category": KnowledgeCategory.DEPRESSION_SUPPORT,
            "tags": ["抑郁", "自我关怀", "作息", "专业帮助"],
            "similarity_score": 0.75
        },
        {
            "id": "kb_005",
            "title": "正念冥想入门指南",
            "content": "正念冥想是一种专注于当下的练习。从简单的呼吸觉察开始，每天5-10分钟，逐渐增加练习时间。",
            "category": KnowledgeCategory.MINDFULNESS,
            "tags": ["正念", "冥想", "呼吸", "专注"],
            "similarity_score": 0.72
        },
        {
            "id": "kb_006",
            "title": "建立健康的人际关系",
            "content": "健康的人际关系需要相互尊重、有效沟通、设定边界。学会表达自己的需求，同时也要倾听他人。",
            "category": KnowledgeCategory.RELATIONSHIP_ADVICE,
            "tags": ["人际关系", "沟通", "边界", "尊重"],
            "similarity_score": 0.70
        },
        {
            "id": "kb_007",
            "title": "何时寻求专业心理帮助",
            "content": "当情绪问题持续影响日常生活、工作或人际关系时，建议寻求专业心理咨询师或心理医生的帮助。",
            "category": KnowledgeCategory.PROFESSIONAL_HELP,
            "tags": ["专业帮助", "心理咨询", "心理医生"],
            "similarity_score": 0.68
        }
    ]
    
    # 基于查询内容和相似度阈值过滤结果
    query_lower = enhanced_query.lower()
    filtered_results = []
    
    for item in mock_knowledge_base:
        # 简单的相似度计算（实际应用中使用向量相似度）
        content_lower = item["content"].lower()
        title_lower = item["title"].lower()
        
        # 检查查询词是否在标题或内容中
        relevance_score = 0.0
        query_words = query_lower.split()
        
        for word in query_words:
            if word in title_lower:
                relevance_score += 0.3
            if word in content_lower:
                relevance_score += 0.2
            if any(word in tag.lower() for tag in item["tags"]):
                relevance_score += 0.1
        
        # 调整相似度分数
        adjusted_score = min(item["similarity_score"] + relevance_score * 0.1, 1.0)
        
        if adjusted_score >= similarity_threshold:
            item_copy = item.copy()
            item_copy["similarity_score"] = adjusted_score
            filtered_results.append(item_copy)
    
    # 按相似度排序并返回指定数量的结果
    filtered_results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return filtered_results[:max_results]


def _format_knowledge_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """格式化知识检索结果"""
    formatted_results = []
    
    for result in results:
        formatted_result = {
            "id": result["id"],
            "title": result["title"],
            "content": result["content"],
            "category": result["category"],
            "relevance_score": round(result["similarity_score"], 2),
            "tags": result["tags"],
            "summary": result["content"][:100] + "..." if len(result["content"]) > 100 else result["content"]
        }
        formatted_results.append(formatted_result)
    
    return formatted_results


def _generate_knowledge_insights(results: List[Dict[str, Any]], emotion_context: Optional[Dict[str, Any]]) -> List[str]:
    """基于检索结果生成知识洞察"""
    insights = []
    
    if not results:
        insights.append("未找到相关的专业知识，建议咨询专业心理健康专家。")
        return insights
    
    # 分析检索到的知识类别
    categories = [result["category"] for result in results]
    category_counts = {}
    for category in categories:
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # 生成基于类别的洞察
    if KnowledgeCategory.ANXIETY_HELP in category_counts:
        insights.append("找到了关于焦虑管理的专业建议，包括放松技巧和应对策略。")
    
    if KnowledgeCategory.DEPRESSION_SUPPORT in category_counts:
        insights.append("检索到抑郁情绪支持的相关资源，建议结合专业帮助。")
    
    if KnowledgeCategory.STRESS_MANAGEMENT in category_counts:
        insights.append("发现了有效的压力管理方法，可以帮助改善当前状况。")
    
    if KnowledgeCategory.MINDFULNESS in category_counts:
        insights.append("正念练习可能对当前的情绪状态有帮助。")
    
    # 基于情绪上下文的洞察
    if emotion_context:
        dominant_emotion = emotion_context.get("dominant_emotion", "")
        intensity = emotion_context.get("intensity", 0.0)
        
        if intensity > 0.7:
            insights.append("考虑到情绪强度较高，建议优先尝试立即可行的应对策略。")
        
        if dominant_emotion in ["depression", "anxiety"] and intensity > 0.6:
            insights.append("建议考虑寻求专业心理健康支持。")
    
    # 检索质量洞察
    avg_relevance = sum(result["relevance_score"] for result in results) / len(results)
    if avg_relevance > 0.8:
        insights.append("检索到的知识与您的情况高度相关。")
    elif avg_relevance > 0.6:
        insights.append("找到了一些相关的专业建议。")
    else:
        insights.append("建议进一步描述具体情况以获得更精准的建议。")
    
    return insights if insights else ["已为您检索相关的心理健康知识。"]


@tool(args_schema=KnowledgeRetrievalInput)
def retrieve_knowledge(
    query: str,
    user_id: str,
    emotion_context: Optional[Dict[str, Any]] = None,
    conversation_context: Optional[List[Dict[str, str]]] = None,
    max_results: int = 5,
    similarity_threshold: float = 0.7
) -> Dict[str, Any]:
    """
    从知识库中检索相关的心理健康知识。
    
    这个工具基于用户查询、情绪上下文和对话历史，
    从向量数据库中检索最相关的专业心理健康知识。
    """
    print(f"--- 执行知识检索工具，用户ID: {user_id} ---")
    
    try:
        # 基于情绪上下文增强查询
        enhanced_query = _enhance_query_with_emotion(query, emotion_context)
        
        # 从对话上下文提取关键词
        conversation_keywords = _extract_conversation_keywords(conversation_context)
        if conversation_keywords:
            enhanced_query += f" {' '.join(conversation_keywords[:3])}"
        
        print(f"增强后的查询: {enhanced_query}")
        
        # 执行向量搜索（这里使用模拟数据）
        search_results = _simulate_vector_search(enhanced_query, max_results, similarity_threshold)
        
        # 格式化结果
        formatted_results = _format_knowledge_results(search_results)
        
        # 生成知识洞察
        insights = _generate_knowledge_insights(formatted_results, emotion_context)
        
        # 计算检索质量指标
        retrieval_quality = {
            "total_found": len(formatted_results),
            "avg_relevance": round(sum(r["relevance_score"] for r in formatted_results) / len(formatted_results), 2) if formatted_results else 0.0,
            "categories_covered": len(set(r["category"] for r in formatted_results)),
            "query_enhancement_applied": enhanced_query != query
        }
        
        result = {
            "knowledge_results": formatted_results,
            "original_query": query,
            "enhanced_query": enhanced_query,
            "insights": insights,
            "retrieval_quality": retrieval_quality,
            "user_id": user_id,
            "total_results": len(formatted_results),
            "search_successful": len(formatted_results) > 0
        }
        
        # 记录知识检索日志
        logger.info(f"用户 {user_id} 知识检索完成，找到 {len(formatted_results)} 条相关知识")
        
        return result
        
    except Exception as e:
        logger.error(f"知识检索执行失败: {str(e)}")
        return {
            "error": f"知识检索失败: {str(e)}",
            "knowledge_results": [],
            "original_query": query,
            "enhanced_query": query,
            "insights": ["知识检索服务暂时不可用，建议稍后重试或咨询专业心理健康专家。"],
            "retrieval_quality": {
                "total_found": 0,
                "avg_relevance": 0.0,
                "categories_covered": 0,
                "query_enhancement_applied": False
            },
            "user_id": user_id,
            "total_results": 0,
            "search_successful": False
        }