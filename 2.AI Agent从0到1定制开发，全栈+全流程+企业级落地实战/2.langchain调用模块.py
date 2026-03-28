"""简单的示例脚本：调用 DeepSeek 模型并打印回复。"""

# 用于读取环境变量（如 API 密钥）
import os
# LangChain：兼容 OpenAI 接口的聊天模型（此处用于调用 DeepSeek）
from langchain_openai import ChatOpenAI# Please install OpenAI SDK first: `pip3 install openai`

llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0.8,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)
response=llm.invoke("介绍一下你自己")
print(response)








