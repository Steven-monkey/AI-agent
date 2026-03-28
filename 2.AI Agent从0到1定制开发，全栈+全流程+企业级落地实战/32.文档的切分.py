from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter


pdf_path = Path(__file__).resolve().parent / "demo.pdf"
loader = PyPDFLoader(str(pdf_path))
pages = []
for page in loader.lazy_load():
    pages.append(page)

text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=50, chunk_overlap=20, encoding_name="cl100k_base"
)
texts = text_splitter.split_text(pages[0].page_content)
print(texts)
docs = text_splitter.create_documents([pages[1].page_content, pages[2].page_content])
print(docs)
