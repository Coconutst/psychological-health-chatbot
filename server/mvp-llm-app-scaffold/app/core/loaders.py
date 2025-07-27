# 导入操作系统模块
import os
# 导入路径处理模块
from pathlib import Path

# 导入LangChain文档加载器模块
from langchain_community.document_loaders import (
    DirectoryLoader,  # 目录加载器，用于批量加载文件
    UnstructuredFileLoader,  # 非结构化文件加载器，支持多种文件格式
)
# 导入文档基础类
from langchain_core.documents import Document

# 导入PDF加载器
from langchain_community.document_loaders import PyPDFLoader  # 导入PyPDFLoader，用于加载PDF文件
# 导入Word文档加载器
from langchain_community.document_loaders import Docx2txtLoader  # 导入Docx2txtLoader，用于加载Word文档
# 导入JSON加载器
from langchain_community.document_loaders import JSONLoader  # 导入JSONLoader，用于加载JSON文件
# 导入文本清洗相关模块
import re  # 导入正则表达式模块，用于文本清洗
import json  # 导入JSON模块，用于处理JSON数据
from typing import Iterator  # 导入Iterator类型，用于类型提示


def load_large_json_file(file_path: str, batch_size: int = 1000) -> list[Document]:
    """分批加载大JSON文件以避免内存溢出。"""
    documents = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # 尝试逐行读取JSON数组
            content = file.read()
            
            # 如果文件是JSON数组格式
            if content.strip().startswith('['):
                # 分批解析JSON数组
                data = json.loads(content)
                
                # 分批处理数据
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    
                    for idx, item in enumerate(batch):
                        # 将每个JSON对象转换为文档
                        doc_content = json.dumps(item, ensure_ascii=False, indent=2)
                        
                        # 创建Document对象
                        doc = Document(
                            page_content=doc_content,
                            metadata={
                                "source": file_path,
                                "batch_index": i // batch_size,
                                "item_index": i + idx,
                                "file_type": "json"
                            }
                        )
                        documents.append(doc)
                    
                    print(f"Processed batch {i // batch_size + 1}, items {i + 1}-{min(i + batch_size, len(data))}")
                    
                    # 如果处理的文档数量过多，可以在这里添加内存管理
                    if len(documents) > 10000:  # 限制内存中的文档数量
                        print(f"Reached document limit (10000), stopping processing for {file_path}")
                        break
            else:
                # 如果不是数组格式，尝试按行处理
                print(f"File {file_path} is not a JSON array, trying line-by-line processing...")
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line_num, line in enumerate(file):
                        line = line.strip()
                        if line and line.startswith('{'):
                            try:
                                item = json.loads(line)
                                doc_content = json.dumps(item, ensure_ascii=False, indent=2)
                                
                                doc = Document(
                                    page_content=doc_content,
                                    metadata={
                                        "source": file_path,
                                        "line_number": line_num + 1,
                                        "file_type": "jsonl"
                                    }
                                )
                                documents.append(doc)
                                
                                if len(documents) % 1000 == 0:
                                    print(f"Processed {len(documents)} lines from {file_path}")
                                    
                                # 限制处理的行数
                                if len(documents) > 10000:
                                    print(f"Reached document limit (10000), stopping processing for {file_path}")
                                    break
                                    
                            except json.JSONDecodeError:
                                continue
                                
    except Exception as e:
        print(f"Error processing large JSON file {file_path}: {e}")
        # 如果分批处理失败，尝试采样处理
        return sample_large_json_file(file_path)
    
    print(f"Successfully loaded {len(documents)} documents from {file_path}")
    return documents


def sample_large_json_file(file_path: str, sample_size: int = 100) -> list[Document]:
    """对大JSON文件进行采样处理。"""
    documents = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            data = json.loads(content)
            
            if isinstance(data, list) and len(data) > sample_size:
                # 均匀采样
                step = len(data) // sample_size
                sampled_data = data[::step][:sample_size]
                
                for idx, item in enumerate(sampled_data):
                    doc_content = json.dumps(item, ensure_ascii=False, indent=2)
                    
                    doc = Document(
                        page_content=doc_content,
                        metadata={
                            "source": file_path,
                            "sample_index": idx,
                            "original_index": idx * step,
                            "file_type": "json_sample",
                            "total_items": len(data),
                            "sample_size": len(sampled_data)
                        }
                    )
                    documents.append(doc)
                    
                print(f"Sampled {len(documents)} documents from {len(data)} total items in {file_path}")
            else:
                print(f"File {file_path} is small enough or not a list, processing normally...")
                
    except Exception as e:
        print(f"Error sampling JSON file {file_path}: {e}")
    
    return documents


