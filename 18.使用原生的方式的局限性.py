import os
from langchain_deepseek import ChatDeepSeek
from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser

llm = ChatDeepSeek(
    model="deepseek-chat",  # 模型名称
    temperature=0.8,  # 采样温度：0~1，越大越随机
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 从环境变量读取 API Key
    base_url="https://api.deepseek.com/v1",  # DeepSeek OpenAI 兼容接口
)


@tool
def get_weather(city: str) -> str:
    """获取城市天气"""
    return "广州今天天气22度，晴天 天气很好"


llm_with_tools = llm.bind_tools([get_weather])
chain = llm_with_tools | StrOutputParser()
response = chain.invoke("广州今天天气怎么样")
print(response)
