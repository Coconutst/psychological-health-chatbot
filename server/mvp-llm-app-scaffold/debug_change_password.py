#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# 测试change-password端点
BASE_URL = "http://localhost:8002"

def test_change_password_endpoint():
    print("🔍 调试change-password端点")
    
    # 1. 先注册一个用户
    print("\n1. 注册用户...")
    import time
    timestamp = int(time.time())
    register_data = {
        "username": "debug_user",
        "email": f"debug{timestamp}@example.com",
        "password": "oldpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        print(f"注册响应状态: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            access_token = result.get('access_token')
            print(f"获得访问令牌: {access_token[:20]}...")
        else:
            print(f"注册失败: {response.text}")
            return
    except Exception as e:
        print(f"注册异常: {e}")
        return
    
    # 2. 测试change-password端点
    print("\n2. 测试change-password端点...")
    change_password_data = {
        "current_password": "oldpassword123",
        "new_password": "newpassword456"
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"请求URL: {BASE_URL}/api/auth/change-password")
        print(f"请求头: {headers}")
        print(f"请求数据: {json.dumps(change_password_data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/auth/change-password", 
            json=change_password_data,
            headers=headers
        )
        
        print(f"\n响应状态: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ change-password端点工作正常！")
        else:
            print("❌ change-password端点返回错误")
            
    except Exception as e:
        print(f"请求异常: {e}")
    
    # 3. 检查所有可用的端点
    print("\n3. 检查OpenAPI规范...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get('paths', {})
            auth_paths = [path for path in paths.keys() if '/auth/' in path]
            print("可用的认证端点:")
            for path in auth_paths:
                methods = list(paths[path].keys())
                print(f"  {path}: {methods}")
        else:
            print(f"获取OpenAPI规范失败: {response.status_code}")
    except Exception as e:
        print(f"获取OpenAPI规范异常: {e}")

if __name__ == "__main__":
    test_change_password_endpoint()