#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
密码修改流程测试
测试完整的用户注册、登录、修改密码、退出、再登录流程
"""

import requests
import json
import time
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8002"
API_PREFIX = "/api"

class PasswordChangeFlowTester:
    """密码修改流程测试类"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.test_email = None
        self.original_password = "test123456"
        self.new_password = "newpassword789"
        self.test_results = []
        
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
            if response.status_code != 200:
                print(f"❌ 响应内容: {response.text}")
            return response
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            raise
    
    def test_step_1_register(self) -> bool:
        """步骤1: 用户注册"""
        print("\n🔐 步骤1: 用户注册")
        
        # 生成唯一的测试邮箱
        timestamp = int(time.time())
        self.test_email = f"password_test_{timestamp}@example.com"
        
        register_data = {
            "username": f"密码测试用户_{timestamp}",
            "email": self.test_email,
            "password": self.original_password
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
    
    def test_step_2_login_original(self) -> bool:
        """步骤2: 使用原密码登录"""
        print("\n🔑 步骤2: 使用原密码登录")
        
        if not self.test_email:
            self.log_test_result("原密码登录", False, "没有测试邮箱")
            return False
        
        login_data = {
            "email": self.test_email,
            "password": self.original_password
        }
        
        try:
            response = self._make_request('POST', '/auth/login', json=login_data)
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get('access_token')
                self.refresh_token = result.get('refresh_token')
                
                self.log_test_result(
                    "原密码登录", 
                    True, 
                    "成功使用原密码登录"
                )
                return True
            else:
                self.log_test_result(
                    "原密码登录", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("原密码登录", False, f"异常: {str(e)}")
            return False
    
    def test_step_3_change_password(self) -> bool:
        """步骤3: 修改密码"""
        print("\n🔄 步骤3: 修改密码")
        
        if not self.access_token:
            self.log_test_result("修改密码", False, "没有访问令牌")
            return False
        
        change_password_data = {
            "current_password": self.original_password,
            "new_password": self.new_password
        }
        
        try:
            response = self._make_request('POST', '/auth/change-password', json=change_password_data)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test_result(
                    "修改密码", 
                    True, 
                    f"密码修改成功: {result.get('message', '成功')}"
                )
                return True
            else:
                self.log_test_result(
                    "修改密码", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("修改密码", False, f"异常: {str(e)}")
            return False
    
    def test_step_4_logout(self) -> bool:
        """步骤4: 退出登录"""
        print("\n🚪 步骤4: 退出登录")
        
        if not self.access_token:
            self.log_test_result("退出登录", False, "没有访问令牌")
            return False
        
        try:
            response = self._make_request('POST', '/auth/logout')
            
            if response.status_code == 200:
                # 清除令牌
                self.access_token = None
                self.refresh_token = None
                
                self.log_test_result(
                    "退出登录", 
                    True, 
                    "成功退出登录"
                )
                return True
            else:
                self.log_test_result(
                    "退出登录", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("退出登录", False, f"异常: {str(e)}")
            return False
    
    def test_step_5_login_old_password_should_fail(self) -> bool:
        """步骤5: 使用旧密码登录（应该失败）"""
        print("\n❌ 步骤5: 使用旧密码登录（应该失败）")
        
        if not self.test_email:
            self.log_test_result("旧密码登录测试", False, "没有测试邮箱")
            return False
        
        login_data = {
            "email": self.test_email,
            "password": self.original_password  # 使用旧密码
        }
        
        try:
            response = self._make_request('POST', '/auth/login', json=login_data)
            
            if response.status_code != 200:
                # 登录失败是预期的
                self.log_test_result(
                    "旧密码登录测试", 
                    True, 
                    f"旧密码登录正确失败，状态码: {response.status_code}"
                )
                return True
            else:
                # 登录成功是不对的
                self.log_test_result(
                    "旧密码登录测试", 
                    False, 
                    "旧密码仍然可以登录，密码修改可能失败"
                )
                return False
                
        except Exception as e:
            self.log_test_result("旧密码登录测试", False, f"异常: {str(e)}")
            return False
    
    def test_step_6_login_new_password(self) -> bool:
        """步骤6: 使用新密码登录"""
        print("\n🔑 步骤6: 使用新密码登录")
        
        if not self.test_email:
            self.log_test_result("新密码登录", False, "没有测试邮箱")
            return False
        
        login_data = {
            "email": self.test_email,
            "password": self.new_password  # 使用新密码
        }
        
        try:
            response = self._make_request('POST', '/auth/login', json=login_data)
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get('access_token')
                self.refresh_token = result.get('refresh_token')
                
                self.log_test_result(
                    "新密码登录", 
                    True, 
                    "成功使用新密码登录"
                )
                return True
            else:
                self.log_test_result(
                    "新密码登录", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("新密码登录", False, f"异常: {str(e)}")
            return False
    
    def test_step_7_verify_user_info(self) -> bool:
        """步骤7: 验证用户信息"""
        print("\n👤 步骤7: 验证用户信息")
        
        if not self.access_token:
            self.log_test_result("验证用户信息", False, "没有访问令牌")
            return False
        
        try:
            response = self._make_request('GET', '/auth/me')
            
            if response.status_code == 200:
                result = response.json()
                self.log_test_result(
                    "验证用户信息", 
                    True, 
                    f"用户名: {result.get('username', 'N/A')}, 邮箱: {result.get('email')}"
                )
                return True
            else:
                self.log_test_result(
                    "验证用户信息", 
                    False, 
                    f"状态码: {response.status_code}, 响应: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("验证用户信息", False, f"异常: {str(e)}")
            return False
    
    def run_complete_flow_test(self):
        """运行完整的密码修改流程测试"""
        print("\n🚀 开始密码修改流程测试")
        print(f"测试服务器: {self.base_url}")
        print(f"原密码: {self.original_password}")
        print(f"新密码: {self.new_password}")
        print("=" * 60)
        
        # 执行测试步骤
        test_steps = [
            self.test_step_1_register,
            self.test_step_2_login_original,
            self.test_step_3_change_password,
            self.test_step_4_logout,
            self.test_step_5_login_old_password_should_fail,
            self.test_step_6_login_new_password,
            self.test_step_7_verify_user_info
        ]
        
        success_count = 0
        total_count = len(test_steps)
        
        for step in test_steps:
            try:
                if step():
                    success_count += 1
                else:
                    print(f"\n⚠️ 测试步骤失败: {step.__name__}")
                    # 继续执行后续步骤，但记录失败
            except Exception as e:
                print(f"\n💥 测试步骤异常: {step.__name__}, 错误: {e}")
        
        # 输出测试总结
        print("\n" + "=" * 60)
        print("📊 测试总结")
        print(f"总测试数: {total_count}")
        print(f"成功数: {success_count}")
        print(f"失败数: {total_count - success_count}")
        print(f"成功率: {(success_count / total_count) * 100:.1f}%")
        
        if success_count == total_count:
            print("\n🎉 所有测试通过！密码修改流程正常工作。")
        else:
            print("\n⚠️ 部分测试失败，请检查API实现。")
        
        # 保存测试报告
        self.save_test_report()
        
        return success_count == total_count
    
    def save_test_report(self):
        """保存测试报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"password_change_test_report_{timestamp}.json"
        
        report = {
            "test_type": "password_change_flow",
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "test_email": self.test_email,
            "original_password": self.original_password,
            "new_password": self.new_password,
            "results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed_tests": len([r for r in self.test_results if r['success']]),
                "failed_tests": len([r for r in self.test_results if not r['success']]),
                "success_rate": len([r for r in self.test_results if r['success']]) / len(self.test_results) * 100 if self.test_results else 0
            }
        }
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n📄 测试报告已保存: {report_file}")
        except Exception as e:
            print(f"\n❌ 保存测试报告失败: {e}")

def main():
    """主函数"""
    tester = PasswordChangeFlowTester()
    tester.run_complete_flow_test()

if __name__ == "__main__":
    main()