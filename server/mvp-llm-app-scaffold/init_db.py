#!/usr/bin/env python3
"""
数据库初始化脚本

此脚本用于初始化数据库表结构，确保所有必要的表和字段都已创建
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.configs.database import init_database, check_database_connection, engine
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.base import BaseModel
from sqlalchemy import text
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database_if_not_exists():
    """创建数据库（如果不存在）"""
    try:
        from app.configs.database import db_settings
        from sqlalchemy import create_engine
        
        # 连接到MySQL服务器（不指定数据库）
        temp_engine = create_engine(db_settings.database_url_without_db)
        
        with temp_engine.connect() as conn:
            # 检查数据库是否存在
            result = conn.execute(text(f"SHOW DATABASES LIKE '{db_settings.mysql_database}'"))
            if not result.fetchone():
                # 创建数据库
                conn.execute(text(f"CREATE DATABASE {db_settings.mysql_database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                conn.commit()
                logger.info(f"✅ 数据库 {db_settings.mysql_database} 创建成功")
            else:
                logger.info(f"✅ 数据库 {db_settings.mysql_database} 已存在")
                
        temp_engine.dispose()
        
    except Exception as e:
        logger.error(f"❌ 创建数据库失败: {e}")
        raise

def check_and_add_emotion_fields():
    """检查并添加情绪相关字段"""
    try:
        with engine.connect() as conn:
            # 检查users表是否存在current_emotion字段
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME IN ('current_emotion', 'emotion_history', 'emotion_updated_at')
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            
            # 添加缺失的字段
            if 'current_emotion' not in existing_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN current_emotion VARCHAR(50) NULL"))
                logger.info("✅ 添加 current_emotion 字段")
            
            if 'emotion_history' not in existing_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN emotion_history JSON NULL"))
                logger.info("✅ 添加 emotion_history 字段")
            
            if 'emotion_updated_at' not in existing_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN emotion_updated_at DATETIME NULL"))
                logger.info("✅ 添加 emotion_updated_at 字段")
            
            conn.commit()
            
            if len(existing_columns) == 3:
                logger.info("✅ 所有情绪相关字段已存在")
                
    except Exception as e:
        logger.error(f"❌ 检查/添加情绪字段失败: {e}")
        raise

def main():
    """主函数"""
    try:
        logger.info("🚀 开始数据库初始化...")
        
        # 1. 创建数据库（如果不存在）
        logger.info("📝 步骤1: 检查/创建数据库")
        create_database_if_not_exists()
        
        # 2. 检查数据库连接
        logger.info("📝 步骤2: 检查数据库连接")
        if not check_database_connection():
            raise Exception("数据库连接失败")
        
        # 3. 创建所有表
        logger.info("📝 步骤3: 创建数据库表")
        init_database()
        
        # 4. 检查并添加情绪相关字段
        logger.info("📝 步骤4: 检查/添加情绪相关字段")
        check_and_add_emotion_fields()
        
        logger.info("🎉 数据库初始化完成！")
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()