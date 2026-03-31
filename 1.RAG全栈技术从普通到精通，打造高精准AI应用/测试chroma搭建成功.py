# 导入 os，用于读取系统环境变量（例如 CHROMA_HOST、CHROMA_PORT）。
import os
# 导入 chromadb 客户端库，用来和远程 Chroma 服务通信。
import chromadb

# 从环境变量读取 Chroma 服务器地址（例如公网 IP）。
# 如果你已在系统中设置 CHROMA_HOST，这里会自动读取到。
CHROMA_HOST = os.getenv("CHROMA_HOST")
# 从环境变量读取 Chroma 端口，并转为整数类型。
# Chroma 常见端口是 8000，所以环境变量通常设置为 8000。
CHROMA_PORT = int(os.getenv("CHROMA_PORT"))

# 用 try 包裹主流程，目的是连接失败时不让程序直接崩溃，而是输出可读提示。
try:
    # 创建 Chroma 的 HTTP 客户端对象。
    # 这一步会准备好后续所有 API 请求使用的连接参数（host、port）。
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

    # 调用 heartbeat() 做最基础的“服务活性”检查。
    # 如果服务在线，通常会返回一个值（如时间戳或状态信息）。
    heartbeat = client.heartbeat()
    # 打印连接成功提示，并把当前连接的目标地址显示出来，方便你核对。
    print(f"✅ Chroma 连通成功！地址: {CHROMA_HOST}:{CHROMA_PORT}")
    # 打印心跳返回值，证明不是“假连接”。
    print("✅ Chroma 心跳:", heartbeat)

    # 调用 list_collections() 进一步验证读接口可用。
    # 这比 heartbeat 更进一步，证明数据库 API 能正常工作。
    collections = client.list_collections()
    # 打印当前集合列表，帮助你确认服务里是否已有业务集合。
    print("✅ 集合接口可用，当前集合列表:", collections)
# 如果 try 里任何一步报错（网络不通、端口错、服务没启动等），会进入 except。
except Exception as e:
    # 打印连接失败提示和目标地址，先定位是不是连错地址。
    print(f"❌ Chroma 连通失败！地址: {CHROMA_HOST}:{CHROMA_PORT}")
    # 打印原始异常，便于你看到具体错误（超时、拒绝连接、502 等）。
    print("❌ 错误信息:", e)
    # 打印固定排查清单，按顺序执行即可快速定位问题。
    print("排查建议：")
    # 第 1 步：检查服务器端 Chroma 服务是否处于运行状态。
    print("1) 确认服务器 Chroma 服务是否运行：systemctl status chroma --no-pager")
    # 第 2 步：检查服务器 8000 端口是否真的在监听。
    print("2) 确认服务器 8000 端口是否监听：ss -lntp | grep 8000")
    # 第 3 步：检查云安全组或系统防火墙有没有放行 8000。
    print("3) 确认云安全组/防火墙已放行 8000 端口")
