import sys
import os

# 获取当前脚本的绝对路径
current_script_path = os.path.abspath(__file__)

# 将项目根目录添加到sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_script_path))))

sys.path.append(root_dir)
print(root_dir)

from sanic import Sanic
from sanic.response import json
from qanything_kernel.utils.general_utils import get_time_async
from qanything_kernel.dependent_server.chunk_server.chunk_backend import ChunkBackend
from qanything_kernel.configs.model_config import LLM_URL, LLM_API_KEY, LLM_MODEL_NAME, C
import argparse

# 接收外部参数mode
parser = argparse.ArgumentParser()
parser.add_argument('--workers', type=int, default=2, help='workers')
args = parser.parse_args()
print("args:", args)

app = Sanic("chunk_server")


@get_time_async
@app.route("/chunk", methods=["POST"])
async def rerank(request):
    data = request.json
    original_text = data.get('text')
    laungege = data.get('language', 'ch')
    chunk_length = data.get('chunk_length', 400)

    onnx_backend: ChunkBackend = request.app.ctx.onnx_backend
    result_data = onnx_backend.meta_chunking(original_text, laungege, chunk_length) #返回的格式为List[str]
    
    return json({"chunk":result_data})


@app.listener('before_server_start')
async def setup_chunk_backend(app, loop):
    app.ctx.onnx_backend = ChunkBackend(LLM_URL, LLM_API_KEY, LLM_MODEL_NAME)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002, workers=args.workers)
