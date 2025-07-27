#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多智能体工作流配置示例
展示如何配置和自定义多智能体系统
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

# 配置类定义
class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LLMProvider(Enum):
    """LLM提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    AZURE = "azure"

@dataclass
class LLMConfig:
    """LLM配置"""
    provider: LLMProvider
    model: str
    api_key: str = None
    base_url: str = None
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: int = 30
    max_retries: int = 3
    
    def __post_init__(self):
        # 从环境变量获取API密钥
        if not self.api_key:
            if self.provider == LLMProvider.OPENAI:
                self.api_key = os.getenv("OPENAI_API_KEY")
            elif self.provider == LLMProvider.ANTHROPIC:
                self.api_key = os.getenv("ANTHROPIC_API_KEY")
            elif self.provider == LLMProvider.GOOGLE:
                self.api_key = os.getenv("GOOGLE_API_KEY")

@dataclass
class WorkflowConfig:
    """工作流配置"""
    timeout_seconds: int = 180
    max_concurrent_agents: int = 5
    enable_parallel_execution: bool = True
    enable_caching: bool = True
    cache_ttl: int = 3600  # 缓存生存时间（秒）
    
@dataclass
class LoggingConfig:
    """日志配置"""
    level: LogLevel = LogLevel.INFO
    file_path: str = "multi_agent_workflow.log"
    max_file_size: str = "10MB"
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_console: bool = True
    enable_file: bool = True

@dataclass
class SafetyConfig:
    """安全配置"""
    enable_safety_check: bool = True
    crisis_keywords: List[str] = None
    emergency_contacts: Dict[str, str] = None
    intervention_threshold: float = 0.7
    
    def __post_init__(self):
        if self.crisis_keywords is None:
            self.crisis_keywords = [
                "自杀", "自残", "结束生命", "不想活", "死了算了",
                "suicide", "kill myself", "end my life", "want to die"
            ]
        
        if self.emergency_contacts is None:
            self.emergency_contacts = {
                "全国心理危机干预热线": "400-161-9995",
                "北京危机干预热线": "400-161-9995",
                "上海心理援助热线": "021-64383562",
                "急救电话": "120"
            }

@dataclass
class KnowledgeConfig:
    """知识库配置"""
    enable_retrieval: bool = True
    vector_store_type: str = "chroma"  # chroma, faiss, pinecone
    embedding_model: str = "text-embedding-ada-002"
    top_k: int = 5
    similarity_threshold: float = 0.7
    chunk_size: int = 1000
    chunk_overlap: int = 200

@dataclass
class AgentConfig:
    """智能体配置"""
    supervisor: Dict[str, Any] = None
    emotion: Dict[str, Any] = None
    safety: Dict[str, Any] = None
    knowledge: Dict[str, Any] = None
    response: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.supervisor is None:
            self.supervisor = {
                "confidence_threshold": 0.6,
                "intent_categories": ["consultation", "crisis", "general", "knowledge"],
                "enable_reasoning": True
            }
        
        if self.emotion is None:
            self.emotion = {
                "emotion_categories": ["happy", "sad", "angry", "anxious", "neutral"],
                "intensity_scale": (0.0, 1.0),
                "enable_detailed_analysis": True
            }
        
        if self.safety is None:
            self.safety = {
                "risk_levels": ["safe", "caution", "danger"],
                "assessment_criteria": [
                    "self_harm_indicators",
                    "suicide_ideation",
                    "violence_potential",
                    "substance_abuse"
                ]
            }
        
        if self.knowledge is None:
            self.knowledge = {
                "retrieval_method": "hybrid",  # semantic, keyword, hybrid
                "reranking_enabled": True,
                "max_documents": 10
            }
        
        if self.response is None:
            self.response = {
                "response_style": "empathetic",  # professional, empathetic, casual
                "max_length": 500,
                "include_resources": True
            }

@dataclass
class MultiAgentConfig:
    """多智能体系统总配置"""
    llm: LLMConfig
    workflow: WorkflowConfig
    logging: LoggingConfig
    safety: SafetyConfig
    knowledge: KnowledgeConfig
    agents: AgentConfig
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'MultiAgentConfig':
        """从字典创建配置"""
        return cls(
            llm=LLMConfig(**config_dict.get("llm", {})),
            workflow=WorkflowConfig(**config_dict.get("workflow", {})),
            logging=LoggingConfig(**config_dict.get("logging", {})),
            safety=SafetyConfig(**config_dict.get("safety", {})),
            knowledge=KnowledgeConfig(**config_dict.get("knowledge", {})),
            agents=AgentConfig(**config_dict.get("agents", {}))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "llm": self.llm.__dict__,
            "workflow": self.workflow.__dict__,
            "logging": self.logging.__dict__,
            "safety": self.safety.__dict__,
            "knowledge": self.knowledge.__dict__,
            "agents": self.agents.__dict__
        }

# 预定义配置模板
class ConfigTemplates:
    """配置模板"""
    
    @staticmethod
    def development_config() -> MultiAgentConfig:
        """开发环境配置"""
        return MultiAgentConfig(
            llm=LLMConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=1000
            ),
            workflow=WorkflowConfig(
                timeout_seconds=60,
                enable_parallel_execution=True,
                enable_caching=False
            ),
            logging=LoggingConfig(
                level=LogLevel.DEBUG,
                enable_console=True,
                enable_file=True
            ),
            safety=SafetyConfig(
                enable_safety_check=True,
                intervention_threshold=0.6
            ),
            knowledge=KnowledgeConfig(
                enable_retrieval=True,
                top_k=3
            ),
            agents=AgentConfig()
        )
    
    @staticmethod
    def production_config() -> MultiAgentConfig:
        """生产环境配置"""
        return MultiAgentConfig(
            llm=LLMConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-4",
                temperature=0.3,
                max_tokens=1500,
                max_retries=5
            ),
            workflow=WorkflowConfig(
                timeout_seconds=180,
                enable_parallel_execution=True,
                enable_caching=True,
                cache_ttl=7200
            ),
            logging=LoggingConfig(
                level=LogLevel.INFO,
                enable_console=False,
                enable_file=True,
                max_file_size="50MB",
                backup_count=10
            ),
            safety=SafetyConfig(
                enable_safety_check=True,
                intervention_threshold=0.8
            ),
            knowledge=KnowledgeConfig(
                enable_retrieval=True,
                top_k=5,
                similarity_threshold=0.8
            ),
            agents=AgentConfig()
        )
    
    @staticmethod
    def testing_config() -> MultiAgentConfig:
        """测试环境配置"""
        return MultiAgentConfig(
            llm=LLMConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-3.5-turbo",
                temperature=0.0,  # 确定性输出
                max_tokens=500
            ),
            workflow=WorkflowConfig(
                timeout_seconds=30,
                enable_parallel_execution=False,  # 简化测试
                enable_caching=False
            ),
            logging=LoggingConfig(
                level=LogLevel.DEBUG,
                enable_console=True,
                enable_file=False
            ),
            safety=SafetyConfig(
                enable_safety_check=True,
                intervention_threshold=0.5
            ),
            knowledge=KnowledgeConfig(
                enable_retrieval=False  # 简化测试
            ),
            agents=AgentConfig()
        )
    
    @staticmethod
    def local_config() -> MultiAgentConfig:
        """本地模型配置"""
        return MultiAgentConfig(
            llm=LLMConfig(
                provider=LLMProvider.OLLAMA,
                model="llama2",
                base_url="http://localhost:11434",
                temperature=0.7
            ),
            workflow=WorkflowConfig(
                timeout_seconds=300,  # 本地模型可能较慢
                enable_parallel_execution=False,
                enable_caching=True
            ),
            logging=LoggingConfig(
                level=LogLevel.INFO,
                enable_console=True,
                enable_file=True
            ),
            safety=SafetyConfig(
                enable_safety_check=True
            ),
            knowledge=KnowledgeConfig(
                enable_retrieval=True,
                vector_store_type="chroma"
            ),
            agents=AgentConfig()
        )

# 配置加载器
class ConfigLoader:
    """配置加载器"""
    
    @staticmethod
    def load_from_env() -> MultiAgentConfig:
        """从环境变量加载配置"""
        env = os.getenv("ENVIRONMENT", "development")
        
        if env == "production":
            return ConfigTemplates.production_config()
        elif env == "testing":
            return ConfigTemplates.testing_config()
        elif env == "local":
            return ConfigTemplates.local_config()
        else:
            return ConfigTemplates.development_config()
    
    @staticmethod
    def load_from_file(file_path: str) -> MultiAgentConfig:
        """从文件加载配置"""
        import json
        import yaml
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    config_dict = json.load(f)
                elif file_path.endswith(('.yml', '.yaml')):
                    config_dict = yaml.safe_load(f)
                else:
                    raise ValueError("不支持的配置文件格式")
            
            return MultiAgentConfig.from_dict(config_dict)
            
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return ConfigTemplates.development_config()
    
    @staticmethod
    def save_to_file(config: MultiAgentConfig, file_path: str):
        """保存配置到文件"""
        import json
        import yaml
        
        config_dict = config.to_dict()
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
                elif file_path.endswith(('.yml', '.yaml')):
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
                else:
                    raise ValueError("不支持的配置文件格式")
            
            print(f"配置已保存到: {file_path}")
            
        except Exception as e:
            print(f"保存配置文件失败: {e}")

# 示例使用
if __name__ == "__main__":
    # 创建开发环境配置
    dev_config = ConfigTemplates.development_config()
    print("开发环境配置:")
    print(f"LLM模型: {dev_config.llm.model}")
    print(f"日志级别: {dev_config.logging.level.value}")
    print(f"超时时间: {dev_config.workflow.timeout_seconds}秒")
    
    # 保存配置到文件
    ConfigLoader.save_to_file(dev_config, "config_dev.json")
    ConfigLoader.save_to_file(dev_config, "config_dev.yml")
    
    # 从环境变量加载配置
    env_config = ConfigLoader.load_from_env()
    print(f"\n当前环境配置: {env_config.llm.model}")
    
    # 自定义配置
    custom_config = MultiAgentConfig(
        llm=LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-sonnet-20240229",
            temperature=0.5
        ),
        workflow=WorkflowConfig(
            timeout_seconds=120,
            enable_parallel_execution=True
        ),
        logging=LoggingConfig(
            level=LogLevel.WARNING
        ),
        safety=SafetyConfig(),
        knowledge=KnowledgeConfig(),
        agents=AgentConfig()
    )
    
    print(f"\n自定义配置: {custom_config.llm.provider.value} - {custom_config.llm.model}")