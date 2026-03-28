# 高速公路机电系统知识问答助手

基于 **LangChain**（RAG：检索 + 大模型）与 **Gradio** Web 界面的本地知识问答示例。知识内容来自本目录下的 `knowledge` 文件夹中的 Markdown / 文本文件。

---

## 环境要求

- Python 3.10+（推荐 3.12）
- 建议使用虚拟环境（如 `venv`）

**对话模型（二选一）：**

1. **DeepSeek（云端 API）**：需网络，并配置 `DEEPSEEK_API_KEY`。
2. **Ollama（本地）**：本机已安装 [Ollama](https://ollama.com/) 且已拉取至少一个对话模型；未配置 DeepSeek 时使用。

**向量嵌入（本地）：** 首次运行会从 Hugging Face 下载句向量模型（可配置模型名），需能访问外网或已缓存模型。

---

## 安装依赖

在项目根目录 `高速公路机电系统知识问答助手` 下执行：

```bash
pip install -r requirements.txt
```

若你已在仓库根目录的 `.venv` 中安装过相关包，也可直接激活该虚拟环境后运行主程序。

---

## 启动方式

```bash
cd 高速公路机电系统知识问答助手
python main.py
```

启动后在浏览器打开终端中显示的地址，默认为：

http://127.0.0.1:7860

监听地址为 `0.0.0.0`，同一局域网内其他设备也可访问（注意防火墙与安全策略）。

---

## 环境变量说明

| 变量 | 说明 |
|------|------|
| `DEEPSEEK_API_KEY` | 若设置，优先使用 DeepSeek 作为对话模型。 |
| `DEEPSEEK_BASE_URL` | 可选，默认 `https://api.deepseek.com/v1`。 |
| `OLLAMA_CHAT_MODEL` | 未使用 DeepSeek 时，Ollama 对话模型名，默认 `deepseek-r1:14b`（请与 `ollama list` 中名称一致）。 |
| `OLLAMA_BASE_URL` | Ollama 服务地址，默认 `http://127.0.0.1:11434`。 |
| `HF_EMBED_MODEL` | Sentence-Transformers 嵌入模型名；不设则使用内置默认（首次会下载）。 |
| `GRADIO_SERVER_PORT` | Gradio 端口，默认 `7860`。 |

**Windows PowerShell 示例（仅当前会话生效）：**

```powershell
$env:DEEPSEEK_API_KEY = "你的密钥"
python main.py
```

**Linux / macOS 示例：**

```bash
export DEEPSEEK_API_KEY="你的密钥"
python main.py
```

---

## 界面说明

- **左侧**：多轮对话区，输入问题后点击「发送」或按回车。
- **右侧**：本次回答所依据的「检索到的参考片段」，便于核对是否来自知识库。
- 若程序启动时向量库或模型初始化失败，页顶会显示错误信息，请根据提示排查后重启。

---

## 如何扩充知识

1. 在 `knowledge` 目录下新增或编辑 `.md`、`.txt`、`.markdown` 文件（支持子目录）。
2. **重启** `main.py`（向量库建在内存中，重启后重新索引）。

建议按主题分文件书写，内容尽量条理清晰，便于检索命中。

---

## 常见问题

**1. 首次启动很慢**  
句向量模型首次需下载，体积较大，请耐心等待；下载完成后会缓存在本机。

**2. 使用 Ollama 时提示连接失败**  
确认已执行 `ollama serve`（或 Ollama 桌面端已运行），且 `OLLAMA_BASE_URL` 与端口正确。

**3. 回答与资料不符或胡编**  
检查右侧参考片段是否包含相关信息；可适当增加 `knowledge` 中的原文描述，或调整问题表述。本示例为教学用 RAG，生产环境需进一步调参与评测。

**4. Windows 控制台中文乱码**  
不影响浏览器界面。若需在终端查看 UTF-8 输出，可在运行前将控制台编码设为 UTF-8（例如 `chcp 65001`）。

---

## 项目结构（简要）

```
高速公路机电系统知识问答助手/
├── main.py           # 入口：RAG 流程 + Gradio 界面
├── knowledge/        # 知识库文本（可增删改）
├── requirements.txt  # Python 依赖
└── README.md         # 本说明
```
