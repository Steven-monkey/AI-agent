"""



本文件演示：LangChain 中 RunnableParallel（并行 / 「并式」）组合多条子链。



RunnableParallel 把多个 Runnable 在同一次调用里并行执行，结果是一个 dict，

键名由你传入的关键字参数决定（此处为 shi、ci）。



对 RunnableParallel 做 stream 时，每个 chunk 往往是带 shi/ci 键的部分更新，

直接 print(chunk) 会像字典碎片交错挤在一行，难以阅读。

并行若要「好看」的输出，常用 invoke 一次取齐，再分段打印；

若必须流式，可对各子链单独 stream/astream 并加标题。



"""

# ---------------------------------------------------------------------------

# import（导入）：从标准库或第三方包引入符号。

# ---------------------------------------------------------------------------

import os


# os.getenv：读取环境变量，用于 API Key 等敏感配置。


from langchain_deepseek import ChatDeepSeek


# ChatDeepSeek：DeepSeek 聊天模型封装，可作为链中的一环。


from langchain_core.prompts import ChatPromptTemplate


# ChatPromptTemplate：提示模板；from_template 用占位符（如 {input}）生成最终提示。


from langchain_core.output_parsers import StrOutputParser


# StrOutputParser：把模型输出解析为 Python str。


from langchain_core.runnables import RunnableParallel


# RunnableParallel：并行组合；parallel = 并行。每个关键字参数名会成为输出 dict 的键。


# ---------------------------------------------------------------------------

# 大模型实例：多条子链可共用同一个 llm（也可各建一个实例）。

# ---------------------------------------------------------------------------

llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.8,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)


# ---------------------------------------------------------------------------

# 子链：每条都是「模板 | 模型 | 解析器」，与 22 节单链相同，只是拆成两个变量。

# |：LCEL 管道，数据从左流到右。

# ---------------------------------------------------------------------------

shi_prompt = (
    ChatPromptTemplate.from_template(
        "你是一个作诗高手，请帮忙写一首关于{input}的诗，不需要任何解释，只给出诗句就可以了。",
    )
    | llm
    | StrOutputParser()
)


ci_prompt = (
    ChatPromptTemplate.from_template(
        "你是一个作词家，请根据我输入的想法{input}，给我写一首歌的词。不需要任何解释，只给出歌词就可以了。",
    )
    | llm
    | StrOutputParser()
)


# ---------------------------------------------------------------------------

# RunnableParallel(shi=..., ci=...)：一次调用时两条子链并行执行（由运行库调度）。

# 输出形如 {"shi": "...", "ci": "..."}，键 shi、ci 对应这里的关键字参数名。

# 入参 dict 需满足各子链模板所需变量：此处两条模板都用 {input}，故传入 {"input": "..."}。

# ---------------------------------------------------------------------------

map_chain = RunnableParallel(shi=shi_prompt, ci=ci_prompt)


# invoke：同步阻塞直到并行全部完成，返回完整结果 dict。

result = map_chain.invoke({"input": "春天的景色"})


# ---------------------------------------------------------------------------

# 控制台排版：用重复字符做分隔线，分段打印，避免并行 stream 的字典 chunk 挤成一行。

# strip()：去掉字符串首尾空白，避免多余空行。

# ---------------------------------------------------------------------------

sep = "=" * 40


print("\n" + sep + " 诗 " + sep)

print(result["shi"].strip())


print("\n" + sep + " 歌词 " + sep)

print(result["ci"].strip())

print()
print(map_chain.get_graph().print_ascii())
