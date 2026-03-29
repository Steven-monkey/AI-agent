"""



本文件演示：ChatDoc —— 读 Word/PDF/txt → 切块 → 向量库（Chroma）→ 检索 + LLM 压缩片段。



--------------------------------------------------------------------------------

【初学者常见错误总结（本项目中已踩过 / 易踩的坑）】



1) 文件路径 demo.docx 找不到

   原因：相对路径是相对「终端当前目录」，不是脚本所在目录。

   处理：用 Path(__file__).parent / "demo.docx" 再 str(...) 传给 Loader。



2) langchain_chroma 导入失败

   原因：包名拼错（如 langchan_chroma 少字母），或未 pip install。

   处理：pip install langchain-chroma；from langchain_chroma import Chroma。



3) OpenAIEmbeddings 报错或警告 temperature

   原因：向量化要用「嵌入模型」（如 text-embedding-3-small），不能用 gpt-4o 等聊天模型名；

   嵌入接口没有 temperature 参数。

   处理：model= 填嵌入模型；不要给 OpenAIEmbeddings 传 temperature。



4) Chroma.from_documents(embedding=...) 报错

   原因：变量名拼写错误（如 emdeddingModel），或对实例错误地加了 ()。

   处理：embedding= 后面是已创建好的 OpenAIEmbeddings 对象，不要加括号调用。



5) retriever.invoke 后写 .page_content 报错

   原因：invoke 返回的是 Document 的「列表」，列表没有 .page_content。

   处理：遍历列表，取每个 d.page_content，或用 "\\n\\n".join(...)。



6) llm = llm 报 UnboundLocalError

   原因：把变量自己赋值给自己，且 llm 尚未定义。

   处理：删除误写行，或写成 llm = ChatOpenAI(...) 等真实构造。



7) MultiQueryRetriever.from_llm 报 retriever 重复

   原因：from_llm 约定顺序是 (retriever, llm)，第一个位置参数是检索器；

   若把 llm 写在第一位同时又 retriever=...，会重复绑定 retriever。

   处理：from_llm(retriever=..., llm=...) 或 (base_retriever, llm) 顺序正确。



8) MultiQueryRetriever 从 langchain_core 导入失败

   原因：该类在 langchain_classic，不在 langchain_core。

   处理：from langchain_classic.retrievers import MultiQueryRetriever（本文件当前未使用）。



9) LLMChainExtractor 未定义

   原因：未 import；该类在 document_compressors 子模块。

   处理：from langchain_classic.retrievers.document_compressors import LLMChainExtractor。



10) ChatPromptTemplate 与 invoke 参数对不上

   原因：模板里是 {context}、{question}，invoke 时必须传同名键；多写/少写占位符会报错或答案异常。

   处理：模板中每个 {xxx} 都在 chain.invoke({...}) 里提供对应键；避免同一占位符重复出现无意义。



11) 全流程只用一个 streaming=True 的 ChatOpenAI

   原因：LLMChainExtractor 内部也会调用 llm；若全局 streaming=True，部分版本下压缩阶段行为异常或难调试。

   处理：压缩用普通 llm；仅「最后对用户输出答案」那条链用 llm_stream（streaming=True）。



--------------------------------------------------------------------------------

【流程简述（从文件到回答）】

Loader 读文档 → CharacterTextSplitter 切块 → OpenAIEmbeddings 向量化 → Chroma 存向量 →

as_retriever 检索 → LLMChainExtractor 压缩片段 → ContextualCompressionRetriever 包装 →

得到 context 字符串 → ChatPromptTemplate 填入 {context}、{question} →

非流式：prompt | llm 后 invoke 得完整回复；流式：prompt | llm_stream | StrOutputParser 后 stream 逐段 print。

StrOutputParser 让 stream 迭代项多为纯 str，便于打字机效果；压缩阶段始终用非流式 llm。



--------------------------------------------------------------------------------

【类里两个对外方法（初学者对照用）】

- askQuestion(question)：一次返回整段 str，内部用 chain.invoke，适合不接流式的场景。

- askQuestionStream(question)：边生成边 print，最后仍 return 全文；内部用 chain.stream。



"""

# ---------------------------------------------------------------------------

# import（导入）：从标准库引入符号。

# ---------------------------------------------------------------------------

import os


# os.getenv：读取环境变量（如 OPENAI_API_KEY、模型名）；改系统环境变量后需重开终端。


from pathlib import Path


