# 导入Chroma向量数据库
from langchain_community.vectorstores import Chroma
# 导入OpenAI嵌入模型
from langchain_openai import OpenAIEmbeddings
# 导入HuggingFace 嵌入模型（新版本）
from langchain_huggingface import HuggingFaceEmbeddings
# 导入嵌入模型基础类
from langchain_core.embeddings import Embeddings
# 导入应用配置和根目录
from app.configs.settings import config, ROOT
# 导入PyTorch深度学习框架
import torch


# 动态加载嵌入模型的函数
def get_embedding_model() -> Embeddings:
    """
    根据配置动态加载嵌入模型。
    """
    # 获取嵌入模型提供商（转换为小写）
    embedding_provider = config.embedding.provider.lower()
    # 获取嵌入模型名称
    embedding_model_name = config.embedding.name

    # 如果使用OpenAI提供商
    if embedding_provider == "openai":
        print("Loading OpenAI embedding model...")
        # 返回OpenAI嵌入模型实例
        return OpenAIEmbeddings(model=embedding_model_name)

    # 如果使用本地提供商
    elif embedding_provider == "local":
        print(f"Loading local embedding model: {embedding_model_name}")
        
        # 检查模型路径是否存在
        from pathlib import Path
        import os
        model_path = Path(embedding_model_name)
        # 修复Windows路径兼容性问题 - 使用更安全的路径检查方法
        try:
            # 使用 os.path.isabs 替代 pathlib 的 is_absolute 方法
            if not os.path.isabs(str(model_path)):
                model_path = ROOT / model_path
        except Exception:
            # 备用方案：字符串检查
            model_path_str = str(model_path)
            if not (model_path_str.startswith('/') or (len(model_path_str) > 1 and model_path_str[1] == ':')):
                model_path = ROOT / model_path
            
        if not model_path.exists():
            print(f"Warning: Model path {model_path} does not exist, using fallback model")
            # 使用在线轻量级模型作为备选
            embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"

        # 确定计算设备：优先使用CUDA，其次是MPS（Apple Silicon），最后是CPU
        if torch.cuda.is_available():
            device = "cuda"  # 使用NVIDIA GPU
        elif torch.backends.mps.is_available():
            device = "mps"  # 使用Apple Silicon GPU
        else:
            device = "cpu"  # 使用CPU

        # 打印使用的设备信息
        print(f"Using device: {device}")

        try:
            # 使用HuggingFaceEmbeddings，支持BGE模型
            return HuggingFaceEmbeddings(
                model_name=str(model_path) if model_path.exists() else embedding_model_name,
                model_kwargs={"device": device, "trust_remote_code": True},  # 模型参数，指定计算设备
                encode_kwargs={"normalize_embeddings": True},  # BGE模型推荐开启归一化
            )
        except Exception as e:
            print(f"Failed to load embedding model: {e}")
            print("Using fallback online model")
            return HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": device},
                encode_kwargs={"normalize_embeddings": True},
            )
    else:
        # 如果是不支持的提供商，抛出异常
        raise ValueError(f"Unsupported embedding provider: {embedding_provider}")
# 使用全局变量缓存嵌入模型实例（单例模式）
_embeddings = None
_vector_store = None

def get_embedding_model_cached() -> Embeddings:
    """获取缓存的嵌入模型实例"""
    global _embeddings
    if _embeddings is None:
        _embeddings = get_embedding_model()
    return _embeddings


# 初始化并返回Chroma向量数据库的函数
def get_vector_store() -> Chroma:
    """
    初始化并返回Chroma向量数据库（使用缓存）。
    """
    global _vector_store
    
    # 如果已经缓存了向量存储实例，直接返回
    if _vector_store is not None:
        return _vector_store
    
    # 构建向量数据库持久化目录的完整路径
    persist_directory = str(ROOT / config.vector_store.persist_directory)

    # 打印向量数据库初始化信息
    print(f"Initializing vector store at: {persist_directory}")

    try:
        # 创建Chroma向量数据库实例
        _vector_store = Chroma(
            collection_name=config.vector_store.collection_name,  # 集合名称
            embedding_function=get_embedding_model_cached(),  # 使用缓存的嵌入函数
            persist_directory=persist_directory,  # 持久化目录
        )
        print("Vector store initialized successfully")
        # 返回向量数据库实例
        return _vector_store
    except Exception as e:
        print(f"Failed to initialize vector store: {e}")
        # 如果向量存储初始化失败，返回None或创建一个空的内存向量存储
        print("Creating fallback in-memory vector store")
        _vector_store = Chroma(
            collection_name=config.vector_store.collection_name,
            embedding_function=get_embedding_model_cached(),
            # 不设置persist_directory，使用内存存储
        )
        return _vector_store