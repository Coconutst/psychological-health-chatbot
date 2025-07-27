#!/usr/bin/env python3
"""
心理健康聊天机器人后端启动脚本

此脚本用于启动FastAPI应用服务器，监听在8001端口
"""
import uvicorn
import os
import sys

# 确保当前目录在Python路径中，以便正确导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # 启动uvicorn服务器
    # host="0.0.0.0" 表示监听所有网络接口
    # port=8001 指定端口号
    # app="app.main:app" 指定FastAPI应用实例的导入路径
    # reload=True 启用热重载，当代码变更时自动重启服务器
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
    
    print("服务器已启动，监听在 http://localhost:8002")