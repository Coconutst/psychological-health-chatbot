#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心理健康聊天机器人 - 对话API专项测试
专门用于测试和改进对话相关功能
"""

import requests
import json
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os

# API基础配置
BASE_URL = "http://localhost:8002"
API_PREFIX = "/api"

class ChatAPITester:
    """对话API专项测试类"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.conversation_id = None
        self.test_email = None
        self.test_password = "test123456"
        self.test_results = []  # 存储测试结果
        
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """统一的请求方法"""
        url = f"{self.base_url}{API_PREFIX}{endpoint}"
        
        # 添加认证头
        headers = kwargs.get('headers', {})
        if self.access_token and 'Authorization' not in headers:
            headers['Authorization'] = f'Bearer {self.access_token}'
            kwargs['headers'] = headers
        
        print(f"📤 {method} {url}")
        if 'json' in kwargs and method != 'GET':
            print(f"📦 请求数据: {json.dumps(kwargs['json'], ensure_ascii=False, indent=2)}")
        
        try:
            response = self.session.request(method, url, **kwargs)
            print(f"📥 响应状态: {response.status_code}")
            return response
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            raise
    
    def test_1_user_registration(self) -> bool:
        """测试1: 用户注册"""
        print("\n🔐 测试1: 用户注册")
        
        # 生成唯一的测试邮箱
        timestamp = int(time.time())
        self.test_email = f"chat_test_{timestamp}@example.com"
        
        # 注册用户
        register_data = {
            "username": f"对话测试用户_{timestamp}",
            "email": self.test_email,
            "password": self.test_password
        }
        
        try:
            response = self._make_request('POST', '/auth/register', json=register_data)
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get('access_token')
                self.refresh_token = result.get('refresh_token')
                self.user_id = result.get('user_id')
                
                self.log_test_result(
                    "用户注册", 
                    True, 
                    f"用户ID: {self.user_id}, 邮箱: {self.test_email}"
                )
                return True
            else:
                self.log_test_result(
                    "用户注册", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("用户注册", False, f"异常: {str(e)}")
            return False
    
    def test_2_user_login(self) -> bool:
        """测试2: 用户登录"""
        print("\n🔑 测试2: 用户登录")
        
        if not self.test_email:
            self.log_test_result("用户登录", False, "没有测试邮箱")
            return False
        
        # 登录用户
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        try:
            response = self._make_request('POST', '/auth/login', json=login_data)
            
            if response.status_code == 200:
                result = response.json()
                # 更新令牌（可能有新的）
                self.access_token = result.get('access_token')
                self.refresh_token = result.get('refresh_token')
                
                self.log_test_result(
                    "用户登录", 
                    True, 
                    f"成功获取访问令牌"
                )
                return True
            else:
                self.log_test_result(
                    "用户登录", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("用户登录", False, f"异常: {str(e)}")
            return False
    
    def test_3_create_conversation(self) -> bool:
        """测试3: 创建对话"""
        print("\n💬 测试3: 创建对话")
        
        if not self.access_token:
            self.log_test_result("创建对话", False, "没有访问令牌")
            return False
        
        # 生成新的对话ID
        new_conversation_id = str(uuid.uuid4())
        self.conversation_id = new_conversation_id
        
        data = {
            "message": "我是谁？",
            "conversation_id": new_conversation_id
        }
        
        try:
            url = f"{self.base_url}{API_PREFIX}/chat"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            print(f"📤 POST {url}")
            print(f"🆔 对话ID: {new_conversation_id}")
            
            response = self.session.post(url, json=data, headers=headers, stream=True, timeout=60)
            
            print(f"📥 响应状态: {response.status_code}")
            print(f"📋 响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ 开始接收流式响应...")
                
                # 从响应头中获取实际的conversation_id
                actual_conversation_id = response.headers.get('X-Conversation-ID')
                if actual_conversation_id:
                    self.conversation_id = actual_conversation_id
                    print(f"🆔 从响应头获取到对话ID: {actual_conversation_id}")
                
                # 处理流式响应
                full_response = ""
                response_chunks = 0
                print("\n💬 AI回复: ", end='', flush=True)
                
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        response_chunks += 1
                        
                        if line.startswith('data: '):
                            try:
                                data_str = line[6:]  # 移除 'data: ' 前缀
                                if data_str == '[DONE]':
                                    break
                                    
                                data_obj = json.loads(data_str)
                                
                                if data_obj.get('type') == 'content':
                                    content = data_obj.get('content', '')
                                    full_response += content
                                    print(content, end='', flush=True)
                                elif data_obj.get('type') == 'response':
                                    # 处理新的响应格式
                                    content = data_obj.get('response', '')
                                    full_response += content
                                    print(content, end='', flush=True)
                                elif data_obj.get('type') == 'end':
                                    break
                                elif data_obj.get('type') == 'error':
                                    error_msg = data_obj.get('content', '未知错误')
                                    print(f"\n❌ 错误: {error_msg}")
                                    self.log_test_result("创建对话", False, f"对话过程中出错: {error_msg}")
                                    return False
                                elif data_obj.get('type') in ['status', 'agent_status']:
                                    # 静默处理状态消息
                                    pass
                                else:
                                    # 尝试其他可能的字段
                                    content = ''
                                    if 'content' in data_obj:
                                        content = data_obj['content']
                                    elif 'output' in data_obj:
                                        content = data_obj['output']
                                    elif 'text' in data_obj:
                                        content = data_obj['text']
                                    elif 'response' in data_obj:
                                        content = data_obj['response']
                                    
                                    if content:
                                        full_response += content
                                        print(content, end='', flush=True)
                            except json.JSONDecodeError:
                                # 可能是纯文本响应
                                full_response += line
                                print(line, end='', flush=True)
                                continue
                        else:
                            # 可能是非SSE格式的流式响应
                            try:
                                data_obj = json.loads(line)
                                content = ''
                                if 'content' in data_obj:
                                    content = data_obj['content']
                                elif 'output' in data_obj:
                                    content = data_obj['output']
                                
                                if content:
                                    full_response += content
                                    print(content, end='', flush=True)
                            except json.JSONDecodeError:
                                # 纯文本响应
                                full_response += line
                                print(line, end='', flush=True)
                
                print(f"\n\n✅ 对话创建完成 (共{response_chunks}个数据块, {len(full_response)}字符)")
                
                if len(full_response) > 0:
                    self.log_test_result(
                        "创建对话", 
                        True, 
                        f"对话ID: {self.conversation_id}, 响应长度: {len(full_response)}字符"
                    )
                    return True
                else:
                    self.log_test_result("创建对话", False, "没有收到有效响应")
                    return False
            else:
                self.log_test_result(
                    "创建对话", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            import traceback
            self.log_test_result("创建对话", False, f"异常: {str(e)}\n详细错误: {traceback.format_exc()}")
            return False
    
    def test_4_continue_conversation(self) -> bool:
        """测试4: 继续对话"""
        print("\n🔄 测试4: 继续对话")
        
        if not self.access_token or not self.conversation_id:
            self.log_test_result("继续对话", False, "没有访问令牌或对话ID")
            return False
        
        data = {
            "message": "谢谢你的建议。我想了解一些具体的放松技巧，比如呼吸练习或冥想方法。",
            "conversation_id": self.conversation_id
        }
        
        try:
            url = f"{self.base_url}{API_PREFIX}/chat"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            print(f"📤 POST {url}")
            print(f"🆔 使用对话ID: {self.conversation_id}")
            
            response = self.session.post(url, json=data, headers=headers, stream=True, timeout=60)
            
            print(f"📥 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 开始接收流式响应...")
                
                # 处理流式响应
                full_response = ""
                response_chunks = 0
                print("\n💬 AI回复: ", end='', flush=True)
                
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        response_chunks += 1
                        
                        if line.startswith('data: '):
                            try:
                                data_str = line[6:]  # 移除 'data: ' 前缀
                                if data_str == '[DONE]':
                                    break
                                    
                                data_obj = json.loads(data_str)
                                
                                if data_obj.get('type') == 'content':
                                    content = data_obj.get('content', '')
                                    full_response += content
                                    print(content, end='', flush=True)
                                elif data_obj.get('type') == 'response':
                                    content = data_obj.get('response', '')
                                    full_response += content
                                    print(content, end='', flush=True)
                                elif data_obj.get('type') == 'end':
                                    break
                                elif data_obj.get('type') == 'error':
                                    error_msg = data_obj.get('content', '未知错误')
                                    print(f"\n❌ 错误: {error_msg}")
                                    self.log_test_result("继续对话", False, f"对话过程中出错: {error_msg}")
                                    return False
                                elif data_obj.get('type') in ['status', 'agent_status']:
                                    # 静默处理状态消息
                                    pass
                                else:
                                    # 尝试其他可能的字段
                                    content = ''
                                    if 'content' in data_obj:
                                        content = data_obj['content']
                                    elif 'output' in data_obj:
                                        content = data_obj['output']
                                    elif 'text' in data_obj:
                                        content = data_obj['text']
                                    elif 'response' in data_obj:
                                        content = data_obj['response']
                                    
                                    if content:
                                        full_response += content
                                        print(content, end='', flush=True)
                            except json.JSONDecodeError:
                                # 可能是纯文本响应
                                full_response += line
                                print(line, end='', flush=True)
                                continue
                        else:
                            # 可能是非SSE格式的流式响应
                            try:
                                data_obj = json.loads(line)
                                content = ''
                                if 'content' in data_obj:
                                    content = data_obj['content']
                                elif 'output' in data_obj:
                                    content = data_obj['output']
                                
                                if content:
                                    full_response += content
                                    print(content, end='', flush=True)
                            except json.JSONDecodeError:
                                # 纯文本响应
                                full_response += line
                                print(line, end='', flush=True)
                
                print(f"\n\n✅ 继续对话完成 (共{response_chunks}个数据块, {len(full_response)}字符)")
                
                if len(full_response) > 0:
                    self.log_test_result(
                        "继续对话", 
                        True, 
                        f"对话ID: {self.conversation_id}, 响应长度: {len(full_response)}字符"
                    )
                    return True
                else:
                    self.log_test_result("继续对话", False, "没有收到有效响应")
                    return False
            else:
                self.log_test_result(
                    "继续对话", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            import traceback
            self.log_test_result("继续对话", False, f"异常: {str(e)}\n详细错误: {traceback.format_exc()}")
            return False
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📊 对话API测试报告")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests} ✅")
        print(f"失败测试: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        print("\n详细结果:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result['success'] else "❌"
            print(f"{i:2d}. {status} {result['test_name']}: {result['details']}")
        
        # 保存测试报告到文件
        report_file = f"chat_api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "summary": {
                        "total_tests": total_tests,
                        "passed_tests": passed_tests,
                        "failed_tests": failed_tests,
                        "success_rate": passed_tests/total_tests*100
                    },
                    "results": self.test_results
                }, f, ensure_ascii=False, indent=2)
            print(f"\n📄 测试报告已保存到: {report_file}")
        except Exception as e:
            print(f"\n❌ 保存测试报告失败: {e}")
        
        return passed_tests == total_tests
    
    def run_chat_tests(self) -> bool:
        """运行对话相关测试"""
        print("🚀 开始对话API专项测试")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试目标: {self.base_url}")
        print("="*60)
        
        # 按顺序执行测试
        test_methods = [
            self.test_1_user_registration,
            self.test_2_user_login,
            self.test_3_create_conversation,
            self.test_4_continue_conversation
        ]
        
        for test_method in test_methods:
            try:
                test_method()
                time.sleep(1)  # 测试间隔
            except Exception as e:
                test_name = test_method.__name__.replace('test_', '').replace('_', ' ').title()
                self.log_test_result(test_name, False, f"测试执行异常: {str(e)}")
        
        # 生成测试报告
        return self.generate_test_report()

def main():
    """主函数"""
    print("心理健康聊天机器人 - 对话API专项测试")
    print("="*60)
    
    # 检查服务器是否可访问
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print(f"✅ 服务器可访问: {BASE_URL}")
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print(f"请确保服务器正在运行: {BASE_URL}")
        return False
    
    # 运行测试
    tester = ChatAPITester()
    success = tester.run_chat_tests()
    
    if success:
        print("\n🎉 所有对话API测试通过！")
        return True
    else:
        print("\n⚠️  部分测试失败，请检查对话API实现。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)