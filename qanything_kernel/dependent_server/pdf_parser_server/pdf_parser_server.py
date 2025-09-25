import sys
import os

# 获取当前脚本的绝对路径
current_script_path = os.path.abspath(__file__)

# 将项目根目录添加到sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_script_path))))
sys.path.append(root_dir)


from qanything_kernel.utils.general_utils import check_internet_connection
if check_internet_connection():
    print("Internet connection is active.")
else:
    print("No internet connection.")
    # 离线模式，不能连接到互联网
    os.environ["SCARF_NO_ANALYTICS"]="true"
    os.environ["DO_NOT_TRACK"]="true"
    # os.environ["TIKTOKEN_CACHE_DIR"] = "./tiktoken_model"


from qanything_kernel.utils.general_utils import safe_get
from sanic import Sanic
from sanic.request import Request
from sanic.response import json
from qanything_kernel.dependent_server.pdf_parser_server.pdf_parser_backend import PdfLoader
from qanything_kernel.configs.model_config import DEFAULT_PARENT_CHUNK_SIZE
import time
import torch
import argparse


# 接收外部参数mode
parser = argparse.ArgumentParser()
parser.add_argument('--use_gpu', action="store_true", help='use gpu or not')
args = parser.parse_args()
print("args:", args)

# 使用系统的日志配置
import logging
logging.getLogger(__name__)


from sanic.worker.manager import WorkerManager
WorkerManager.THRESHOLD = 6000
app = Sanic("pdf_parser_server")


@app.before_server_start
async def init_pdf_parser(app, loop):
    start = time.time()
    app.ctx.pdf_parser = PdfLoader(device=torch.device('cpu') if not args.use_gpu else torch.device('cuda'), zoomin=3)
    end = time.time()
    print(f'init pdf_parser cost {end - start}s', flush=True)


@app.post("/pdfparser")
async def pdf_parser(request: Request):
    filename = safe_get(request, 'filename')
    save_dir = safe_get(request, 'save_dir')

    pdf_parser_: PdfLoader = request.app.ctx.pdf_parser
    markdown_file = pdf_parser_.load_to_markdown(filename, save_dir)

    return json({"markdown_file": markdown_file})

# PDF解析服务
@app.post("/pdfparser_chunk")
async def pdf_parser_chunk(request: Request):
    filename = safe_get(request, 'filename')
    chunk_size = safe_get(request, 'chunk_size', DEFAULT_PARENT_CHUNK_SIZE)
    delimer = safe_get(request, "delimer", "\n。；！？")
    save_dir = safe_get(request, 'save_dir')

    pdf_parser_: PdfLoader = request.app.ctx.pdf_parser
    chunks = pdf_parser_.load_to_chunks(filename, chunk_size, delimer, save_dir)

    return json({"chunks": chunks, "delimer": delimer, "chunk_size": chunk_size})


from qanything_kernel.configs.model_config import PDFPARSER_SERVER_PORT, PDFPARSER_SERVER_WORKERS
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PDFPARSER_SERVER_PORT, workers=PDFPARSER_SERVER_WORKERS)
