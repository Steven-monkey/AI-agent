"""



本文件演示：LangChain 中「链（chain）」的基本用法。



链 = 把「提示模板 → 大模型 → 输出解析」像流水线一样串起来，一次 invoke 跑完全程。



"""

# ---------------------------------------------------------------------------

# import（导入）：从别的 Python 文件/库里拿来名字，当前文件才能用。

# ---------------------------------------------------------------------------

import os


# os：Python 标准库 module（模块），名字来自 "operating system"。

# 常用：读环境变量、路径操作等。这里主要用 os.getenv。


from langchain_deepseek import ChatDeepSeek


# from ... import ...：从指定模块里只导入某一个（或几个）名字。

# langchain_deepseek：第三方包，封装 DeepSeek 的聊天模型。

# ChatDeepSeek：类名，Chat = 对话式，DeepSeek = 厂商/模型系列；实例化后得到可调用的「聊天模型」对象。


from langchain_core.prompts import ChatPromptTemplate


# langchain_core：LangChain 核心库；prompts 子模块放各类「提示」模板。

# ChatPromptTemplate：类名，Template = 模板；Chat = 面向多轮/聊天消息结构。

# 作用：用带占位符的字符串生成「最终发给模型的提示」。


from langchain_core.output_parsers import StrOutputParser


# output_parsers：把模型原始输出「解析」成 Python 方便用的类型。

# StrOutputParser：类名，Str = string（字符串）；把模型返回解析成普通 str。


# ---------------------------------------------------------------------------

# 实例化大模型：llm = Large Language Model 的惯用缩写变量名。

# ---------------------------------------------------------------------------

llm = ChatDeepSeek(
    # model：参数名，字符串，指定远端 API 要跑哪一个模型。
    model="deepseek-chat",
    # temperature：采样温度。常见范围因厂商而异：许多 OpenAI 兼容接口支持约 0～2。
    # 越大：输出越随机、越有「发散」感；越小：越接近贪心/高概率词，越稳定。
    # 设为 1.5 比 0.8 更随机；若接口只认 0～1，需按官方文档改回范围内。
    temperature=1.5,
    # api_key：鉴权密钥；os.getenv("DEEPSEEK_API_KEY") 从系统环境变量里读同名变量。
    # getenv = get environment variable（获取环境变量）；若未设置则为 None，可能报错。
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    # base_url：API 根地址；DeepSeek 提供 OpenAI 兼容 REST 接口，故路径常带 /v1。
    base_url="https://api.deepseek.com/v1",
)


# ---------------------------------------------------------------------------

# 提示模板：花括号 {input} 是占位符，invoke 时再传入真实值。

# ---------------------------------------------------------------------------

prompt = ChatPromptTemplate.from_template(
    # from_template：classmethod（类方法），用单个模板字符串快速建模板。
    "你是一个作诗高手，请帮忙写一首关于{input}的诗",
)


# 上面字符串里的 {input}：模板变量名，invoke 时字典的键必须叫 "input"（与这里一致）。


# ---------------------------------------------------------------------------

# 链：LangChain LCEL（LangChain Expression Language）里组合 Runnable 的两种方式。

#

# - Runnable：可运行对象；prompt、llm、解析器等都实现同一套接口（invoke、stream 等）。

# - |（竖线）：语法糖，表示「前一个的输出 → 后一个的输入」，从左到右串联。

# - .pipe(other)：实例方法，pipe = 管道；a.pipe(b) 与 a | b 含义相同，可连续 .pipe()。

#

# 下面只保留一种赋值即可；若写两行且变量名相同，后一行会覆盖前一行。

# ---------------------------------------------------------------------------

chain = prompt | llm | StrOutputParser()


# 与上一行完全等价（任选其一，不要对同一个 chain 连续赋值两次）：

# chain = prompt.pipe(llm).pipe(StrOutputParser())


# |：在纯 Python 里常表示按位或；在 LangChain Runnable 上被重载为「管道组合」。

# StrOutputParser()：括号 = 调用类生成实例；无参构造，得到「把模型输出转成 str」的解析器。


# ---------------------------------------------------------------------------

# invoke：动词「调用、执行」；对链传入「一次运行所需的输入字典」。

# ---------------------------------------------------------------------------

response = chain.invoke({"input": "春天的景色"})


# {"input": "春天的景色"}：dict（字典），键 input 对应模板里的 {input}。

# response：变量名，这里类型为 str（因为最后一步是 StrOutputParser）。


print(response)


# print：内置函数，把对象打印到标准输出（控制台）。
