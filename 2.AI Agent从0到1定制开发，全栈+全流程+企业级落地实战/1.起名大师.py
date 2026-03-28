"""简单的示例脚本：调用 DeepSeek 模型并打印回复。"""

# 用于读取环境变量（如 API 密钥）
import os
# LangChain：兼容 OpenAI 接口的聊天模型（此处用于调用 DeepSeek）
from langchain_openai import ChatOpenAI
# LangChain：提示词模板，支持变量占位符
from langchain_core.prompts import PromptTemplate
# LangChain：输出解析器基类，用于把模型输出转成结构化数据
from langchain_core.output_parsers import BaseOutputParser


class CommmaSeparatedListOutputParser(BaseOutputParser):
    """自定义解析器：将模型返回的逗号分隔文本解析为字符串列表。"""

    def parse(self, text: str) -> list[str]:
        """去掉首尾空白后按逗号拆分，返回名字列表。"""
        return text.strip().split(",")


# 初始化 DeepSeek 聊天模型：使用 OpenAI 兼容接口，temperature=0 使输出更稳定
llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)

# 起名提示词模板：{county} 为地区特色，{boy}/{girl} 为示例名字，要求返回逗号分隔列表
prompt = PromptTemplate.from_template(
    "你是一个起名大师,请模仿示例起3个具有{county}特色的名字,"
    "示例：男孩常用名{boy},女孩常用名{girl}。"
    "请返回以逗号分隔的列表形式。仅返回逗号分隔的列表，不要返回其他内容。"
)

# 填入模板变量，生成最终发给模型的提示内容
message = prompt.format(county="中国特色的", boy="狗剩", girl="李狗蛋")
print(message)
# 调用模型得到 AIMessage，用 .content 取文本后再用自定义解析器转成列表并打印
result = llm.invoke(message)
print(CommmaSeparatedListOutputParser().parse(result.content))
