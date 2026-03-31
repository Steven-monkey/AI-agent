import os
import chromadb
from chromadb.utils import embedding_functions
import numpy as np

# ==========================================================
# Chroma 向量数据库（服务端）示例脚本
# ----------------------------------------------------------
# 本文件按 7 个步骤组织：
# 1) 连接服务端
# 2) 准备 embedding 模型与集合
# 3) 增（add）
# 4) 查（get/query）
# 5) 改（update）
# 6) 删（delete）
# 7) 删除整个集合（危险）
#
# 你可以把它当作“最小可用模板”：
# - 平时只开 3) add + 4) query
# - 需要维护数据时再打开 5) update / 6) delete
# ==========================================================

# =========================
# 1) 连接 Chroma 服务端
# =========================
# 从环境变量读取 IP 和端口，避免把地址硬编码在代码里
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = os.getenv("CHROMA_PORT")

# 连接远程 Chroma（端口需为整数；环境变量里读出来是字符串）
# 若未配置 CHROMA_PORT，默认使用 8000
client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=int(CHROMA_PORT) if CHROMA_PORT else 8000,
)

# =========================
# 2) 准备向量模型与集合
# =========================
# 这里使用 bge-m3 作为 embedding 模型
# 注意：首次加载模型可能较慢，属于正常现象
model_name = "BAAI/bge-m3"
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=model_name
)

# 如果集合不存在就创建，存在则直接复用
# name 相当于“表名/索引名”
collection = client.get_or_create_collection(
    name="test",
    embedding_function=embedding_function,
)

# =========================
# 3) 增（Create）: add
# =========================
# 新增数据：documents / metadatas / ids 必须一一对应

# ----- 你的原始写法（保留作对照，不执行）-----
# collection.add(
#     documents=[
#         "切尔西",
#         "利物浦",
#         "曼城",
#         "热刺",
#         "曼联",
#         "阿森纳",
#         "皇家马德里",
#         "巴塞罗那",
#         "拜仁慕尼黑",
#         "多特蒙德",
#         "巴黎圣日耳曼",
#         "尤文图斯",
#         "AC米兰",
#         "国际米兰",
#         "曼联",
#         "阿森纳",
#         "切尔西",
#         "利物浦",
#         "曼城",
#         "热刺",
#         "皇家马德里",
#         "巴塞罗那",
#         "拜仁慕尼黑",
#         "多特蒙德",
#         "巴黎圣日耳曼",
#         "尤文图斯",
#         "AC米兰",
#         "国际米兰",
#     ],
#     # 注意：这里数量要和 documents/ids 完全一致
#     # metadatas=[{"source": "英超联赛球队"} for _ in range(28)],
#     metadatas=[{"source": "英超联赛球队"} for _ in range(20)],
#     ids=[str(i) for i in range(1, 21)],
# )

# ----- 推荐写法：结构化数据 + 自动生成 ids/metadatas -----
# records 是“源数据层”，后续统一拆分成 documents/metadatas/ids
# 这样维护数据时只改一处，代码不容易乱
records = [
    {"document": "切尔西", "league": "英超", "country": "英格兰"},
    {"document": "利物浦", "league": "英超", "country": "英格兰"},
    {"document": "曼城", "league": "英超", "country": "英格兰"},
    {"document": "热刺", "league": "英超", "country": "英格兰"},
    {"document": "曼联", "league": "英超", "country": "英格兰"},
    {"document": "阿森纳", "league": "英超", "country": "英格兰"},
    {"document": "皇家马德里", "league": "西甲", "country": "西班牙"},
    {"document": "巴塞罗那", "league": "西甲", "country": "西班牙"},
    {"document": "拜仁慕尼黑", "league": "德甲", "country": "德国"},
    {"document": "多特蒙德", "league": "德甲", "country": "德国"},
    {"document": "巴黎圣日耳曼", "league": "法甲", "country": "法国"},
    {"document": "尤文图斯", "league": "意甲", "country": "意大利"},
    {"document": "AC米兰", "league": "意甲", "country": "意大利"},
    {"document": "国际米兰", "league": "意甲", "country": "意大利"},
]

# add() 需要的文本列表
documents = [item["document"] for item in records]
# 每条 metadata 可以不同：从 records 动态生成
metadatas = [
    {"source": "欧洲足球俱乐部", "league": item["league"], "country": item["country"]}
    for item in records
]
# ids 用循环自动生成，避免手写长列表
# 说明：生产环境建议使用更稳定的业务 id（如 team_xxx）
ids = [str(i) for i in range(1, len(records) + 1)]

# 真正写入向量库
collection.add(documents=documents, metadatas=metadatas, ids=ids)

# 通过 get_collection 再次获取集合（常用于脚本拆分后的独立读写）
get_collection = client.get_collection(
    name="test", embedding_function=embedding_function
)

# =========================
# 4) 查（Read）: get / query
# =========================
# 4.1 按 ID 精确读取
# 适合：已知主键 id，要拿回原文和 metadata
# id_list = get_collection.get(
#     ids=["1", "2", "3", "4", "5", "6"],
#     include=[
#         "documents",
#         "metadatas",
#         "embeddings",
#     ],
# )

# 4.2 按语义相似度检索（向量召回）
# query_texts 是“自然语言问题”
# n_results 是返回条数
# include 控制返回字段：documents / metadatas / distances / embeddings
query = "西甲球队有哪些"
results = get_collection.query(
    query_texts=[query],
    n_results=5,
    include=["documents", "embeddings"],
)
print(results)

# 查看 embedding 维度（可选）
# print(np.array(id_list["embeddings"]).shape)
# print(id_list["documents"])
# print(id_list["metadatas"])
# print(id_list["embeddings"])

# =========================
# 5) 改（Update）: update
# =========================
# 按 ID 更新文档和元数据（常用于修正文档内容、补标签）
# 注意：只会更新你传入的字段
# 注意：update 的 ids 必须已存在，否则不会更新到目标数据
# get_collection.update(
#     ids=["1"],
#     documents=["切尔西足球俱乐部"],
#     metadatas=[{"source": "英超联赛球队", "city": "London"}],
# )

# =========================
# 6) 删（Delete）: delete
# =========================
# 6.1 按 ID 删除（最常见）
# 如果你现在不想真的删除，可先注释掉
# get_collection.delete(ids=["6"])

# 6.2 按条件删除（where 过滤 metadata）
# 适合批量删除某一类数据
# 示例：删除 source=英超联赛球队 且 city=London 的数据
# get_collection.delete(where={"$and": [{"source": "英超联赛球队"}, {"city": "London"}]})

# =========================
# 7) 删除整个集合（危险操作）
# =========================
# 会把整个 test 集合清空并删除
# client.delete_collection("test")

# 验证连接（可选）：能返回心跳说明服务正常
# print("✅ 连接成功，服务端心跳：", client.heartbeat())
