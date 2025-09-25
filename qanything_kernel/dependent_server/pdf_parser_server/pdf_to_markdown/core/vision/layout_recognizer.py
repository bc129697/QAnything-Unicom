import os
import re
import cv2
from collections import Counter
from copy import deepcopy
import numpy as np
from qanything_kernel.dependent_server.pdf_parser_server.pdf_to_markdown.core.vision import Recognizer
from qanything_kernel.configs.model_config import PDF_MODEL_PATH
from tqdm import tqdm

import logging
logger = logging.getLogger(__name__)

class LayoutRecognizer(Recognizer):
    labels = ['Text', 'Title', 'Figure', 'Equation', 'Table', 
        'Caption', 'Header', 'Footer', 'BibInfo', 'Reference',
        'Content', 'Code', 'Other', 'Item', 'Author']

    def __init__(self, domain, device):
        model_dir = os.path.join(
                    PDF_MODEL_PATH,
                    "checkpoints/layout")
        super().__init__(self.labels, domain, model_dir, device)
        self.garbage_layouts = ["footer", "header", "reference"]

    def __call__(self, image_list, ocr_res, scale_factor=3, thr=0.4, batch_size=16, drop=True):
        def __is_garbage(b):
            patt = ['\* Corresponding Author', '\*Corresponding to']
            return any([re.search(p, b["text"]) for p in patt])

        layouts = super().__call__(image_list, thr, batch_size)
        # save_results(image_list, layouts, self.labels, output_dir='output/', threshold=0.7)
        logging.info(f"Layout recognition done:\n{layouts}")
        assert len(image_list) == len(ocr_res)
        # Tag layout type
        boxes = []
        assert len(image_list) == len(layouts)
        garbages = {}
        page_layout = []
        for pn, lts in tqdm(enumerate(layouts)):
            bxs = ocr_res[pn]
            lts = [{"type": b["type"],
                    "score": float(b["score"]),
                    "x0": b["bbox"][0] / scale_factor, "x1": b["bbox"][2] / scale_factor,
                    "top": b["bbox"][1] / scale_factor, "bottom": b["bbox"][-1] / scale_factor,
                    "page_number": pn,
                    } for b in lts]
            lts = self.sort_Y_firstly(lts, np.mean(
                [l["bottom"] - l["top"] for l in lts]) / 2)
            lts = self.layouts_cleanup(bxs, lts)
            if pn == 0:
                try:
                    idx = [b['x0'] for b in lts].index(min([b['x0'] for b in lts if b['type'] == 'text']))
                    if (lts[idx]['bottom']-lts[idx]['top'])/(lts[idx]['x1']-lts[idx]['x0']) > 15:
                        lts.pop(idx)
                except:
                    lts = lts
            page_layout.append(lts)

            # Tag layout type, layouts are ready
            def findLayout(ty):
                nonlocal bxs, lts, self
                lts_ = [lt for lt in lts if lt["type"] == ty]
                i = 0
                while i < len(bxs):
                    if bxs[i].get("layout_type"):
                        i += 1
                        continue
                    if __is_garbage(bxs[i]):
                        bxs.pop(i)
                        continue

                    ii = self.find_overlapped_with_threashold(bxs[i], lts_,
                                                              thr=0.4)

                    if ii is None:  # belong to nothing
                        bxs[i]["layout_type"] = ""
                        i += 1
                        continue
                    lts_[ii]["visited"] = True
                    keep_feats = [
                        lts_[
                            ii]["type"] == "footer" and bxs[i]["bottom"] < image_list[pn].size[1] * 0.9 / scale_factor,
                        lts_[
                            ii]["type"] == "header" and bxs[i]["top"] > image_list[pn].size[1] * 0.1 / scale_factor,
                    ]
                    if drop and lts_[
                            ii]["type"] in self.garbage_layouts and not any(keep_feats):
                        if lts_[ii]["type"] not in garbages:
                            garbages[lts_[ii]["type"]] = []
                        garbages[lts_[ii]["type"]].append(bxs[i]["text"])
                        bxs.pop(i)
                        continue

                    bxs[i]["layoutno"] = f"{ty}-{ii}"
                    bxs[i]["layout_type"] = lts_[ii]["type"] if lts_[
                        ii]["type"] != "equation" else "figure"
                    i += 1

            for ty in ["footer", "header", "reference", "caption", "author",
                       "title", "table", "text", "figure", "equation", "content"]:
                findLayout(ty)
            # add box to figure layouts which has not text box
            for i, lt in enumerate(
                    [lt for lt in lts if lt["type"] in ["figure", "equation", "table"]]):
                if lt.get("visited"):
                    continue
                lt = deepcopy(lt)
                del lt["type"]
                lt["text"] = ""
                lt["layout_type"] = "figure"
                lt["layoutno"] = f"figure-{i}"
                lt["page_number"] = pn + 1
                bxs.append(lt)
            
            lts_ = [lt for lt in lts if lt["type"] == 'item']
            for i, bx in enumerate(bxs):
                if bx["layout_type"] != 'reference': continue
                ii = self.find_overlapped_with_threashold(bx, lts_,
                                                              thr=0.4)
                if ii is None:
                    continue
                layoutno = bx["layoutno"]
                bxs[i]["layoutno"] = f"{layoutno}-item-{ii}"

            boxes.extend(bxs)

        ocr_res = boxes

        garbag_set = set()
        for k in garbages.keys():
            garbages[k] = Counter(garbages[k])
            for g, c in garbages[k].items():
                if c > 1:
                    garbag_set.add(g)

        ocr_res = [b for b in ocr_res if b["text"].strip() not in garbag_set]
        return ocr_res, page_layout

    def layouts(self, image_list, thr):
        layouts = super().__call__(image_list, thr)
        return layouts


