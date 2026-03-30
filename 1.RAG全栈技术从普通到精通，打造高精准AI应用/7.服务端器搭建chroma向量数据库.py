import os
import chromadb
from chromadb.utils import embedding_functions
import numpy as np

# 从环境变量读取IP，代码里完全不暴露
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = os.getenv("CHROMA_PORT")  # 端口也可以一起设环境变量

# 连接远程Chroma（端口需为整数；环境变量里是字符串）
client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=int(CHROMA_PORT) if CHROMA_PORT else 8000,
)
model_name = "BAAI/bge-m3"
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=model_name
)
collection = client.get_or_create_collection(
    name="test",
    embedding_function=embedding_function,
)
collection.add(
    documents=["切尔西", "利物浦", "曼城", "热刺", "曼联", "阿森纳"],
    # metadatas 与 documents/ids 必须一一对应，每条一条 dict
    metadatas=[{"source": "英超联赛球队"} for _ in range(6)],
    ids=["1", "2", "3", "4", "5", "6"],
)
get_collection = client.get_collection(
    name="test", embedding_function=embedding_function
)
id_list = get_collection.get(
    ids=["1", "2", "3", "4", "5", "6"],
    include=[
        "documents",
        "metadatas",
        "embeddings",
    ],
)
query = "英超球队有哪些"
results = get_collection.query(
    query_texts=[query], n_results=2, include=["documents", "metadatas"]
)
print(results)
# print(np.array(id_list["embeddings"]).shape)
# print(id_list["documents"])
# print(id_list["metadatas"])
# print(id_list["embeddings"])

# 验证连接
# print("✅ 连接成功，服务端心跳：", client.heartbeat())
