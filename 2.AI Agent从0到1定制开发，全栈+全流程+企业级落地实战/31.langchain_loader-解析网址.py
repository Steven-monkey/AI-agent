import bs4
from langchain_community.document_loaders import WebBaseLoader

page_url="https://www.x6d.com/"
loader = WebBaseLoader(web_path=[page_url])
docs=[]
for doc in loader.lazy_load():
    docs.append(doc)

print(len(docs))
print(docs[0].page_content)