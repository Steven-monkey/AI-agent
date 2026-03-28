"""
DeepSeek 调用示例：使用 LangChain 调用 DeepSeek 
"""
import os
from langchain_deepseek import ChatDeepSeek


llm = ChatDeepSeek(
    model="deepseek-chat",  # 模型名称
    temperature=0.8,  # 采样温度：0~1，越大越随机
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 从环境变量读取 API Key
    base_url="https://api.deepseek.com/v1",  # DeepSeek OpenAI 兼容接口
)
