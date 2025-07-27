# 数据库配置模块
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, Field
import pymysql
import os
from .settings import api_settings

# 数据库配置类
class DatabaseSettings(BaseModel):
    """数据库配置设置"""
    # MySQL数据库配置
    mysql_host: str = Field(default="localhost", description="MySQL主机地址")
    mysql_port: int = Field(default=3306, description="MySQL端口")
    mysql_user: str = Field(default="root", description="MySQL用户名")
    mysql_password: str = Field(default="", description="MySQL密码")
    mysql_database: str = Field(default="psychological_chatbot", description="数据库名称")
    
    # 数据库连接池配置
    pool_size: int = Field(default=10, description="连接池大小")
    max_overflow: int = Field(default=20, description="最大溢出连接数")
    pool_timeout: int = Field(default=30, description="连接超时时间")
    pool_recycle: int = Field(default=3600, description="连接回收时间")
    
    @property
    def database_url(self) -> str:
        """构建数据库连接URL"""
        return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"
    
    @property
    def database_url_without_db(self) -> str:
        """构建不包含数据库名的连接URL（用于创建数据库）"""
        return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}?charset=utf8mb4"

# 创建数据库设置实例，从环境变量读取配置
db_settings = DatabaseSettings(
    mysql_host=api_settings.MYSQL_HOST,
    mysql_port=api_settings.MYSQL_PORT,
    mysql_user=api_settings.MYSQL_USER,
    mysql_password=api_settings.MYSQL_PASSWORD,
    mysql_database=api_settings.MYSQL_DATABASE
)

# 创建数据库引擎
engine = create_engine(
    db_settings.database_url,
    pool_size=db_settings.pool_size,
    max_overflow=db_settings.max_overflow,
    pool_timeout=db_settings.pool_timeout,
    pool_recycle=db_settings.pool_recycle,
    echo=False,  # 设置为True可以看到SQL语句
    pool_pre_ping=True  # 连接前检查连接是否有效
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# 数据库依赖注入函数
def get_db() -> Session:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 数据库初始化函数
def init_database():
    """初始化数据库表"""
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功")
    except Exception as e:
        print(f"❌ 数据库表创建失败: {e}")
        raise

# 检查数据库连接
def check_database_connection() -> bool:
    """检查数据库连接是否正常"""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("✅ 数据库连接正常")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False