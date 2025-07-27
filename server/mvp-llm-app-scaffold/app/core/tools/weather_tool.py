import random
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# 使用 Pydantic 定义工具的输入参数，这对于模型的理解至关重要
class WeatherInput(BaseModel):
    city: str = Field(description="The name of the city for which to get the weather.")

@tool(args_schema=WeatherInput)
def get_current_weather(city: str) -> str:
    """
    Get the current weather for a specific city.
    Use this tool when you need to find out the weather.
    """
    # 这是一个模拟工具，真实场景下你会在这里调用天气API
    print(f"--- Calling Weather Tool for city: {city} ---")
    if "beijing" in city.lower():
        return f"The weather in Beijing is sunny, 25°C."
    elif "shanghai" in city.lower():
        return f"It's raining in Shanghai, 22°C."
    else:
        # 随机返回一个天气，让它更有趣
        temp = random.randint(15, 30)
        return f"The weather in {city} is clear, {temp}°C."