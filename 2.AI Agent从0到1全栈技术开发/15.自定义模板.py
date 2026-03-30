# =============================================================================
# 脚本目标：演示「自定义 Prompt 模板」—— 根据函数名自动取源码，拼成提示词，再交给 LLM 解释
# 英文标题：Function Master — given a function name, find code and explain in Chinese
# =============================================================================

## 函数大师：根据函数名称，查找函数代码，并给出中文的代码说明
# Function Master: Given a function name, find the function code and provide a Chinese code explanation

# langchain_core.prompts.StringPromptTemplate：字符串提示词模板的基类
# 我们继承它并重写 format()，在「格式化」时动态插入函数源码，而不是只替换占位符
from langchain_core.prompts import StringPromptTemplate


# -----------------------------------------------------------------------------
# 示例：后面会把这个函数传给模板，让 inspect 取出它的源代码
# -----------------------------------------------------------------------------
# 定义一个简单的函数作为示例效果
def hello_world(abc):
    print("Hello, world!")  # 副作用：打印到控制台（解释代码时 LLM 会提到这点）
    return abc  # 把入参原样返回，便于演示「有参数、有返回值」的函数


# -----------------------------------------------------------------------------
# 静态提示词骨架：{function_name} 和 {source_code} 会在 format 时被 .format() 填入
# 使用 """\ 是为了让第一行后面紧跟换行，避免提示词开头多一个空行（风格问题）
# -----------------------------------------------------------------------------
PROMPT = """\
你是一个非常有经验和天赋的程序员，现在给你如下函数名称，你会按照如下格式，输出这段代码的名称、源代码、中文解释。
函数名称: {function_name}
源代码:
{source_code}
代码解释:
"""

# inspect：Python 标准库，用于「自省」—— 在运行时查看对象（模块、类、函数）的源码、签名等
import inspect


def get_source_code(function_name):
    """
    根据「函数对象」取出其在 .py 文件里的源代码字符串。
    function_name 必须是可调用的函数对象（如 hello_world），不能只是字符串 "hello_world"。
    """
    # 获得源代码：inspect.getsource 会读取定义该函数的源文件并返回对应文本
    # Get the source code
    return inspect.getsource(function_name)


# -----------------------------------------------------------------------------
# 自定义模板类：继承 StringPromptTemplate，实现「输入变量 → 完整提示字符串」的定制逻辑
# 类名 CustmPrompt 应为 Custom 的简写/笔误，运行不受影响
# -----------------------------------------------------------------------------
# 自定义的模板class
# Custom template class
class CustmPrompt(StringPromptTemplate):

    def format(self, **kwargs) -> str:
        """
        重写父类 format：父类通常只做 {var} 替换；这里我们先根据函数对象拉取源码，再拼 PROMPT。

        kwargs 里预期有：
          - function_name: 函数对象（如 hello_world），用于 getsource 和 __name__
        """
        # 获得源代码：kwargs["function_name"] 必须是函数对象，才能被 inspect.getsource 处理
        # Get the source code
        source_code = get_source_code(kwargs["function_name"])

        # 生成提示词模板：把函数名字符串 + 源码文本填进 PROMPT
        # Generate the prompt template
        prompt = PROMPT.format(
            function_name=kwargs[
                "function_name"
            ].__name__,  # 函数名字符串，如 "hello_world"
            source_code=source_code,  # 该函数的完整源码（多行字符串）
        )
        return prompt  # 返回最终给 LLM 的完整 user 侧提示文本


# input_variables=["function_name"]：声明这个模板对外只暴露一个占位变量名 "function_name"
# 调用 .format(function_name=hello_world) 时传入的是函数对象（注意没有括号，不是调用）
a = CustmPrompt(input_variables=["function_name"])
pm = a.format(function_name=hello_world)  # pm 即为拼好源码说明任务说明的完整字符串

print(pm)  # 先打印出来，便于不调 LLM 时也能看到最终 prompt

# -----------------------------------------------------------------------------
# 和 LLM 连接起来：把上面生成的字符串作为用户消息发给 DeepSeek
# -----------------------------------------------------------------------------
# Connect to LLM
from langchain_deepseek import ChatDeepSeek
import os

# ChatDeepSeek：LangChain 里对接 DeepSeek API 的聊天模型封装
llm = ChatDeepSeek(
    model="deepseek-chat",  # 模型名称（与 DeepSeek 控制台/文档一致）
    temperature=0.8,  # 采样温度：0~1，越大输出越随机；解释代码时常用中等偏高以增加表述多样性
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 从环境变量读取 API Key，避免写死在代码里
    base_url="https://api.deepseek.com/v1",  # OpenAI 兼容接口基址
)
# invoke：同步调用，传入字符串时会作为单条 user 消息；返回 AIMessage（含 .content 等字段）
msg = llm.invoke(pm)
print(msg.content)  # 打印整条消息对象；若只要文本可 print(msg.content)
