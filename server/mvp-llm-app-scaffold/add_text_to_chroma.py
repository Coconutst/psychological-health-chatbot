#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向Chroma向量数据库添加文本
"""

import os
import sys
import logging
from typing import List, Dict, Any

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def add_text_to_chroma(text: str, metadata: Dict[str, Any] | None = None):
    """向Chroma向量数据库添加文本"""
    try:
        import chromadb
        from langchain_community.vectorstores import Chroma
        from langchain_openai import OpenAIEmbeddings
        
        logger.info("开始向Chroma数据库添加文本...")
        
        persist_directory = "./chroma_db"
        
        # 尝试使用本地BGE模型
        try:
            from sentence_transformers import SentenceTransformer
            from langchain.embeddings.base import Embeddings
            
            class BGEEmbeddings(Embeddings):
                def __init__(self, model_path):
                    self.model = SentenceTransformer(model_path)
                
                def embed_documents(self, texts):
                    return self.model.encode(texts).tolist()
                
                def embed_query(self, text):
                    return self.model.encode([text])[0].tolist()
            
            model_path = "./models/bge-small-zh"
            embeddings = BGEEmbeddings(model_path)
            logger.info(f"使用本地BGE模型: {model_path}")
        except Exception as e:
            logger.warning(f"本地BGE模型加载失败: {e}，尝试使用OpenAI embeddings")
            try:
                embeddings = OpenAIEmbeddings()
                logger.info("使用OpenAI embeddings")
            except Exception as e2:
                logger.error(f"OpenAI embeddings初始化失败: {e2}")
                return False
        
        # 检查是否存在现有的Chroma数据库
        if os.path.exists(persist_directory):
            logger.info(f"加载现有Chroma数据库: {persist_directory}")
            vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings
            )
            
            # 检查数据库中的文档数量
            try:
                collection = vectorstore._collection
                result = collection.get()
                doc_count = len(result['documents']) if result['documents'] else 0
                logger.info(f"数据库中当前包含 {doc_count} 个文档")
            except Exception as e:
                logger.error(f"检查数据库内容失败: {e}")
        else:
            logger.info("创建新的Chroma数据库")
            # 创建新的数据库
            vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings
            )
        
        # 添加新文本
        if metadata is None:
            metadata = {"source": "user_input", "type": "personal_info"}
        
        logger.info(f"添加文本: {text}")
        logger.info(f"元数据: {metadata}")
        
        # 使用add_texts方法添加文本
        vectorstore.add_texts(
            texts=[text],
            metadatas=[metadata]
        )
        
        # 持久化数据库
        vectorstore.persist()
        logger.info("文本已成功添加到Chroma数据库")
        
        # 验证添加结果
        try:
            collection = vectorstore._collection
            result = collection.get()
            new_doc_count = len(result['documents']) if result['documents'] else 0
            logger.info(f"数据库中现在包含 {new_doc_count} 个文档")
            
            # 显示最新添加的文档
            if result['documents']:
                latest_doc = result['documents'][-1]
                latest_metadata = result['metadatas'][-1] if result['metadatas'] else {}
                logger.info(f"最新文档: {latest_doc[:100]}...")
                logger.info(f"最新文档元数据: {latest_metadata}")
        except Exception as e:
            logger.error(f"验证添加结果失败: {e}")
        
        # 测试检索功能
        logger.info("\n测试检索功能:")
        test_query = "软件工程学生"
        try:
            docs = vectorstore.similarity_search_with_score(test_query, k=3)
            if docs:
                logger.info(f"找到 {len(docs)} 个相关文档:")
                for i, (doc, score) in enumerate(docs):
                    source = doc.metadata.get("source", "未知来源")
                    logger.info(f"  文档 {i+1}: {source} (相似度: {score:.3f})")
                    logger.info(f"  内容: {doc.page_content[:100]}...")
            else:
                logger.warning("未找到相关文档")
        except Exception as e:
            logger.error(f"检索测试失败: {e}")
        
        return True
        
    except ImportError as e:
        logger.error(f"导入Chroma相关库失败: {e}")
        logger.error("请安装: pip install chromadb langchain-community")
        return False
    except Exception as e:
        logger.error(f"添加文本到Chroma失败: {e}")
        return False

if __name__ == "__main__":
    # 要添加的文本
    text_to_add = "我是一名软件工程大三学生。"
    
    # 元数据
    metadata = {
        "topic": "个人信息",
        "category": "学生身份",
        "source": "用户输入",
        "timestamp": "2025-07-26"
    }
    
    logger.info("开始向Chroma向量数据库添加文本")
    success = add_text_to_chroma(text_to_add, metadata)
    
    if success:
        logger.info("文本添加成功！")
    else:
        logger.error("文本添加失败！")