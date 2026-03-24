# 引入依赖包，这里的pydantic版本为v2
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field, model_validator
from langchain_deepseek import ChatDeepSeek
import os
from langchain_core.output_parsers import JsonOutputParser

llm = ChatDeepSeek(
    model="deepseek-chat",  # 模型名称
    temperature=0.8,  # 采样温度：0~1，越大越随机
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 从环境变量读取 API Key
    base_url="https://api.deepseek.com/v1",  # DeepSeek OpenAI 兼容接口
)


# 定义一个名为Joke的数据模型
# 必须要包含的数据字段：铺垫(setup)、抖包袱(punchline)
class Joke(BaseModel):
    setup: str = Field(description="笑话中的铺垫问题，必须以?结尾")
    punchline: str = Field(
        description="笑话中回答铺垫问题的部分，通常是一种抖包袱方式回答铺垫问题，例如谐音、会错意等"
    )

    # 验证器，你可以根据自己的数据情况进行自定义
    # 注意mode=before意思是数据被转成pydantic模型的字段之前，对原始数据进行验证
    @model_validator(mode="before")
    @classmethod
    def question_ends_with_question_mark(cls, values: dict) -> dict:
        setup = values.get("setup")
        # 英文 ? 与中文 ？ 都算合法问句结尾
        if setup and setup[-1] not in ("?", "？"):
            raise ValueError("Badly formed question!")
        return values


# JsonOutputParser 带 pydantic_object 时会在链末尾解析并校验为 Joke
json_parser = JsonOutputParser(pydantic_object=Joke)
prompt = PromptTemplate(
    template="回答用户的查询.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": json_parser.get_format_instructions()},
)

chain = prompt | llm | json_parser
output = chain.invoke({"query": "给我讲一个笑话"})
print(output)
