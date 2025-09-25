import sys
import os

# 获取当前脚本的绝对路径
current_script_path = os.path.abspath(__file__)

# 将项目根目录添加到sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_script_path))))
sys.path.append(root_dir)


from qanything_kernel.configs.model_config import OCR_MODEL_PATH, OCR_SERVER_PORT, OCR_SERVER_WORKERS
from ocr import OCRQAnything

import numpy as np
import onnxruntime as ort
from sanic import Sanic, response
from sanic.request import Request
from sanic.response import json
from sanic.exceptions import BadRequest
from sanic.worker.manager import WorkerManager
WorkerManager.THRESHOLD = 6000
app = Sanic("OCRService")
import cv2
import copy
import time
import base64
import argparse
import traceback




# 接收外部参数mode
parser = argparse.ArgumentParser()
parser.add_argument('--use_gpu', action="store_true", help='use gpu or not')
args = parser.parse_args()
print("args:", args)


# 使用系统的日志配置
import logging
import qanything_kernel.utils.custom_log as custom_log
logging.getLogger(__name__)



def safe_get(req: Request, attr: str, default=None):
    try:
        if attr in req.form:
            return req.form.getlist(attr)[0]
        if attr in req.args:
            return req.args[attr]
        if attr in req.json:
            return req.json[attr]
    except BadRequest:
        logging.warning(f"missing {attr} in request")
    except Exception as e:
        logging.warning(f"get {attr} from request failed:")
        logging.warning(traceback.format_exc())
    return default


@app.before_server_start
async def setup_ocr(app, loop):
    if args.use_gpu:
        app.ctx.ocr = OCRQAnything(model_dir=OCR_MODEL_PATH, device='cuda')
    else:
        app.ctx.ocr = OCRQAnything(model_dir=OCR_MODEL_PATH, device='cpu')

@app.post("/ocr")
async def ocr_api(request: Request):
    img64 = safe_get(request, 'img64')

    if img64 is None:
        return json({"error": "No image data provided"}, status=400)

    try:
        img_data = base64.b64decode(img64)
        img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
    except Exception as e:
        return json({"error": "Invalid image data"}, status=400)

    if img is None:
        return json({"error": "Invalid image file"}, status=400)

    start = time.perf_counter()
    result = app.ctx.ocr(img)
    logging.info(f'ocr run time: {time.perf_counter() - start}')
    return json({"result": result})


@app.post("/ocr_detect")
async def ocr_detect(request: Request):
    img64 = safe_get(request, 'img64')

    if img64 is None:
        return json({"error": "No image data provided"}, status=400)

    try:
        img_data = base64.b64decode(img64)
        img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
    except Exception as e:
        return json({"error": "Invalid image data"}, status=400)

    if img is None:
        return json({"error": "Invalid image file"}, status=400)

    start = time.perf_counter()
    result = app.ctx.ocr.detect(img)
    result = list(result)
    result_bbox = []
    for i in range(len(result)):
        result_tmp = result[i][0].tolist()
        result_bbox.append(result_tmp)
    logging.info(f'ocr detect run time: {time.perf_counter() - start}')
    result_bbox_text = [(result_bbox[i],"" ) for i in range(len(result_bbox))]
    return json({"result": result_bbox_text})


@app.post("/ocr_recognizer")
async def ocr_recognizer(request: Request):
    img64 = safe_get(request, 'img64')
    box = safe_get(request, 'bbox')
    box_array = np.array(box, dtype=np.float32)

    if img64 is None:
        return json({"error": "No image data provided"}, status=400)

    try:
        img_data = base64.b64decode(img64)
        img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
    except Exception as e:
        return json({"error": "Invalid image data"}, status=400)

    if img is None:
        return json({"error": "Invalid image file"}, status=400)

    start = time.perf_counter()
    result_text = app.ctx.ocr.recognize(img, box_array)
    logging.info(f'ocr recognize run time: {time.perf_counter() - start}')
    return json({"result": result_text})



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=OCR_SERVER_PORT, workers=OCR_SERVER_WORKERS)