# 从指定目录路径加载文档的函数
def load_documents(data_path: str) -> list[Document]:
    """从指定目录路径加载文档。"""
    # 将字符串路径转换为Path对象
    path = Path(data_path)
    # 检查路径是否存在且为目录
    if not path.exists() or not path.is_dir():
        # 如果路径无效，抛出异常
        raise ValueError(f"The path '{data_path}' is not a valid directory.")

    # 打印加载进度信息
    print(f"Loading documents from {data_path}...")

    # 修改加载器以支持多种文件类型
    # 使用DirectoryLoader处理TXT文件
    txt_loader = DirectoryLoader(  # 创建TXT加载器
        str(path),  # 目录路径
        glob="**/*.txt",  # 匹配所有TXT文件，包括子目录
        show_progress=True,  # 显示进度
        use_multithreading=True,  # 使用多线程
        loader_cls=UnstructuredFileLoader  # 使用非结构化加载器
    )  # 初始化TXT加载器
    txt_docs = txt_loader.load()  # 加载TXT文档
    
    # 使用DirectoryLoader处理PDF文件
    pdf_loader = DirectoryLoader(  # 创建PDF加载器
        str(path),  # 目录路径
        glob="**/*.pdf",  # 匹配所有PDF文件
        show_progress=True,  # 显示进度
        use_multithreading=True,  # 使用多线程
        loader_cls=PyPDFLoader  # 使用PDF加载器
    )  # 初始化PDF加载器
    pdf_docs = pdf_loader.load()  # 加载PDF文档
    
    # 使用DirectoryLoader处理DOCX文件
    docx_loader = DirectoryLoader(  # 创建DOCX加载器
        str(path),  # 目录路径
        glob="**/*.docx",  # 匹配所有DOCX文件
        show_progress=True,  # 显示进度
        use_multithreading=True,  # 使用多线程
        loader_cls=Docx2txtLoader  # 使用Word加载器
    )  # 初始化DOCX加载器
    docx_docs = docx_loader.load()  # 加载DOCX文档
    
    # 处理JSON文件（支持大文件分批处理）
    json_docs = []  # 初始化JSON文档列表
    json_files = list(path.glob("**/*.json"))  # 获取所有JSON文件
    for json_file in json_files:  # 遍历每个JSON文件
        print(f"Processing JSON file: {json_file}")
        try:
            # 检查文件大小，如果超过100MB则分批处理
            file_size = json_file.stat().st_size
            if file_size > 100 * 1024 * 1024:  # 100MB
                print(f"Large JSON file detected ({file_size / 1024 / 1024:.1f}MB), processing in batches...")
                json_docs.extend(load_large_json_file(str(json_file)))
            else:
                # 小文件直接使用JSONLoader
                loader = JSONLoader(
                    file_path=str(json_file),
                    jq_schema=".[]",
                    text_content=False
                )
                json_docs.extend(loader.load())
        except Exception as e:
            print(f"Error loading JSON file {json_file}: {e}")
            continue
    
    # 合并所有文档
    documents = txt_docs + pdf_docs + docx_docs + json_docs  # 将所有加载的文档合并到列表中
    
    # 对每个文档应用文本清洗
    for doc in documents:  # 遍历每个文档
        doc.page_content = clean_text(doc.page_content)  # 清洗文档内容并更新
    
    # 打印加载完成的文档数量
    print(f"Loaded {len(documents)} documents.")  # 输出加载文档数量
    # 返回加载和清洗后的文档列表
    return documents  # 返回文档列表

    # 定义文本清洗函数
def clean_text(text: str) -> str:  # 定义函数，接受字符串并返回清洗后的字符串
    text = re.sub(r'\s+', ' ', text)  # 替换多个空白字符为单个空格
    text = text.strip()  # 去除首尾空白
    return text  # 返回清洗后的文本
