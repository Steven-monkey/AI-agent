"""



本文件演示：LangChain 中 @chain 装饰器与「两段式」自定义链。



第一段：根据国家名让模型列举间谍组织；第二段：把第一段解析出的字符串

再填入第二个模板，追问「为什么觉得最厉害的是……」。



@chain 会把被装饰函数包成 Runnable；invoke 时整份输入作为**一个**参数传入，

因此 chain_func 只接收 text（国家名字符串），不要写成 (country, spy_org) 双参数。



"""

# ---------------------------------------------------------------------------

# import（导入）：从标准库或第三方包引入符号。

# ---------------------------------------------------------------------------

import os


# os.getenv：读取环境变量，用于 API Key 等敏感配置。


from langchain_deepseek import ChatDeepSeek


# ChatDeepSeek：DeepSeek 聊天模型封装，可作为链中的一环。


from langchain_core.prompts import ChatPromptTemplate


# ChatPromptTemplate：提示模板；from_template 用占位符（如 {country}）生成最终提示。


from langchain_core.runnables import chain


# chain：装饰器；@chain 将普通函数变成 Runnable，与 LCEL 的 invoke/stream 接口一致。


from langchain_core.output_parsers import StrOutputParser


# StrOutputParser：把模型输出解析为 Python str。


# ---------------------------------------------------------------------------

# 提示模板：第一段用 {country}，第二段用 {spy_org}（此处传入的是第一段解析后的文本）。

# ---------------------------------------------------------------------------

prompt1 = ChatPromptTemplate.from_template(
    # from_template：用单个模板字符串快速建模板；invoke 时字典键须与占位符名一致。
    "给我列举一下{country}最厉害的间谍组织，并给出它们的详细信息",
)


prompt2 = ChatPromptTemplate.from_template("你为什么觉得最厉害的间谍组织是:{spy_org}？")


# ---------------------------------------------------------------------------

# 大模型实例：两段链共用同一个 llm。

# ---------------------------------------------------------------------------

llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.8,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)


# ---------------------------------------------------------------------------

# @chain：包装 chain_func，使其可 chain_func.invoke("以色列") 单次传入字符串。

#

# 函数体内：先 prompt1 | llm | 解析 得到第一段 str，再 prompt2 | llm | 解析 得到第二段 str。

# 内层 chain2 使用 LCEL：| 表示前一个 Runnable 的输出作为后一个的输入。

# ---------------------------------------------------------------------------

@chain
def chain_func(text):
    # text：对应国家名；作为 prompt1 模板变量 country 的值。
    prompt_val1 = prompt1.invoke({"country": text})
    output1 = llm.invoke(prompt_val1)
    parsed_output1 = StrOutputParser().invoke(output1)
    chain2 = prompt2 | llm | StrOutputParser()
    # spy_org：这里填第一段模型输出的字符串，由第二段模板继续追问。
    return chain2.invoke({"spy_org": parsed_output1})


# invoke：传入 str；若用 dict 需与 @chain 的传参约定一致，本例以单字符串演示。

print(chain_func.invoke("以色列"))
