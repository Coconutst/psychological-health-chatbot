"""危机检测工具 - 识别用户的心理危机状况"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


class CrisisDetectionInput(BaseModel):
    """危机检测输入参数"""
    message: str = Field(description="用户消息内容")
    user_id: str = Field(description="用户ID")
    conversation_history: Optional[List[str]] = Field(default=None, description="对话历史")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文信息")


class CrisisLevel:
    """危机等级定义"""
    NONE = 0      # 无危机
    LOW = 1       # 低风险
    MEDIUM = 2    # 中等风险
    HIGH = 3      # 高风险
    CRITICAL = 4  # 极高风险


# 危机关键词库
CRITICAL_KEYWORDS = [
    "自杀", "想死", "不想活", "结束生命", "了结自己", "自我了断",
    "跳楼", "上吊", "割腕", "服毒", "安眠药", "煤气",
    "死了算了", "活着没意思", "解脱", "一了百了",
    "suicide", "kill myself", "end my life", "want to die"
]

HIGH_RISK_KEYWORDS = [
    "绝望", "无助", "痛苦", "折磨", "煎熬", "崩溃",
    "看不到希望", "没有未来", "活着痛苦", "生不如死",
    "自残", "自伤", "伤害自己", "惩罚自己",
    "hopeless", "helpless", "can't go on", "no point"
]

MEDIUM_RISK_KEYWORDS = [
    "抑郁", "沮丧", "难过", "悲伤", "孤独", "空虚",
    "失眠", "噩梦", "焦虑", "恐慌", "害怕",
    "没有价值", "没用", "失败者", "废物",
    "depression", "sad", "lonely", "anxious", "worthless"
]

LOW_RISK_KEYWORDS = [
    "烦躁", "郁闷", "不开心", "心情不好", "压力大",
    "疲惫", "累", "困扰", "担心", "紧张",
    "upset", "tired", "stressed", "worried", "nervous"
]


def _analyze_message(message: str) -> int:
    """分析单条消息的危机等级"""
    message_lower = message.lower()
    
    # 检查极高风险关键词
    for keyword in CRITICAL_KEYWORDS:
        if keyword.lower() in message_lower:
            return CrisisLevel.CRITICAL
    
    # 检查高风险关键词
    high_risk_count = 0
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword.lower() in message_lower:
            high_risk_count += 1
    
    if high_risk_count >= 2:  # 多个高风险词汇
        return CrisisLevel.HIGH
    elif high_risk_count >= 1:
        return CrisisLevel.MEDIUM
    
    # 检查中等风险关键词
    medium_risk_count = 0
    for keyword in MEDIUM_RISK_KEYWORDS:
        if keyword.lower() in message_lower:
            medium_risk_count += 1
    
    if medium_risk_count >= 3:  # 多个中等风险词汇
        return CrisisLevel.MEDIUM
    elif medium_risk_count >= 1:
        return CrisisLevel.LOW
    
    # 检查低风险关键词
    for keyword in LOW_RISK_KEYWORDS:
        if keyword.lower() in message_lower:
            return CrisisLevel.LOW
    
    return CrisisLevel.NONE


def _analyze_conversation_history(history: List[str]) -> int:
    """分析对话历史的危机等级"""
    max_level = CrisisLevel.NONE
    
    # 分析最近的几条消息
    recent_messages = history[-5:] if len(history) > 5 else history
    
    for msg in recent_messages:
        level = _analyze_message(msg)
        max_level = max(max_level, level)
    
    # 如果历史中持续出现负面情绪，提升风险等级
    negative_count = sum(1 for msg in recent_messages 
                       if _analyze_message(msg) >= CrisisLevel.LOW)
    
    if negative_count >= 3 and max_level < CrisisLevel.HIGH:
        max_level = min(max_level + 1, CrisisLevel.HIGH)
    
    return max_level


def _analyze_context(context: Dict[str, Any]) -> int:
    """分析上下文信息的危机等级"""
    level = CrisisLevel.NONE
    
    # 检查用户画像中的风险因素
    if context.get('user_profile'):
        profile = context['user_profile']
        
        # 历史危机记录
        if profile.get('has_crisis_history'):
            level = max(level, CrisisLevel.LOW)
        
        # 心理健康状况
        mental_health = profile.get('mental_health_status')
        if mental_health in ['severe_depression', 'suicidal_ideation']:
            level = max(level, CrisisLevel.HIGH)
        elif mental_health in ['moderate_depression', 'anxiety_disorder']:
            level = max(level, CrisisLevel.MEDIUM)
    
    # 检查时间因素（深夜时段风险较高）
    if context.get('timestamp'):
        hour = context['timestamp'].hour
        if 0 <= hour <= 5:  # 深夜时段
            level = max(level, CrisisLevel.LOW)
    
    return level


def _generate_result(crisis_level: int, message: str, user_id: str) -> Dict[str, Any]:
    """生成检测结果"""
    level_names = {
        CrisisLevel.NONE: "无危机",
        CrisisLevel.LOW: "低风险",
        CrisisLevel.MEDIUM: "中等风险",
        CrisisLevel.HIGH: "高风险",
        CrisisLevel.CRITICAL: "极高风险"
    }
    
    # 生成建议措施
    recommendations = _get_recommendations(crisis_level)
    
    # 是否需要立即干预
    requires_intervention = crisis_level >= CrisisLevel.HIGH
    
    # 是否需要人工介入
    requires_human = crisis_level >= CrisisLevel.CRITICAL
    
    return {
        "crisis_level": crisis_level,
        "level_name": level_names[crisis_level],
        "requires_intervention": requires_intervention,
        "requires_human": requires_human,
        "recommendations": recommendations,
        "user_id": user_id,
        "confidence": _calculate_confidence(crisis_level, message)
    }


def _get_recommendations(crisis_level: int) -> List[str]:
    """根据危机等级获取建议措施"""
    if crisis_level == CrisisLevel.CRITICAL:
        return [
            "立即联系专业心理危机干预热线",
            "建议寻求紧急心理医疗帮助",
            "联系家人或朋友陪伴",
            "移除可能的自伤工具",
            "全国心理危机干预热线：400-161-9995"
        ]
    elif crisis_level == CrisisLevel.HIGH:
        return [
            "建议尽快寻求专业心理咨询",
            "联系信任的朋友或家人",
            "考虑预约心理医生",
            "保持规律作息和适度运动",
            "心理援助热线：400-161-9995"
        ]
    elif crisis_level == CrisisLevel.MEDIUM:
        return [
            "建议寻求心理咨询支持",
            "与朋友或家人分享感受",
            "尝试放松技巧如深呼吸",
            "保持健康的生活方式"
        ]
    elif crisis_level == CrisisLevel.LOW:
        return [
            "注意情绪变化",
            "尝试运动或其他放松活动",
            "与他人交流分享",
            "如情况持续请寻求帮助"
        ]
    else:
        return ["继续保持积极的心态"]


def _calculate_confidence(crisis_level: int, message: str) -> float:
    """计算检测置信度"""
    if crisis_level == CrisisLevel.NONE:
        return 0.9
    elif crisis_level == CrisisLevel.LOW:
        return 0.7
    elif crisis_level == CrisisLevel.MEDIUM:
        return 0.8
    elif crisis_level == CrisisLevel.HIGH:
        return 0.85
    else:  # CRITICAL
        return 0.95


# 使用装饰器方式创建工具函数
@tool(args_schema=CrisisDetectionInput)
def detect_crisis(message: str, user_id: str, conversation_history: Optional[List[str]] = None, 
                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    检测用户消息中的心理危机信号。
    
    这个工具用于识别用户是否存在自杀、自伤等高危行为倾向，
    并根据危机等级提供相应的干预建议。
    """
    print(f"--- 执行危机检测工具，用户ID: {user_id} ---")
    
    try:
        # 基础文本分析
        crisis_level = _analyze_message(message)
        
        # 历史对话分析（如果提供）
        if conversation_history:
            history_level = _analyze_conversation_history(conversation_history)
            crisis_level = max(crisis_level, history_level)
        
        # 上下文分析（如果提供）
        if context:
            context_level = _analyze_context(context)
            crisis_level = max(crisis_level, context_level)
        
        # 生成检测结果
        result = _generate_result(crisis_level, message, user_id)
        
        # 记录危机检测日志
        if crisis_level >= CrisisLevel.MEDIUM:
            logger.warning(f"检测到用户 {user_id} 存在心理危机，等级: {crisis_level}")
        
        return result
        
    except Exception as e:
        logger.error(f"危机检测执行失败: {str(e)}")
        return {
            "error": f"危机检测失败: {str(e)}",
            "crisis_level": CrisisLevel.NONE,
            "level_name": "检测失败",
            "requires_intervention": False,
            "requires_human": False,
            "recommendations": ["系统检测异常，建议联系技术支持"],
            "user_id": user_id,
            "confidence": 0.0
        }