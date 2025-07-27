#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心理健康聊天机器人 - 全面API自动化测试
从用户注册开始，测试所有主要功能接口
"""

import requests
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
import os

# API基础配置
BASE_URL = "http://localhost:8002"
API_PREFIX = "/api"

class ComprehensiveAPITester:
    """全面的API测试类"""
    
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
        self.test_email = f"comprehensive_test_{timestamp}@example.com"
        
        # 注册用户
        register_data = {
            "username": f"综合测试用户_{timestamp}",
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
    
    def test_3_token_validation(self) -> bool:
        """测试3: 令牌验证"""
        print("\n🔍 测试3: 令牌验证")
        
        if not self.access_token:
            self.log_test_result("令牌验证", False, "没有访问令牌")
            return False
        
        try:
            response = self._make_request('POST', '/auth/validate')
            
            if response.status_code == 200:
                result = response.json()
                self.log_test_result(
                    "令牌验证", 
                    True, 
                    f"用户信息: {result.get('username', 'N/A')}, 活跃状态: {result.get('is_active')}"
                )
                return True
            else:
                self.log_test_result(
                    "令牌验证", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("令牌验证", False, f"异常: {str(e)}")
            return False
    
    def test_4_get_user_info(self) -> bool:
        """测试4: 获取用户信息"""
        print("\n👤 测试4: 获取用户信息")
        
        if not self.access_token:
            self.log_test_result("获取用户信息", False, "没有访问令牌")
            return False
        
        try:
            response = self._make_request('GET', '/auth/me')
            
            if response.status_code == 200:
                result = response.json()
                self.log_test_result(
                    "获取用户信息", 
                    True, 
                    f"用户名: {result.get('username', 'N/A')}, 邮箱: {result.get('email')}"
                )
                return True
            else:
                self.log_test_result(
                    "获取用户信息", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("获取用户信息", False, f"异常: {str(e)}")
            return False
    
    def test_5_create_conversation(self) -> bool:
        """测试5: 创建对话"""
        print("\n💬 测试5: 创建对话")
        
        if not self.access_token:
            self.log_test_result("创建对话", False, "没有访问令牌")
            return False
        
        # 生成新的对话ID
        new_conversation_id = str(uuid.uuid4())
        self.conversation_id = new_conversation_id
        
        data = {
            "message": "你好，我想测试心理健康聊天功能。我最近感到有些焦虑，能给我一些建议吗？",
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
                    self.log_test_result("创建对话", False, f"没有收到有效响应，原始数据: {raw_lines[:3]}")
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
    
    def test_6_get_conversation_messages(self) -> bool:
        """测试6: 获取对话消息列表"""
        print("\n📋 测试6: 获取对话消息列表")
        
        if not self.access_token or not self.conversation_id:
            self.log_test_result("获取对话消息", False, "没有访问令牌或对话ID")
            return False
        
        try:
            response = self._make_request('GET', f'/conversations/{self.conversation_id}/messages')
            
            if response.status_code == 200:
                messages = response.json()
                
                # 保存assistant消息的message_id用于后续测试
                assistant_messages = 0
                for message in messages:
                    if message.get('role') == 'assistant':
                        message_id = message.get('message_id')
                        if message_id:
                            self.message_ids.append(message_id)
                            assistant_messages += 1
                            print(f"📝 保存消息ID: {message_id}")
                
                self.log_test_result(
                    "获取对话消息", 
                    True, 
                    f"获取到 {len(messages)} 条消息，其中 {assistant_messages} 条助手消息"
                )
                return len(messages) > 0
            else:
                self.log_test_result(
                    "获取对话消息", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("获取对话消息", False, f"异常: {str(e)}")
            return False
    
    def test_7_message_feedback_positive(self) -> bool:
        """测试7: 消息正面反馈"""
        print("\n👍 测试7: 消息正面反馈")
        
        if not self.access_token or not self.message_ids:
            self.log_test_result("消息正面反馈", False, "没有访问令牌或消息ID")
            return False
        
        message_id = self.message_ids[0]  # 使用第一个消息ID
        data = {"feedback": 1}  # 正面反馈
        
        try:
            response = self._make_request('PATCH', f'/conversations/messages/{message_id}/feedback', json=data)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test_result(
                    "消息正面反馈", 
                    True, 
                    f"消息ID: {message_id}, 反馈值: 1"
                )
                return True
            else:
                self.log_test_result(
                    "消息正面反馈", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("消息正面反馈", False, f"异常: {str(e)}")
            return False
    
    def test_8_message_feedback_negative(self) -> bool:
        """测试8: 消息负面反馈"""
        print("\n👎 测试8: 消息负面反馈")
        
        if not self.access_token or len(self.message_ids) < 1:
            self.log_test_result("消息负面反馈", False, "没有访问令牌或足够的消息ID")
            return False
        
        # 如果只有一个消息，就用同一个消息测试负面反馈
        message_id = self.message_ids[0]
        data = {"feedback": -1}  # 负面反馈
        
        try:
            response = self._make_request('PATCH', f'/conversations/messages/{message_id}/feedback', json=data)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test_result(
                    "消息负面反馈", 
                    True, 
                    f"消息ID: {message_id}, 反馈值: -1"
                )
                return True
            else:
                self.log_test_result(
                    "消息负面反馈", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("消息负面反馈", False, f"异常: {str(e)}")
            return False
    
    def test_9_additional_conversation(self) -> bool:
        """测试9: 继续对话"""
        print("\n🔄 测试9: 继续对话")
        
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
                                    # 处理新的响应格式
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
                            except json.JSONDecodeError as e:
                                print(f"⚠️ JSON解析错误: {e}, 数据: {data_str[:100]}...")
                                # 可能是纯文本响应
                                full_response += line
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
                        f"响应长度: {len(full_response)}字符"
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
    
    def test_10_token_refresh(self) -> bool:
        """测试10: 令牌刷新"""
        print("\n🔄 测试10: 令牌刷新")
        
        if not self.refresh_token:
            self.log_test_result("令牌刷新", False, "没有刷新令牌")
            return False
        
        try:
            # 使用查询参数而不是请求体参数
            url = f"{self.base_url}{API_PREFIX}/auth/refresh"
            params = {"refresh_token": self.refresh_token}
            headers = {}
            if self.access_token:
                headers['Authorization'] = f'Bearer {self.access_token}'
            
            print(f"📤 POST {url}")
            print(f"📦 查询参数: refresh_token={self.refresh_token[:50]}...")
            
            response = self.session.post(url, params=params, headers=headers)
            print(f"📥 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                new_access_token = result.get('access_token')
                if new_access_token:
                    old_token_prefix = self.access_token[:20] if self.access_token else "N/A"
                    self.access_token = new_access_token  # 更新访问令牌
                    
                    self.log_test_result(
                        "令牌刷新", 
                        True, 
                        f"成功获取新的访问令牌"
                    )
                    return True
                else:
                    self.log_test_result("令牌刷新", False, "响应中没有新的访问令牌")
                    return False
            else:
                self.log_test_result(
                    "令牌刷新", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("令牌刷新", False, f"异常: {str(e)}")
            return False
    
    def test_11_change_password(self) -> bool:
        """测试11: 修改用户密码"""
        print("\n🔐 测试11: 修改用户密码")
        
        if not self.access_token:
            self.log_test_result("修改用户密码", False, "没有访问令牌")
            return False
        
        try:
            # 测试修改密码
            change_password_data = {
                "current_password": "testpassword123",
                "new_password": "newtestpassword123"
            }
            
            response = self._make_request('POST', '/auth/change-password', json=change_password_data)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test_result(
                    "修改用户密码", 
                    True, 
                    f"消息: {result.get('message', '密码修改成功')}"
                )
                
                # 测试用新密码登录
                print("\n🔄 验证新密码登录...")
                login_data = {
                    "username": self.test_username,
                    "password": "newtestpassword123"
                }
                
                login_response = self._make_request('POST', '/auth/login', json=login_data, use_auth=False)
                
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    # 更新token以便后续测试
                    self.access_token = login_result.get('access_token')
                    self.refresh_token = login_result.get('refresh_token')
                    
                    self.log_test_result(
                        "新密码登录验证", 
                        True, 
                        "新密码登录成功"
                    )
                    return True
                else:
                    self.log_test_result(
                        "新密码登录验证", 
                        False, 
                        f"新密码登录失败: {login_response.status_code}"
                    )
                    return False
            else:
                self.log_test_result(
                    "修改用户密码", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("修改用户密码", False, f"异常: {str(e)}")
            return False
    
    def test_12_logout(self) -> bool:
        """测试12: 用户登出"""
        print("\n🚪 测试12: 用户登出")
        
        if not self.access_token:
            self.log_test_result("用户登出", False, "没有访问令牌")
            return False
        
        try:
            response = self._make_request('POST', '/auth/logout')
            
            if response.status_code == 200:
                result = response.json()
                self.log_test_result(
                    "用户登出", 
                    True, 
                    f"消息: {result.get('message', '成功登出')}"
                )
                return True
            else:
                self.log_test_result(
                    "用户登出", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("用户登出", False, f"异常: {str(e)}")
            return False
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📊 测试报告")
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
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    
    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("🚀 开始全面API自动化测试")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试目标: {self.base_url}")
        print("="*60)
        
        # 按顺序执行所有测试
        test_methods = [
            self.test_1_user_registration,
            self.test_2_user_login,
            self.test_3_token_validation,
            self.test_4_get_user_info,
            self.test_5_create_conversation,
            self.test_6_get_conversation_messages,
            self.test_7_message_feedback_positive,
            self.test_8_message_feedback_negative,
            self.test_9_additional_conversation,
            self.test_10_token_refresh,
            self.test_11_change_password,
            self.test_12_logout
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
    print("心理健康聊天机器人 - 全面API自动化测试")
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
    tester = ComprehensiveAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 所有测试通过！API功能正常。")
        return True
    else:
        print("\n⚠️  部分测试失败，请检查服务器状态和配置。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)