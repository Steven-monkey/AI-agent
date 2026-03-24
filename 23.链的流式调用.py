"""



本文件演示：LangChain 链的「流式（stream）」调用。



与一次性 invoke 不同：stream 像打字机一样，边生成边收到多块（chunk），

适合长文本、降低首字等待时间、做实时展示。



链本身仍是：提示模板 → 大模型 → 输出解析（StrOutputParser），

只是 Runnable 上除了 invoke，还可以用 stream（异步场景常用 astream）。



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

# ChatDeepSeek：类名；实例化后得到可调用的「聊天模型」对象。


from langchain_core.prompts import ChatPromptTemplate


# langchain_core：LangChain 核心库；prompts 子模块放各类「提示」模板。

# ChatPromptTemplate：用带占位符的字符串生成「最终发给模型的提示」。


from langchain_core.output_parsers import StrOutputParser


# output_parsers：把模型原始输出「解析」成 Python 方便用的类型。

# StrOutputParser：把模型返回解析成普通 str；流式时解析器按块增量处理，最终拼成完整文本。


# ---------------------------------------------------------------------------

# 实例化大模型：llm = Large Language Model 的惯用缩写变量名。

# ---------------------------------------------------------------------------

llm = ChatDeepSeek(
    # model：指定远端 API 使用的模型标识字符串。
    model="deepseek-chat",
    # temperature：采样温度；越大越随机。具体合法范围以厂商文档为准。
    temperature=1.5,
    # api_key：鉴权；getenv 从环境变量读取，未设置可能为 None。
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    # base_url：OpenAI 兼容接口的根地址。
    base_url="https://api.deepseek.com/v1",
)


# ---------------------------------------------------------------------------

# 提示模板：{input} 为占位符，invoke / stream 时传入同名键。

# ---------------------------------------------------------------------------

prompt = ChatPromptTemplate.from_template(
    # from_template：用单条字符串模板快速构建 ChatPromptTemplate。
    "你是一个作诗高手，请帮忙写一首关于{input}的诗",
)


# ---------------------------------------------------------------------------

# 链：LCEL 中用 | 或 .pipe() 串联 Runnable（与 22 节相同）。

# ---------------------------------------------------------------------------

chain = prompt | llm | StrOutputParser()

# 等价写法：chain = prompt.pipe(llm).pipe(StrOutputParser())


# ---------------------------------------------------------------------------

# invoke：阻塞直到整段生成完，一次返回完整结果（这里是 str）。

# stream：返回可迭代对象，每次迭代得到一块增量（chunk），边下边显。

#

# 若同时执行 invoke 与 stream，会对同一问题请求模型两次（费 token）。

# 本文件默认只跑 stream；若要对比「整段结果」，可取消下面一行注释并删掉或注释掉 stream 循环。

# ---------------------------------------------------------------------------

# response = chain.invoke({"input": "春天的景色"})


for chunk in chain.stream({"input": "春天的景色"}):

    # chunk：本段增量；类型通常为 str（经 StrOutputParser 后多为纯文本片段）。

    # stream(...)：与 invoke 入参相同，仍是模板所需变量的字典。

    # for ... in ...：迭代器协议，每次从 stream 里取下一块，直到模型结束。

    print(
        chunk,
        end="",  # end：print 默认 end="\n" 会换行；改成空串 = 不换行，多段拼成连续输出。
        flush=True,  # flush：True 时立即刷新缓冲区，终端里更像「实时打字」；False 可能攒一批再显示。
    )

print()  # 流式结束后补一个换行，避免命令行提示符贴在诗末同一行。
