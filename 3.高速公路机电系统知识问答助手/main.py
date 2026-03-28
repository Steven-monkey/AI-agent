# -*- coding: utf-8 -*-
"""
高速公路机电系统知识问答助手（面向过程实现）

使用 LangChain 构建检索增强生成（RAG）流程：从本地 knowledge 目录加载文档、切分、
向量化存入内存向量库，用户提问时检索相关片段再交给大语言模型生成回答。
界面使用 Gradio 提供 Web 可视化交互。

环境变量（可选）：
- DEEPSEEK_API_KEY：若设置则优先使用 DeepSeek 对话模型；否则使用本地 Ollama。
- OLLAMA_CHAT_MODEL：Ollama 对话模型名，默认 deepseek-r1:14b（可按本机 ollama list 调整）。
- OLLAMA_BASE_URL：Ollama 服务地址，默认 http://127.0.0.1:11434。
- HF_EMBED_MODEL：Sentence-Transformers 模型名，用于本地向量嵌入（首次运行会下载）。
"""

from __future__ import annotations

import os
import traceback
from pathlib import Path

# LangChain 核心：文档、提示词、向量库
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore

# LangChain 社区：文档加载
from langchain_community.document_loaders import DirectoryLoader, TextLoader

# Hugging Face 本地句向量（推荐用 langchain-huggingface，避免弃用警告）
from langchain_huggingface import HuggingFaceEmbeddings

# 文本切分（独立包）
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 大模型：DeepSeek（API）与 Ollama（本地）
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama

# 可视化 Web 界面
import gradio as gr

# ---------------------------------------------------------------------------
# 全局状态（面向过程：在初始化函数中赋值，供问答函数读取）
# ---------------------------------------------------------------------------
# 向量检索器：根据用户问题返回最相关的文档片段
_retriever = None
# 对话大模型：根据提示词生成自然语言回答
_llm = None
# 初始化阶段的错误信息；非空时在界面中提示用户
_init_error: str | None = None


def get_project_paths() -> tuple[Path, Path]:
    """
    解析项目根目录与知识库目录路径。
    知识库默认位于本脚本同级的 knowledge 文件夹下。
    """
    # 本文件所在目录作为项目根
    base_dir = Path(__file__).resolve().parent
    # 存放 *.md 等文本资料的目录
    knowledge_dir = base_dir / "knowledge"
    return base_dir, knowledge_dir


def load_documents_from_knowledge_dir(knowledge_dir: Path) -> list[Document]:
    """
    从 knowledge 目录递归加载所有文本文件为 LangChain Document 列表。
    使用 TextLoader 并指定 UTF-8，避免中文乱码。
    """
    if not knowledge_dir.is_dir():
        raise FileNotFoundError(f"知识库目录不存在: {knowledge_dir}")

    # DirectoryLoader：批量加载目录下符合 glob 的文件
    loader = DirectoryLoader(
        str(knowledge_dir),
        # 同时匹配 Markdown 与纯文本；recursive=True 时会在子目录中递归查找
        glob=["*.md", "*.txt", "*.markdown"],
        recursive=True,
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=False,
        silent_errors=True,
    )
    # 执行加载；若目录为空则返回空列表
    documents = loader.load()
    if not documents:
        raise ValueError(
            f"在 {knowledge_dir} 中未找到可用的 .md / .txt 文件，请添加知识文件后再试。"
        )
    return documents


def split_documents_into_chunks(documents: list[Document]) -> list[Document]:
    """
    将长文档切分为较小文本块，便于向量检索时匹配更精确的段落。
    chunk_size / overlap 可按资料特点调整。
    """
    # 递归字符切分：尽量在段落、句号等处断开
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # 每块约 500 字符
        chunk_overlap=80,  # 块之间重叠，避免语义在边界被切断
        length_function=len,
        separators=["\n\n", "\n", "。", "；", " ", ""],
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