# Path：面向对象路径；__file__ 为当前脚本；resolve().parent 为脚本所在文件夹（绝对路径）。


# ---------------------------------------------------------------------------

# import：第三方包（文档加载、切分、输出解析、提示词、向量库、OpenAI、检索与压缩）。

# ---------------------------------------------------------------------------

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader


# Docx2txtLoader / PyPDFLoader / TextLoader：按文件后缀选加载器，load() 得到 Document 列表。


from langchain_text_splitters.character import CharacterTextSplitter


# CharacterTextSplitter：按字符数切分；chunk_size 每块最大长度，chunk_overlap 相邻块重叠减少断句。


from langchain_core.output_parsers import StrOutputParser


# StrOutputParser：把模型消息解析成 str；接在 llm 后时，stream() 常逐段产出纯文本，便于流式打印。


from langchain_core.prompts import ChatPromptTemplate


# ChatPromptTemplate：聊天提示模板；from_template 中 {context}、{question} 需在 invoke 时传入键名一致的字段。


from langchain_chroma import Chroma


# Chroma：向量库；from_documents 会用 embedding 把每块文本变成向量并写入。


from langchain_openai import OpenAIEmbeddings


# OpenAIEmbeddings：走 OpenAI 的 Embeddings（向量化）接口，与 Chat 接口不是同一类。


from langchain_openai import ChatOpenAI


# ChatOpenAI：聊天模型；LLMChainExtractor 用 llm 做「压缩」（建议关闭流式，见下方 llm_stream）。


from langchain_classic.retrievers import ContextualCompressionRetriever


# ContextualCompressionRetriever：包装底层检索器 + 文档压缩器，先检索再压缩。


from langchain_classic.retrievers.document_compressors import LLMChainExtractor


# LLMChainExtractor：用 LLM 从每条检索结果里抽取与问题相关的文字。


# ---------------------------------------------------------------------------

# 全局配置：路径、嵌入模型、聊天模型（import 本文件时执行一次）

# ---------------------------------------------------------------------------

# demo.docx 建议与本 .py 同目录；用 __file__ 定位，避免从别的目录运行 python 时找不到文件。

_SCRIPT_DIR = Path(__file__).resolve().parent


embedding_model = OpenAIEmbeddings(
    # model：须为嵌入模型名（如 text-embedding-3-small），不要用 gpt-4o 等聊天模型名。
    model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
    api_key=os.getenv("OPENAI_API_KEY"),
)


llm = ChatOpenAI(
    # model：聊天补全模型，与上面 embedding 的 model 含义不同。
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
)


# llm_stream：与 llm 参数一致，仅 streaming=True，用于最终「秘书回答」链的 stream()；不向 LLMChainExtractor 传入。

llm_stream = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
    streaming=True,
)


# ---------------------------------------------------------------------------

# 类 ChatDoc：读文件 → 切块 → 建向量库 → 带压缩的检索问答（支持流式打印）

# ---------------------------------------------------------------------------


