import json
import re
from qanything_kernel.dependent_server.pdf_parser_server.pdf_to_markdown.core.parser import PdfParser
from qanything_kernel.dependent_server.pdf_parser_server.pdf_to_markdown.convert2markdown import json2markdown
from qanything_kernel.utils.model_utils import num_tokens_embed
from timeit import default_timer as timer
import numpy as np
import os


import logging
logger = logging.getLogger(__name__)

class PdfLoader(PdfParser):
    def __init__(self, device, binary=None, from_page=0, to_page=10000, zoomin=3, callback=None):
        super().__init__(device=device)
        self.binary = binary
        self.from_page = from_page
        self.to_page = to_page
        self.zoomin = zoomin
        self.callback = callback
        

    def load_to_markdown(self, filename, save_dir):
        os.makedirs(save_dir, exist_ok=True)
        json_dir = os.path.join(save_dir, os.path.basename(filename)[:-4]) + '.json'
        basedir = os.path.dirname(json_dir)
        basename = os.path.basename(json_dir)
        markdown_path = os.path.join(basedir, basename.split('.')[0] + '_md')
        os.makedirs(markdown_path, exist_ok=True)
        markdown_dir = os.path.join(markdown_path, basename.split('.')[0] + '.md')

        ocr_start = timer()
        self.__images__(
            filename if self.binary is None else self.binary,
            self.zoomin,
            self.from_page,
            self.to_page,
            self.callback
        )
        logging.info("OCR finished in %s seconds" % (timer() - ocr_start))

        layout_start = timer()
        np.set_printoptions(threshold=np.inf)
        start = timer()
        self._layouts_rec(self.zoomin)
        logging.info("Layout finished in %s seconds" % (timer() - layout_start))

        merge_start = timer()
        self._text_merge()
        tbls = self._extract_table_figure(True, self.zoomin, True, True, markdown_path)
        logging.info("extract_table_figure in %s seconds" % (timer() - merge_start))
        try:
            page_width = max([b["x1"] for b in self.boxes if b['layout_type'] == 'text']) - min(
                [b["x0"] for b in self.boxes if b['layout_type'] == 'text'])
            self._concat_downward()
            self._filter_forpages()
            column_width = np.median([b["x1"] - b["x0"] for b in self.boxes if b['layout_type'] == 'text'])
            text_width = np.argmax(np.bincount([b["x1"] - b["x0"] for b in self.boxes if b['layout_type'] == 'text']))

            # clean mess
            if column_width < page_width / 2 and text_width < page_width / 2:
                self.boxes = self.sort_X_by_page(self.boxes, 0.9 * column_width)

            for b in self.boxes:
                b["text"] = re.sub(r"([\t 　]|\u3000){2,}", " ", b["text"].strip())

            if self.from_page > 0:
                return {
                    "title": "",
                    "authors": "",
                    "abstract": "",
                    "sections": [(b["text"] + self._line_tag(b, self.zoomin), b.get("layoutno", "")) for b in self.boxes if
                                 re.match(r"(text|title)", b.get("layoutno", "text"))],
                    "tables": tbls
                }
        except Exception as e:
            logging.warning("Error in Powerful PDF parsing: %s" % e)
        i = 0
        sections = [(b["text"] + self._line_tag(b, self.zoomin), b.get("layoutno", "")) for b in self.boxes[i:] if
                    re.match(r"(text|title|author|reference|content)", b.get("layoutno", "text"))]
        new_sections = {}

        for sec in sections:
            i = 0
            pn = int(sec[0].split('@@')[-1].split('\t')[0])
            top = float(sec[0].split('@@')[-1].split('\t')[3]) + self.page_cum_height[pn - 1]
            right = float(sec[0].split('@@')[-1].split('\t')[2])
            sec_no = str(pn) + '-' + sec[1]
            while i < len(tbls):
                tbl = tbls[i]
                t_pn = int(tbl[1][0][0]) + 1
                t_bottom = float(tbl[1][0][4]) + self.page_cum_height[t_pn - 1]
                t_left = float(tbl[1][0][1])
                tbl_no = tbl[0][1]
                if t_pn > pn:
                    i += 1
                    continue
                if t_bottom < top and t_left < right:
                    new_sections[tbl_no] = {'text': tbl[0][0], 'type': tbl[0][1]}
                    tbls.pop(i)
                    continue
                if t_bottom < top and t_left > right and t_pn < pn:
                    new_sections[tbl_no] = {'text': tbl[0][0], 'type': tbl[0][1]}
                    tbls.pop(i)
                    continue
                i += 1
            if sec_no not in new_sections.keys():
                new_sections[sec_no] = {'text': sec[0].split('@@')[0], 'type': sec[1]}
            else:
                new_sections[sec_no]['text'] += sec[0].split('@@')[0]
        if tbls:
            for tbl in tbls:
                tbl_no = tbl[0][1]
                new_sections[tbl_no] = {'text': tbl[0][0], 'type': tbl[0][1]}

        json.dump(new_sections, open(json_dir, 'w'), ensure_ascii=False, indent=4)
        markdown_str = json2markdown(json_dir, markdown_dir)
        logging.info("PDF Parse finished in %s seconds" % (timer() - start))
        # print(new_sections, flush=True)
        return markdown_dir



    def load_to_chunks(self, filename, chunk_size, delimer, save_dir):
        self.filename = filename

        # TODO:实现相应功能
        ocr_start = timer()
        self.__images2__(
            filename if self.binary is None else self.binary,
            self.zoomin,
            self.from_page,
            self.to_page,
            self.callback
        )
        logging.info("OCR finished in %s seconds" % (timer() - ocr_start))

        layout_start = timer()
        logging.info("Layout started...")
        np.set_printoptions(threshold=np.inf)
        self._layouts_rec(self.zoomin)
        logging.info("Layout finished in %s seconds" % (timer() - layout_start))

        from PIL import Image, ImageDraw, ImageFont
        def save(name_qianzui):
            # 为每个图像处理对应的bbox
            for index,image in enumerate(self.page_images):
                # 获取页码（假设文件名是page1.jpg, page2.jpg等）
                page_num = index + 1
                
                
                # 找出当前页面的所有bbox
                page_bboxes = [box for box in self.boxes if box['page_number'] == page_num]
                
                clean_image = image.copy()
                draw = ImageDraw.Draw(clean_image)
                for box in page_bboxes:
                    # 绘制矩形框
                    draw.rectangle(
                        [(box['x0']*self.zoomin, box['top']*self.zoomin), (box['x1']*self.zoomin, box['bottom']*self.zoomin)],
                        outline="red",
                        width=2
                    )
                    
                    # 可选：在框上方显示文本
                    draw.text(
                        (box['x0']*self.zoomin, box['top']*self.zoomin - 15),
                        f"{box['layout_type']}",
                        fill="blue",
                        width = 2
                    )
                
                # 保存结果
                output_path = os.path.join("./pdf_parser_output", f"{name_qianzui}_{page_num}.jpg")
                clean_image.save(output_path)
                print(f"已保存: {output_path}")
        
        merge_start = timer()
        self._text_merge()
        tbls = self._extract_table_figure(True, self.zoomin, True, True, os.path.dirname(filename))
        logging.info("extract_table_figure in %s seconds" % (timer() - merge_start))
        try:
            page_width = max([b["x1"] for b in self.boxes if b['layout_type'] == 'text']) - min(
                [b["x0"] for b in self.boxes if b['layout_type'] == 'text'])
            self._concat_downward()
            self._filter_forpages()
            column_width = np.median([b["x1"] - b["x0"] for b in self.boxes if b['layout_type'] == 'text'])
            text_width = np.argmax(np.bincount([b["x1"] - b["x0"] for b in self.boxes if b['layout_type'] == 'text']))

            # clean mess
            if column_width < page_width / 2 and text_width < page_width / 2:
                self.boxes = self.sort_X_by_page(self.boxes, 0.9 * column_width)

            for b in self.boxes:
                b["text"] = re.sub(r"([\t 　]|\u3000){2,}", " ", b["text"].strip())

            # if self.from_page > 0:
            #     return {
            #         "title": "",
            #         "authors": "",
            #         "abstract": "",
            #         "sections": [(b["text"] + self._line_tag(b, self.zoomin), b.get("layoutno", "")) for b in self.boxes if
            #                      re.match(r"(text|title)", b.get("layoutno", "text"))],
            #         "tables": tbls
            #     }
        except Exception as e:
            logging.warning("Error in Powerful PDF parsing: %s" % e)
        i = 0
        logging.warning(f'boxes:{self.boxes}')
        sections = [(b["text"] + self._line_tag(b, self.zoomin), b.get("layoutno", ""), [b["x0"], b["x1"], b["top"], b["bottom"], b["page_number"]]) for b in self.boxes[i:] if
                    re.match(r"(text|title|author|reference|content)", b.get("layoutno", "text"))]
        # sections = [(b["text"] + self._line_tag(b, self.zoomin), b.get("layoutno", ""), [b["x0"], b["x1"], b["top"], b["bottom"], b["page_number"]]) for b in self.boxes[i:] if
        #             re.match(r"(text|title|author|reference|content)", b.get("layoutno", "other"))]
        new_sections = {}

        for sec in sections:
            i = 0
            pn = int(sec[0].split('@@')[-1].split('\t')[0])
            top = float(sec[0].split('@@')[-1].split('\t')[3]) + self.page_cum_height[pn - 1]
            right = float(sec[0].split('@@')[-1].split('\t')[2])
            sec_no = str(pn) + '-' + sec[1]
            while i < len(tbls):
                tbl = tbls[i]
                t_pn = int(tbl[1][0][0]) + 1
                t_bottom = float(tbl[1][0][4]) + self.page_cum_height[t_pn - 1]
                t_left = float(tbl[1][0][1])
                t_right = float(tbl[1][0][2])
                t_top = float(tbl[1][0][3]) + self.page_cum_height[t_pn - 1]
                tbl_no = tbl[0][1]
                if t_pn > pn:
                    i += 1
                    continue
                if t_bottom < top and t_left < right:
                    new_sections[tbl_no] = {'text': tbl[0][0], 'type': tbl[0][1], 'bbox': [t_left, t_right, t_top, t_bottom, t_pn]}
                    tbls.pop(i)
                    continue
                if t_bottom < top and t_left > right and t_pn < pn:
                    new_sections[tbl_no] = {'text': tbl[0][0], 'type': tbl[0][1], 'bbox': [t_left, t_right, t_top, t_bottom, t_pn]}
                    tbls.pop(i)
                    continue
                i += 1
            if sec_no not in new_sections.keys():
                new_sections[sec_no] = {'text': sec[0].split('@@')[0], 'type': sec[1], 'bbox': sec[2]}
            else:
                new_sections[sec_no]['text'] += sec[0].split('@@')[0]
        if tbls:
            for tbl in tbls:
                t_pn = int(tbl[1][0][0]) + 1
                t_bottom = float(tbl[1][0][4]) + self.page_cum_height[t_pn - 1]
                t_left = float(tbl[1][0][1])
                t_right = float(tbl[1][0][2])
                t_top = float(tbl[1][0][3]) + self.page_cum_height[t_pn - 1]
                tbl_no = tbl[0][1]
                new_sections[tbl_no] = {'text': tbl[0][0], 'type': tbl[0][1], 'bbox': [t_left, t_right, t_top, t_bottom, t_pn]}



        os.makedirs(save_dir, exist_ok=True)
        json_dir = os.path.join(save_dir, os.path.basename(filename)[:-4]) + '.json'
        json.dump(new_sections, open(json_dir, 'w'), ensure_ascii=False, indent=4)

        # 将new_sections中的元素按照chunk_size, delimer，进行切分
        # 写代码实现遍历new_sections，每个Title之间的内容算作一个chunk，合并text，当text达到chunk_size了，就使用delimer切分
        from qanything_kernel.utils.custom_log import insert_logger
        new_sections_chunks_id = []
        new_sections_chunks_type = []
        chunks = []
        merge_text=""
        def save_chunk():
            insert_logger.info('save_chunk')
            insert_logger.info(f'new_sections_chunks_id: {new_sections_chunks_id}')
            tmp_merge_text = ""
            has_table = False
            title_lst = []
            page_id = int(new_sections_chunks_id[0].split('-')[0])
            before_patt = ['[a-z]', ',', '，', '-', '\(', '\)', '（', '）']
            after_patt = ['[a-z]', '·', '\(', '\)', '（', '）']
            bboxes = []
            for id,type in zip(new_sections_chunks_id, new_sections_chunks_type):
                if isinstance(new_sections[id]['text'], dict) or type == "table":
                    table = new_sections[id]['text']['table_html']
                    caption = new_sections[id]['text']['table_caption']
                    text = table + '\n' + caption + '\n\n'
                    has_table = True
                elif type == "title":
                    text = "##" + new_sections[id]['text'] + "\n\n"
                    title_lst.append(new_sections[id]['text'])
                elif 'figure' in type:
                    text = '![figure]'+'({}.jpg "{}")'.format(new_sections[id]['type'], new_sections[id]['text']) + '\n'
                elif 'equation' in type:
                    text = '![equation]'+'({}.jpg)'.format(new_sections[id]['type']) + '\n'
                else:
                    text = new_sections[id]['text']
                
                if tmp_merge_text:
                    if any([re.match(p, tmp_merge_text[-2]) for p in before_patt]) and any([re.match(p, text[0]) for p in after_patt]):
                        tmp_merge_text = tmp_merge_text[-1] +" "+ text + "\n"
                    else:
                        tmp_merge_text += text+"\n"
                else:
                    tmp_merge_text += text+"\n"
                
                bboxes.append(new_sections[id]['bbox'])
            
            chunks.append({'text': tmp_merge_text, 'page_id': page_id, 'has_table': has_table, 'title_lst': title_lst, 'bboxes': bboxes})

        for key, value in new_sections.items():
            layout_type = key.split('-')[1]
            text = value['text']['table_caption'] + value['text']['table_html'] if layout_type=="table" else value['text']

            if len(new_sections_chunks_id) and num_tokens_embed(merge_text)+num_tokens_embed(text)>chunk_size:
                # 1、有文本，又遇到标题，则直接将其保存为一个chunk
                # 2、有文本，当前的文本长度加上新文本超过切分的长度，则直接将其保存为一个chunk
                save_chunk()
                new_sections_chunks_id.clear()
                new_sections_chunks_type.clear()
                merge_text = text
                new_sections_chunks_id.append(key)
                new_sections_chunks_type.append(layout_type)
                

            elif "text" in new_sections_chunks_type and layout_type == "title":
                # 当前chunk有内容，且包含text类型，又遇到标题，则直接将其保存为一个chunk
                save_chunk()
                new_sections_chunks_id.clear()
                new_sections_chunks_type.clear()
                merge_text = text
                new_sections_chunks_id.append(key)
                new_sections_chunks_type.append(layout_type)
                
            else:
                # 当前chunk没有内容，或者没有text类型，直接加到当前chunk中
                merge_text += text
                new_sections_chunks_id.append(key)
                new_sections_chunks_type.append(layout_type)

            
            # 先根据layout_type判断是否需要切分，将都是text的部分合并
            # labels = ['Text', 'Title', 'Figure', 'Equation', 'Table', 
            #         'Caption', 'Header', 'Footer', 'BibInfo', 'Reference',
            #         'Content', 'Code', 'Other', 'Item', 'Author']
        if new_sections_chunks_id:
            save_chunk()
        
        insert_logger.info(f"pdf_parser_backend: {chunks}")
            
        return chunks
    