def build_embedding_model() -> HuggingFaceEmbeddings:
    """
    构建本地 HuggingFace 句子嵌入模型，用于将文本转为向量。
    默认使用多语言小模型，对中文有一定支持；首次运行会从网络下载权重。
    """
    # 可通过环境变量切换为其他 sentence-transformers 兼容模型
    model_name = os.environ.get(
        "HF_EMBED_MODEL",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )
    # model_kwargs：底层 SentenceTransformer 参数；device 由库自动选择 CPU/GPU
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={},  # 若换用需 trust_remote_code 的模型，可在此传入
        encode_kwargs={"normalize_embeddings": True},  # 归一化后便于余弦相似度检索
    )
    return embeddings


def build_in_memory_vector_store(chunks: list[Document], embeddings) -> InMemoryVectorStore:
    """
    使用内存向量库索引所有文本块；数据不落盘，进程退出后需重新构建。
    """
    vector_store = InMemoryVectorStore(embeddings)
    # 批量写入文档并计算向量
    vector_store.add_documents(chunks)
    return vector_store


def build_language_model():
    """
    根据环境变量选择大语言模型：有 DEEPSEEK_API_KEY 则用云端 DeepSeek，否则用本地 Ollama。
    """
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if api_key:
        # OpenAI 兼容接口调用 DeepSeek
        return ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.3,  # 知识问答略降低随机性，答案更稳
            api_key=api_key,
            base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        )
    # 本地 Ollama：模型名需与本机 `ollama list` 中已有模型一致
    chat_model = os.environ.get("OLLAMA_CHAT_MODEL", "deepseek-r1:14b")
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    return ChatOllama(model=chat_model, temperature=0.3, base_url=base_url)


def build_rag_prompt() -> ChatPromptTemplate:
    """
    构造 RAG 提示词模板：明确要求模型只依据给定资料作答，减少幻觉。
    """
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是高速公路机电系统领域的知识助手。请严格根据下面「参考资料」回答用户问题；"
                "若资料中没有相关信息，请直接说明无法从所给资料中得出答案，不要编造。"
                "回答使用简体中文，条理清晰。",
            ),
            (
                "human",
                "参考资料：\n{context}\n\n用户问题：{question}",
            ),
        ]
    )


def format_reference_documents(docs: list[Document]) -> str:
    """
    将检索到的文档块格式化为字符串，用于界面展示「参考片段」。
    """
    parts: list[str] = []
    for i, doc in enumerate(docs, start=1):
        src = doc.metadata.get("source", "未知来源")
        # 只取文件名，路径更短更易读
        short_src = Path(str(src)).name
        parts.append(f"【片段 {i}】（来源: {short_src}）\n{doc.page_content.strip()}")
    return "\n\n---\n\n".join(parts)


def initialize_rag_pipeline() -> None:
    """
    初始化全局检索器与语言模型：加载知识、切分、建库、创建 retriever。
    若任一步失败，记录错误信息到 _init_error，供界面展示。
    """
    global _retriever, _llm, _init_error

    _retriever = None
    _llm = None
    _init_error = None

    try:
        _, knowledge_dir = get_project_paths()
        # 1) 加载原始文档
        documents = load_documents_from_knowledge_dir(knowledge_dir)
        # 2) 切分为块
        chunks = split_documents_into_chunks(documents)
        # 3) 嵌入模型 + 向量库
        embeddings = build_embedding_model()
        vector_store = build_in_memory_vector_store(chunks, embeddings)
        # 4) 从向量库得到检索器：相似度 Top-K
        _retriever = vector_store.as_retriever(search_kwargs={"k": 4})
        # 5) 语言模型
        _llm = build_language_model()
    except Exception:
        _init_error = traceback.format_exc()


