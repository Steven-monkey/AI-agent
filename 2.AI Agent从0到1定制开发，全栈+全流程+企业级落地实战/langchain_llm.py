"""
================================================================================
langchain_llm.py —— 统一创建「聊天大模型」（OpenAI / DeepSeek）
================================================================================

【一、使用说明】

1) 环境变量（推荐，不要把 Key 写进代码再提交 Git）
   - OpenAI：OPENAI_API_KEY（必填）；可选 OPENAI_MODEL 覆盖默认模型名
   - DeepSeek：DEEPSEEK_API_KEY（必填）；可选 DEEPSEEK_MODEL
   在 Windows「系统/用户环境变量」里改完后，务必关掉终端再开，否则读不到。

2) 在本文件同目录下的其它 .py 里
   from langchain_llm import create_deepseek_llm
   llm = create_deepseek_llm()
   print(llm.invoke("你好").content)

3) 用字符串二选一
   from langchain_llm import get_chat_llm
   llm = get_chat_llm("openai", temperature=0.3)

4) 临时指定模型名（覆盖环境变量与默认值）
   create_openai_llm(model="gpt-4o")
   create_deepseek_llm(model="deepseek-reasoner")

5) 和提示词模板串成链（LCEL）
   from langchain_core.prompts import ChatPromptTemplate
   from langchain_llm import create_deepseek_llm
   p = ChatPromptTemplate.from_template("把下面这句话翻译成英文：{t}")
   chain = p | create_deepseek_llm()
   print(chain.invoke({"t": "早上好"}).content)

--------------------------------------------------------------------------------
【二、如何自己调研（查文档、查模型、排错）】

OpenAI
  - 文档首页：https://platform.openai.com/docs
  - 模型名称：控制台或文档里的 Models / 定价页，以你账号实际可用为准
  - 常见调用错误：401=Key 无效；404=model 名称写错或无权使用

DeepSeek
  - 文档：https://api-docs.deepseek.com/
  - 模型：常见为 deepseek-chat、deepseek-reasoner（以官网为准）
  - 接口为 OpenAI 兼容风格，本模块里的 base_url 一般不用改

本地快速检查「环境变量有没有进到 Python」
  在终端执行（PowerShell）：
    python -c "import os; print('OPENAI', bool(os.getenv('OPENAI_API_KEY'))); print('DEEPSEEK', bool(os.getenv('DEEPSEEK_API_KEY')))"
  两个都是 False，说明当前终端里没配好，不是本文件的问题。

建议调试顺序
  1. 先确认 Key 在终端里可见（上一行命令）
  2. 直接运行本文件：python langchain_llm.py
  3. 若仍报错，看报错最后一行英文提示（缺 Key / 模型名 / 网络）

--------------------------------------------------------------------------------
【三、示例代码片段（复制到别的 .py 里用）】

# --- 示例 A：DeepSeek 一问一答 ---
# from langchain_llm import create_deepseek_llm
# llm = create_deepseek_llm()
# r = llm.invoke("用不超过20字介绍 Python")
# print(r.content)

# --- 示例 B：OpenAI 一问一答 ---
# from langchain_llm import create_openai_llm
# llm = create_openai_llm()
# r = llm.invoke("用不超过20字介绍 Python")
# print(r.content)

# --- 示例 C：按变量选厂商 ---
# from langchain_llm import get_chat_llm
# vendor = "deepseek"  # 或 "openai"
# llm = get_chat_llm(vendor)
# print(llm.invoke("1+1等于几？").content)

================================================================================
"""

from __future__ import annotations

import os
import sys
from typing import Literal

from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI

OPENAI_MODEL_DEFAULT = "gpt-4o-mini"
DEEPSEEK_MODEL_DEFAULT = "deepseek-chat"
DEEPSEEK_URL_DEFAULT = "https://api.deepseek.com/v1"

Provider = Literal["openai", "deepseek"]


def create_openai_llm(
    *,
    model: str | None = None,
    temperature: float = 0.7,
    api_key: str | None = None,
) -> ChatOpenAI:
    """创建 OpenAI 聊天模型。"""
    key = api_key or os.getenv("OPENAI_API_KEY")
    name = model or os.getenv("OPENAI_MODEL", OPENAI_MODEL_DEFAULT)
    return ChatOpenAI(model=name, temperature=temperature, api_key=key)


def create_deepseek_llm(
    *,
    model: str | None = None,
    temperature: float = 0.8,
    api_key: str | None = None,
    base_url: str = DEEPSEEK_URL_DEFAULT,
) -> ChatDeepSeek:
    """创建 DeepSeek 聊天模型（接口格式与 OpenAI 兼容）。"""
    key = api_key or os.getenv("DEEPSEEK_API_KEY")
    name = model or os.getenv("DEEPSEEK_MODEL", DEEPSEEK_MODEL_DEFAULT)
    return ChatDeepSeek(
        model=name,
        temperature=temperature,
        api_key=key,
        base_url=base_url,
    )


def get_chat_llm(
    provider: Provider,
    *,
    model: str | None = None,
    temperature: float | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> ChatOpenAI | ChatDeepSeek:
    """用字符串选择厂商："openai" 或 "deepseek"。"""
    if provider == "openai":
        t = 0.7 if temperature is None else temperature
        return create_openai_llm(model=model, temperature=t, api_key=api_key)
    if provider == "deepseek":
        t = 0.8 if temperature is None else temperature
        url = base_url or DEEPSEEK_URL_DEFAULT
        return create_deepseek_llm(
            model=model, temperature=t, api_key=api_key, base_url=url
        )
    raise ValueError('provider 只能是 "openai" 或 "deepseek"')


__all__ = [
    "Provider",
    "get_chat_llm",
    "create_openai_llm",
    "create_deepseek_llm",
    "OPENAI_MODEL_DEFAULT",
    "DEEPSEEK_MODEL_DEFAULT",
    "DEEPSEEK_URL_DEFAULT",
]


def _print_env_check() -> None:
    """终端演示：当前进程能否读到 Key（只显示有没有，不打印密钥）。"""
    oa = bool(os.getenv("OPENAI_API_KEY"))
    ds = bool(os.getenv("DEEPSEEK_API_KEY"))
    print(f"[环境变量] OPENAI_API_KEY 已设置: {oa}  |  DEEPSEEK_API_KEY 已设置: {ds}")


if __name__ == "__main__":
    # 用法：在本文件所在目录执行
    #   python langchain_llm.py           → 默认跑 DeepSeek 一句测试
    #   python langchain_llm.py openai    → 跑 OpenAI
    #   python langchain_llm.py env       → 只检查环境变量，不请求网络
    mode = (sys.argv[1] if len(sys.argv) > 1 else "deepseek").lower()

    if mode == "env":
        _print_env_check()
        sys.exit(0)

    _print_env_check()

    if mode == "openai":
        print("\n[示例] OpenAI 单轮对话 …")
        llm = create_openai_llm()
        msg = llm.invoke("只回答一个字：好")
        print(msg.content)
    else:
        print("\n[示例] DeepSeek 单轮对话 …")
        llm = create_deepseek_llm()
        msg = llm.invoke("只回答一个字：好")
        print(msg.content)

# 跨目录 import 时，在别的脚本最上面加（路径改成你的实际目录）：
#
#   import sys
#   from pathlib import Path
#   sys.path.insert(0, str(Path(r"D:\...\2.AI Agent从0到1定制开发，全栈+全流程+企业级落地实战")))
#   from langchain_llm import create_deepseek_llm
