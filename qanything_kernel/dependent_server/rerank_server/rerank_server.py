import sys
import os

# 获取当前脚本的绝对路径
current_script_path = os.path.abspath(__file__)

# 将项目根目录添加到sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_script_path))))
sys.path.append(root_dir)


from sanic import Sanic
from sanic.response import json
from qanything_kernel.dependent_server.rerank_server.rerank_onnx_backend import RerankOnnxBackend
from qanything_kernel.dependent_server.rerank_server.rerank_torch_backend import RerankTorchBackend
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
app = Sanic("rerank_server")


@get_time_async
@app.route("/rerank", methods=["POST"])
async def rerank(request):
    data = request.json
    query = data.get('query')
    passages = data.get('passages')
    # onnx_backend: RerankAsyncBackend = request.app.ctx.onnx_backend
    # result_data = await onnx_backend.get_rerank_async(query, passages)

    if "npu" in args.devices:
        npu_backend: RerankTorchBackend = request.app.ctx.npu_backend
        result_data = npu_backend.get_rerank(query, passages)
    else:
        onnx_backend: RerankOnnxBackend = request.app.ctx.onnx_backend
        result_data = onnx_backend.get_rerank(query, passages)
    # print("local rerank query:", query, flush=True)
    # print("local rerank passages number:", len(passages), flush=True)

    return json(result_data)


@get_time_async
@app.route("/general_rerank", methods=["POST"])
async def general_rerank(request):
    data = request.json
    query = data.get('query')
    passages = data.get('documents')
    top_n = data.get('top_n', None)
    return_documents =data.get('return_documents', False)
    try:
        if "npu" in args.devices:
            npu_backend: RerankTorchBackend = request.app.ctx.npu_backend
            result_data = npu_backend.get_rerank(query, passages)
        else:
            onnx_backend: RerankOnnxBackend = request.app.ctx.onnx_backend
            result_data = onnx_backend.get_rerank(query, passages)
        
        results = []
        for i, score in enumerate(result_data):
            results.append({
                "index": i,
                "relevance_score": score
            })
            if return_documents:
                results[-1]["document"] = {"text":passages[i]}
        
        results = sorted(results, key=lambda x: x["relevance_score"], reverse=True)

        if top_n is not None and top_n > 0:
            results = results[:top_n]
        return json({"results": results})
    
    except Exception as e:
        logging.error(f"general rerank error: {e}")
        return json({"error": str(e)})




@app.listener('before_server_start')
async def setup_onnx_backend(app, loop):
    # app.ctx.onnx_backend = RerankAsyncBackend(model_path=LOCAL_RERANK_MODEL_PATH, use_cpu=not args.use_gpu,
    #                                           num_threads=LOCAL_RERANK_THREADS)
    if "npu" in args.devices:
        app.ctx.npu_backend = RerankTorchBackend(device=args.devices)
    else:
        app.ctx.onnx_backend = RerankOnnxBackend(use_cpu=not args.use_gpu)


from qanything_kernel.configs.model_config import RERANK_SERVER_PORT, RERANK_SERVER_WORKERS
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=RERANK_SERVER_PORT, workers=RERANK_SERVER_WORKERS)
