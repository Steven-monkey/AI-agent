"""



本文件演示：LangChain Community 中 WebBaseLoader 抓取网页 HTML，解析为 Document 列表。



WebBaseLoader：用 requests 拉取 URL，再用 BeautifulSoup 等提取正文；web_path 可为

单个 URL 字符串或 URL 列表。lazy_load() 惰性迭代，每个 URL 对应若干 Document（视页面结构而定）。



依赖：需安装 requests、beautifulsoup4。若终端提示 USER_AGENT 未设置，可在运行前设置环境变量

USER_AGENT，减少被站点拒绝的概率。



"""

# ---------------------------------------------------------------------------

# import（导入）：从第三方包引入符号。

# ---------------------------------------------------------------------------

from langchain_community.document_loaders import WebBaseLoader


# WebBaseLoader：面向公开网页的加载器；适合静态或简单动态页面，复杂反爬需自行扩展 Headers 等。


# ---------------------------------------------------------------------------

# web_path：要抓取的网址列表；单页也可写成 [url]。Loader 内部会请求并解析 HTML。

# ---------------------------------------------------------------------------

page_url = "https://www.x6d.com/"


loader = WebBaseLoader(web_path=[page_url])


# ---------------------------------------------------------------------------

# lazy_load：同步惰性迭代，逐条产出 Document；page_content 多为抽取后的文本，metadata 常含 source 等。

# ---------------------------------------------------------------------------

docs = []


for doc in loader.lazy_load():
    docs.append(doc)


print(len(docs))


print(docs[0].page_content)