def run_rag_question_answer(user_question: str) -> tuple[str, str]:
    """
    执行一次完整的 RAG 问答：检索 -> 拼上下文 -> 调用 LLM -> 返回（回答，参考片段）。
    """
    global _retriever, _llm, _init_error

    if _init_error:
        return ("系统未完成初始化，请根据下方错误信息排查后重启。", _init_error)
    if _retriever is None or _llm is None:
        return ("内部错误：检索器或模型未就绪。", "")

    question = (user_question or "").strip()
    if not question:
        return ("请输入您的问题。", "")

    # 相似度检索：返回与问题最相关的若干文档块
    retrieved_docs = _retriever.invoke(question)
    ref_text = format_reference_documents(retrieved_docs)

    # 若无检索结果（极端情况），仍让模型说明资料不足
    context = "\n\n".join(d.page_content for d in retrieved_docs) or "（无匹配片段）"

    prompt = build_rag_prompt()
    # 将提示词模板与变量交给模型
    messages = prompt.format_messages(context=context, question=question)
    response = _llm.invoke(messages)
    answer_text = getattr(response, "content", str(response))

    return (answer_text.strip(), ref_text)


def _make_chatbot(**kwargs) -> gr.Chatbot:
    """创建 Chatbot；在支持的 Gradio 版本上附加复制按钮与空状态提示。"""
    extra = {
        "show_copy_button": True,
        "placeholder": "在下方输入问题并发送，对话将显示在这里。",
    }
    try:
        return gr.Chatbot(**{**kwargs, **extra})
    except TypeError:
        return gr.Chatbot(**kwargs)


def _gradio_ui_css() -> str:
    """Gradio 自定义样式：柔和背景、圆角卡片、侧栏与按钮细节。"""
    return """
    .gradio-container {
        max-width: 1180px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding: 1.25rem 1rem 2rem !important;
    }
    .app-hero-wrap {
        margin-bottom: 1.25rem;
    }
    /* 主题会覆盖 h1/p 颜色，需显式指定浅色并加 !important */
    .app-hero {
        background: linear-gradient(125deg, #1d4ed8 0%, #2563eb 38%, #0ea5e9 72%, #38bdf8 100%);
        color: #ffffff !important;
        padding: 1.6rem 1.5rem 1.45rem;
        border-radius: 14px;
        box-shadow: 0 12px 40px rgba(30, 64, 175, 0.22);
    }
    .app-hero h1 {
        margin: 0 0 0.45rem 0;
        font-size: 1.55rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        line-height: 1.3;
        color: #ffffff !important;
    }
    .app-hero .sub {
        margin: 0;
        color: rgba(255, 255, 255, 0.96) !important;
        opacity: 1;
        font-size: 0.92rem;
        line-height: 1.65;
        max-width: 52rem;
    }
    .app-hero .sub code {
        color: #f0f9ff !important;
        background: rgba(255, 255, 255, 0.22) !important;
        padding: 0.12em 0.45em;
        border-radius: 6px;
        font-size: 0.88em;
        border: 1px solid rgba(255, 255, 255, 0.28);
    }
    .app-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.85rem;
    }
    .app-badge {
        display: inline-block;
        font-size: 0.72rem;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.22);
        border: 1px solid rgba(255, 255, 255, 0.38);
    }
    .app-alert {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        color: #9a3412;
        padding: 0.9rem 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        font-size: 0.88rem;
    }
    .app-alert pre {
        margin: 0.5rem 0 0 0;
        white-space: pre-wrap;
        word-break: break-word;
        font-size: 0.78rem;
        color: #7c2d12;
    }
    .ref-col textarea {
        border-radius: 10px !important;
        font-size: 0.88rem !important;
        line-height: 1.55 !important;
    }
    .chat-wrap {
        border-radius: 12px !important;
        overflow: hidden;
    }
    """


