"""共情对话工具 - 生成具有共情能力的回应"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


class EmpathyDialogueInput(BaseModel):
    """共情对话输入参数"""
    user_message: str = Field(description="用户消息内容")
    emotion_analysis: Dict[str, Any] = Field(description="情绪分析结果")
    user_id: str = Field(description="用户ID")
    conversation_history: Optional[List[Dict[str, str]]] = Field(default=None, description="对话历史")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文信息")


class EmpathyStrategy:
    """共情策略定义"""
    VALIDATION = "validation"           # 情感验证
    REFLECTION = "reflection"           # 情感反映
    NORMALIZATION = "normalization"     # 情感正常化
    SUPPORT = "support"                 # 情感支持
    ENCOURAGEMENT = "encouragement"     # 鼓励
    GUIDANCE = "guidance"               # 引导
    ACTIVE_LISTENING = "active_listening" # 积极倾听
    REFRAMING = "reframing"             # 重新框架


# 共情回应模板库
EMPATHY_TEMPLATES = {
    "joy": {
        EmpathyStrategy.VALIDATION: [
            "我能感受到你的快乐，这真是太好了！",
            "看到你这么开心，我也为你感到高兴。",
            "你的喜悦之情溢于言表，这种感觉一定很棒。"
        ],
        EmpathyStrategy.ENCOURAGEMENT: [
            "保持这种积极的心态，你做得很好！",
            "这种正能量很珍贵，希望你能继续保持。",
            "你的快乐也感染了我，继续享受这美好的时刻吧。"
        ]
    },
    "sadness": {
        EmpathyStrategy.VALIDATION: [
            "我理解你现在的难过，这种感受是完全可以理解的。",
            "感到悲伤是很正常的，你不需要为此感到羞愧。",
            "我能感受到你内心的痛苦，你并不孤单。"
        ],
        EmpathyStrategy.SUPPORT: [
            "虽然现在很难过，但请记住这种感觉会过去的。",
            "我会陪伴你度过这个困难时期。",
            "你很勇敢地表达了自己的感受，这需要很大的勇气。"
        ],
        EmpathyStrategy.NORMALIZATION: [
            "每个人都会经历悲伤的时刻，这是人之常情。",
            "感到难过并不意味着你软弱，而是说明你是一个有感情的人。"
        ]
    },
    "anger": {
        EmpathyStrategy.VALIDATION: [
            "我能理解你为什么会感到愤怒，这种情绪是可以理解的。",
            "你的愤怒是有原因的，我听到了你的声音。",
            "感到生气是正常的，特别是在这种情况下。"
        ],
        EmpathyStrategy.GUIDANCE: [
            "愤怒是一种信号，告诉我们什么对我们很重要。",
            "让我们一起探讨一下，是什么让你感到如此愤怒。",
            "深呼吸可能会帮助你冷静下来，然后我们可以谈谈。"
        ]
    },
    "anxiety": {
        EmpathyStrategy.VALIDATION: [
            "焦虑的感觉确实很不舒服，我理解你现在的状态。",
            "很多人都会经历焦虑，你并不孤单。",
            "我能感受到你内心的不安，这一定很难受。"
        ],
        EmpathyStrategy.SUPPORT: [
            "让我们一步一步来处理这种焦虑感。",
            "你已经很勇敢地面对这些担忧了。",
            "焦虑虽然难受，但它也说明你很在乎。"
        ],
        EmpathyStrategy.GUIDANCE: [
            "试着专注于当下这一刻，深呼吸可能会有帮助。",
            "让我们一起分析一下你担心的具体是什么。"
        ]
    },
    "depression": {
        EmpathyStrategy.VALIDATION: [
            "我听到了你的痛苦，这种感觉一定很沉重。",
            "抑郁是一种真实的疾病，不是你的错。",
            "你能够表达这些感受，这已经是很大的进步了。"
        ],
        EmpathyStrategy.SUPPORT: [
            "即使在最黑暗的时刻，也有希望的光芒。",
            "你不需要独自承受这一切，我在这里陪伴你。",
            "每一小步都是进步，不要对自己太苛刻。"
        ],
        EmpathyStrategy.ENCOURAGEMENT: [
            "你比你想象的更坚强。",
            "寻求帮助是勇敢的表现，不是软弱。"
        ]
    },
    "fear": {
        EmpathyStrategy.VALIDATION: [
            "恐惧是一种保护机制，感到害怕是很自然的。",
            "我理解你的担心，这种感觉确实很不好受。",
            "面对未知会让人感到恐惧，这是人之常情。"
        ],
        EmpathyStrategy.SUPPORT: [
            "你不需要独自面对这些恐惧。",
            "一步一步来，我们可以慢慢克服这种恐惧。",
            "勇气不是没有恐惧，而是带着恐惧继续前行。"
        ]
    },
    "stress": {
        EmpathyStrategy.VALIDATION: [
            "我能感受到你承受的压力，这一定很累。",
            "现代生活确实充满压力，你的感受很真实。",
            "压力大的时候，人很容易感到疲惫和焦虑。"
        ],
        EmpathyStrategy.GUIDANCE: [
            "让我们一起找一些减压的方法。",
            "适当的休息和放松对缓解压力很重要。",
            "有时候，分解大任务为小步骤会让压力减轻。"
        ]
    },
    "loneliness": {
        EmpathyStrategy.VALIDATION: [
            "孤独感是很痛苦的，我理解你现在的感受。",
            "即使周围有很多人，有时候还是会感到孤独。",
            "你的孤独感是真实的，不要忽视这种感受。"
        ],
        EmpathyStrategy.SUPPORT: [
            "虽然你感到孤独，但你并不孤单，我在这里。",
            "连接和理解是人类的基本需求。",
            "分享你的感受是建立连接的第一步。"
        ]
    },
    "neutral": {
        EmpathyStrategy.ACTIVE_LISTENING: [
            "我在认真听你说，请继续分享你的想法。",
            "你的感受对我来说很重要，请告诉我更多。",
            "我想更好地理解你的情况。"
        ]
    }
}


# 共情增强词汇
EMPATHY_ENHANCERS = {
    "understanding": ["我理解", "我明白", "我能感受到", "我听到了"],
    "validation": ["这很正常", "你的感受是有效的", "这是可以理解的"],
    "support": ["我在这里", "你不孤单", "我们一起面对", "我支持你"],
    "encouragement": ["你很勇敢", "你做得很好", "你很坚强", "我相信你"]
}


def _select_empathy_strategy(emotion: str, intensity: float) -> str:
    """根据情绪选择共情策略"""
    if emotion in ["sadness", "depression", "loneliness"]:
        return EmpathyStrategy.VALIDATION if intensity > 0.6 else EmpathyStrategy.SUPPORT
    elif emotion in ["anger", "frustration"]:
        return EmpathyStrategy.VALIDATION if intensity > 0.7 else EmpathyStrategy.GUIDANCE
    elif emotion in ["anxiety", "fear", "stress"]:
        return EmpathyStrategy.SUPPORT if intensity > 0.5 else EmpathyStrategy.GUIDANCE
    elif emotion == "joy":
        return EmpathyStrategy.ENCOURAGEMENT
    else:
        return EmpathyStrategy.ACTIVE_LISTENING


def _get_empathy_template(emotion: str, strategy: str) -> str:
    """获取共情回应模板"""
    import random
    
    if emotion in EMPATHY_TEMPLATES and strategy in EMPATHY_TEMPLATES[emotion]:
        templates = EMPATHY_TEMPLATES[emotion][strategy]
        return random.choice(templates)
    
    # 默认回应
    default_responses = [
        "我听到了你的话，你的感受对我很重要。",
        "谢谢你与我分享这些，我想更好地理解你。",
        "我在这里倾听，请告诉我你需要什么样的支持。"
    ]
    return random.choice(default_responses)


def _enhance_response_with_empathy(base_response: str, emotion: str, intensity: float) -> str:
    """用共情词汇增强回应"""
    import random
    
    enhanced_response = base_response
    
    # 根据情绪强度添加共情增强词汇
    if intensity > 0.6:
        if emotion in ["sadness", "depression", "anxiety"]:
            enhancer = random.choice(EMPATHY_ENHANCERS["validation"])
            enhanced_response = f"{enhancer}。{enhanced_response}"
        elif emotion in ["anger", "frustration"]:
            enhancer = random.choice(EMPATHY_ENHANCERS["understanding"])
            enhanced_response = f"{enhancer}。{enhanced_response}"
    
    # 添加支持性语言
    if emotion in ["sadness", "depression", "loneliness", "anxiety"]:
        support = random.choice(EMPATHY_ENHANCERS["support"])
        enhanced_response += f" {support}。"
    
    return enhanced_response


def _analyze_conversation_context(conversation_history: Optional[List[Dict[str, str]]]) -> Dict[str, Any]:
    """分析对话上下文"""
    if not conversation_history:
        return {"is_first_interaction": True, "recurring_themes": [], "emotional_trend": "neutral"}
    
    # 简单的上下文分析
    recent_messages = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
    
    # 检查是否是首次互动
    is_first_interaction = len(conversation_history) <= 1
    
    # 检查重复主题（简化版）
    recurring_themes = []
    message_content = " ".join([msg.get("content", "") for msg in recent_messages])
    
    theme_keywords = {
        "work_stress": ["工作", "压力", "加班", "同事", "老板"],
        "relationship": ["关系", "朋友", "家人", "恋人", "分手"],
        "health": ["身体", "健康", "生病", "疲劳", "睡眠"],
        "future_worry": ["未来", "担心", "不确定", "迷茫", "选择"]
    }
    
    for theme, keywords in theme_keywords.items():
        if any(keyword in message_content for keyword in keywords):
            recurring_themes.append(theme)
    
    return {
        "is_first_interaction": is_first_interaction,
        "recurring_themes": recurring_themes,
        "emotional_trend": "mixed"  # 简化处理
    }


def _generate_personalized_response(emotion: str, strategy: str, context: Dict[str, Any], user_message: str) -> str:
    """生成个性化回应"""
    base_template = _get_empathy_template(emotion, strategy)
    
    # 根据上下文调整回应
    if context.get("is_first_interaction", False):
        greeting = "很高兴认识你。"
        base_template = f"{greeting}{base_template}"
    
    # 根据重复主题调整
    recurring_themes = context.get("recurring_themes", [])
    if "work_stress" in recurring_themes:
        base_template += " 工作压力确实是现代人常面临的挑战。"
    elif "relationship" in recurring_themes:
        base_template += " 人际关系的问题往往很复杂，需要时间来处理。"
    
    return base_template


@tool(args_schema=EmpathyDialogueInput)
def generate_empathy_response(
    user_message: str,
    emotion_analysis: Dict[str, Any],
    user_id: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    生成具有共情能力的回应。
    
    这个工具基于用户的情绪状态和对话上下文，
    生成温暖、理解和支持性的回应。
    """
    print(f"--- 执行共情对话工具，用户ID: {user_id} ---")
    
    try:
        # 提取情绪信息
        dominant_emotion = emotion_analysis.get("dominant_emotion", "neutral")
        intensity = emotion_analysis.get("intensity", 0.0)
        insights = emotion_analysis.get("insights", [])
        
        # 选择共情策略
        strategy = _select_empathy_strategy(dominant_emotion, intensity)
        
        # 分析对话上下文
        conversation_context = _analyze_conversation_context(conversation_history)
        
        # 生成个性化回应
        empathy_response = _generate_personalized_response(
            dominant_emotion, strategy, conversation_context, user_message
        )
        
        # 用共情词汇增强回应
        enhanced_response = _enhance_response_with_empathy(
            empathy_response, dominant_emotion, intensity
        )
        
        # 生成回应建议
        response_suggestions = []
        if dominant_emotion in ["sadness", "depression"]:
            response_suggestions.extend([
                "询问用户是否需要专业帮助",
                "提供情感支持资源",
                "建议适当的自我关怀活动"
            ])
        elif dominant_emotion in ["anxiety", "stress"]:
            response_suggestions.extend([
                "提供放松技巧",
                "建议分解问题的方法",
                "推荐压力管理策略"
            ])
        elif dominant_emotion == "anger":
            response_suggestions.extend([
                "引导冷静思考",
                "探索愤怒背后的需求",
                "提供情绪调节技巧"
            ])
        
        result = {
            "empathy_response": enhanced_response,
            "strategy_used": strategy,
            "emotion_addressed": dominant_emotion,
            "response_tone": "supportive" if intensity > 0.5 else "gentle",
            "suggestions": response_suggestions,
            "context_factors": conversation_context,
            "user_id": user_id,
            "confidence": min(0.9, 0.6 + (intensity * 0.3))  # 基于情绪强度调整置信度
        }
        
        # 记录共情回应日志
        logger.info(f"用户 {user_id} 共情回应生成完成，策略: {strategy}, 情绪: {dominant_emotion}")
        
        return result
        
    except Exception as e:
        logger.error(f"共情回应生成失败: {str(e)}")
        return {
            "error": f"共情回应生成失败: {str(e)}",
            "empathy_response": "我听到了你的话，虽然我现在无法完全理解你的感受，但我想让你知道，我在这里倾听。",
            "strategy_used": "fallback",
            "emotion_addressed": "unknown",
            "response_tone": "neutral",
            "suggestions": ["联系技术支持"],
            "context_factors": {},
            "user_id": user_id,
            "confidence": 0.0
        }