#!/usr/bin/env python3
"""
下载BGE-small-zh嵌入模型到本地
"""

import os
from sentence_transformers import SentenceTransformer

def download_bge_model():
    """
    下载BGE-small-zh模型到./models/bge-small-zh目录
    """
    model_name = "BAAI/bge-small-zh"
    local_path = "./models/bge-small-zh"
    
    print(f"开始下载模型: {model_name}")
    print(f"目标路径: {local_path}")
    
    try:
        # 下载模型
        model = SentenceTransformer(model_name)
        
        # 保存到本地路径
        model.save(local_path)
        
        print(f"模型下载完成！保存在: {os.path.abspath(local_path)}")
        
        # 验证模型是否可以正常加载
        print("验证模型加载...")
        test_model = SentenceTransformer(local_path)
        test_embedding = test_model.encode(["测试文本"])
        print(f"模型验证成功！嵌入维度: {test_embedding.shape}")
        
    except Exception as e:
        print(f"下载模型时出错: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = download_bge_model()
    if success:
        print("\n✅ 模型下载和配置完成！")
    else:
        print("\n❌ 模型下载失败！")