# 认证相关API端点
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
import uuid
import logging
from datetime import datetime

# 导入数据库相关模块
from app.configs.database import get_db
from app.models.user import User
from app.configs.settings import get_settings
from app.utils.datetime_utils import beijing_now_naive

# 创建API路由器实例
router = APIRouter()

# 匿名用户类
class AnonymousUser:
    """匿名用户类，用于未登录用户"""
    def __init__(self):
        self.user_id = "anonymous"
        self.email = "anonymous@example.com"
        self.username = "匿名用户"
        self.is_active = True
        self.is_anonymous = True
        self.chat_count = 0  # 聊天次数计数
        self.max_chat_count = 105  # 最大聊天次数限制

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = "your-secret-key-here"  # 在生产环境中应该从环境变量读取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# HTTP Bearer认证
security = HTTPBearer()

# 请求模型
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., min_length=6, description="用户密码")

class RegisterRequest(BaseModel):
    username: Optional[str] = Field(None, description="用户名")
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., min_length=6, description="用户密码")

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=6, description="新密码")

# 响应模型
class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    username: Optional[str] = None

class UserInfo(BaseModel):
    user_id: str
    email: str
    username: Optional[str] = None
    is_active: bool
    created_at: str

# 工具函数
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = beijing_now_naive() + expires_delta
    else:
        expire = beijing_now_naive() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = beijing_now_naive() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """获取当前用户"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [AUTH DEBUG] get_current_user 被调用")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        print(f"[{timestamp}] [AUTH DEBUG] 没有提供认证凭证")
        raise credentials_exception
        
    print(f"[{timestamp}] [AUTH DEBUG] 收到的token前缀: {credentials.credentials[:20]}...")
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"[{timestamp}] [AUTH DEBUG] JWT解析成功，payload: {payload}")
        user_id: str = payload.get("sub")
        print(f"[{timestamp}] [AUTH DEBUG] 从token中提取的user_id: {user_id}")
        if user_id is None:
            print(f"[{timestamp}] [AUTH DEBUG] user_id为None，抛出异常")
            raise credentials_exception
    except JWTError as e:
        print(f"[{timestamp}] [AUTH DEBUG] JWT解析失败: {e}")
        raise credentials_exception
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        print(f"[{timestamp}] [AUTH DEBUG] 数据库中未找到user_id为{user_id}的用户")
        raise credentials_exception
    
    print(f"[{timestamp}] [AUTH DEBUG] 成功找到用户: {str(user.user_id)}, email: {str(user.email)}")
    return user

def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)), db: Session = Depends(get_db)):
    """获取当前用户（可选认证，支持匿名用户）"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [AUTH DEBUG] get_current_user_optional 被调用")
    
    # 如果没有提供认证凭证，返回匿名用户
    if not credentials:
        print(f"[{timestamp}] [AUTH DEBUG] 没有提供认证凭证，返回匿名用户")
        return AnonymousUser()
    
    print(f"[{timestamp}] [AUTH DEBUG] 收到的token前缀: {credentials.credentials[:20]}...")
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"[{timestamp}] [AUTH DEBUG] JWT解析成功，payload: {payload}")
        user_id: str = payload.get("sub")
        print(f"[{timestamp}] [AUTH DEBUG] 从token中提取的user_id: {user_id}")
        if user_id is None:
            print(f"[{timestamp}] [AUTH DEBUG] user_id为None，返回匿名用户")
            return AnonymousUser()
    except JWTError as e:
        print(f"[{timestamp}] [AUTH DEBUG] JWT解析失败: {e}，返回匿名用户")
        return AnonymousUser()
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        print(f"[{timestamp}] [AUTH DEBUG] 数据库中未找到user_id为{user_id}的用户，返回匿名用户")
        return AnonymousUser()
    
    print(f"[{timestamp}] [AUTH DEBUG] 成功找到用户: {str(user.user_id)}, email: {str(user.email)}")
    # 为真实用户添加is_anonymous属性
    user.is_anonymous = False
    return user

# API端点
@router.post("/register", response_model=AuthResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查邮箱是否已存在
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 创建新用户
    user = User(
        user_id=str(uuid.uuid4()),
        username=request.username,
        email=request.email,
        password_hash=get_password_hash(request.password),
        is_active="true"
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 生成令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user.user_id)})
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=str(user.user_id),
        email=str(user.email),
        username=str(user.username) if user.username else None
    )

@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, str(user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.is_active != "true":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # 更新最后登录时间
    setattr(user, 'last_login_at', beijing_now_naive())
    db.commit()
    
    # 生成令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user.user_id)})
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=str(user.user_id),
        email=str(user.email),
        username=str(user.username) if user.username else None
    )

@router.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """刷新访问令牌"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise credentials_exception
    
    # 生成新的访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/validate")
def validate_token(current_user: User = Depends(get_current_user)):
    """验证令牌"""
    return UserInfo(
        user_id=str(current_user.user_id),
        email=str(current_user.email),
        username=str(current_user.username) if current_user.username else None,
        is_active=current_user.is_active == "true",
        created_at=current_user.created_at.isoformat()
    )

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """用户登出"""
    # 在实际应用中，这里可以将令牌加入黑名单
    # 目前只是返回成功消息
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserInfo)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserInfo(
        user_id=str(current_user.user_id),
        email=str(current_user.email),
        username=str(current_user.username) if current_user.username else None,
        is_active=current_user.is_active == "true",
        created_at=current_user.created_at.isoformat()
    )

@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改用户密码"""
    # 验证当前密码
    if not verify_password(request.current_password, str(current_user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # 检查新密码是否与当前密码相同
    if verify_password(request.new_password, str(current_user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # 更新密码
    current_user.password_hash = get_password_hash(request.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}