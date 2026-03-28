"""



本文件演示：LangChain Community 中 PyPDFLoader 按页懒加载 PDF，得到 Document 列表。



PyPDFLoader：基于 pypdf 等后端，将 PDF 切成多页；lazy_load() 返回迭代器，

按需逐页读取（适合大文件）。每页一个 Document，含 page_content 与 metadata（如页码）。



路径用 Path(__file__).parent / "demo.pdf"：PDF 与脚本同目录，且不依赖终端当前工作目录。



"""

# ---------------------------------------------------------------------------

# import（导入）：从标准库或第三方包引入符号。

# ---------------------------------------------------------------------------

from pathlib import Path


# Path：面向对象的路径；__file__ 为当前脚本路径；parent 为所在目录；/ 拼接子路径。


from langchain_community.document_loaders import PyPDFLoader


# PyPDFLoader：langchain_community 文档加载器；构造时传入 PDF 文件路径字符串。


# ---------------------------------------------------------------------------

# 解析路径并创建 Loader：str(pdf_path) 满足 PyPDFLoader 对字符串路径的要求。

# ---------------------------------------------------------------------------

pdf_path = Path(__file__).resolve().parent / "demo.pdf"


loader = PyPDFLoader(str(pdf_path))


# ---------------------------------------------------------------------------

# lazy_load：同步惰性迭代，每步产出一个 Document；比一次性 load() 更省内存。

#

# Document：LangChain 文档单元；page_content 为文本，metadata 常含 source、page 等。

# ---------------------------------------------------------------------------

pages = []


for page in loader.lazy_load():
    pages.append(page)


# 按页打印正文；索引需小于 len(pages)，页数因 PDF 而异。

print(pages[1].page_content)
