import os
from pymilvus import connections, utility

MILVUS_HOST = os.getenv("MILVUS_HOST")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")

connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
print("连接成功:", utility.get_server_version())