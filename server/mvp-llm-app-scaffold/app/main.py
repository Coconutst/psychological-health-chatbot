# 主应用入口文件
from app.api.main import app

# 导出app实例供uvicorn使用
__all__ = ["app"]