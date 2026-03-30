from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers.util import cos_sim
import numpy as np

# 1) 选择 embedding 模型名
# - 推荐将分词器/模型统一为同一个模型族，这里使用 bge-m3（常用于检索与语义相似度）。
model_name = "BAAI/bge-m3"

# 2) 初始化 LangChain 的 HuggingFaceEmbeddings
# - 该对象内部会调用 sentence-transformers 完成“文本 -> 向量”。
model = HuggingFaceEmbeddings(model_name=model_name)

# 3) 准备待编码文本
input_texts = [
    "中国的首都是哪里？",
    "今天天气不错",
    "今天中午吃什么？",
    "北京",
]

# 4) 生成文档向量
# - embed_documents 返回“列表[list]”，每个元素是一条文本对应的向量。
embeddings = model.embed_documents(input_texts)

# embed_documents 返回的是 Python 列表，不是 numpy 数组；先转一下再看形状
embeddings = np.array(embeddings)

# 5) 相似度计算（当前逻辑：第0句分别与其余句子比较）
# - i 从 1 开始，避免自己与自己比较；
# - cos_sim 越接近 1，通常语义越相似。
for i in range(1, len(input_texts)):
    print(input_texts[0], input_texts[i], cos_sim(embeddings[0], embeddings[i]))


# ========================= 学习笔记（你问过的问题 + 注意点） =========================
# Q1: “无法解析导入 langchain.embeddings.huggingface” 是什么问题？
# A:
# - 是包路径升级导致的导入路径变化；
# - 老路径：from langchain.embeddings.huggingface import HuggingFaceEmbeddings（已不可用）
# - 当前可用：from langchain_community.embeddings import HuggingFaceEmbeddings
#
# Q2: 这个包名改了吗？
# A:
# - 是的，LangChain 拆分后，社区组件迁到了 langchain_community；
# - 你的环境已验证该新路径可用。
#
# Q3: 为什么之前 print(embeddings.shape) 会出问题？
# A:
# - 因为 embed_documents 返回 list，不是 numpy 数组；
# - 先 embeddings = np.array(embeddings) 再看 shape。
#
# Q4: 可以用更新模型/分词器吗？去哪里找？
# A:
# - 可以，通常直接更换 model_name；
# - 模型可在 Hugging Face Models 页面搜索（关键词：embedding/chinese/bge/gte）。
#
# Q5: 余弦相似度这段循环是什么意思？
# A:
# - 它在做“第0句和后面每句”的相似度对比；
# - 若要“所有句子两两比较”，可用双层循环（j 从 i+1 开始，避免重复比较）。
#
# 【注意点】
# - 你的环境可能会提示 deprecation：未来推荐 `langchain_huggingface` 包。
#   可选迁移：
#   1) pip install -U langchain-huggingface
#   2) from langchain_huggingface import HuggingFaceEmbeddings
# - 首次下载模型较慢，且可能受网络影响；必要时配置 HF 镜像或本地缓存目录。
# - 若只做学习演示，这份代码够用；若上生产，建议固定依赖版本并写 requirements.txt。
# ============================================================================
