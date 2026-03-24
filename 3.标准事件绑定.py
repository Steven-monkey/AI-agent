"""简单的示例脚本：调用 DeepSeek 模型并打印回复。"""  # 模块级文档字符串：说明脚本用途（调用 DeepSeek 并输出结果）

# invoke  # 预留：使用 llm.invoke（一次性调用）的示例
# stream  # 预留：使用 llm.stream（流式输出）的示例
# batch  # 预留：使用 llm.batch（批量调用）的示例
# astream_events  # 预留：使用 llm.astream_events（异步流事件）的示例
# 用于读取环境变量（如 API 密钥）
import os  # os：读取环境变量（DEEPSEEK_API_KEY）
import asyncio  # asyncio：用于运行异步主函数 main()

# LangChain：兼容 OpenAI 接口的聊天模型（此处用于调用 DeepSeek）
from langchain_openai import (  # 从 langchain_openai 导入 ChatOpenAI（用于 OpenAI 兼容接口）
    ChatOpenAI,  # ChatOpenAI：聊天模型封装类
)  # 安装提示：如需 openai 相关依赖请先安装 `pip3 install openai`

llm = ChatOpenAI(  # 创建一个可复用的聊天模型客户端（统一在此处配置）
    model="deepseek-chat",  # 指定模型名称（DeepSeek 的模型标识）
    temperature=0.8,  # 采样温度：越大越随机（0~1 常见范围）
    api_key=os.getenv(
        "DEEPSEEK_API_KEY"
    ),  # 从环境变量读取 API Key（避免把密钥写死在代码里）
    base_url="https://api.deepseek.com/v1",  # 指定服务端点基地址（OpenAI 兼容路径）
)  # 结束 ChatOpenAI 配置

response = llm.batch(  # 批量调用：一次性发送多个输入并返回对应结果
    [  # 这里的列表元素会分别对应成不同请求
        "langchain的创始人是谁",  # 请求 1：询问 LangChain 创始人是谁
        "langchain的主要竞争是谁",  # 请求 2：询问 LangChain 主要竞争是谁
    ]  # 结束输入列表
)  # 结束 batch 调用

print(response)  # 打印 batch 的整体返回内容（具体格式取决于库实现）
for chunk in llm.stream("langchain的创始人是谁"):  # 流式调用：逐块获取模型生成的内容
    print(chunk.content, end="", flush=True)  # 逐块打印 content：不换行并立即刷新输出

response = llm.invoke(
    "langchain的创始人是谁"
)  # 一次性调用：返回最终完整消息（或封装对象）
print(response.content)  # 打印 invoke 的最终文本内容（访问 response.content 字段）


async def main():  # 异步主函数：用于演示 astream_events 的事件流处理
    async for event in llm.astream_events(
        "langchain的创始人是谁"
    ):  # 异步流：逐事件处理模型输出
        chunk = event.get("data", {}).get(
            "chunk"
        )  # 从事件字典中尝试取出 data.chunk（可能为空）
        if chunk and getattr(
            chunk, "content", None
        ):  # 过滤：确保 chunk 存在且 content 可读
            print(
                chunk.content, end="", flush=True
            )  # 逐块打印事件中的 content：不换行并刷新


asyncio.run(main())  # 运行异步 main 函数（在当前事件循环环境中执行）
