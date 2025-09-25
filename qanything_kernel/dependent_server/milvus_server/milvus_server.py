import sys
import os
# 获取当前脚本的绝对路径
current_script_path = os.path.abspath(__file__)

# 将项目根目录添加到sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_script_path))))
sys.path.append(root_dir)


from sanic.worker.manager import WorkerManager
from sanic import Sanic
from sanic_ext import Extend
import time
import argparse



WorkerManager.THRESHOLD = 6000
app = Sanic("MilvusService")
app.config.CORS_ORIGINS = "*"
Extend(app)

# 设置请求体最大为 128MB
app.config.REQUEST_MAX_SIZE = 128 * 1024 * 1024


from milvus_handle import *
# 相关接口
# app.add_route(document, "/api/docs", methods=['GET'])
app.add_route(create_collection, "/api/milvus/create_collection", methods=['POST'])  # tags=["创建一个集合"]
app.add_route(delete_collection, "/api/milvus/delete_collection", methods=['POST'])  # tags=["删除一个集合"]
app.add_route(get_collection_info, "/api/milvus/get_collection_info", methods=['POST'])    # tags=["获取集合信息"]
app.add_route(list_collections, "/api/milvus/list_collections", methods=['GET','POST'])    # tags=["获取所有集合"]
app.add_route(set_collection_index, "/api/milvus/set_collection_index", methods=['POST'])  # tags=["在实体上生成索引"]
app.add_route(insert_vectors, "/api/milvus/insert_vectors", methods=['POST'])  # tags=["在集合中插入向量"]
app.add_route(delete_vectors, "/api/milvus/delete_vectors", methods=['POST'])  # tags=["在集合中删除向量"]
app.add_route(search_vectors, "/api/milvus/search_vectors", methods=['POST'])  # tags=["在集合中搜索向量"]
app.add_route(expr_search, "/api/milvus/expr_search", methods=['POST'])        # tags=["在集合中查询向量"]
app.add_route(clear_deleted_vectors, "/api/milvus/clear_deleted_vectors", methods=['POST'])  # tags=["清除删除的向量"]



from qanything_kernel.configs.model_config import MILVUS_SERVER_PORT, MILVUS_SERVER_WORKERS
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=MILVUS_SERVER_PORT, workers=MILVUS_SERVER_WORKERS, access_log=False)

