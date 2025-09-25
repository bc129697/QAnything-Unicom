import sys
import os
import platform

# 获取当前脚本的绝对路径
current_script_path = os.path.abspath(__file__)

# 将项目根目录添加到sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_script_path))))
sys.path.append(root_dir)


from sanic import Sanic
from sanic.response import json
from qanything_kernel.dependent_server.embedding_server.embedding_onnx_backend import EmbeddingOnnxBackend
from qanything_kernel.dependent_server.embedding_server.embedding_torch_backend import EmbeddingTorchBackend
from qanything_kernel.configs.model_config import LOCAL_EMBED_MAX_LENGTH
from qanything_kernel.utils.general_utils import get_time_async
import argparse

# 接收外部参数mode
parser = argparse.ArgumentParser()
parser.add_argument('--use_gpu', action="store_true", help='use gpu or not')
parser.add_argument('--devices', type=str, default="cpu", help='use devices')
args = parser.parse_args()
print("args:", args)

# 使用系统的日志配置
import logging
logging.getLogger(__name__)


from sanic.worker.manager import WorkerManager
WorkerManager.THRESHOLD = 6000
app = Sanic("embedding_server")



@get_time_async
@app.route("/embedding", methods=["POST"])
async def embedding(request):
    data = request.json
    texts = data.get('texts')

    if "npu" in args.devices:
        npu_backend: EmbeddingTorchBackend = request.app.ctx.npu_backend
        result_data = npu_backend.get_embedding(texts, LOCAL_EMBED_MAX_LENGTH)
    else:
        onnx_backend: EmbeddingOnnxBackend = request.app.ctx.onnx_backend
        result_data = onnx_backend.predict(texts)

    return json(result_data)



@get_time_async
@app.route("/general_embedding", methods=["POST"])
async def general_embedding(request):
    data = request.json
    texts = data.get('input')
    encoding_format = data.get('encoding_format', "float")
    if encoding_format not in ["float", "base64"]:
        return json({"error": "encoding_format must be float or base64"})
    

    if "npu" in args.devices:
        npu_backend: EmbeddingTorchBackend = request.app.ctx.npu_backend
        result_data = npu_backend.get_embedding(texts, LOCAL_EMBED_MAX_LENGTH)
    else:
        onnx_backend: EmbeddingOnnxBackend = request.app.ctx.onnx_backend
        result_data = onnx_backend.predict(texts)

    if encoding_format == "base64":
        import struct
        import base64

        def float_list_to_base64(float_list):
            # 将每个浮点数打包为二进制格式（小端模式）
            byte_data = b''.join(struct.pack('<f', num) for num in float_list)
            
            # 将字节数据编码为 Base64 字符串
            base64_string = base64.b64encode(byte_data).decode('utf-8')
            
            return base64_string
        result_data = [float_list_to_base64(item) for item in result_data]
    
    data = []
    for i, emb_data in enumerate(result_data):
        data.append({
            "index": i,
            "object": "embedding",
            "embedding": emb_data
        })
    result_data = {
        "data": data,
    }
    return json(result_data)


@app.listener('before_server_start')
async def setup_onnx_backend(app, loop):
    if "npu" in args.devices:
        app.ctx.npu_backend = EmbeddingTorchBackend(device=args.devices)
    else:
        app.ctx.onnx_backend = EmbeddingOnnxBackend(use_cpu=not args.use_gpu)


from qanything_kernel.configs.model_config import EMBEDDING_SERVER_PORT, EMBEDDING_SERVER_WORKERS
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=EMBEDDING_SERVER_PORT, workers=EMBEDDING_SERVER_WORKERS)
