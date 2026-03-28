from langchain_ollama import ChatOllama

llm = ChatOllama(model="deepseek-r1:14b")

response = llm.invoke("介绍一下你自己")
print(response.content)