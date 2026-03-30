"""



本文件演示：把 PDF 读成 Document 后，用 SemanticChunker 按「语义相似度」切块。



流程：PyPDFLoader 抽文本 → HuggingFace 本地句向量模型算 embedding →

SemanticChunker 在语义变化大的位置断开，得到若干 Document（比纯按字数切更贴主题边界）。



依赖：需安装 sentence-transformers（首次运行会下载模型，体积约几百 MB）。

  pip install sentence-transformers



说明：DeepSeek 官方 API 目前以对话为主，未提供与 OpenAI /v1/embeddings 对等的公开向量接口；

本 demo 用本地多语种模型做向量，与你在其它脚本里用 DeepSeek 做对话可以并存。



"""

# ---------------------------------------------------------------------------

# import（导入）

# ---------------------------------------------------------------------------

import os
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker

# 可选：离线时让 HuggingFace 走镜像（按你网络环境设置）
# os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

# ---------------------------------------------------------------------------

# 1) 加载文档：PDF 放在与本脚本同一目录，或修改 pdf_path

# ---------------------------------------------------------------------------

pdf_path = Path(__file__).resolve().parent / "demo.pdf"
loader = PyPDFLoader(str(pdf_path))
pages = list(loader.lazy_load())

if not pages:
    raise SystemExit("未读到任何页面：请确认 demo.pdf 存在且非空。")

# ---------------------------------------------------------------------------

# 2) 嵌入模型：多语种 MiniLM，中英文 PDF 都较合适；CPU 即可跑

# ---------------------------------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

# ---------------------------------------------------------------------------

# 3) 语义切块：在相邻句子向量差异大的位置切分（具体阈值由 breakpoint_threshold_type 等控制）

# ---------------------------------------------------------------------------

splitter = SemanticChunker(
    embeddings,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=95,
)

chunks = splitter.split_documents(pages)

print(f"共 {len(chunks)} 个语义块\n")

for i, doc in enumerate(chunks[:5]):
    preview = doc.page_content.strip().replace("\n", " ")[:200]
    print(f"--- 块 {i + 1} ---\n{preview}{'…' if len(doc.page_content) > 200 else ''}\n")

if len(chunks) > 5:
    print(f"... 其余 {len(chunks) - 5} 块略")
