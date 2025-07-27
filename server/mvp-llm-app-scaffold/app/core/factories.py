# 导入类型提示模块
from typing import List, Dict, Any

# 导入LangChain工具基础类
from langchain_core.tools import BaseTool
# 导入OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入向量存储相关模块
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# 导入应用配置和设置
from app.configs.settings import api_settings, config as app_config
# 导入天气工具
from app.core.tools.weather_tool import get_current_weather

# 外部工具注册表，用于管理可用的工具
EXTERNAL_TOOL_REGISTRY: Dict[str, BaseTool] = {
    "get_current_weather": get_current_weather,  # 注册天气查询工具
}


# 创建LLM实例的工厂函数
def create_llm_instance(llm_config: Dict[str, Any] = None) -> ChatOpenAI:
    # llm_config现在是可选的，默认为None
    # 合并用户配置和默认配置
    user_config = llm_config or {}
    # 构建完整的配置字典
    config = {
        "model": app_config.llm.name,  # 从应用配置获取模型名称
        "temperature": app_config.llm.temperature,  # 从应用配置获取温度参数
        **user_config,  # 合并用户自定义配置
    }
    
    # 根据provider选择合适的配置
    provider = app_config.llm.provider.lower()
    
    if provider in ["openai", "deepseek"]:
        # OpenAI兼容的API（包括DeepSeek）
        return ChatOpenAI(
            model=config["model"],  # 设置模型名称
            temperature=config["temperature"],  # 设置温度参数
            api_key=api_settings.OPENAI_API_KEY,  # 设置API密钥
            base_url=api_settings.OPENAI_BASE_URL,  # 设置基础URL
            max_tokens=getattr(app_config.llm, 'max_tokens', 512),  # 限制最大令牌数
            timeout=60,  # 设置60秒超时，支持并行工作流
            max_retries=3  # 增加重试次数到3次
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


# 根据工具名称列表获取工具实例的函数
def get_tools(tool_names: List[str]) -> List[BaseTool]:
    # 如果提供了工具名称列表
    if tool_names:
        # 从工具注册表中获取对应的工具实例
        return [
            EXTERNAL_TOOL_REGISTRY[name]  # 获取工具实例
            for name in tool_names  # 遍历工具名称
            if name in EXTERNAL_TOOL_REGISTRY  # 只返回已注册的工具
        ]
    else:
        # 如果没有提供工具名称，返回空列表
        return []


# 创建向量存储实例的工厂函数
def create_vector_store_instance(persist_directory: str = "./chroma_db") -> Chroma:
    """
    创建ChromaDB向量存储实例
    
    Args:
        persist_directory: ChromaDB持久化目录路径
        
    Returns:
        Chroma: ChromaDB向量存储实例
    """
    # 创建OpenAI嵌入模型实例
    embeddings = OpenAIEmbeddings(
        api_key=api_settings.OPENAI_API_KEY,
        base_url=api_settings.OPENAI_BASE_URL
    )
    
    # 创建并返回ChromaDB实例
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
