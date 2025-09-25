#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
from qanything_kernel.utils.custom_log import debug_logger
from bs4 import BeautifulSoup
from abc import ABC
import html2text
import requests
import string
import json
import re


def is_punctuation(char):
    # 判断是否为ASCII或非ASCII标点符号
    return char in string.punctuation or '\u3000' <= char <= '\u303F'  # CJK符号和标点

def is_digit(char):
    # 判断是否为ASCII或非ASCII数字
    return char in string.digits or '\uFF10' <= char <= '\uFF19'  # 全角数字

def calculate_chinese_ratio(text):
    if not text:
        return 0.0

    chinese_count = 0
    total_count = 0

    for char in text:
        # 检查字符是否为中文字符、标点符号或数字
        if '\u4e00' <= char <= '\u9fff' or is_punctuation(char) or is_digit(char):
            chinese_count += 1
        total_count += 1

    # 避免除以零的情况
    if total_count == 0:
        return 0.0

    ratio = chinese_count / total_count
    return ratio


class BaiduSearch(ABC):
    component_name = "Baidu Search"
    h = html2text.HTML2Text()
    h.ignore_images = True
    h.ignore_links = True
    

    def run(self, question, top_n=3, detail=True):
        msg = "Baidu Search: "
        ans = question
        if not ans:
            msg += "No question provided."
            return [], msg
        
        try:
            url = 'https://www.baidu.com/s?wd=' + str(question) # + '&rn=' + str(top_n)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'}
            response = requests.get(url=url, headers=headers, timeout=2)
            # print(response.text)

            # with open('baidu_search.txt', 'w', encoding='utf-8') as f:
            #     f.write(response.text)
            # 初始化 BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取搜索结果
            search_results = []
            for item in soup.select('div.c-container, div.result'):  # 每个搜索结果容器
                # 过滤广告结果（通常包含ec_类）
                # print(f"item class: {item.get('class', [])}\n\n\n")  # 调试输出标题
                if 'EC_result' in item.get('class', []):
                    # print(f"Skipping ad item: {item.get('class', [])}")
                    continue
                

                # 提取标题
                title_tag = item.select_one('h3 a')  # 定位到 <h3> 标签内的 <a> 标签
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    link = title_tag['href'] if 'href' in title_tag.attrs else None
                    text_content = item.get_text(strip=True)  # 使用整个项的文本作为内容
                else:
                    # AI生成的结果可能没有标题标签
                    title = "AI Summary Result"
                    link = ""
                    text_content = item.get_text(strip=True)  # 使用整个项的文本作为标题
                
                               
                # 提取来源和时间（可选）
                source = item.select_one('.cosc-source-text').get_text(strip=True) if item.select_one('.cosc-source-text') else None
                # source_elem = item.select_one('div.c-showurl, .c-color-gray')
                # source = source_elem.get_text().strip() if source_elem else ""    
                
                result = {
                    'title': title,
                    'url': link,
                    'content': text_content,
                    'source': source
                }
                search_results.append(result)

            # 打印提取的结果
            # for idx, result in enumerate(search_results, start=1):
            #     print(f"Result {idx}:")
            #     print(f"  Title: {result['title']}")
            #     print(f"  Link: {result['url']}")
            #     print(f"  Text Content: {result['content']}")
            #     print()

                    
                    
            
                    
            if len(search_results) > top_n:
                search_results = search_results[:top_n]

            # # 获取网页内容详情
            if detail:
                for i in range(len(search_results)):
                    url = search_results[i]['url']
                    if not url:
                        continue  # 如果没有链接，则跳过
                    # debug_logger.info(f"Fetching content from URL: {url}")
                    page_content = self.get_url_content(url)
                    ratio = calculate_chinese_ratio(page_content)
                    if ratio > 0.6 and len(page_content) > len(search_results[i]['content']):
                        search_results[i]['content'] = page_content
            msg += "success"
            return search_results, msg

        except Exception as e:
            msg += f"**ERROR**: {e}"
            debug_logger.error(f"**ERROR**: {e}")
            return [], msg

        
        

    def get_url_content(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'}
        response = requests.get(url=url, headers=headers, timeout=2)
        if not response.status_code == 200:
            debug_logger.info(f"timeout: {url}")
            return ""
        
        page_content=self.h.handle(response.text)
        # debug_logger.info("page_content:",page_content)
        return page_content



if __name__ == '__main__':
    search = BaiduSearch()
    results = search.run('985大学有哪些?', 3)
    print(json.dumps(results, ensure_ascii=False, indent=4))
else:
    from qanything_kernel.configs.model_config import SUPORT_WEBSEARCH_TOOLS
    if BaiduSearch.__name__ not in SUPORT_WEBSEARCH_TOOLS:
        SUPORT_WEBSEARCH_TOOLS.append(BaiduSearch.__name__)

    