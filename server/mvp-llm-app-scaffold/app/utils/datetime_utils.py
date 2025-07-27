"""时间处理工具模块"""
from datetime import datetime, timezone, timedelta
from typing import Optional

# 中国北京时间时区（UTC+8）
BEIJING_TZ = timezone(timedelta(hours=8))

def beijing_now() -> datetime:
    """获取当前北京时间"""
    return datetime.now(BEIJING_TZ)

def utc_to_beijing(utc_dt: datetime) -> datetime:
    """将UTC时间转换为北京时间"""
    if utc_dt.tzinfo is None:
        # 如果没有时区信息，假设是UTC时间
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(BEIJING_TZ)

def beijing_to_utc(beijing_dt: datetime) -> datetime:
    """将北京时间转换为UTC时间"""
    if beijing_dt.tzinfo is None:
        # 如果没有时区信息，假设是北京时间
        beijing_dt = beijing_dt.replace(tzinfo=BEIJING_TZ)
    return beijing_dt.astimezone(timezone.utc)

def format_beijing_time(dt: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化北京时间为字符串"""
    if dt is None:
        dt = beijing_now()
    elif dt.tzinfo is None:
        # 如果没有时区信息，假设是UTC时间并转换为北京时间
        dt = utc_to_beijing(dt)
    elif dt.tzinfo != BEIJING_TZ:
        # 如果有时区信息但不是北京时间，转换为北京时间
        dt = dt.astimezone(BEIJING_TZ)
    
    return dt.strftime(format_str)

def parse_beijing_time(time_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """解析时间字符串为北京时间"""
    dt = datetime.strptime(time_str, format_str)
    return dt.replace(tzinfo=BEIJING_TZ)

# 为了兼容现有代码，提供一个替代datetime.utcnow()的函数
# 但实际返回北京时间的naive datetime（去掉时区信息）
def beijing_now_naive() -> datetime:
    """获取当前北京时间（无时区信息）
    
    用于替代datetime.utcnow()，但返回北京时间
    这样可以保持与现有数据库字段的兼容性
    """
    return beijing_now().replace(tzinfo=None)