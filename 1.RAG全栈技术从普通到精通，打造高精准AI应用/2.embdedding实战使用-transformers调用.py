from transformers import AutoTokenizer, AutoModel
from sentence_transformers.util import cos_sim
import torch.nn.functional as F
import torch

model_name = "BAAI/bge-m3"
input_texts = [
    "中国的首都是哪里？",
    "今天天气不错",
    "今天中午吃什么？",
    "北京",
]
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
batch_tokens = tokenizer(
    input_texts, padding=True, truncation=True, return_tensors="pt"
)
outputs = model(**batch_tokens)
# print(outputs)
# print(outputs.last_hidden_state.shape)
embeddings = outputs.last_hidden_state[:, 0, :]
embeddings = F.normalize(embeddings, p=2, dim=1)
for i in range(1, len(input_texts)):
    print(input_texts[0], input_texts[i], cos_sim(embeddings[0], embeddings[i]))


# print(embeddings.shape)


# print(batch_tokens[0].tokens)
# print(batch_tokens[0].ids)

# print(batch_tokens[3].tokens)
# print(batch_tokens[3].ids)
