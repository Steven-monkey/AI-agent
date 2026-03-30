"""
Few-shot（少样本）提示 + DeepSeek 调用示例。

---------------------------------------------------------------------------
【你之前遇到的错误】与注意点（为何会用错、如何避免）
---------------------------------------------------------------------------

1. 错误现象
   使用 FewShotPromptTemplate，并把 ChatPromptTemplate 传给 example_prompt 时，
   可能抛出：AttributeError: 'ChatPromptTemplate' object has no attribute 'get'

2. 根本原因（两类模板不要混用）
   - FewShotPromptTemplate：面向「单条字符串」补全（StringPromptTemplate 体系）。
     它的 example_prompt 必须是 PromptTemplate（一段带 {变量} 的纯文本），
     且通常还要配 prefix、suffix 等拼成一整段字符串。
   - FewShotChatMessagePromptTemplate：面向「多轮对话消息」（human/ai/system）。
     它的 example_prompt 可以是 ChatPromptTemplate（或消息级模板），
     输出的是 BaseMessage 列表，适合 Chat 模型。

   若把 ChatPromptTemplate 塞进 FewShotPromptTemplate，类型与校验链路都不匹配，
   内部会误把「聊天模板对象」当成「字典」去 .get("template")，从而报错。

3. 你需要记住的注意点
   - 先想清楚：模型吃的是「一条长字符串」还是「消息列表」？Chat 模型用后者。
   - 多轮 few-shot → 用 FewShotChatMessagePromptTemplate + ChatPromptTemplate。
   - 字符串 few-shot → 用 FewShotPromptTemplate + PromptTemplate，并补齐 suffix 等。
   - 示例字典里的键名，要和 example_prompt 里占位符一致（本例为 input、output）。

4. 运行环境
   - 需设置环境变量 DEEPSEEK_API_KEY；Windows 终端若中文乱码，可改用 UTF-8 编码或 IDE 查看输出。

5. 【对照】字符串版 Few-shot 写法见 import 下方「仅作对照」注释块（与本文件可执行代码无关）。
"""

import os

from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

from langchain_deepseek import ChatDeepSeek

# ========== 【仅作对照、不执行】字符串版 Few-shot：FewShotPromptTemplate + PromptTemplate ==========
# 与上方文档「错误说明」对应：这里必须用 PromptTemplate，不能用 ChatPromptTemplate。
# 适用于：只要拼出一段长字符串（如 legacy 补全接口）；Chat 模型若要用，多半再包成一条 HumanMessage。
#
# from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
#
# examples_str = [{"input": "你好", "output": "您好！"}]
# example_prompt_str = PromptTemplate(
#     input_variables=["input", "output"],
#     template="用户：{input}\n助手：{output}",
# )
# few_shot_str = FewShotPromptTemplate(
#     example_prompt=example_prompt_str,
#     examples=examples_str,
#     prefix="参考示例：\n",
#     suffix="\n请回答：{question}",
# )
# text = few_shot_str.format(question="今天天气怎样？")
# ====================================================================================================

# ---------- 1. 语言模型（Chat 接口，与「消息列表」提示配套）----------
llm = ChatDeepSeek(
    model="deepseek-chat",  # DeepSeek 对话模型名
    temperature=1.5,  # 采样温度：越高越随机（具体范围以厂商文档为准）
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 勿把密钥写进代码，用环境变量
    base_url="https://api.deepseek.com/v1",  # OpenAI 兼容接口地址
)

# ---------- 2. Few-shot 示例数据：每条是一个 dict，键对应 example_prompt 里的占位符 ----------
# 这里的 "input" / "output" 必须与下面 ChatPromptTemplate 中的 {input}、{output} 同名
examples = [
    {
        "input": "《蜀道难》",
        "output": """
            噫吁嚱，危乎高哉！蜀道之难，难于上青天！
            蚕丛及鱼凫，开国何茫然！
            尔来四万八千岁，不与秦塞通人烟。
            西当太白有鸟道，可以横绝峨眉巅。
            地崩山摧壮士死，然后天梯石栈相钩连。
            上有六龙回日之高标，下有冲波逆折之回川。
            黄鹤之飞尚不得过，猿猱欲度愁攀援。
            青泥何盘盘，百步九折萦岩峦。
            扪参历井仰胁息，以手抚膺坐长叹。
            问君西游何时还？畏途巉岩不可攀。
            但见悲鸟号古木，雄飞雌从绕林间。
            又闻子规啼夜月，愁空山。
            蜀道之难,难于上青天，使人听此凋朱颜！
            连峰去天不盈尺，枯松倒挂倚绝壁。
            飞湍瀑流争喧豗，砯崖转石万壑雷。
            其险也如此，嗟尔远道之人胡为乎来哉！(也若此 一作：也如此)
            剑阁峥嵘而崔嵬，一夫当关，万夫莫开。
            所守或匪亲，化为狼与豺。
            朝避猛虎，夕避长蛇；磨牙吮血，杀人如麻。
            锦城虽云乐，不如早还家。
            蜀道之难,难于上青天，侧身西望长咨嗟！
            """,
    },
]

# ---------- 3. 单条「示例」长什么样：一轮用户 + 一轮助手（变量名与 examples 对齐）----------
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)

# ---------- 4. 将多组示例展开成多轮消息：必须用 FewShotChatMessagePromptTemplate ----------
# 若误用 FewShotPromptTemplate，且传入 ChatPromptTemplate，就会触发你之前看到的 AttributeError
fewshot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,  # 每条示例如何格式化成消息
    examples=examples,  # 静态示例列表；也可改用 example_selector 做动态选例
)

# 调试：只看 few-shot 展开后的消息列表（不经过 system / 最后一条 human）
# print(fewshot_prompt.format_messages())

# ---------- 5. 最终发给模型的完整对话结构：system → 若干示例轮次 → 当前用户问题 ----------
final_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一位作诗作词的高手"),
        fewshot_prompt,  # 插入占位：运行时会按 examples 展开成多轮 HumanMessage / AIMessage
        ("human", "{input}"),  # 本轮真实用户输入；invoke 时传入的键名必须是 "input"
    ]
)

# ---------- 6. LCEL：提示模板管道连接到 LLM，一次调用完成「格式化 + 请求」----------
chain = final_prompt | llm
result = chain.invoke({"input": "给我写一首，踌躇满志的诗。"})
# result 为 AIMessage（或厂商封装），.content 为助手回复正文
print(result.content)