class LayoutRecognizer4YOLOv10(LayoutRecognizer):
    labels = [
        "title",
        "Text",
        "Reference",
        "Figure",
        "caption", # "Figure caption",
        "Table",
        "caption", #"Table caption",
        "caption", #"Table caption",
        "Equation",
        "caption", #"Figure caption",
    ]

    def __init__(self, domain, device):
        domain = "layout"
        super().__init__(domain, device)
        self.auto = False
        self.scaleFill = False
        self.scaleup = True
        self.stride = 32
        self.center = True

    def preprocess(self, image_list):
        inputs = []
        new_shape = self.input_shape # height, width
        for img in image_list:
            shape = img.shape[:2]# current shape [height, width]
            # Scale ratio (new / old)
            r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
            # Compute padding
            new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
            dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
            dw /= 2  # divide padding into 2 sides
            dh /= 2
            ww, hh = new_unpad
            img = np.array(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).astype(np.float32)
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
            top, bottom = int(round(dh - 0.1)) if self.center else 0, int(round(dh + 0.1))
            left, right = int(round(dw - 0.1)) if self.center else 0, int(round(dw + 0.1))
            img = cv2.copyMakeBorder(
                img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114)
            )  # add border
            img /= 255.0
            img = img.transpose(2, 0, 1)
            img = img[np.newaxis, :, :, :].astype(np.float32)
            inputs.append({self.input_names[0]: img, "scale_factor": [shape[1]/ww, shape[0]/hh, dw, dh]})

        return inputs

    def postprocess(self, boxes, inputs, thr):
        thr = 0.08
        boxes = np.squeeze(boxes)
        scores = boxes[:, 4]
        boxes = boxes[scores > thr, :]
        scores = scores[scores > thr]
        if len(boxes) == 0:
            return []
        class_ids = boxes[:, -1].astype(int)
        boxes = boxes[:, :4]
        boxes[:, 0] -= inputs["scale_factor"][2]
        boxes[:, 2] -= inputs["scale_factor"][2]
        boxes[:, 1] -= inputs["scale_factor"][3]
        boxes[:, 3] -= inputs["scale_factor"][3]
        input_shape = np.array([inputs["scale_factor"][0], inputs["scale_factor"][1], inputs["scale_factor"][0],
                                inputs["scale_factor"][1]])
        boxes = np.multiply(boxes, input_shape, dtype=np.float32)

        unique_class_ids = np.unique(class_ids)
        indices = []
        def nms(bboxes, scores, iou_thresh):
            import numpy as np
            x1 = bboxes[:, 0]
            y1 = bboxes[:, 1]
            x2 = bboxes[:, 2]
            y2 = bboxes[:, 3]
            areas = (y2 - y1) * (x2 - x1)

            indices = []
            index = scores.argsort()[::-1]
            while index.size > 0:
                i = index[0]
                indices.append(i)
                x11 = np.maximum(x1[i], x1[index[1:]])
                y11 = np.maximum(y1[i], y1[index[1:]])
                x22 = np.minimum(x2[i], x2[index[1:]])
                y22 = np.minimum(y2[i], y2[index[1:]])
                w = np.maximum(0, x22 - x11 + 1)
                h = np.maximum(0, y22 - y11 + 1)
                overlaps = w * h
                ious = overlaps / (areas[i] + areas[index[1:]] - overlaps)
                idx = np.where(ious <= iou_thresh)[0]
                index = index[idx + 1]
            return indices
        
        for class_id in unique_class_ids:
            class_indices = np.where(class_ids == class_id)[0]
            class_boxes = boxes[class_indices, :]
            class_scores = scores[class_indices]
            class_keep_boxes = nms(class_boxes, class_scores, 0.45)
            indices.extend(class_indices[class_keep_boxes])

        return [{
            "type": self.label_list[class_ids[i]].lower(),
            "bbox": [float(t) for t in boxes[i].tolist()],
            "score": float(scores[i])
        } for i in indices]

