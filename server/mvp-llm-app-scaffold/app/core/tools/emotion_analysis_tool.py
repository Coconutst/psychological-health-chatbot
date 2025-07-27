"""情绪分析工具 - 识别和分析用户的情绪状态"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


class EmotionAnalysisInput(BaseModel):
    """情绪分析输入参数"""
    message: str = Field(description="用户消息内容")
    user_id: str = Field(description="用户ID")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文信息")


class EmotionType:
    """情绪类型定义"""
    # 基础情绪
    JOY = "joy"           # 快乐
    SADNESS = "sadness"   # 悲伤
    ANGER = "anger"       # 愤怒
    FEAR = "fear"         # 恐惧
    SURPRISE = "surprise" # 惊讶
    DISGUST = "disgust"   # 厌恶
    
    # 复合情绪
    ANXIETY = "anxiety"   # 焦虑
    DEPRESSION = "depression" # 抑郁
    EXCITEMENT = "excitement" # 兴奋
    FRUSTRATION = "frustration" # 挫折
    HOPE = "hope"         # 希望
    LONELINESS = "loneliness" # 孤独
    STRESS = "stress"     # 压力
    CALM = "calm"         # 平静
    NEUTRAL = "neutral"   # 中性


# 情绪关键词库
EMOTION_KEYWORDS = {
    EmotionType.JOY: [
        "开心", "快乐", "高兴", "愉快", "兴奋", "满足", "幸福", "欣喜",
        "happy", "joy", "glad", "pleased", "delighted", "cheerful"
    ],
    EmotionType.SADNESS: [
        "难过", "悲伤", "伤心", "沮丧", "失落", "郁闷", "心情不好",
        "sad", "sorrow", "grief", "melancholy", "down", "blue"
    ],
    EmotionType.ANGER: [
        "愤怒", "生气", "恼火", "气愤", "暴躁", "愤恨", "恼怒",
        "angry", "mad", "furious", "rage", "irritated", "annoyed"
    ],
    EmotionType.FEAR: [
        "害怕", "恐惧", "担心", "忧虑", "紧张", "不安", "惊慌",
        "afraid", "scared", "fearful", "terrified", "worried", "nervous"
    ],
    EmotionType.ANXIETY: [
        "焦虑", "焦急", "不安", "紧张", "担忧", "忐忑", "心慌",
        "anxious", "anxiety", "restless", "uneasy", "apprehensive"
    ],
    EmotionType.DEPRESSION: [
        "抑郁", "绝望", "无助", "空虚", "麻木", "消沉", "低落",
        "depressed", "hopeless", "helpless", "empty", "numb", "despair"
    ],
    EmotionType.STRESS: [
        "压力", "紧张", "疲惫", "累", "疲劳", "负担", "重压",
        "stress", "stressed", "pressure", "overwhelmed", "exhausted", "tired"
    ],
    EmotionType.LONELINESS: [
        "孤独", "寂寞", "孤单", "独自", "无人理解", "被遗忘",
        "lonely", "alone", "isolated", "solitary", "abandoned"
    ],
    EmotionType.HOPE: [
        "希望", "期待", "憧憬", "向往", "乐观", "信心", "期望",
        "hope", "hopeful", "optimistic", "confident", "expectant"
    ],
    EmotionType.CALM: [
        "平静", "冷静", "安静", "宁静", "放松", "舒缓", "淡定",
        "calm", "peaceful", "relaxed", "serene", "tranquil", "composed"
    ]
}


def _analyze_emotion_keywords(message: str) -> Dict[str, float]:
    """基于关键词分析情绪"""
    message_lower = message.lower()
    emotion_scores = {emotion: 0.0 for emotion in EMOTION_KEYWORDS.keys()}
    
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in message_lower:
                emotion_scores[emotion] += 1.0
    
    # 归一化分数
    total_score = sum(emotion_scores.values())
    if total_score > 0:
        emotion_scores = {k: v / total_score for k, v in emotion_scores.items()}
    
    return emotion_scores


def _analyze_emotion_patterns(message: str) -> Dict[str, float]:
    """基于语言模式分析情绪"""
    message_lower = message.lower()
    pattern_scores = {}
    
    # 问号模式（可能表示困惑或寻求帮助）
    question_count = message.count('?') + message.count('？')
    if question_count > 0:
        pattern_scores['confusion'] = min(question_count * 0.3, 1.0)
    
    # 感叹号模式（可能表示强烈情绪）
    exclamation_count = message.count('!') + message.count('！')
    if exclamation_count > 0:
        pattern_scores['intensity'] = min(exclamation_count * 0.2, 1.0)
    
    # 重复字符模式（可能表示强调或情绪激动）
    import re
    repeated_chars = re.findall(r'(.)\1{2,}', message)
    if repeated_chars:
        pattern_scores['emphasis'] = min(len(repeated_chars) * 0.2, 1.0)
    
    # 否定词模式
    negative_words = ['不', '没', '无', '非', 'not', 'no', 'never', 'nothing']
    negative_count = sum(1 for word in negative_words if word in message_lower)
    if negative_count > 0:
        pattern_scores['negativity'] = min(negative_count * 0.3, 1.0)
    
    return pattern_scores


def _calculate_emotion_intensity(emotion_scores: Dict[str, float], patterns: Dict[str, float]) -> float:
    """计算情绪强度"""
    base_intensity = max(emotion_scores.values()) if emotion_scores else 0.0
    
    # 根据语言模式调整强度
    intensity_modifier = 1.0
    if patterns.get('intensity', 0) > 0:
        intensity_modifier += patterns['intensity'] * 0.5
    if patterns.get('emphasis', 0) > 0:
        intensity_modifier += patterns['emphasis'] * 0.3
    
    return min(base_intensity * intensity_modifier, 1.0)


def _get_dominant_emotion(emotion_scores: Dict[str, float]) -> str:
    """获取主导情绪"""
    if not emotion_scores or max(emotion_scores.values()) == 0:
        return EmotionType.NEUTRAL
    
    return max(emotion_scores, key=emotion_scores.get)


def _generate_emotion_insights(dominant_emotion: str, intensity: float, patterns: Dict[str, float]) -> List[str]:
    """生成情绪洞察"""
    insights = []
    
    # 基于主导情绪的洞察
    if dominant_emotion == EmotionType.SADNESS:
        insights.append("检测到悲伤情绪，可能需要情感支持")
    elif dominant_emotion == EmotionType.ANXIETY:
        insights.append("检测到焦虑情绪，建议尝试放松技巧")
    elif dominant_emotion == EmotionType.ANGER:
        insights.append("检测到愤怒情绪，建议冷静处理")
    elif dominant_emotion == EmotionType.DEPRESSION:
        insights.append("检测到抑郁情绪，建议寻求专业帮助")
    elif dominant_emotion == EmotionType.JOY:
        insights.append("检测到积极情绪，保持良好状态")
    elif dominant_emotion == EmotionType.STRESS:
        insights.append("检测到压力情绪，建议适当休息")
    
    # 基于强度的洞察
    if intensity > 0.7:
        insights.append("情绪强度较高，需要特别关注")
    elif intensity > 0.4:
        insights.append("情绪强度中等，建议适当调节")
    
    # 基于语言模式的洞察
    if patterns.get('negativity', 0) > 0.5:
        insights.append("表达中包含较多负面词汇")
    if patterns.get('confusion', 0) > 0.3:
        insights.append("可能存在困惑或需要澄清")
    
    return insights if insights else ["情绪状态相对稳定"]


@tool(args_schema=EmotionAnalysisInput)
def analyze_emotion(message: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    分析用户消息中的情绪状态。
    
    这个工具用于识别用户的情绪类型、强度和相关洞察，
    帮助系统更好地理解用户的心理状态。
    """
    print(f"--- 执行情绪分析工具，用户ID: {user_id} ---")
    
    try:
        # 基于关键词的情绪分析
        emotion_scores = _analyze_emotion_keywords(message)
        
        # 基于语言模式的分析
        patterns = _analyze_emotion_patterns(message)
        
        # 计算情绪强度
        intensity = _calculate_emotion_intensity(emotion_scores, patterns)
        
        # 获取主导情绪
        dominant_emotion = _get_dominant_emotion(emotion_scores)
        
        # 生成洞察
        insights = _generate_emotion_insights(dominant_emotion, intensity, patterns)
        
        # 情绪稳定性评估
        stability = "stable" if intensity < 0.5 else "unstable" if intensity > 0.7 else "moderate"
        
        result = {
            "dominant_emotion": dominant_emotion,
            "emotion_scores": emotion_scores,
            "intensity": round(intensity, 2),
            "stability": stability,
            "patterns": patterns,
            "insights": insights,
            "user_id": user_id,
            "confidence": round(max(emotion_scores.values()) if emotion_scores else 0.0, 2)
        }
        
        # 记录情绪分析日志
        logger.info(f"用户 {user_id} 情绪分析完成，主导情绪: {dominant_emotion}, 强度: {intensity}")
        
        return result
        
    except Exception as e:
        logger.error(f"情绪分析执行失败: {str(e)}")
        return {
            "error": f"情绪分析失败: {str(e)}",
            "dominant_emotion": EmotionType.NEUTRAL,
            "emotion_scores": {},
            "intensity": 0.0,
            "stability": "unknown",
            "patterns": {},
            "insights": ["情绪分析异常，建议联系技术支持"],
            "user_id": user_id,
            "confidence": 0.0
        }