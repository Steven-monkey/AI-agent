from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(
    model="Pro/MiniMaxAI/MiniMax-M2.5",
    api_key="sk-gmefuspqkkmqfhkggpcdabybaxvkdxamibvndwlabxcbqfqj",
    base_url="https://api.siliconflow.cn/v1",
)

examples = [
    {
        "query": "什么是手机？",
        "answer": "手机是一种神奇的设备，可以装进口袋，就像一个迷你魔法游乐场。\
    它有游戏、视频和会说话的图片，但要小心，它也可能让大人变成屏幕时间的怪兽!",
    },
    {
        "query": "你的梦想是什么？",
        "answer": "我的梦想就像多彩的冒险，在那里我变成超级英雄，\
        拯救世界!我梦见欢笑声、冰淇淋派对，还有一只名叫Sparkles的宠物龙。",
    },
]
example_template = """
Query: {query}
Answer: {answer}
"""
example_prompt = PromptTemplate(
    template=example_template,
    input_variables=["query", "answer"],
)

prefix = """假如你是一个5岁小朋友，非常有趣，非常活泼可爱：
以下是一列子：
"""
suffix = """
Query: {query}
Answer: {answer}
"""

few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix=prefix,
    suffix=suffix,
    input_variables=["query", "answer"],
    example_separator="\n\n",
)
query = "房子是什么？"
real_prompt = few_shot_prompt.format(query=query, answer="")
chain = few_shot_prompt | llm | StrOutputParser()
print(real_prompt)
print("-" * 100)
print(chain.invoke({"query": query, "answer": ""}))
print("-" * 100)
