# 导入类型提示模块
from typing import Optional

# 导入YAML配置文件处理模块
import yaml
# 导入Pydantic数据验证模块
from pydantic import BaseModel, Field
# 导入Pydantic设置管理模块
from pydantic_settings import BaseSettings, SettingsConfigDict
# 导入路径处理模块
from pathlib import Path

# 项目根目录配置
ROOT = Path(__file__).resolve().parent.parent.parent


# 定义LLM模型配置数据模型
class ModelConfig(BaseModel):
    # 模型提供商（如openai、local等）
    provider: str
    # 模型名称
    name: str
    # 生成温度参数，控制输出的随机性
    temperature: float


# 定义嵌入模型配置数据模型
class EmbeddingConfig(BaseModel):
    # 嵌入模型提供商
    provider: str
    # 嵌入模型名称
    name: str


# 定义向量数据库配置数据模型
class VectorStoreConfig(BaseModel):
    # 向量数据库持久化目录
    persist_directory: str
    # 向量数据库集合名称
    collection_name: str


# 定义文本分割器配置数据模型
class TextSplitterConfig(BaseModel):
    # 文本块大小
    chunk_size: int
    # 文本块重叠大小
    chunk_overlap: int


# 定义整体配置数据模型
class Config(BaseModel):
    # LLM模型配置
    llm: ModelConfig
    # 嵌入模型配置
    embedding: EmbeddingConfig
    # 向量数据库配置
    vector_store: VectorStoreConfig
    # 文本分割器配置
    text_splitter: TextSplitterConfig
    


# 加载配置文件函数
def load_config(config_path: Path = ROOT / "app/configs/model_config.yaml") -> Config:
    # 打开并读取YAML配置文件
    with open(config_path, "r", encoding="utf-8") as f:
        # 解析YAML内容为Python字典
        config_data = yaml.safe_load(f)
    # 将配置数据转换为Config对象
    return Config(**config_data)


# 定义API设置类，用于管理环境变量和API配置
class APISettings(BaseSettings):
    # 配置从.env文件加载设置
    model_config = SettingsConfigDict(env_file=str(ROOT / ".env"), env_file_encoding="utf-8")

    # LLM API密钥（支持OpenAI、DeepSeek等兼容API）
    OPENAI_API_KEY: str

    # LLM API基础URL（可选，支持自定义端点如DeepSeek）
    OPENAI_BASE_URL: Optional[str] = Field(default=None, alias="OPENAI_BASE_URL")
    
    # CORS允许的来源地址（可选，从环境变量加载）
    ALLOWED_ORIGINS: Optional[str] = Field(default=None, alias="ALLOWED_ORIGINS")
    
    # MySQL数据库配置
    MYSQL_HOST: str = Field(default="localhost", alias="MYSQL_HOST")
    MYSQL_PORT: int = Field(default=3306, alias="MYSQL_PORT")
    MYSQL_USER: str = Field(default="root", alias="MYSQL_USER")
    MYSQL_PASSWORD: str = Field(default="", alias="MYSQL_PASSWORD")
    MYSQL_DATABASE: str = Field(default="psychological_chatbot", alias="MYSQL_DATABASE")


# 创建全局设置和配置实例，供整个应用程序使用
api_settings = APISettings()
config = load_config()

# 将API密钥设置到环境变量中，供Langchain使用
import os

# 设置LLM API密钥环境变量（支持OpenAI、DeepSeek等）
os.environ["OPENAI_API_KEY"] = api_settings.OPENAI_API_KEY

# 如果配置了LLM API基础URL，也设置到环境变量中
if api_settings.OPENAI_BASE_URL:
    os.environ["OPENAI_BASE_URL"] = api_settings.OPENAI_BASE_URL


# 获取设置函数，供其他模块调用
def get_settings() -> APISettings:
    """获取API设置实例"""
    return api_settings


# 获取配置函数，供其他模块调用
def get_config() -> Config:
    """获取配置实例"""
    return config