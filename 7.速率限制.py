# 速率限制 - 控制调用频率，避免触发 API 限流
# 使用 LangChain 的 InMemoryRateLimiter（令牌桶算法）

import os
import time

from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama

# 创建速率限制器：每秒最多 1 次请求，检查间隔 0.1 秒，桶容量 2（允许短时突发）
rate_limiter = InMemoryRateLimiter(
    requests_per_second=1,
    check_every_n_seconds=0.1,
    max_bucket_size=2,
)

# 创建模型时传入 rate_limiter（在构造函数中传入，而非 bind_tools）
llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.8,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base="https://api.deepseek.com/v1",
    rate_limiter=rate_limiter,
)

# 单次调用（速率限制会在此次 invoke 内部生效）
response = llm.invoke("用一句话介绍你自己")
print(response.content)

# 演示速率限制效果：连续 3 次调用，观察间隔（约 1 秒一次）
print("\n--- 连续 3 次调用，观察速率限制 ---")
for i in range(3):
    t0 = time.perf_counter()
    r = llm.invoke(f"说一个数字：{i + 1}")
    t1 = time.perf_counter()
    print(f"第{i+1}次: {r.content[:30]}... | 耗时 {t1 - t0:.2f}s")
