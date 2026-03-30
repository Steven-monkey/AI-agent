"""
DeepSeek 调用示例：使用 LangChain 调用 DeepSeek



return 与 yield 的区别（结合本文件里的 split_into_list）：



- return：普通函数里「交还控制权并结束」。执行到 return 后，函数这一次调用就结束，

  局部变量销毁；再次调用会从头执行。一次调用最多沿 return 路径结束一次。



- yield：只在「生成器函数」里使用；遇到 yield 时，把右侧的值「产出」给调用方，

  但函数**暂停**在 yield 之后，局部变量保留；下次从暂停处继续跑，再遇到 yield 再产出。

  这样同一次「逻辑流程」可以多次向外给值，适合流式、分段结果、惰性迭代。



- 本链中 split_into_list 用 yield：上游（模型）可能一块块吐字符，按逗号切好后

  每凑齐一段就 yield 一个列表，下游 Runnable 可以边收边处理；若改成 return 一个

  大列表，要么得等全部处理完才能返回，要么无法用这种「多次产出」的写法。



"""

import os
from typing import Iterator, List

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
    # 本函数是生成器：用 yield 多次产出，而不是 return 一次交卷。
    # 保存部分输入直到遇到逗号
    buffer = ""
    for chunk in input:
        # 将当前块添加到缓冲区
        buffer += chunk
        # 当缓冲区中有逗号时
        while "," in buffer:
            # 在逗号处分割缓冲区
            comma_index = buffer.index(",")
            # yield：产出当前这一段列表，函数暂停；流式链路可继续消费后续块。
            yield [buffer[:comma_index].strip()]
            # 保存剩余部分用于下一次迭代
            buffer = buffer[comma_index + 1 :]
    # 最后一段也用 yield 产出（若用 return，只能返回一次，无法与上面多次 yield 并存于同一逻辑流）。
    yield [buffer.strip()]


chain = prompt | llm | split_into_list | StrOutputParser()
print(chain.invoke({"country": "美国"}))
