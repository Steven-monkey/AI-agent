# -*- coding: utf-8 -*-
"""
本示例演示：用 LangChain 的 bind_tools 把「工具定义」绑定到聊天模型（DeepSeek），
让模型根据用户问题决定是否调用工具、以及用哪些参数调用。

下面注释会说明：每个 import、每个类/字段、每个变量在整条链路里扮演什么角色。
"""

# ---------------------------------------------------------------------------
# 导入说明
# ---------------------------------------------------------------------------
# BaseModel：Pydantic 的基类。继承它后，类体里的字段名 + 类型注解会生成「数据模型」，
#   LangChain 用它来表示「工具的名字、参数结构、说明」，从而转成 OpenAI 的 function/tool 格式。
# Field：给字段加「约束」和「描述」；description 会传给模型，帮助它理解何时、如何填参数。
from pydantic import BaseModel, Field

# ChatDeepSeek：LangChain 对 DeepSeek 聊天接口的封装；协议与 OpenAI Chat Completions 兼容，
#   因此同样支持 bind_tools、invoke 等用法，base_url 指向 DeepSeek 官方或自建兼容网关。
from langchain_deepseek import ChatDeepSeek

# os：读取环境变量，避免把 API 密钥写死在代码里。
import os

# ---------------------------------------------------------------------------
# 「工具」在这里用 Pydantic 模型表示（不是普通 Python 函数）
# ---------------------------------------------------------------------------
# 类名 add / multiply 会作为「工具名称」出现在 bind_tools 之后模型可见的工具列表里
# （具体命名规则以 LangChain + 模型提供商为准，一般与类名对应）。


class add(BaseModel):
    """Add two integers.
    类文档字符串：有的版本/链路会把它当作工具说明的一部分；与 Field 的 description 互补。
    """

    # a、b：工具的两个参数名；模型若决定调用 add，会在 tool_calls 里给出 argument 的 JSON，
    #   键名就是这里的 a、b。
    # int：参数类型，会参与生成 JSON Schema，约束模型只能填整数（或可被解析为整数的值）。
    # Field(..., ...)：... 表示该字段必填（无默认值）。
    # description：给人/模型看的自然语言说明，帮助模型正确填参。
    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")


class multiply(BaseModel):
    """Multiply two integers."""

    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")


# ---------------------------------------------------------------------------
# llm：裸的聊天模型实例（尚未绑定任何工具）
# ---------------------------------------------------------------------------
# model：DeepSeek 侧提供的模型 id（如 deepseek-chat），须与账号与 base_url 可用模型一致。
# temperature：采样温度，常见 0~2（此处 0.8）；数值越高回复越多样，选工具时也可能略不稳定，
#   若你更在意「每次选同一工具、参数一致」，可改小（例如 0~0.3）。
# api_key：DeepSeek API 密钥；建议用环境变量 DEEPSEEK_API_KEY，勿提交到仓库。
# base_url：OpenAI 兼容 REST 根路径；官方一般为 https://api.deepseek.com/v1（末尾 /v1 视 SDK 要求而定）。
llm = ChatDeepSeek(
    model="deepseek-chat",  # DeepSeek 对话模型名称
    temperature=0.8,  # 采样温度：越高越随机
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 从环境变量读取，未设置则为 None
    base_url="https://api.deepseek.com/v1",  # DeepSeek OpenAI 兼容接口基址
)

# tools：「工具定义」的列表。元素必须是可被 bind_tools 接受的类型：
#   常见是 Pydantic 子类（本例）、或 @tool 装饰的函数、或 StructuredTool 等。
# 顺序一般只影响展示/部分实现的稳定性，不影响「能否调用」。
tools = [add, multiply]

# llm_with_tools：在 llm 上绑定了 tools 后的 Runnable（可链式调用）。
# bind_tools(tools) 的作用：
#   1）把每个工具转成模型 API 所需的 schema（OpenAI 兼容的 tools 格式，DeepSeek 兼容接口同样支持）；
#   2）之后 invoke 时，模型可以返回普通文本，也可以返回 tool_calls（结构化调用请求）。
# 注意：这里只是「让模型会选工具」，并不会自动执行 Python 里的乘加——要执行需另写代码解析 tool_calls。
llm_with_tools = llm.bind_tools(tools)

# query：发给模型的用户消息内容（字符串形式的一条用户输入）。
query = "3乘以12是多少？"

# invoke(query)：同步调用，把 query 包装成 HumanMessage 等消息后发给模型。
# 返回的是 AIMessage（或子类），上面可能有：
#   - .content：模型给用户的自然语言（可能为空，若模型只返回工具调用）；
#   - .tool_calls：列表，每项通常含 name（工具名）、args（参数 dict）等（具体结构以版本为准）。
# 下面只写 .tool_calls 会取出该列表；若要在终端看到结果，需要用 print(...) 包起来。
response = llm_with_tools.invoke(query)
print("完整响应:", response)
print("模型请求调用的工具:", response.tool_calls)