def build_gradio_interface() -> gr.Blocks:
    """
    搭建 Gradio 页面：标题说明、多轮对话、参考片段展示区。
    """
    # 页面打开时的说明文案（页头内展示）
    description = (
        "基于 LangChain 的检索增强生成（RAG），知识来自本项目 <code>knowledge</code> 目录。"
        " 模型优先读取环境变量 <code>DEEPSEEK_API_KEY</code> 调用 DeepSeek，否则使用本地 Ollama。"
    )

    theme = gr.themes.Soft(
        primary_hue=gr.themes.colors.blue,
        secondary_hue=gr.themes.colors.slate,
    ).set(
        body_background_fill="#eef2f7",
        block_background_fill="#ffffff",
        block_border_width="0px",
        block_shadow="0 2px 12px rgba(15, 23, 42, 0.06)",
        button_primary_background_fill="#2563eb",
        button_primary_background_fill_hover="#1d4ed8",
    )

    with gr.Blocks(
        title="高速公路机电系统知识问答助手",
        theme=theme,
        css=_gradio_ui_css(),
    ) as demo:
        gr.HTML(
            f"""
            <div class="app-hero-wrap">
              <div class="app-hero">
                <h1>高速公路机电系统 · 知识问答助手</h1>
                <p class="sub">{description}</p>
                <div class="app-badges">
                  <span class="app-badge">本地知识库检索</span>
                  <span class="app-badge">RAG 增强回答</span>
                  <span class="app-badge">参考片段可核对</span>
                </div>
              </div>
            </div>
            """
        )

        # 若向量库或模型初始化失败，在页首直接展示错误堆栈，便于排查
        if _init_error:
            err_preview = _init_error[:4000].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            gr.HTML(
                f"""
                <div class="app-alert">
                  <strong>系统初始化未完全成功</strong>，请根据下方信息排查后重新启动程序。
                  <pre>{err_preview}</pre>
                </div>
                """
            )

        with gr.Row(equal_height=True):
            with gr.Column(scale=5, elem_classes=["chat-col"]):
                chatbot = _make_chatbot(
                    label="对话",
                    height=440,
                    elem_classes=["chat-wrap"],
                )
                with gr.Row():
                    user_input = gr.Textbox(
                        label="问题",
                        placeholder="例如：隧道通风系统常见检测手段有哪些？",
                        lines=2,
                        scale=5,
                        show_label=True,
                    )
                    submit_btn = gr.Button("发送", variant="primary", scale=1, min_width=100)
                clear_btn = gr.Button("清空对话", variant="secondary")

            with gr.Column(scale=3, elem_classes=["ref-col"]):
                reference_box = gr.Textbox(
                    label="检索到的参考片段",
                    lines=20,
                    max_lines=32,
                    interactive=False,
                    placeholder="提交问题后，这里会显示与答案相关的知识库原文片段。",
                )

        # 单轮提交：把新问答追加到历史，并清空输入框（返回空字符串到 user_input）
        def on_submit(message: str, history: list):
            # Gradio Chatbot 在较新版本中 history 为消息列表；兼容旧版 [用户, 助手] 二元组列表
            if history is None:
                history = []

            answer, ref = run_rag_question_answer(message)

            # 若历史为旧格式，先转成统一的消息字典列表，避免混用导致渲染异常
            if history and isinstance(history[0], (list, tuple)):
                new_hist = []
                for pair in history:
                    if pair and len(pair) >= 2:
                        new_hist.append({"role": "user", "content": pair[0]})
                        new_hist.append({"role": "assistant", "content": pair[1]})
                history = new_hist

            history = list(history)
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": answer})
            return history, ref, ""

        # 清空对话区、参考区与输入框
        def on_clear():
            return [], "", ""

        submit_btn.click(
            on_submit,
            inputs=[user_input, chatbot],
            outputs=[chatbot, reference_box, user_input],
        )
        user_input.submit(
            on_submit,
            inputs=[user_input, chatbot],
            outputs=[chatbot, reference_box, user_input],
        )
        clear_btn.click(on_clear, outputs=[chatbot, reference_box, user_input])

    return demo


def launch_web_ui(server_port: int | None = None) -> None:
    """
    启动 Gradio 本地 Web 服务并阻塞运行。
    """
    port = server_port if server_port is not None else int(os.environ.get("GRADIO_SERVER_PORT", "7860"))
    demo = build_gradio_interface()
    # share=False：仅本机或局域网访问；可在需要时改为 True 生成公网链接（慎用）
    demo.launch(server_name="0.0.0.0", server_port=port, share=False)


def main() -> None:
    """
    程序入口：先构建 RAG 管线，再启动可视化界面。
    """
    # 在启动 Web 前完成向量库构建（首次下载嵌入模型可能较慢）
    initialize_rag_pipeline()
    launch_web_ui()


if __name__ == "__main__":
    main()
