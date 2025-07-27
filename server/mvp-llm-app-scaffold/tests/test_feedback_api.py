#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试消息反馈API端点
基于 register_fixed.py 的结构进行测试
"""

import requests
import json
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

# API基础配置
BASE_URL = "http://localhost:8001"
API_PREFIX = "/api"

class FeedbackAPITester:
    """消息反馈API测试类"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.conversation_id = None
        self.test_email = None
        self.test_password = "test123456"
        self.message_ids = []  # 存储创建的消息ID
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """统一的请求方法"""
        url = f"{self.base_url}{API_PREFIX}{endpoint}"
        
        # 添加认证头
        headers = kwargs.get('headers', {})
        if self.access_token and 'Authorization' not in headers:
            headers['Authorization'] = f'Bearer {self.access_token}'
            kwargs['headers'] = headers
        
        print(f"📤 {method} {url}")
        if 'json' in kwargs:
            print(f"📦 请求数据: {json.dumps(kwargs['json'], ensure_ascii=False, indent=2)}")
        
        response = self.session.request(method, url, **kwargs)
        print(f"📥 响应状态: {response.status_code}")
        
        return response
    
    def test_register_and_login(self) -> bool:
        """测试用户注册和登录"""
        print("🔐 测试用户注册和登录")
        
        # 生成唯一的测试邮箱
        timestamp = int(time.time())
        self.test_email = f"feedback_test_{timestamp}@example.com"
        
        # 注册用户
        register_data = {
            "username": f"反馈测试用户_{timestamp}",
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = self._make_request('POST', '/auth/register', json=register_data)
        
        if response.status_code == 200:
            result = response.json()
            self.access_token = result.get('access_token')
            self.refresh_token = result.get('refresh_token')
            self.user_id = result.get('user_id')
            print(f"✅ 注册成功 - 用户ID: {self.user_id}")
            return True
        else:
            print(f"❌ 注册失败: {response.text}")
            return False

    def test_create_conversation_and_message(self) -> bool:
        """测试创建对话和消息"""
        print("💬 测试创建对话和消息")
        
        if not self.access_token:
            print("❌ 没有访问令牌")
            return False
        
        # 生成新的对话ID
        new_conversation_id = str(uuid.uuid4())
        self.conversation_id = new_conversation_id
        
        data = {
            "message": "你好，我想测试反馈功能，请给我一些建议。",
            "conversation_id": new_conversation_id
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            url = f"{self.base_url}{API_PREFIX}/chat"
            print(f"📤 POST {url}")
            print(f"🆔 对话ID: {new_conversation_id}")
            
            response = self.session.post(url, json=data, headers=headers, stream=True, timeout=30)
            
            if response.status_code == 200:
                print("✅ 开始接收流式响应...")
                
                # 从响应头中获取实际的conversation_id
                actual_conversation_id = response.headers.get('X-Conversation-ID')
                if actual_conversation_id:
                    self.conversation_id = actual_conversation_id
                    print(f"🆔 从响应头获取到对话ID: {actual_conversation_id}")
                
                # 处理流式响应
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            try:
                                data_str = line_str[6:]  # 移除 'data: ' 前缀
                                data_obj = json.loads(data_str)
                                
                                if data_obj.get('type') == 'content':
                                    content = data_obj.get('content', '')
                                    full_response += content
                                    print(content, end='', flush=True)
                                elif data_obj.get('type') == 'end':
                                    print("\n✅ 对话创建完成")
                                    break
                                elif data_obj.get('type') == 'error':
                                    print(f"\n❌ 对话过程中出错: {data_obj.get('content')}")
                                    return False
                            except json.JSONDecodeError:
                                continue
                
                return len(full_response) > 0
            else:
                print(f"❌ 创建对话失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 创建对话异常: {e}")
            return False
    
    def test_get_conversation_messages(self) -> bool:
        """测试获取对话消息列表"""
        print("📋 测试获取对话消息列表")
        
        if not self.access_token or not self.conversation_id:
            print("❌ 没有访问令牌或对话ID")
            return False
        
        # 直接使用conversation_id UUID获取消息列表
        response = self._make_request('GET', f'/conversations/{self.conversation_id}/messages')
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ 获取到 {len(messages)} 条消息")
            
            # 保存assistant消息的message_id用于后续测试
            for message in messages:
                if message.get('role') == 'assistant':
                    self.message_ids.append(message.get('message_id'))  # 使用message_id而不是id
                    print(f"📝 保存消息ID: {message.get('message_id')} (角色: {message.get('role')})")
            
            return len(messages) > 0
        else:
            print(f"❌ 获取消息列表失败: {response.text}")
            return False
    
    def test_update_message_feedback_positive(self) -> bool:
        """测试更新消息正面反馈"""
        print("👍 测试更新消息正面反馈")
        
        if not self.access_token or not self.message_ids:
            print("❌ 没有访问令牌或消息ID")
            return False
        
        message_id = self.message_ids[0]  # 使用第一个消息ID
        data = {"feedback": 1}  # 正面反馈
        
        response = self._make_request('PATCH', f'/conversations/messages/{message_id}/feedback', json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 正面反馈更新成功: {result}")
            return True
        else:
            print(f"❌ 正面反馈更新失败: {response.text}")
            return False
    
    def test_update_message_feedback_negative(self) -> bool:
        """测试更新消息负面反馈"""
        print("👎 测试更新消息负面反馈")
        
        if not self.access_token or len(self.message_ids) < 2:
            print("❌ 没有访问令牌或足够的消息ID")
            # 如果只有一个消息，就用它来测试负面反馈
            if len(self.message_ids) == 1:
                message_id = self.message_ids[0]
            else:
                return False
        else:
            message_id = self.message_ids[1] if len(self.message_ids) > 1 else self.message_ids[0]
        
        data = {"feedback": -1}  # 负面反馈
        
        response = self._make_request('PATCH', f'/conversations/messages/{message_id}/feedback', json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 负面反馈更新成功: {result}")
            return True
        else:
            print(f"❌ 负面反馈更新失败: {response.text}")
            return False
    
    def test_verify_feedback_values(self) -> bool:
        """测试验证反馈值是否正确保存"""
        print("🔍 测试验证反馈值")
        
        if not self.access_token or not self.conversation_id:
            print("❌ 没有访问令牌或对话ID")
            return False
        
        # 直接使用conversation_id UUID获取消息列表
        response = self._make_request('GET', f'/conversations/{self.conversation_id}/messages')
        
        if response.status_code == 200:
            messages = response.json()
            feedback_found = False
            
            for message in messages:
                if message.get('role') == 'assistant' and 'feedback' in message:
                    feedback_value = message.get('feedback')
                    print(f"📝 消息ID {message.get('message_id')} 的反馈值: {feedback_value}")
                    if feedback_value in [-1, 1]:  # 有效的反馈值
                        feedback_found = True
            
            if feedback_found:
                print("✅ 反馈值验证成功")
                return True
            else:
                print("❌ 未找到有效的反馈值")
                return False
        else:
            print(f"❌ 验证反馈值失败: {response.text}")
            return False
    
    def test_unauthorized_feedback_update(self) -> bool:
        """测试未授权用户更新反馈"""
        print("🚫 测试未授权用户更新反馈")
        
        if not self.message_ids:
            print("❌ 没有消息ID")
            return False
        
        # 临时清除访问令牌
        original_token = self.access_token
        self.access_token = None
        
        message_id = self.message_ids[0]
        data = {"feedback": 1}
        
        response = self._make_request('PATCH', f'/conversations/messages/{message_id}/feedback', json=data)
        
        # 恢复访问令牌
        self.access_token = original_token
        
        if response.status_code in [401, 403]:  # 期望返回未授权错误（401或403都是正确的）
            print("✅ 未授权访问正确被拒绝")
            return True
        else:
            print(f"❌ 未授权访问测试失败: {response.status_code} - {response.text}")
            return False
    
    def test_feedback_impact_on_next_conversation(self) -> bool:
        """测试反馈对下次对话的影响"""
        print("🔄 测试反馈对下次对话的影响")
        
        if not self.access_token or not self.conversation_id:
            print("❌ 没有访问令牌或对话ID")
            return False
        
        # 使用相同的对话ID进行新的聊天，测试反馈分析功能
        data = {
            "message": "基于我之前的反馈，请继续为我提供建议。",
            "conversation_id": self.conversation_id
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            url = f"{self.base_url}{API_PREFIX}/chat"
            print(f"📤 POST {url}")
            print(f"🆔 使用现有对话ID: {self.conversation_id}")
            
            response = self.session.post(url, json=data, headers=headers, stream=True, timeout=30)
            
            if response.status_code == 200:
                print("✅ 开始接收基于反馈的流式响应...")
                
                # 处理流式响应
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            try:
                                data_str = line_str[6:]
                                data_obj = json.loads(data_str)
                                
                                if data_obj.get('type') == 'content':
                                    content = data_obj.get('content', '')
                                    full_response += content
                                    print(content, end='', flush=True)
                                elif data_obj.get('type') == 'end':
                                    print("\n✅ 基于反馈的对话完成")
                                    break
                                elif data_obj.get('type') == 'error':
                                    print(f"\n❌ 基于反馈的对话出错: {data_obj.get('content')}")
                                    return False
                            except json.JSONDecodeError:
                                continue
                
                return len(full_response) > 0
            else:
                print(f"❌ 基于反馈的对话失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 基于反馈的对话异常: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有反馈API测试"""
        print("🚀 开始消息反馈API测试套件")
        print("=" * 60)
        
        tests = [
            ("用户注册和登录", self.test_register_and_login),
            ("创建对话和消息", self.test_create_conversation_and_message),
            ("获取对话消息列表", self.test_get_conversation_messages),
            ("更新消息正面反馈", self.test_update_message_feedback_positive),
            ("更新消息负面反馈", self.test_update_message_feedback_negative),
            ("验证反馈值", self.test_verify_feedback_values),
            ("测试未授权反馈更新", self.test_unauthorized_feedback_update),
            ("测试反馈对下次对话的影响", self.test_feedback_impact_on_next_conversation),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                results.append((test_name, result))
                if result:
                    print(f"✅ {test_name} 通过")
                else:
                    print(f"❌ {test_name} 失败")
            except Exception as e:
                print(f"❌ {test_name} 异常: {e}")
                results.append((test_name, False))
            
            # 测试间隔
            time.sleep(1)
        
        # 输出测试总结
        print("\n" + "=" * 60)
        print("📊 测试结果总结")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name:<25} {status}")
        
        print(f"\n总计: {passed}/{total} 个测试通过")
        
        if passed == total:
            print("🎉 所有反馈API测试都通过了！")
        else:
            print(f"⚠️ 有 {total - passed} 个测试失败")
        
        return passed == total

def main():
    """主函数"""
    print("消息反馈API测试套件")
    print("=" * 60)
    
    tester = FeedbackAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎊 所有反馈API测试完成，功能运行正常！")
    else:
        print("\n🔧 部分测试失败，请检查反馈API配置")
    
    return success

if __name__ == "__main__":
    main()