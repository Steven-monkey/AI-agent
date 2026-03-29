from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters.character import CharacterTextSplitter

# 脚本所在目录：相对路径相对这里解析，不依赖终端当前工作目录
_SCRIPT_DIR = Path(__file__).resolve().parent


class ChatDoc:
    def __init__(self, file_path):
        self.file_path = file_path

    def getFile(self):
        if self.file_path.endswith(".docx"):
            loader = Docx2txtLoader(self.file_path)
            text = loader.load()
            return text
        elif self.file_path.endswith(".pdf"):
            loader = PyPDFLoader(self.file_path)
            text = loader.load()
            return text
        elif self.file_path.endswith(".txt"):
            loader = TextLoader(self.file_path)
            text = loader.load()
            return text

    def splitSentence(self):
        full_text = self.getFile()
        if full_text != None:
            text_split = CharacterTextSplitter(chunk_size=150, chunk_overlap=20)
            texts = text_split.split_documents(full_text)
            self.splitText = texts


chat_doc = ChatDoc(str(_SCRIPT_DIR / "demo.docx"))
chat_doc.splitSentence()
print(chat_doc.splitText)