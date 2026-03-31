# 导入 numpy，用于把 embedding 列表转成数组结构（便于批量写入）。
import numpy as np
# 导入 os，用于读取环境变量（例如 MILVUS_HOST、MILVUS_PORT）。
import os
# 从 pymilvus 导入连接、集合管理、Schema 定义等核心能力。
from pymilvus import (
    # 负责建立/管理与 Milvus 的连接。
    connections,
    # 提供集合是否存在、删除集合等工具方法。
    utility,
    # 定义单个字段（列）结构。
    FieldSchema,
    # 定义整个集合的结构（由多个字段组成）。
    CollectionSchema,
    # 字段类型枚举（如 VARCHAR、FLOAT_VECTOR、INT64）。
    DataType,
    # 集合对象：创建集合、插入、建索引、搜索都通过它操作。
    Collection,
)
# 导入 LangChain 的 HuggingFace 向量模型封装。
from langchain_huggingface import HuggingFaceEmbeddings

# =========================
# 1) 基础配置（可改参数集中放顶部）
# =========================
# Milvus 服务器地址：优先读环境变量，未设置时用默认公网 IP。
MILVUS_HOST = os.getenv("MILVUS_HOST", "120.78.121.40")
# Milvus 端口：默认 19530（Milvus 常用 gRPC 端口）。
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
# 集合名称：本脚本把数据写入该集合。
COLLECTION_NAME = "rag_db"
# 向量模型名称：用于把文本转成向量。
MODEL_NAME = "BAAI/bge-m3"
# 向量维度：必须与模型输出维度一致。
VECTOR_DIM = 1024

# =========================
# 2) 连接 Milvus（只保留一次连接）
# =========================
# 建立默认连接，后续所有 Collection 操作都依赖它。
connections.connect(
    # 连接别名，后续未指定 using 时默认走该连接。
    alias="default",
    # 连接目标主机。
    host=MILVUS_HOST,
    # 连接目标端口。
    port=MILVUS_PORT,
)

# =========================
# 3) 加载 embedding 模型
# =========================
# 初始化文本向量模型对象，后续用它生成文档向量和查询向量。
model = HuggingFaceEmbeddings(model_name=MODEL_NAME)

# =========================
# 4) 定义集合 Schema 并创建/获取集合
# =========================
# 每次运行前先删除旧集合，避免数据累计导致 num_entities 越来越大。
# 判断目标集合是否已经存在。
if utility.has_collection(COLLECTION_NAME):
    # 若存在则删除集合（含历史数据），确保本次是“干净写入”。
    utility.drop_collection(COLLECTION_NAME)

# 定义集合字段列表（Schema）。
fields = [
    # 主键字段：字符串类型，手动提供值，不自动生成。
    FieldSchema(
        # 字段名（只能字母/数字/下划线）。
        name="primary_id",
        # 字段类型：可变长字符串。
        dtype=DataType.VARCHAR,
        # 标记为主键字段。
        is_primary=True,
        # 字段说明（可选）。
        description="primary id",
        # VARCHAR 必须设置最大长度。
        max_length=100,
    ),
    # 原始文本字段。
    FieldSchema(
        name="document",
        dtype=DataType.VARCHAR,
        max_length=512,
        description="document",
    ),
    # 向量字段：用于向量索引和相似度搜索。
    FieldSchema(
        name="embedding",
        dtype=DataType.FLOAT_VECTOR,
        # 向量维度，必须与 embedding 模型输出一致。
        dim=VECTOR_DIM,
        description="embedding",
    ),
    # 额外标量字段（示例：分段编号/时间戳等）。
    FieldSchema(
        name="verse",
        dtype=DataType.INT64,
        description="timestamp",
    ),
]
# 根据上面字段定义创建集合对象（不存在则创建）。
rag_db = Collection(
    # 集合名 + Schema + 一致性级别。
    COLLECTION_NAME, CollectionSchema(fields=fields), consistency_level="Strong"
)

# =========================
# 5) 准备文本并生成向量
# =========================
# 准备要入库的文本列表（每个元素是一条文档）。
documents = [
    "有人说，世界杯是四年一次的狂欢，可对他们而言，是一生一次的奔赴。",
    "他们流过泪，受过伤，尝尽遗憾与失落，却从未放下心中热爱。",
    "胜负会被淡忘，冠军会被更迭，但那些坚守、救赎、思念与不屈，永远刻在世界杯的记忆里。",
    "原来最动人的从不是金杯闪耀，而是以凡人之躯，赴理想之约，用一生热爱，对抗岁月漫长。",
]
# 把所有文本批量转成向量（二维列表：条数 x 维度）。
embeddings = model.embed_documents(documents)

# =========================
# 6) 组装实体并写入 Milvus
# =========================
# 按字段顺序组织数据，顺序必须和 Schema 字段一一对应。
entities = [
    # 主键列表：这里按 0..N-1 生成字符串主键。
    [str(i) for i in range(len(documents))],
    # 文本内容列表。
    documents,
    # 向量列表（转成 numpy 数组也可正常写入）。
    np.array(embeddings),
    # 示例标量字段值，数量需与 documents 长度一致。
    [16, 5, 5, 7],
]
# 执行插入操作。
insert_result = rag_db.insert(entities)
# 刷盘，确保插入数据可见并持久化。
rag_db.flush()
# 定义索引参数（用于加速向量检索）。
index = {
    # 索引类型：IVF_FLAT（入门常用）。
    "index_type": "IVF_FLAT",
    # 向量模型常用 COSINE，相似度检索时也要保持一致。
    "metric_type": "COSINE",
    # nlist 是 IVF 的聚类桶数量，越大通常越精细但建索引开销更高。
    "params": {"nlist": 128},
}


# create_index 推荐显式使用 index_params 参数名，避免参数被误识别。
# 在 embedding 字段上创建向量索引。
rag_db.create_index(field_name="embedding", index_params=index)

# 再次获取集合对象（演示“读取路径”也能操作同一集合）。
get_collection = Collection("rag_db")
# 搜索前需要先 load，把集合加载到查询节点内存。
get_collection.load()
# 定义查询文本。
query = "世界杯"
# 这里用 embed_query 生成“单条查询向量”，返回一维向量（长度=VECTOR_DIM）。
query_emb = model.embed_query(query)
# 定义搜索参数（度量类型要与建索引保持一致）。
search_params = {
    # 必须与索引 metric_type 一致，否则会报 metric type not match。
    "metric_type": "COSINE",
    # nprobe 控制查询时扫描多少个桶，越大通常召回更高、速度更慢。
    "params": {"nprobe": 10},
}
# 执行向量搜索。
results = get_collection.search(
    # Milvus 的 data 需要二维结构，所以把单条向量再包一层列表。
    data=[query_emb],
    # 在哪个向量字段上搜索。
    anns_field="embedding",
    # search() 的必填参数名是 param，值使用上面定义的 search_params。
    param=search_params,
    # 返回前 K 条最相似结果。
    limit=2,
    # 指定结果中要带回的标量字段。
    output_fields=["document", "verse"],
)
# 遍历每个查询返回的命中列表（本例只有 1 条查询，所以通常 1 组 hits）。
for hits in results:
    # 遍历该查询下的每一条命中结果。
    for hit in hits:
        # 主键建议从 hit.id 读取；output_fields 里不包含主键字段时，hit.primary_id 可能不存在。
        # 打印主键和原文，方便观察搜索效果。
        print(f"primary_id: {hit.id}, document: {hit.entity.get('document')}")
