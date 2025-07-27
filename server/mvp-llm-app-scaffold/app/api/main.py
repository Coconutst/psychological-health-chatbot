# 导入FastAPI框架
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入聊天相关的端点模块
from app.api.endpoints import conversations
from app.api.endpoints import chat  # 导入聊天模块
from app.api.endpoints import auth  # 导入认证模块
from app.api.endpoints import user_profile  # 导入用户画像模块

# 导入设置配置
from app.configs.settings import get_settings

# 创建FastAPI应用实例，配置应用信息
app = FastAPI(
    title="LLM Application Scaffold - Separated Endpoints",
    description="An API with distinct, stateful endpoints for Knowledge Base (RAG) chat and Agent (Tool-calling) chat.",
    version="2.2.0",
)

# 获取设置实例
settings = get_settings()

# 配置CORS允许的来源
allowed_origins = ["*"]  # 默认允许所有来源
if settings.ALLOWED_ORIGINS:
    # 如果环境变量中配置了ALLOWED_ORIGINS，则使用配置的值
    allowed_origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],  # 明确指定允许的方法
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
        "X-Conversation-ID"  # 添加自定义会话ID头
    ],
    expose_headers=["*"],  # 暴露所有响应头
)

# 注册认证路由，设置路径前缀和标签
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# 注册心理咨询聊天路由，设置路径前缀和标签
app.include_router(chat.router, prefix="/api", tags=["Psychology Chat"])  # 心理咨询聊天端点
# 注册会话管理路由，设置路径前缀和标签
app.include_router(conversations.router, prefix="/api/conversations", tags=["Conversations"])
# 注册用户画像路由，设置路径前缀和标签
app.include_router(user_profile.router, prefix="/api/user", tags=["User Profile"])


# 定义根路径的健康检查端点
@app.get("/", tags=["Health Check"])
def read_root():
    # 返回应用状态和欢迎信息
    return {"status": "ok", "message": "Welcome to the LLM Scaffold API!"}
