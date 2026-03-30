"""



本文件演示：通过 langchain_llm.py 里的 create_deepseek_llm 获取 ChatDeepSeek。

用法说明见同目录 langchain_llm.py 文件开头注释。



"""

# ---------------------------------------------------------------------------

from langchain_llm import create_deepseek_llm

# ---------------------------------------------------------------------------

llm = create_deepseek_llm()

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    reply = llm.invoke("用一句话介绍 DeepSeek 能帮你做什么。")
    print(reply.content)
