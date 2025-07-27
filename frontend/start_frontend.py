#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端启动脚本
用于启动Vue.js前端开发服务器
"""

import os
import sys
import subprocess
import platform

def check_node_npm():
    """检查Node.js和npm是否已安装"""
    # 检查Node.js
    try:
        node_version = subprocess.run(['node', '--version'], 
                                    capture_output=True, text=True, check=True)
        print(f"✓ Node.js版本: {node_version.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 错误: 未找到Node.js")
        print("请先安装Node.js: https://nodejs.org/")
        return False
    
    # 检查npm
    try:
        npm_version = subprocess.run(['npm', '--version'], 
                                   capture_output=True, text=True, check=True, shell=True)
        print(f"✓ npm版本: {npm_version.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 错误: 未找到npm")
        print("请先安装Node.js: https://nodejs.org/")
        return False
        
    return True

def install_dependencies():
    """安装项目依赖"""
    print("\n📦 检查并安装依赖...")
    try:
        # 检查package.json是否存在
        if not os.path.exists('package.json'):
            print("❌ 错误: 未找到package.json文件")
            return False
            
        # 检查node_modules是否存在
        if not os.path.exists('node_modules'):
            print("正在安装依赖...")
            subprocess.run(['npm', 'install'], check=True, shell=True)
            print("✓ 依赖安装完成")
        else:
            print("✓ 依赖已存在")
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def start_dev_server():
    """启动开发服务器"""
    print("\n🚀 启动前端开发服务器...")
    try:
        # 启动开发服务器
        print("正在启动Vue.js开发服务器...")
        print("服务器将在 http://localhost:3000 启动")
        print("按 Ctrl+C 停止服务器\n")
        
        subprocess.run(['npm', 'run', 'dev'], check=True, shell=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
        return True

def main():
    """主函数"""
    print("=" * 50)
    print("🌟 心理健康聊天机器人 - 前端启动脚本")
    print("=" * 50)
    
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"📁 工作目录: {os.getcwd()}")#111
    
    # 检查Node.js和npm
    if not check_node_npm():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 启动开发服务器
    start_dev_server()

if __name__ == "__main__":
    main()