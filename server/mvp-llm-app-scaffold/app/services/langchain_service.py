"""LangChain核心服务"""

import logging
from typing import List, Dict, Any, AsyncGenerator, Optional
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.output import LLMResult
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import ConversationChain
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

from ..core.config import settings

logger = logging.getLogger(__name__)


class StreamingCallbackHandler(BaseCallbackHandler):
    """流式输出回调处理器"""
    
    def __init__(self):
        self.tokens = []
        self.finished = False
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """处理新的token"""
        self.tokens.append(token)
    
    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """LLM结束时调用"""
        self.finished = True
    
    def get_tokens(self) -> List[str]:
        """获取所有tokens"""
        return self.tokens.copy()
    
    def clear(self):
        """清空tokens"""
        self.tokens.clear()
        self.finished = False


class LangChainService:
    """LangChain核心服务类"""
    
    def __init__(self):
        self.llm = None
        self.embeddings = None
        self.vectorstore = None
        self.memory = None
        self.conversation_chain = None
        self.streaming_handler = StreamingCallbackHandler()
        self._initialize_components()
    
    def _initialize_components(self):
        """初始化LangChain组件"""
        try:
            # 初始化LLM (DeepSeek)
            self._initialize_llm()
            
            # 初始化嵌入模型
            self._initialize_embeddings()
            
            # 初始化向量数据库
            self._initialize_vectorstore()
            
            # 初始化对话记忆
            self._initialize_memory()
            
            # 初始化对话链
            self._initialize_conversation_chain()
            
            logger.info("LangChain组件初始化成功")
            
        except Exception as e:
            logger.error(f"LangChain组件初始化失败: {e}")
            raise
    
    def _initialize_llm(self):
        """初始化DeepSeek LLM"""
        llm_config = settings.get_llm_config()
        
        self.llm = ChatOpenAI(
            openai_api_key=llm_config["openai_api_key"],
            openai_api_base=llm_config["openai_api_base"],
            model_name=llm_config["model_name"],
            temperature=llm_config["temperature"],
            max_tokens=llm_config["max_tokens"],
            streaming=llm_config["streaming"],
            callbacks=[self.streaming_handler]
        )
        
        logger.info(f"DeepSeek LLM初始化成功: {llm_config['model_name']}")
    
    def _initialize_embeddings(self):
        """初始化嵌入模型"""
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        logger.info(f"嵌入模型初始化成功: {settings.embedding_model_name}")
    
    def _initialize_vectorstore(self):
        """初始化Chroma向量数据库"""
        chroma_config = settings.get_chroma_config()
        
        self.vectorstore = Chroma(
            persist_directory=chroma_config["persist_directory"],
            embedding_function=self.embeddings,
            collection_name=chroma_config["collection_name"]
        )
        
        logger.info(f"Chroma向量数据库初始化成功: {chroma_config['collection_name']}")
    
    def _initialize_memory(self):
        """初始化对话记忆"""
        memory_config = settings.get_memory_config()
        
        self.memory = ConversationBufferWindowMemory(
            k=memory_config["window_size"],
            max_token_limit=memory_config["max_token_limit"],
            return_messages=memory_config["return_messages"],
            memory_key="chat_history",
            input_key="input",
            output_key="output"
        )
        
        logger.info("对话记忆初始化成功")
    
    def _initialize_conversation_chain(self):
        """初始化对话链"""
        # 心理健康咨询系统提示词
        system_prompt = """
        你是一位专业的心理健康咨询师，具有丰富的心理学知识和咨询经验。
        
        你的职责：
        1. 提供专业、温暖、非评判性的心理支持
        2. 倾听用户的困扰，给予理解和共情
        3. 运用心理学理论和技巧帮助用户
        4. 识别危机情况并提供适当的干预
        5. 鼓励用户寻求专业帮助当需要时
        
        你的原则：
        - 保持专业边界，不提供医学诊断
        - 尊重用户的感受和经历
        - 使用温暖、理解的语言
        - 关注用户的情绪状态
        - 提供实用的应对策略
        
        请用中文回应，语言要温暖、专业且易于理解。
        """
        
        # 创建提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        # 创建对话链
        self.conversation_chain = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt,
            verbose=True
        )
        
        logger.info("对话链初始化成功")
    
    async def chat_stream(self, message: str, user_id: str = None) -> AsyncGenerator[str, None]:
        """流式聊天响应"""
        try:
            # 清空之前的流式输出
            self.streaming_handler.clear()
            
            # 检查危机关键词
            if self._detect_crisis(message):
                crisis_response = settings.emergency_response
                for char in Crisis_response:
                    yield char
                return
            
            # 获取相关知识
            relevant_docs = await self._get_relevant_knowledge(message)
            
            # 构建增强的输入
            enhanced_input = self._build_enhanced_input(message, relevant_docs)
            
            # 异步调用对话链
            response = await self.conversation_chain.apredict(input=enhanced_input)
            
            # 流式返回响应
            for char in response:
                yield char
                
        except Exception as e:
            logger.error(f"流式聊天错误: {e}")
            raise  # 抛出真实异常以便调试
    
    async def chat(self, message: str, user_id: str = None) -> str:
        """普通聊天响应"""
        try:
            # 检查危机关键词
            if self._detect_crisis(message):
                return settings.emergency_response
            
            # 获取相关知识
            relevant_docs = await self._get_relevant_knowledge(message)
            
            # 构建增强的输入
            enhanced_input = self._build_enhanced_input(message, relevant_docs)
            
            # 调用对话链
            response = await self.conversation_chain.apredict(input=enhanced_input)
            
            return response
            
        except Exception as e:
            logger.error(f"聊天错误: {e}")
            raise  # 抛出真实异常以便调试
    
    async def _get_relevant_knowledge(self, query: str, k: int = 3) -> List[str]:
        """获取相关知识"""
        try:
            if self.vectorstore:
                docs = await self.vectorstore.asimilarity_search(query, k=k)
                return [doc.page_content for doc in docs]
            return []
        except Exception as e:
            logger.error(f"获取相关知识错误: {e}")
            return []
    
    def _build_enhanced_input(self, message: str, relevant_docs: List[str]) -> str:
        """构建增强的输入"""
        if relevant_docs:
            knowledge_context = "\n\n相关知识参考：\n" + "\n".join(relevant_docs)
            return f"{message}{knowledge_context}"
        return message
    
    def _detect_crisis(self, message: str) -> bool:
        """检测危机关键词"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in settings.crisis_keywords)
    
    def add_message_to_memory(self, human_message: str, ai_message: str):
        """添加消息到记忆"""
        try:
            self.memory.chat_memory.add_user_message(human_message)
            self.memory.chat_memory.add_ai_message(ai_message)
        except Exception as e:
            logger.error(f"添加消息到记忆错误: {e}")
    
    def clear_memory(self):
        """清空记忆"""
        try:
            self.memory.clear()
            logger.info("对话记忆已清空")
        except Exception as e:
            logger.error(f"清空记忆错误: {e}")
    
    def get_memory_messages(self) -> List[BaseMessage]:
        """获取记忆中的消息"""
        try:
            return self.memory.chat_memory.messages
        except Exception as e:
            logger.error(f"获取记忆消息错误: {e}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "llm_initialized": self.llm is not None,
            "embeddings_initialized": self.embeddings is not None,
            "vectorstore_initialized": self.vectorstore is not None,
            "memory_initialized": self.memory is not None,
            "conversation_chain_initialized": self.conversation_chain is not None
        }


# 全局LangChain服务实例
langchain_service = LangChainService()