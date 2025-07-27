#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
from datetime import datetime

def test_who_am_i():
    """测试'我是谁'查询的详细处理过程"""
    
    base_url = "http://localhost:8002"
    
    # 1. 用户注册
    print("=== 步骤1: 用户注册 ===")
    register_data = {
        "username": f"debug_user_{int(time.time())}",
        "email": f"debug_{int(time.time())}@example.com",
        "password": "test123456"
    }
    
    response = requests.post(f"{base_url}/api/auth/register", json=register_data)
    if response.status_code != 200:
        print(f"注册失败: {response.status_code} - {response.text}")
        return
    
    user_data = response.json()
    print(f"注册成功: 用户ID {user_data['user_id']}")
    
    # 2. 用户登录
    print("\n=== 步骤2: 用户登录 ===")
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"登录失败: {response.status_code} - {response.text}")
        return
    
    auth_data = response.json()
    access_token = auth_data["access_token"]
    print(f"登录成功: 获取到访问令牌")
    
    # 3. 测试"我是谁"查询
    print("\n=== 步骤3: 测试'我是谁'查询 ===")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    chat_data = {
        "message": "我是谁？",
        "conversation_id": None
    }
    
    print(f"发送查询: {chat_data['message']}")
    
    response = requests.post(
        f"{base_url}/api/chat",
        json=chat_data,
        headers=headers,
        stream=True
    )
    
    if response.status_code != 200:
        print(f"聊天请求失败: {response.status_code} - {response.text}")
        return
    
    print("\n=== 流式响应详情 ===")
    
    # 解析流式响应
    full_response = ""
    analysis_data = {}
    
    for line in response.iter_lines():
        if line:
            line_text = line.decode('utf-8')
            if line_text.startswith('data: '):
                try:
                    data = json.loads(line_text[6:])
                    
                    if data.get('type') == 'thinking':
                        print(f"🤔 思考过程: {data.get('content', '')}")
                    elif data.get('type') == 'response_start':
                        print(f"\n🤖 AI回复开始")
                    elif data.get('type') == 'content':
                        content = data.get('content', '')
                        full_response += content
                        print(content, end='', flush=True)
                    elif data.get('type') == 'analysis':
                        analysis_data = data.get('data', {})
                        print(f"\n\n📊 分析结果:")
                        print(f"• 意图识别: {analysis_data.get('intent', 'unknown')}")
                        print(f"• 情绪状态: {analysis_data.get('emotion', 'unknown')}")
                        print(f"• 置信度: {analysis_data.get('confidence', 0)}%")
                        print(f"• 参考文档: {analysis_data.get('used_documents', 0)}篇")
                        print(f"• 处理时间: {analysis_data.get('processing_time', 0):.2f}秒")
                    elif data.get('type') == 'error':
                        print(f"❌ 错误: {data.get('content', '')}")
                    elif data.get('type') == 'done':
                        print(f"\n✅ 对话完成")
                        break
                        
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e} - 原始数据: {line_text}")
    
    print(f"\n\n=== 分析总结 ===")
    print(f"完整回复长度: {len(full_response)} 字符")
    print(f"意图识别: {analysis_data.get('intent', 'unknown')}")
    print(f"使用文档数: {analysis_data.get('used_documents', 0)}")
    
    # 检查是否检索到了用户信息
    if analysis_data.get('used_documents', 0) == 0:
        print("\n⚠️  问题分析: 没有检索到任何文档")
        print("可能原因:")
        print("1. 意图分析可能将'我是谁'识别为非知识查询类型")
        print("2. 向量检索没有找到相关的用户信息文档")
        print("3. 查询词与知识库中的内容相似度太低")
    else:
        print(f"\n✅ 成功检索到 {analysis_data.get('used_documents', 0)} 个文档")

if __name__ == "__main__":
    test_who_am_i()