from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers.util import cos_sim
import numpy as np
from numpy.linalg import norm
from numpy import dot

# 1) 选择 embedding 模型（用于把文本转成向量）
model_name = "BAAI/bge-m3"

# 2) 初始化向量模型（内部会完成分词和编码）
model = HuggingFaceEmbeddings(model_name=model_name)

# 3) 准备待比较的文本
input_texts = [
    "中国的首都是哪里？",
    "今天天气不错",
    "今天中午吃什么？",
    "北京",
]

# 4) 生成每条文本的向量（列表）
embeddings = model.embed_documents(input_texts)

# 5) 转成 numpy 数组，方便后续做数学计算
embeddings = np.array(embeddings)

# 6) 这里选第 0 句和第 3 句做示例比较
a=embeddings[0]
b=embeddings[3]

# 7) 余弦相似度（Cosine Similarity）
# 公式：cos(a,b) = dot(a,b) / (||a||*||b||)
# 用法：衡量“方向是否相似”（不太受向量长度影响）
# 大小比较：
# - 值越大越相似（通常越接近 1 越像）
# - 值越小越不相似（接近 0 相关性弱，负数表示方向相反）
dot_product = dot(a, b)/(norm(a)*norm(b))

# 8) 欧几里得距离（Euclidean Distance）
# 公式：||a - b||
# 用法：衡量“直线距离有多远”
# 大小比较：
# - 值越小越相似（距离更近）
# - 值越大越不相似（距离更远）
norm_product = norm(a-b)

# 9) 同时打印余弦相似度（手动 vs 工具函数）：
# - dot_product：手动计算结果
# - cos_sim(a,b)：sentence-transformers 工具函数结果（用于对照，二者应接近）
print(dot_product,cos_sim(a,b))

# 10) 打印欧几里得距离：
# - 这里没有固定上限，一般只看“相对大小”
# - 在同一批向量里，距离更小的 pair 往往更相似
print(norm_product)
