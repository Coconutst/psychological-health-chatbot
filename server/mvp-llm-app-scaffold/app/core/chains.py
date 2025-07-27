# 导入类型提示模块
from typing import List, Optional
# 导入LangChain链相关模块
from langchain.chains import create_history_aware_retriever, create_retrieval_chain, LLMChain
# 导入文档组合链模块
from langchain.chains.combine_documents import create_stuff_documents_chain
# 导入代理相关模块
from langchain.agents import AgentExecutor, create_tool_calling_agent
# 导入对话记忆模块
from langchain.memory import ConversationBufferWindowMemory
# 导入聊天历史基础类
from langchain_core.chat_history import BaseChatMessageHistory
# 导入自定义工厂模块
from app.core.factories import create_llm_instance, get_tools
# 导入提示词模板模块
from app.core.prompts import (
    agent_prompt,
    rephrase_question_prompt,
    rag_answer_prompt,
    SIMPLE_CHAT_PROMPT,
    psychological_counselor_prompt,
    emotion_recognition_prompt,
    psychological_rag_prompt
)
# 导入向量存储模块
from app.core.vector_store import get_vector_store
# 旧的LangGraph多智能体架构已迁移到基于LangChain Tools的新架构
# 相关功能现在在 app.core.psychological_controller 中实现

# 创建RAG（检索增强生成）链的函数
def get_rag_chain():
    # 获取向量存储实例
    vector_store = get_vector_store()
    # 创建检索器
    retriever = vector_store.as_retriever()
    # 创建LLM实例
    llm = create_llm_instance()

    # 创建历史感知检索器，能够根据对话历史重新表述问题
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, rephrase_question_prompt
    )
    # 创建问答链，用于基于检索到的文档生成答案，使用心理健康专用RAG提示词
    question_answer_chain = create_stuff_documents_chain(llm, psychological_rag_prompt)
    # 组合检索器和问答链，创建完整的RAG链
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    # 返回RAG链
    return rag_chain

# 创建对话链的函数，支持工具调用和简单对话
def get_conversation_chain(
    tool_names: List[str],  # 工具名称列表
    chat_history_backend: Optional[BaseChatMessageHistory] = None,  # 可选的聊天历史后端
    memory_window_size: int =5 # 记忆窗口大小，默认为5
):
    # 创建LLM实例
    llm = create_llm_instance()
    # 根据工具名称获取工具列表
    tools = get_tools(tool_names)

    # 创建对话记忆，使用滑动窗口机制
    memory_kwargs = {
        "k": memory_window_size,  # 记忆窗口大小
        "memory_key": "chat_history",  # 记忆键名
        "return_messages": True,  # 返回消息格式
    }
    
    # 只有当chat_history_backend不为None时才添加chat_memory参数
    if chat_history_backend is not None:
        memory_kwargs["chat_memory"] = chat_history_backend
    
    memory = ConversationBufferWindowMemory(**memory_kwargs)

    # 如果提供了工具，创建代理链
    if tools:
        print("--- Creating Agent chain with tools ---")
        # 使用代理提示词模板
        prompt = agent_prompt
        # 创建工具调用代理
        agent = create_tool_calling_agent(llm, tools, prompt)
        # 返回代理执行器
        return AgentExecutor(
            agent=agent,  # 代理实例
            tools=tools,  # 工具列表
            memory=memory,  # 对话记忆
            verbose=True  # 启用详细输出
        )
    else:
        # 如果没有提供工具，创建简单的LLM链
        print("--- No tools provided, creating simple LLM chain ---")  # 打印调试信息，表示创建简单LLM链
        # 使用心理咨询师提示词模板代替简单聊天提示词
        prompt = psychological_counselor_prompt  # 分配心理咨询师提示词模板到prompt变量
        # 返回LLM链实例
        return LLMChain(
            llm=llm,  # LLM实例，用于生成响应
            prompt=prompt,  # 提示词模板，定义了AI的响应方式
            memory=memory,  # 对话记忆，用于保持会话上下文
            verbose=True  # 启用详细输出，用于调试
        )


# 新增：创建心理咨询对话链的函数，支持情绪识别
# 定义函数，接受工具名称、聊天历史后端和记忆窗口大小参数
def get_psychological_chain(
    tool_names: List[str],  # 工具名称列表，用于代理功能
    chat_history_backend: Optional[BaseChatMessageHistory] = None,  # 可选的聊天历史后端，用于存储会话历史
    memory_window_size: int = 5  # 记忆窗口大小，默认为5，控制保留的历史消息数量
):
    # 创建LLM实例，用于情绪识别和响应生成
    llm = create_llm_instance()  # 调用工厂函数创建ChatOpenAI实例
    
    # 创建对话记忆，使用滑动窗口机制保持最近的消息
    memory_kwargs = {
        "k": memory_window_size,  # 设置记忆窗口大小
        "memory_key": "chat_history",  # 设置记忆键名，用于提示词模板
        "return_messages": True  # 返回消息格式，便于处理
    }
    
    # 只有当chat_history_backend不为None时才添加chat_memory参数
    if chat_history_backend is not None:
        memory_kwargs["chat_memory"] = chat_history_backend
    
    memory = ConversationBufferWindowMemory(**memory_kwargs)
    
    # 创建情绪识别链，使用情绪识别提示词模板
    emotion_chain = LLMChain(
        llm=llm,  # LLM实例，用于生成情绪类别
        prompt=emotion_recognition_prompt,  # 情绪识别提示词模板
        verbose=True  # 启用详细输出，用于调试
    )
    
    # 创建心理咨询响应链，使用心理咨询师提示词模板
    response_chain = LLMChain(
        llm=llm,  # LLM实例，用于生成共情回应
        prompt=psychological_counselor_prompt,  # 心理咨询师提示词模板，包括{emotion}
        memory=memory,  # 对话记忆，用于保持上下文
        verbose=True  # 启用详细输出，用于调试
    )
    
    # 定义一个包装函数来顺序执行情绪识别和响应生成
    def psychological_invoke(input_dict: dict) -> dict:
        # 先识别情绪
        emotion_result = emotion_chain.invoke({"input": input_dict["input"]})  # 调用情绪链，传入用户输入
        emotion = emotion_result.get("text", "中性")  # 从结果中提取情绪类别，默认中性
        # 然后生成响应，传入情绪和输入
        response = response_chain.invoke({
            "input": input_dict["input"],  # 用户输入
            "emotion": emotion  # 识别出的情绪
        })  # 调用响应链
        return {"output": response.get("text")}  # 返回响应文本
    
    # 返回一个字典，模拟链的invoke方法
    return {"invoke": psychological_invoke}  # 返回自定义invoke函数的链对象


# 注意：原有的多智能体工作流链已迁移到基于LangChain Tools的新架构
# 新的实现位于 app/core/psychological_controller.py
# 详细信息请参考 LANGCHAIN_TOOLS_MIGRATION.md