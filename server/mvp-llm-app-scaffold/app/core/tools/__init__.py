"""心理健康聊天机器人工具模块"""

# 注释掉不存在的base模块导入
# from ..base import PsychologyBaseTool, ToolRegistry, tool_registry
from .weather_tool import get_current_weather
from .crisis_detection_tool import detect_crisis
from .emotion_analysis_tool import analyze_emotion
from .empathy_dialogue_tool import generate_empathy_response
from .knowledge_retrieval_tool import retrieve_knowledge

__all__ = [
    # "PsychologyBaseTool",
    # "ToolRegistry",
    # "tool_registry",
    "get_current_weather",
    "detect_crisis",
    "analyze_emotion",
    "generate_empathy_response",
    "retrieve_knowledge",
    # "user_auth_tool"  # 暂时注释掉，文件不存在
]