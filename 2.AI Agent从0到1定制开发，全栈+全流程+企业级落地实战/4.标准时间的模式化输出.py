# 标准事件之结构化输出 - with_structured_output
# 目标：对比两种“结构化输出”写法在 DeepSeek 上的表现。

from typing import Optional
import os

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek

PROMPT = "给我讲一个关于程序员的笑话"


class Joke(BaseModel):
    """结构化笑话的返回格式。"""

    setup: str = Field(description="The setup of the joke")
    punchline: str = Field(description="The punchline to the joke")
    rating: Optional[int] = Field(
        default=None, description="How funny the joke is, from 1 to 10"
    )


# 方案A：ChatOpenAI + method="function_calling"
llm_openai = ChatOpenAI(
    model="deepseek-chat",
    temperature=0.8,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)
structured_openai_fn = llm_openai.with_structured_output(
    Joke, method="function_calling"
)

print("=== 方案A：ChatOpenAI + function_calling ===")
print(structured_openai_fn.invoke(PROMPT))


# 方案B：使用 langchain_deepseek 的 ChatDeepSeek（更贴合 DeepSeek 适配）
llm_deepseek = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.8,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base="https://api.deepseek.com/v1",
)
structured_deepseek = llm_deepseek.with_structured_output(Joke)

print("=== 方案B：ChatDeepSeek + with_structured_output(默认) ===")
print(structured_deepseek.invoke(PROMPT))