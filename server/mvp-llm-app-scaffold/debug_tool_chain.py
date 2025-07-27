#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试工具链执行流程
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入必要的模块
from app.core.tools.psychological_controller import PsychologicalChatController
from app.core.tools.psychological_tools import (
    analyze_intent,
    check_safety,
    retrieve_documents,
    rerank_documents,
    generate_answer
)

async def test_individual_tools():
    """测试各个工具的独立功能"""
    print("\n=== 测试各个工具的独立功能 ===")
    
    test_input = "我是谁？"
    chat_history = []
    
    # 1. 测试意图分析
    print("\n1. 测试意图分析工具")
    try:
        intent_result = await asyncio.to_thread(
            analyze_intent, 
            {"args": {"user_input": test_input, "chat_history": chat_history}}
        )
        print(f"意图分析结果: {intent_result}")
        intent = intent_result.get('intent', 'consultation')
    except Exception as e:
        print(f"意图分析失败: {e}")
        intent = 'consultation'
    
    # 2. 测试安全检查
    print("\n2. 测试安全检查工具")
    try:
        safety_result = await asyncio.to_thread(
            check_safety, 
            {"args": {"user_input": test_input, "chat_history": chat_history}}
        )
        print(f"安全检查结果: {safety_result}")
    except Exception as e:
        print(f"安全检查失败: {e}")
    
    # 3. 测试文档检索
    print("\n3. 测试文档检索工具")
    try:
        retrieval_result = await asyncio.to_thread(
            retrieve_documents, 
            {"args": {"user_input": test_input, "intent": intent, "chat_history": chat_history}}
        )
        print(f"文档检索结果: {retrieval_result}")
        documents = retrieval_result.get('retrieved_documents', [])
        print(f"检索到的文档数量: {len(documents)}")
        if documents:
            print(f"第一个文档内容: {documents[0][:200] if isinstance(documents[0], str) else documents[0]}")
    except Exception as e:
        print(f"文档检索失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        documents = []
    
    # 4. 测试文档重排序（如果有文档）
    if documents:
        print("\n4. 测试文档重排序工具")
        try:
            rerank_result = await asyncio.to_thread(
                rerank_documents, 
                {"args": {"user_input": test_input, "documents": documents}}
            )
            print(f"文档重排序结果: {rerank_result}")
            documents = rerank_result.get('reranked_documents', documents)
        except Exception as e:
            print(f"文档重排序失败: {e}")
    
    # 5. 测试答案生成
    print("\n5. 测试答案生成工具")
    try:
        answer_result = await asyncio.to_thread(
            generate_answer,
            {
                "args": {
                    "user_input": test_input,
                    "intent": intent,
                    "documents": documents,
                    "chat_history": chat_history,
                    "safety_triggered": False
                }
            }
        )
        print(f"答案生成结果: {answer_result}")
    except Exception as e:
        print(f"答案生成失败: {e}")

async def test_controller():
    """测试控制器的完整流程"""
    print("\n=== 测试控制器的完整流程 ===")
    
    controller = PsychologicalChatController()
    test_input = "我是谁？"
    chat_history = []
    
    try:
        result = await controller.process_message(test_input, chat_history)
        print(f"\n控制器处理结果:")
        print(f"- 回复: {result.get('response', '')[:200]}...")
        print(f"- 意图: {result.get('intent', '')}")
        print(f"- 置信度: {result.get('confidence', 0)}")
        print(f"- 情绪: {result.get('emotion', '')}")
        print(f"- 文档数量: {result.get('documents_count', 0)}")
        print(f"- 安全触发: {result.get('safety_triggered', False)}")
        print(f"- 执行时间: {result.get('execution_time', 0):.2f}秒")
        
        if 'metadata' in result:
            metadata = result['metadata']
            print(f"\n元数据信息:")
            print(f"- 工作流路径: {metadata.get('workflow_path', '')}")
            
            if 'document_retrieval' in metadata and metadata['document_retrieval']:
                print(f"- 文档检索详情: {metadata['document_retrieval']}")
            else:
                print(f"- 文档检索详情: 无或为空")
                
    except Exception as e:
        print(f"控制器处理失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")

async def test_with_different_queries():
    """测试不同类型的查询"""
    print("\n=== 测试不同类型的查询 ===")
    
    controller = PsychologicalChatController()
    test_queries = [
        "我是谁？",
        "新疆大学有什么专业？",
        "软件工程专业怎么样？",
        "我感到很焦虑",
        "心理健康的重要性"
    ]
    
    for query in test_queries:
        print(f"\n--- 测试查询: {query} ---")
        try:
            result = await controller.process_message(query, [])
            print(f"意图: {result.get('intent', '')}")
            print(f"文档数量: {result.get('documents_count', 0)}")
            print(f"回复长度: {len(result.get('response', ''))}")
        except Exception as e:
            print(f"查询失败: {e}")

async def main():
    """主函数"""
    print("开始调试工具链执行流程...")
    
    # 测试各个工具的独立功能
    await test_individual_tools()
    
    # 测试控制器的完整流程
    await test_controller()
    
    # 测试不同类型的查询
    await test_with_different_queries()
    
    print("\n调试完成！")

if __name__ == "__main__":
    asyncio.run(main())