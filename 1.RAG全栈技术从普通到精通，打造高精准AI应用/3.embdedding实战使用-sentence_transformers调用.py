from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

# 1) 选择模型名（分词器和编码过程会由 SentenceTransformer 内部自动处理）
# 这里使用 bge-m3，它常用于检索和语义相似度任务。
model_name = "BAAI/bge-m3"

# 2) 加载句向量模型：
# 与 transformers 手动流程相比，这里更简单，一行就封装了“分词 + 前向 + pooling”等步骤。
model = SentenceTransformer(model_name)

# 3) 准备要编码的文本（一个列表里放多句）
input_texts = [
    "中国的首都是哪里？",
    "今天天气不错",
    "今天中午吃什么？",
    "北京",
]

# 4) 直接将文本编码为向量：
# 返回值 embeddings 通常是二维数组，形状约为 [句子数量, 向量维度]。
embeddings = model.encode(input_texts)
# print(embeddings.shape)

# 5) 计算相似度（当前写法：第0句依次和后面每句比较）
# i 从 1 开始，因此会比较：
# - 第0句 vs 第1句
# - 第0句 vs 第2句
# - 第0句 vs 第3句
# cos_sim 值越接近 1，通常语义越相似。
for i in range(1, len(input_texts)):
    print(input_texts[0], input_texts[i], cos_sim(embeddings[0], embeddings[i]))

# ========================= 学习笔记（对照 transformers 版本） =========================
# - 这个写法更“省事”：你不需要手动写 tokenizer、padding、truncation、取 CLS 等步骤。
# - 如果你是做教学/想理解底层流程，用 transformers 写法更直观；
#   如果你是做业务开发、想快速得到句向量，sentence-transformers 更方便。
# - 若想“所有句子两两比较”，可改成双层循环：
#   for i in range(len(input_texts)):
#       for j in range(i + 1, len(input_texts)):
#           print(input_texts[i], input_texts[j], cos_sim(embeddings[i], embeddings[j]))
# ==========================================================================
