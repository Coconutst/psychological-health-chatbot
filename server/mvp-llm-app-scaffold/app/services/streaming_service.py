"""流式处理服务模块"""

import json
import logging
import requests
from typing import AsyncGenerator, Dict, Any, Optional
from datetime import datetime

from ..configs.settings import api_settings

logger = logging.getLogger(__name__)


class StreamingService:
    """流式处理服务类"""
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {api_settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        self.base_url = api_settings.OPENAI_BASE_URL or "https://api.openai.com/v1"
    
    async def stream_chat_completion(
        self, 
        messages: list, 
        conversation_id: str = None,
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式聊天完成
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            conversation_id: 对话ID
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            
        Yields:
            Dict: 包含流式响应数据的字典
        """
        try:
            # 构建请求数据
            request_data = {
                "model": model,
                "messages": messages,
                "stream": True,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            logger.info(f"[StreamingService] 开始流式请求，模型: {model}")
            
            # 发起流式请求
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=request_data,
                headers=self.headers,
                stream=True,
                timeout=30
            )
            
            if response.status_code != 200:
                error_msg = f"LLM API请求失败: {response.status_code} - {response.text}"
                logger.error(f"[StreamingService] {error_msg}")
                raise Exception(error_msg)
            
            # 流式处理响应
            full_response = ""
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    # 处理SSE格式的数据
                    if line.startswith('data: '):
                        data_str = line[6:]  # 移除'data: '前缀
                        
                        # 检查是否为结束标志
                        if data_str.strip() == '[DONE]':
                            break
                        
                        try:
                            # 解析JSON数据
                            data = json.loads(data_str)
                            
                            # 提取内容
                            if 'choices' in data and len(data['choices']) > 0:
                                choice = data['choices'][0]
                                if 'delta' in choice and 'content' in choice['delta']:
                                    content = choice['delta']['content']
                                    if content:
                                        full_response += content
                                        
                                        # 构建响应数据
                                        response_data = {
                                            "type": "response",
                                            "response": content,
                                            "timestamp": datetime.now().isoformat()
                                        }
                                        
                                        if conversation_id:
                                            response_data["conversation_id"] = conversation_id
                                        
                                        yield response_data
                                        
                        except json.JSONDecodeError as e:
                            logger.warning(f"[StreamingService] JSON解析错误: {e}, 数据: {data_str}")
                            continue
            
            # 返回完整响应
            yield {
                "type": "complete",
                "full_response": full_response,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"[StreamingService] 流式请求完成，响应长度: {len(full_response)}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[StreamingService] 流式请求错误: {e}")
            # 直接抛出异常，不返回错误响应
            raise
            
        except Exception as e:
            logger.error(f"[StreamingService] 流式处理错误: {e}")
            # 直接抛出异常，不返回错误响应
            raise
    
    async def stream_psychological_chat(
        self, 
        user_message: str, 
        conversation_id: str = None,
        system_prompt: str = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式心理咨询聊天
        
        Args:
            user_message: 用户消息
            conversation_id: 对话ID
            system_prompt: 系统提示词
            
        Yields:
            Dict: 包含流式响应数据的字典
        """
        # 默认心理咨询系统提示词
        if not system_prompt:
            system_prompt = (
                "你是一位专业的心理健康咨询师，具有丰富的心理学知识和咨询经验。"
                "请提供专业、温暖、非评判性的心理支持。你的回应应该：\n"
                "1. 体现专业的心理学知识\n"
                "2. 表达理解和共情\n"
                "3. 提供实用的建议和策略\n"
                "4. 使用温暖、支持性的语言\n"
                "5. 在必要时建议寻求专业帮助"
            )
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # 调用通用流式聊天完成方法
        async for response_data in self.stream_chat_completion(
            messages=messages,
            conversation_id=conversation_id,
            temperature=0.7,
            max_tokens=2000
        ):
            yield response_data
    
    def format_sse_data(self, data: Dict[str, Any]) -> str:
        """格式化SSE数据
        
        Args:
            data: 要发送的数据字典
            
        Returns:
            str: 格式化的SSE数据字符串
        """
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    
    async def get_fallback_response(self, error_message: str = None) -> str:
        """获取备用响应
        
        Args:
            error_message: 错误消息
            
        Returns:
            str: 备用响应内容
        """
        fallback_responses = [
            "抱歉，我现在遇到了一些技术问题。请稍后再试，或者寻求专业帮助。",
            "很抱歉，系统暂时无法正常响应。建议您联系专业的心理咨询师获得帮助。",
            "系统正在维护中，请稍后重试。如果您需要紧急帮助，请联系当地的心理健康服务机构。"
        ]
        
        # 根据错误类型选择合适的备用响应
        if error_message and "网络" in error_message:
            return fallback_responses[0]
        elif error_message and "超时" in error_message:
            return fallback_responses[2]
        else:
            return fallback_responses[1]


# 全局流式服务实例
streaming_service = StreamingService()