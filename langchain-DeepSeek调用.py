"""
DeepSeek 调用示例：使用 LangChain 调用 DeepSeek 并打印 response 的各类字段，便于学习与调试。
"""
import os
from langchain_deepseek import ChatDeepSeek


llm = ChatDeepSeek(
    model="deepseek-chat",  # 模型名称
    temperature=0.8,  # 采样温度：0~1，越大越随机
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 从环境变量读取 API Key
    base_url="https://api.deepseek.com/v1",  # DeepSeek OpenAI 兼容接口
)

response = llm.invoke("介绍一下你自己")


def safe_get(obj, name):
    """安全读取对象属性，不存在时返回 None。"""
    return getattr(obj, name, None)


# 打印 response 类型及关键字段
print("=== response 类型 ===")
print(type(response))

print("\n=== response 关键字段 ===")
print("content:", safe_get(response, "content"))  # 模型生成的文本内容
print("tool_calls:", safe_get(response, "tool_calls"))  # 工具调用列表（未绑定时多为空）
print("invalid_tool_calls:", safe_get(response, "invalid_tool_calls"))  # 无效工具调用
print("usage_metadata:", safe_get(response, "usage_metadata"))  # token 用量统计
print("id:", safe_get(response, "id"))  # 响应唯一标识
print("response_metadata:", safe_get(response, "response_metadata"))  # 元信息（finish_reason 等）
print("additional_kwargs:", safe_get(response, "additional_kwargs"))  # 扩展字段

