"""



本文件演示：使用 LangChain 的 ChatOpenAI 调用 OpenAI 官方聊天补全接口。



ChatOpenAI：对 OpenAI Chat Completions（及兼容网关）的封装；invoke 传入字符串或

Message 列表，返回 AIMessage，常用 .content 取助手正文。



鉴权：默认从环境变量 OPENAI_API_KEY 读取。若在「系统/用户环境变量」中配置，

需重新打开终端后进程才能看到；也可用 api_key="sk-..." 显式传入（勿提交到 Git）。



"""

# ---------------------------------------------------------------------------

# import（导入）：标准库与第三方包。

# ---------------------------------------------------------------------------

import os


# os.getenv：读取环境变量；键名须与 OpenAI 约定一致，即 OPENAI_API_KEY。


from langchain_openai import ChatOpenAI


# ChatOpenAI：langchain_openai 提供的聊天模型类；实现 LangChain Runnable（invoke、stream 等）。


# ---------------------------------------------------------------------------

# 实例化大模型：model、temperature、api_key 与 OpenAI 控制台/文档一致。

# ---------------------------------------------------------------------------

llm = ChatOpenAI(
    # model：远端可用的模型标识；以你账号在平台列表为准，如 gpt-4o-mini、gpt-4o 等。
    model="gpt-5.4-mini",
    # temperature：采样温度，越高输出越随机，越低越稳定。
    temperature=0.7,
    # api_key：不传时由集成库从环境变量 OPENAI_API_KEY 推断；此处显式 getenv 便于阅读来源。
    api_key=os.getenv("OPENAI_API_KEY"),
)


# ---------------------------------------------------------------------------

# invoke：同步调用一次；返回 AIMessage，.content 为模型回复字符串。

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    reply = llm.invoke("介绍一下你自己？")
    print(reply.content)
