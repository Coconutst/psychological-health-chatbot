#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量导入心理健康知识数据到Chroma向量数据库
"""

import os
import sys
import json
import logging
from typing import List, Dict, Any

# 检查并导入可选依赖
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("警告: pandas未安装，无法处理CSV和Excel文件")
    print("请运行: pip install pandas openpyxl 来安装支持")

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def load_bge_embeddings(model_path: str):
    """加载本地BGE嵌入模型"""
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
        
        embeddings = BGEEmbeddings(model_path)
        logger.info(f"成功加载本地BGE模型: {model_path}")
        return embeddings
    except Exception as e:
        logger.error(f"加载BGE模型失败: {e}")
        raise

def create_vector_store(persist_directory: str, embeddings):
    """创建或加载向量数据库"""
    try:
        # 尝试使用新版本的langchain_chroma
        try:
            from langchain_chroma import Chroma
            logger.info("使用新版本 langchain_chroma")
        except ImportError:
            # 回退到旧版本
            from langchain_community.vectorstores import Chroma
            logger.info("使用旧版本 langchain_community.vectorstores")
        
        # 确保目录存在
        os.makedirs(persist_directory, exist_ok=True)
        
        if os.path.exists(persist_directory) and os.listdir(persist_directory):
            logger.info(f"加载现有Chroma数据库: {persist_directory}")
            vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings,
                collection_name="psychological_knowledge"
            )
            
            # 检查现有文档数量
            try:
                collection = vectorstore._collection
                result = collection.get()
                doc_count = len(result['documents']) if result and result.get('documents') else 0
                logger.info(f"数据库中当前包含 {doc_count} 个文档")
            except Exception as e:
                logger.warning(f"检查数据库内容失败: {e}")
        else:
            logger.info(f"创建新的Chroma数据库: {persist_directory}")
            vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings,
                collection_name="psychological_knowledge"
            )
        
        return vectorstore
    except Exception as e:
        logger.error(f"创建向量数据库失败: {e}")
        raise

def load_knowledge_data(file_path: str) -> List[Dict[str, Any]]:
    """加载心理健康知识数据，支持多种文件格式"""
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        logger.info(f"检测到文件格式: {file_ext}")
        
        data = []
        
        if file_ext == '.json':
            # JSON格式
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # 处理不同的JSON结构
            if isinstance(json_data, list):
                logger.info(f"JSON数据格式: 列表，包含 {len(json_data)} 条记录")
                data = json_data
            elif isinstance(json_data, dict):
                # 如果是字典，尝试找到包含数据的键
                if 'data' in json_data:
                    logger.info(f"JSON数据格式: 字典，'data'键包含 {len(json_data['data'])} 条记录")
                    data = json_data['data']
                elif 'knowledge' in json_data:
                    logger.info(f"JSON数据格式: 字典，'knowledge'键包含 {len(json_data['knowledge'])} 条记录")
                    data = json_data['knowledge']
                elif 'items' in json_data:
                    logger.info(f"JSON数据格式: 字典，'items'键包含 {len(json_data['items'])} 条记录")
                    data = json_data['items']
                else:
                    # 将字典转换为单条记录
                    logger.info("JSON数据格式: 单个字典记录")
                    data = [json_data]
                    
        elif file_ext == '.txt':
            # TXT格式 - 每行一条记录或JSON格式
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    # 尝试解析为JSON
                    json_line = json.loads(line)
                    data.append(json_line)
                except json.JSONDecodeError:
                    # 如果不是JSON，作为纯文本处理
                    data.append({
                        'content': line,
                        'source': 'txt_file',
                        'line_number': i + 1
                    })
            
            logger.info(f"TXT文件包含 {len(data)} 条记录")
            
        elif file_ext in ['.csv']:
            # CSV格式
            if not PANDAS_AVAILABLE:
                logger.error("处理CSV文件需要pandas库，请运行: pip install pandas")
                return []
            df = pd.read_csv(file_path, encoding='utf-8')
            data = df.to_dict('records')
            logger.info(f"CSV文件包含 {len(data)} 条记录")
            
        elif file_ext in ['.xlsx', '.xls']:
            # Excel格式
            if not PANDAS_AVAILABLE:
                logger.error("处理Excel文件需要pandas和openpyxl库，请运行: pip install pandas openpyxl")
                return []
            df = pd.read_excel(file_path)
            data = df.to_dict('records')
            logger.info(f"Excel文件包含 {len(data)} 条记录")
            
        elif file_ext == '.jsonl':
            # JSONL格式 (每行一个JSON对象)
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    line = line.strip()
                    if line:
                        try:
                            json_obj = json.loads(line)
                            data.append(json_obj)
                        except json.JSONDecodeError as e:
                            logger.warning(f"第 {i+1} 行JSON解析失败: {e}")
            
            logger.info(f"JSONL文件包含 {len(data)} 条记录")
            
        else:
            logger.error(f"不支持的文件格式: {file_ext}")
            logger.info("支持的格式: .json, .txt, .csv, .xlsx, .xls, .jsonl")
            return []
        
        logger.info(f"成功加载知识数据文件: {file_path}，共 {len(data)} 条记录")
        return data
            
    except FileNotFoundError:
        logger.error(f"文件不存在: {file_path}")
        return []
    except Exception as e:
        logger.error(f"加载数据失败: {e}")
        return []

def process_knowledge_item(item: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """处理单条知识数据，返回文本内容和元数据"""
    # 尝试提取文本内容
    text_content = ""
    metadata = {}
    
    # 常见的文本字段名
    text_fields = ['content', 'text', 'description', 'answer', 'response', 'knowledge', 'info']
    
    for field in text_fields:
        if field in item and item[field]:
            text_content = str(item[field])
            break
    
    # 如果没有找到文本字段，将整个item转为字符串
    if not text_content:
        text_content = json.dumps(item, ensure_ascii=False)
    
    # 提取元数据
    metadata_fields = ['category', 'type', 'topic', 'emotion', 'tag', 'tags', 'source', 'id', 'title']
    
    for field in metadata_fields:
        if field in item and item[field] is not None:
            metadata[field] = item[field]
    
    # 添加默认元数据
    metadata.update({
        'source': metadata.get('source', 'knowledge_base'),
        'type': metadata.get('type', 'psychological_knowledge'),
        'imported_from': 'dataset.json'
    })
    
    return text_content, metadata

def import_knowledge_to_chroma(
    data_file: str,
    model_path: str = "./models/bge-small-zh",
    persist_directory: str = "./chroma_db",
    batch_size: int = 500
) -> bool:
    """批量导入心理健康知识数据到Chroma向量数据库"""
    try:
        logger.info("开始批量导入心理健康知识数据...")
        
        # 1. 加载嵌入模型
        embeddings = load_bge_embeddings(model_path)
        
        # 2. 创建向量数据库
        vectorstore = create_vector_store(persist_directory, embeddings)
        
        # 3. 加载知识数据
        knowledge_data = load_knowledge_data(data_file)
        
        if not knowledge_data:
            logger.error("没有找到有效的知识数据")
            return False
        
        logger.info(f"准备导入 {len(knowledge_data)} 条知识记录")
        
        # 4. 批量处理和导入
        texts = []
        metadatas = []
        
        for i, item in enumerate(knowledge_data):
            try:
                text_content, metadata = process_knowledge_item(item)
                
                if text_content.strip():  # 确保文本不为空
                    texts.append(text_content)
                    metadatas.append(metadata)
                    
                    # 批量导入
                    if len(texts) >= batch_size:
                        logger.info(f"导入批次 {i//batch_size + 1}: {len(texts)} 条记录")
                        vectorstore.add_texts(texts=texts, metadatas=metadatas)
                        texts = []
                        metadatas = []
                        
            except Exception as e:
                logger.warning(f"处理第 {i+1} 条记录失败: {e}")
                continue
        
        # 导入剩余的记录
        if texts:
            logger.info(f"导入最后批次: {len(texts)} 条记录")
            vectorstore.add_texts(texts=texts, metadatas=metadatas)
        
        # 5. 持久化数据库
        vectorstore.persist()
        logger.info("数据库持久化完成")
        
        # 6. 验证导入结果
        try:
            collection = vectorstore._collection
            result = collection.get()
            total_docs = len(result['documents']) if result['documents'] else 0
            logger.info(f"导入完成！数据库中现在包含 {total_docs} 个文档")
        
            # 测试检索功能
            logger.info("\n测试检索功能:")
            test_queries = ["我感到很焦虑怎么办？","如何缓解压力？","抑郁症的症状有哪些？"]
            
            for query in test_queries:
                try:
                    docs = vectorstore.similarity_search_with_score(query, k=3)
                    if docs:
                        logger.info(f"查询 '{query}' 找到 {len(docs)} 个相关文档")
                        for j, (doc, score) in enumerate(docs[:2]):  # 只显示前2个
                            logger.info(f"  文档 {j+1} (相似度: {score:.3f}): {doc.page_content[:100]}...")
                    else:
                        logger.warning(f"查询 '{query}' 未找到相关文档")
                except Exception as e:
                    logger.error(f"查询 '{query}' 失败: {e}")
                    
        except Exception as e:
            logger.error(f"验证导入结果失败: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"批量导入失败: {e}")
        return False

def get_supported_formats():
    """获取支持的文件格式列表"""
    return {
        '.json': 'JSON格式 - 标准JSON文件，支持嵌套结构',
        '.txt': 'TXT格式 - 纯文本或每行JSON格式',
        '.csv': 'CSV格式 - 逗号分隔值文件',
        '.xlsx': 'Excel格式 - Excel工作簿文件',
        '.xls': 'Excel格式 - 旧版Excel文件',
        '.jsonl': 'JSONL格式 - 每行一个JSON对象'
    }

def print_usage():
    """打印使用说明"""
    print("\n=== 心理健康知识数据导入工具 ===")
    print("\n支持的文件格式:")
    for ext, desc in get_supported_formats().items():
        print(f"  {ext}: {desc}")
    
    print("\n使用方法:")
    print("1. 将数据文件放在 ./data_sample/ 目录下")
    print("2. 修改下面的 data_file 变量指向你的数据文件")
    print("3. 运行脚本开始导入")
    
    print("\n数据格式要求:")
    print("- JSON: 可以是数组或包含'data'/'knowledge'/'items'键的对象")
    print("- TXT: 每行一条记录，可以是JSON格式或纯文本")
    print("- CSV/Excel: 每行一条记录，列名作为字段名")
    print("- JSONL: 每行一个独立的JSON对象")
    print("\n" + "="*50)

if __name__ == "__main__":
    # 打印使用说明
    print_usage()
    
    # 配置参数 - 用户可以修改这里指定不同的数据文件
    data_file = "./data_sample/test.txt"  # 支持 .json, .txt, .csv, .xlsx, .xls, .jsonl
    model_path = "./models/bge-small-zh"
    persist_directory = "./chroma_db"
    
    logger.info("开始批量导入心理健康知识数据到Chroma向量数据库")
    logger.info(f"数据文件: {data_file}")
    logger.info(f"模型路径: {model_path}")
    logger.info(f"数据库路径: {persist_directory}")
    
    success = import_knowledge_to_chroma(
        data_file=data_file,
        model_path=model_path,
        persist_directory=persist_directory,
        batch_size=50
    )
    
    if success:
        logger.info("✅ 知识数据导入成功！")
    else:
        logger.error("❌ 知识数据导入失败！")