"""
DeepSeek 调用示例：使用 LangChain 调用 DeepSeek
"""

from ast import List
import os
from typing import Iterator
from langchain_deepseek import ChatDeepSeek
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

llm = ChatDeepSeek(
    model="deepseek-chat",  # 模型名称
    temperature=0.8,  # 采样温度：0~1，越大越随机
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 从环境变量读取 API Key
    base_url="https://api.deepseek.com/v1",  # DeepSeek OpenAI 兼容接口
)

prompt = ChatPromptTemplate.from_template(
    "给我列举一下{country}最厉害的间谍组织，并给出它们的详细信息"
)


def split_into_list(input: Iterator[str]) -> Iterator[List[str]]:
    # 保存部分输入直到遇到逗号
    buffer = ""
    for chunk in input:
        # 将当前块添加到缓冲区
        buffer += chunk
        # 当缓冲区中有逗号时
        while "," in buffer:
            # 在逗号处分割缓冲区
            comma_index = buffer.index(",")
            # 输出逗号之前的所有内容
            yield [buffer[:comma_index].strip()]
            # 保存剩余部分用于下一次迭代
            buffer = buffer[comma_index + 1 :]
    # 输出最后一块
    yield [buffer.strip()]

chain = prompt | llm | split_into_list | StrOutputParser()
print(chain.invoke({"country": "美国"}))
