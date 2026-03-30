from langchain_community.embeddings import HuggingFaceEmbeddings
from sklearn.cluster import KMeans


# 1) 准备文本数据：
# 这里放了 6 个词，前 3 个偏“水果”，后 3 个偏“动物”。
# 目标是看聚类后能否大致分成两组。
texts = ["苹果", "菠萝", "西瓜", "斑马", "大象", "老鼠"]

# 2) 选择并加载向量模型：
# 使用 bge-m3 把每条文本转换为向量（embedding）。
model_name = "BAAI/bge-m3"
model = HuggingFaceEmbeddings(model_name=model_name)

# 3) 文本 -> 向量：
# embed_documents 返回一个向量列表，每条文本对应一个高维向量。
embeddings = model.embed_documents(texts)

# 4) KMeans 聚类：
# n_clusters=2 表示分成 2 类；
# random_state=0 用于固定随机种子，便于复现实验结果。
kmeans = KMeans(n_clusters=2, random_state=0).fit(embeddings)

# 5) 获取每条文本的聚类标签：
# labels[i] 是第 i 条文本所属的簇编号（通常是 0 或 1）。
# 注意：标签数字本身没有语义，只代表“第几个簇”。
labels = kmeans.labels_

# 6) 打印每条文本及其聚类结果
for i in range(len(texts)):
    print(f"文本：{texts[i]} 聚类标签：{labels[i]}")


# ========================= 使用注意点 =========================
# - 聚类结果受样本数量影响：样本太少时，分组可能不稳定。
# - n_clusters 需要按任务调整：不知道分几类时可先试 2~5，再结合业务观察。
# - 标签 0/1 不代表“好/坏”或固定类别名称，需你自己解释每个簇的主题。
# ============================================================