class ChatDoc:
    # -----------------------------------------------------------------------
    # __init__：记录要读的文件路径，并准备好「秘书」提示词模板（RAG 最后一步用）
    # -----------------------------------------------------------------------

    def __init__(self, file_path):
        # file_path：建议绝对路径，或 str(_SCRIPT_DIR / "xxx.docx")，避免相对路径找不到文件（见文首错误 1）。
        self.file_path = file_path
        # vector_db：Chroma 向量库对象；一开始 None，embedding_and_vector_database 里赋值。
        self.vector_db = None
        # 模板字符串里的 {context}、{question} 必须与 chain.invoke / stream 传入的字典键完全一致（见错误 10）。
        self.template = """你是一个处理文档的秘书，从不说自己是 AI；只根据下面 Context 回答 Question，勿编造。

Context:
{context}

Question:
{question}

Answer:"""
        # from_template：把字符串变成可复用的 ChatPromptTemplate，后面用 | 与 llm 串成链。
        self.prompt = ChatPromptTemplate.from_template(self.template)

    # -----------------------------------------------------------------------
    # getFile：只负责「读入原始文档」，返回 Document 列表；不做切块、不做向量
    # -----------------------------------------------------------------------

    def getFile(self):
        """按扩展名选 Loader，返回 Document 列表；不支持的扩展名返回 None。"""

        if self.file_path.endswith(".docx"):
            loader = Docx2txtLoader(self.file_path)
            text = loader.load()
            return text
        elif self.file_path.endswith(".pdf"):
            loader = PyPDFLoader(self.file_path)
            text = loader.load()
            return text
        elif self.file_path.endswith(".txt"):
            loader = TextLoader(self.file_path)
            text = loader.load()
            return text
        return None

    # -----------------------------------------------------------------------
    # splitSentence：把长文档切成很多小段，方便向量库按「块」建索引
    # -----------------------------------------------------------------------

    def splitSentence(self):
        """把 getFile 得到的 Document 列表再切成小块，写入 self.splitText。"""

        full_text = self.getFile()
        if full_text is not None:
            text_split = CharacterTextSplitter(chunk_size=150, chunk_overlap=20)
            texts = text_split.split_documents(full_text)
            self.splitText = texts

    # -----------------------------------------------------------------------
    # embedding_and_vector_database：切块 → 向量 → 写入 Chroma（内存；未 persist 到磁盘）
    # -----------------------------------------------------------------------

    def embedding_and_vector_database(self):
        """用全局 embedding_model 向量化 self.splitText 并写入 Chroma，赋给 self.vector_db。"""

        self.vector_db = Chroma.from_documents(
            documents=self.splitText,
            embedding=embedding_model,
        )
        return self.vector_db

    # -----------------------------------------------------------------------
    # _retrieve_context：不直接给初学者用；把「检索到的文档」压成一段 context 文本
    # -----------------------------------------------------------------------

    def _retrieve_context(self, question: str) -> str:
        """向量检索 + LLM 压缩，返回拼好的 context 字符串（同步、非流式）。"""

        if self.vector_db is None:
            self.embedding_and_vector_database()
        # LLMChainExtractor.from_llm(llm)：这里只传入「用来做片段压缩」的聊天模型即可（见错误 6、11）。
        compressor = LLMChainExtractor.from_llm(llm)
        # 先 as_retriever() 做相似度检索，再交给 compressor 用 LLM 删掉无关句子。
        compressor_retriever = ContextualCompressionRetriever(
            base_retriever=self.vector_db.as_retriever(),
            base_compressor=compressor,
        )
        docs = compressor_retriever.invoke(question)
        # docs 是 list[Document]，没有整体的 .page_content，只能逐条 join（见错误 5）。
        return "\n\n".join(d.page_content for d in docs)

    # -----------------------------------------------------------------------
    # askQuestion：一次性生成完整回答（非流式），返回 str
    # -----------------------------------------------------------------------

    def askQuestion(self, question):
        """检索 + 压缩 + 非流式 invoke，返回完整回答字符串。"""

        context_text = self._retrieve_context(question)
        # LCEL：竖线左边提示词，右边模型；invoke 的字典键要与模板占位符一致。
        chain = self.prompt | llm
        reply = chain.invoke({"context": context_text, "question": question})
        return reply.content

    # -----------------------------------------------------------------------
    # askQuestionStream：流式打印 + 仍返回完整 str（适合终端里「看着它打字」）
    # -----------------------------------------------------------------------

    def askQuestionStream(self, question):
        """同 askQuestion，但 prompt | llm_stream | StrOutputParser 的 stream() 边生成边 print；返回全文。"""

        context_text = self._retrieve_context(question)
        # llm_stream 带 streaming=True；StrOutputParser 让 stream 产出 str 片段（见文首说明与错误 11）。
        chain = self.prompt | llm_stream | StrOutputParser()
        inputs = {"context": context_text, "question": question}
        parts = []
        # end=""：不换行；flush=True：尽快显示，减少控制台缓冲导致「一整段才出来」的感觉。
        for token in chain.stream(inputs):
            if token:
                print(token, end="", flush=True)
                parts.append(token)
        print()
        return "".join(parts)

# ---------------------------------------------------------------------------

# 主流程（直接运行本脚本时执行）

# ---------------------------------------------------------------------------

# 1）构造 ChatDoc，路径相对脚本目录，避免工作目录不对找不到 demo.docx。

chat_doc = ChatDoc(str(_SCRIPT_DIR / "demo.docx"))


# 2）切块：得到 self.splitText。

chat_doc.splitSentence()


# 3）建向量库：得到 self.vector_db（内存中的 Chroma，未 persist 到磁盘）。

chat_doc.embedding_and_vector_database()


# 4）提问：流式打印回答（逐字/逐块出现）；若只要一次性完整字符串可改用 askQuestion。

chat_doc.askQuestionStream("地方大官员利用职务便利，为他人谋取利益，收受贿赂，数额巨大，情节严重，应当如何处理？")
