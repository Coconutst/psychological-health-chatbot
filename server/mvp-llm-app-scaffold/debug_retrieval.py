#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试文档检索功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.tools.psychological_tools import retrieve_documents
from app.core.vector_store import get_vector_store
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_retrieve_documents():
    """测试文档检索功能"""
    print("=== 测试文档检索功能 ===")
    
    # 测试查询
    test_queries = [
        "我是谁",
        "我是一名软件工程大三的学生",
        "新疆大学",
        "学生",
        "软件工程"
    ]
    
    for query in test_queries:
        print(f"\n🔍 测试查询: '{query}'")
        
        # 直接测试向量存储
        try:
            vector_store = get_vector_store()
            docs = vector_store.similarity_search(query, k=5)
            print(f"   直接向量检索结果: {len(docs)} 个文档")
            for i, doc in enumerate(docs):
                print(f"   文档 {i+1}: {doc.page_content[:100]}...")
        except Exception as e:
            print(f"   直接向量检索失败: {e}")
        
        # 测试工具函数
        try:
            args = {
                "args": {
                    "user_input": query,
                    "intent": "knowledge",
                    "chat_history": []
                }
            }
            result = retrieve_documents(args)
            print(f"   工具函数检索结果: {result.get('document_count', 0)} 个文档")
            
            if result.get('retrieved_documents'):
                for i, doc in enumerate(result['retrieved_documents']):
                    print(f"   文档 {i+1}: {doc.get('content', '')[:100]}...")
            else:
                print(f"   错误信息: {result.get('error', '无错误信息')}")
                
        except Exception as e:
            print(f"   工具函数检索失败: {e}")

def test_vector_store_content():
    """检查向量存储中的内容"""
    print("\n=== 检查向量存储内容 ===")
    
    try:
        vector_store = get_vector_store()
        
        # 获取所有文档
        all_docs = vector_store.similarity_search("", k=100)  # 空查询获取所有文档
        print(f"向量存储中总共有 {len(all_docs)} 个文档")
        
        for i, doc in enumerate(all_docs[:5]):  # 只显示前5个
            print(f"文档 {i+1}:")
            print(f"  内容: {doc.page_content[:200]}...")
            print(f"  元数据: {doc.metadata}")
            print()
            
    except Exception as e:
        print(f"检查向量存储内容失败: {e}")

if __name__ == "__main__":
    test_vector_store_content()
    test_retrieve_documents()