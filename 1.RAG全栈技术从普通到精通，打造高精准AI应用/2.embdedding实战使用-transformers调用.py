from transformers import AutoTokenizer, AutoModel
from sentence_transformers.util import cos_sim
import torch.nn.functional as F
import torch

# 1) 选择模型名：
# - 分词器(tokenizer)和模型(model)要使用同一个 model_name。
# - 这里用的是 BAAI/bge-m3（常用于检索和向量表示）。
model_name = "BAAI/bge-m3"

# 2) 准备要转向量的文本列表（一个列表里可以放多句）。
input_texts = [
    "中国的首都是哪里？",
    "今天天气不错",
    "今天中午吃什么？",
    "北京",
]

# 3) 加载分词器：
# 分词器负责把中文句子切分并转换为模型可读的数字ID。
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 4) 加载模型：
# AutoModel 返回的是基础模型输出（隐藏状态），通常用于自己做 pooling 或相似度计算。
model = AutoModel.from_pretrained(model_name)

# 5) 批量分词并转成 PyTorch 张量：
# - padding=True: 把短句补齐到同长度，便于批量计算；
# - truncation=True: 超长文本会截断，防止超过模型最大长度；
# - return_tensors="pt": 返回 PyTorch Tensor，而不是普通列表。
batch_tokens = tokenizer(
    input_texts, padding=True, truncation=True, return_tensors="pt"
)

# 6) 前向推理：
# 把分词结果作为关键字参数喂给模型（等价于 model(input_ids=..., attention_mask=...)）。
outputs = model(**batch_tokens)
# print(outputs)
# print(outputs.last_hidden_state.shape)

# 7) 取句向量（embedding）：
# outputs.last_hidden_state 形状一般是 [batch_size, seq_len, hidden_size]。
# [:, 0, :] 表示取每个句子的第 1 个 token 向量（常被当作句向量的一种简化做法）。
embeddings = outputs.last_hidden_state[:, 0, :]

# 8) 做 L2 归一化：
# 归一化后向量长度为 1，后续计算余弦相似度更稳定，数值更容易比较。
embeddings = F.normalize(embeddings, p=2, dim=1)

# 9) 计算相似度（当前写法：只拿第 0 句和后面每句比较）：
# i 从 1 开始，所以会比较：
# - 第0句 vs 第1句
# - 第0句 vs 第2句
# - 第0句 vs 第3句
# cos_sim 越接近 1，语义通常越相近。
for i in range(1, len(input_texts)):
    print(input_texts[0], input_texts[i], cos_sim(embeddings[0], embeddings[i]))


# print(embeddings.shape)


# print(batch_tokens[0].tokens)
# print(batch_tokens[0].ids)

# print(batch_tokens[3].tokens)
# print(batch_tokens[3].ids)

# ========================= 学习笔记（你问过的问题汇总） =========================
# Q1: 可以用更新的分词器吗？去哪里找？
# A:
# - 可以，通常是“换模型名”，分词器和模型一起换；
# - 模型可在 Hugging Face: https://huggingface.co/models 搜索（关键词如 embedding/chinese/bge/gte）。
#
# Q2: 这段 tokenizer(...) 是什么意思？
# A:
# - 它把 input_texts 变成模型能读的数字输入（input_ids、attention_mask 等）；
# - return_tensors="pt" 让输出变成 PyTorch Tensor。
#
# Q3: 为什么有些代码要双层循环 i/j？
# A:
# - 双层循环常用于“所有句子两两比较相似度”；
# - j 从 i+1 开始可避免“自己和自己比”及重复比较（A-B 和 B-A）。
#
# Q4: 你之前遇到的 stream 报错（tuple 没有 choices）是什么意思？
# A:
# - 当 stream=False 时，返回的是一次性完整响应，不应按流式 chunk 遍历；
# - 流式要用 stream=True，并按 chunk 读取 delta；
# - 非流式应直接读取 response.choices[0].message.content。
# ==========================================================================
