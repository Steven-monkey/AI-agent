import os  # 从环境变量读取 DEEPSEEK_API_KEY 等配置
from langchain_deepseek import ChatDeepSeek  # DeepSeek 专用 LangChain 聊天模型封装


llm = ChatDeepSeek(  # 创建一个可复用的模型客户端实例
    model="deepseek-chat",  # 指定 DeepSeek 模型名称
    temperature=0.8,  # 采样温度：越大越随机
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # API Key：从环境变量读取，避免写死在代码中
    base_url="https://api.deepseek.com/v1",  # DeepSeek API 基地址（OpenAI 兼容 v1 路径）
)

response = llm.invoke("介绍一下你自己")  # 同步调用模型：返回 LangChain 的响应对象
print(response.usage_metadata)