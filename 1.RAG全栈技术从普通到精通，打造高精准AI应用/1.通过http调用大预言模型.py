# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "你用中文回答我"},
    ],
    stream=True,#开启流式输出
    temperature=1.5 #采样温度
)
for chunk in response:
    print(chunk.choices[0].delta.content, end="", flush=True)