"""



本文件演示：LangChain 链的「异步流式」调用——astream（async stream）。



与 23 节的同步 stream 对应：

- stream：在普通代码里 for chunk in chain.stream(...)，按块收数据（同步迭代）。

- astream：在 async def 里 async for chunk in chain.astream(...)，配合 asyncio 事件循环，

  适合与 FastAPI、aiohttp 等异步框架一起使用。



async / async for / await 不能写在模块最顶层，必须放在 async def 里；

入口用 asyncio.run(main()) 启动事件循环。



"""

# ---------------------------------------------------------------------------

# import（导入）：从标准库或第三方包中引入名字，当前文件才能使用。

# ---------------------------------------------------------------------------

import asyncio


# asyncio：标准库模块，async + I/O；提供事件循环、run、create_task、sleep 等。

# 这里主要用 asyncio.run：在「普通脚本入口」里启动一个协程并跑完。


import os


# os：operating system；常用 getenv 读环境变量、路径操作等。


from langchain_core.prompts import ChatPromptTemplate


# langchain_core：LangChain 核心库；prompts 存放各类 Prompt 模板。

# ChatPromptTemplate：聊天式提示模板；from_template 用一条字符串快速构建。


from langchain_deepseek import ChatDeepSeek


# langchain_deepseek：集成 DeepSeek API 的包。

# ChatDeepSeek：对话模型封装，实现 Runnable，支持 invoke / stream / ainvoke / astream 等。


from langchain_core.output_parsers import StrOutputParser


# output_parsers：输出解析器，把模型原始输出变成 Python 类型。

# StrOutputParser：str = string，把最终内容解析为普通字符串。


# ---------------------------------------------------------------------------

# 实例化大模型：变量名 llm 常表示 Large Language Model。

# ---------------------------------------------------------------------------

llm = ChatDeepSeek(
    # model：字符串，指定远端要调用的模型 ID。
    model="deepseek-chat",
    # temperature：采样温度；越大随机性越强，具体合法区间见厂商文档。
    temperature=1.5,
    # api_key：鉴权密钥；os.getenv("DEEPSEEK_API_KEY") 从环境变量读取同名变量。
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    # base_url：API 根 URL；DeepSeek 使用 OpenAI 兼容 REST，路径中常见 /v1。
    base_url="https://api.deepseek.com/v1",
)


# ---------------------------------------------------------------------------

# 提示模板：{input} 为占位符，invoke / stream / astream 时传入 {"input": "..."}。

# ---------------------------------------------------------------------------

prompt = ChatPromptTemplate.from_template(
    # from_template：类方法，用单条模板字符串创建 ChatPromptTemplate。
    "你是一个作诗高手，请帮忙写一首关于{input}的诗，不需要任何解释，只给出诗句就可以了。",
)


# ---------------------------------------------------------------------------

# 链：LCEL（LangChain Expression Language）中用 | 串联 Runnable。

# 数据流：prompt → llm → StrOutputParser，与 22、23 节相同。

# ---------------------------------------------------------------------------

chain = prompt | llm | StrOutputParser()

# 等价：chain = prompt.pipe(llm).pipe(StrOutputParser())


# ---------------------------------------------------------------------------

# async def：定义协程函数；函数体里可使用 async for、await。

# -> None：类型注解，表示不返回有意义的值（隐式返回 None）。

# ---------------------------------------------------------------------------


async def main() -> None:
    """协程入口：内部使用 astream 异步流式读取模型输出。"""

    # async for：异步版 for；右侧必须是「异步可迭代」对象（astream 返回的流）。

    # astream：async stream；在网络 I/O 上不阻塞整个事件循环（与其它异步任务协作）。

    # chunk：每次迭代得到的一小段文本（经解析器后多为 str 片段）。

    async for chunk in chain.astream({"input": "春天的景色"}):

        print(
            chunk,
            end="",  # end 默认 "\n"；空串表示不换行，多块连成一段输出。
            flush=True,  # 立即刷新 stdout，终端里更像「逐字打出」。
        )

    print()  # 流结束后换行，避免命令行提示符紧贴在最后一字后。


# ---------------------------------------------------------------------------

# if __name__ == "__main__"：只有「直接运行本文件」时执行块内代码；被 import 时不执行。

# __name__：模块名；直接运行时 Python 设为 "__main__"。

# asyncio.run(main())：创建事件循环、运行协程 main 直到结束，再关闭循环。

# ---------------------------------------------------------------------------

if __name__ == "__main__":

    asyncio.run(main())
