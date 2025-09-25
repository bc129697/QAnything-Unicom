import os
import sys
import json
import base64
import requests
import pdfplumber
import io
from io import BytesIO
from tqdm import tqdm
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def get_ocr_result_sync(image_data, api="ocr"):
    try:
        response = requests.post(f"http://localhost:7001/" + api, json=image_data, timeout=120)
        response.raise_for_status()  # 如果请求返回了错误状态码，将会抛出异常
        ocr_res = response.text
        ocr_res = json.loads(ocr_res)
        return ocr_res['result']
    except Exception as e:
        print(f"ocr error: {e}")
        return None


if __name__ == "__main__":
    image_path = sys.argv[1] if len(sys.argv) > 1 else "ocr_test.png"
    
    if not os.path.exists(image_path):
        print("Image file not found")
        sys.exit(1)
    
    fnm = image_path

    if fnm.endswith('.pdf'):
        zoomin = 3
        pdf = pdfplumber.open(fnm) if isinstance(
                    fnm, str) else pdfplumber.open(BytesIO(fnm))
        page_images = [p.to_image(resolution=72 * zoomin).annotated for i, p in
                                    enumerate(pdf.pages[0:3])]
        
        
        for i, img in tqdm(enumerate(page_images)):
            # 将PIL.Image.Image对象转换为字节流
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')  # 你可以根据需要选择不同的格式，如JPEG、PNG等
            img_byte_arr = img_byte_arr.getvalue()
            # img = img.tobytes()
            # print(type(img))
            # print(img)
            img_data = {
                "img64": base64.b64encode(img_byte_arr).decode("utf-8"),
            }
            

            result = get_ocr_result_sync(img_data, api="ocr_detect")
            print("ocr_detect:", result)
            

            draw = ImageDraw.Draw(img)  # 创建ImageDraw对象
            for bbox, _ in result:
                
                # bbox为4个点，每个点为(x, y)格式，遍历，将每相邻两个点连成线
                if (abs(bbox[0][1]-bbox[1][1])/abs(bbox[1][0]-bbox[0][0])>0.05):
                    continue
                
                img_data["bbox"] = bbox
                result = get_ocr_result_sync(img_data, api="ocr_recognizer")
                print("ocr bbox:", result)

                for i in range(4):
                    x1, y1 = bbox[i]
                    x2, y2 = bbox[(i+1)%4]
                    draw.line([(x1, y1), (x2, y2)], fill='red', width=3)
                    draw.text((bbox[0][0], bbox[0][1]), result, fill='red', ) #, font=ImageFont.truetype("arial.ttf", 20), fill='red')
                
            # 显示图像
            img.show()

            # 暂停程序，等待用户输入
            input("Press Enter to continue...")
        
    elif fnm.endswith('.png') or fnm.endswith('.jpg'):
        # 读取图片
        img_np = open(image_path, 'rb').read()
        print(type(img_np))

        img_data = {
            "img64": base64.b64encode(img_np).decode("utf-8"),
        }
        
        result = get_ocr_result_sync(img_data, api="ocr")
        print("ocr detect:", result)

        result = get_ocr_result_sync(img_data, api="ocr_detect")
        print("ocr_detect:", result)

        for bbox, _ in result:
            img_data["bbox"] = bbox
            result = get_ocr_result_sync(img_data, api="ocr_recognizer")
            print("ocr bbox:", result)
    else:
        print("Unsupported file format")
        sys.exit(1)

