# 导入 os，用于读取环境变量（MILVUS_HOST、MILVUS_PORT）。
import os
# 从 pymilvus 导入连接模块和工具模块。
# - connections: 用于建立与 Milvus 的连接
# - utility: 提供服务端版本等工具方法
from pymilvus import connections, utility

# 读取 Milvus 主机地址。
# 优先用环境变量 MILVUS_HOST；如果没配，默认用你当前服务器公网 IP。
MILVUS_HOST = os.getenv("MILVUS_HOST", "120.78.121.40")
# 读取 Milvus 端口。
# Milvus 默认 gRPC 端口一般是 19530。
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")

# 用 try 包裹连接与验证流程，避免报错时直接中断。
try:
    # 建立到 Milvus 的连接。
    # alias="default" 表示给这条连接起名为 default，后续 API 会复用它。
    connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)

    # 获取 Milvus 服务端版本，用于确认“连接不仅建立了，而且服务正常响应”。
    version = utility.get_server_version()
    # 打印连接成功信息和目标地址，方便核对连接目标。
    print(f"✅ Milvus 连通成功！地址: {MILVUS_HOST}:{MILVUS_PORT}")
    # 打印版本号（例如 v2.4.9），作为连通证据。
    print("✅ Milvus 版本:", version)
# 连接失败、端口不通、服务未启动等异常都会进入这里。
except Exception as e:
    # 打印失败信息和连接地址，先排查是否 host/port 写错。
    print(f"❌ Milvus 连通失败！地址: {MILVUS_HOST}:{MILVUS_PORT}")
    # 打印具体报错文本，便于定位是超时、拒绝连接还是认证问题。
    print("❌ 错误信息:", e)
    # 打印排查步骤，按顺序执行可快速定位问题。
    print("排查建议：")
    # 第 1 步：确认服务器 Milvus 容器组是否都在运行。
    print("1) 确认服务器 Milvus 服务是否运行：cd ~/milvus-standalone && docker compose ps")
    # 第 2 步：确认 19530 端口是否监听（Milvus 核心端口）。
    print("2) 确认服务器 19530 端口是否监听：ss -lntp | grep 19530")
    # 第 3 步：确认云厂商安全组和防火墙放行了 19530。
    print("3) 确认云安全组/防火墙已放行 19530 端口")