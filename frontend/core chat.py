# streaming_service.py
# from openai import AsyncOpenAI
# import json
#
# class StreamingService:
#     def __init__(self):
#         self.client = AsyncOpenAI(
#             api_key="your_deepseek_key",
#             base_url="https://api.deepseek.com/v1"
#         )
#
#     async def stream_chat(self, messages: list[dict], **kwargs) -> str:
#         """核心聊天流式接口"""
#         completion = await self.client.chat.completions.create(
#             model="deepseek-chat",
#             messages=messages,
#             stream=True,
#             temperature=kwargs.get("temperature", 0.75),
#             max_tokens=kwargs.get("max_tokens", 512)
#         )
#         async for chunk in completion:
#             delta = chunk.choices[0].delta.content or ""
#             yield f"data: {json.dumps({'delta': delta}, ensure_ascii=False)}\n\n"

# 判断是否为危机意图
# if intent == "crisis":
#     yield "data: {\"type\":\"alert\",\"msg\":\"检测到高风险内容，请拨打400-161-9995\"}\n\n"
#     return
