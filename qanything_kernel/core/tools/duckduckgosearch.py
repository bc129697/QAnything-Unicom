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
from abc import ABC
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from qanything_kernel.utils.custom_log import debug_logger
import string
import json

import urllib.request
import urllib.error
def is_url_reachable(url, timeout=2):
    try:  
        with urllib.request.urlopen(url, timeout=timeout) as response:  
            # 如果能成功打开URL，并且返回状态码是200（OK），则认为URL是可达的  
            if response.status == 200:  
                return True  
            else:  
                return False  # 或者你可以根据具体需求返回其他值或抛出异常  
    except urllib.error.URLError as e:  
        # URLError会在URL无效、无法访问等情况下抛出  
        debug_logger.warning(f"URL Error: {e.reason}")  
        return False  
    except urllib.error.HTTPError as e:  
        # HTTPError是URLError的子类，用于处理HTTP错误（如404、500等）  
        debug_logger.warning(f"HTTP Error: {e.code} {e.reason}")  
        return False  
    except Exception as e:  
        # 捕获其他可能的异常  
        debug_logger.warning(f"An error occurred: {e}")  
        return False

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

class DuckDuckGoSearch(ABC):
    component_name = "DuckDuckGo Search"
    html2text = Html2TextTransformer()

    def run(self, question, top_n=3, detail=True):
        msg = "DuckDuckGo Search: "
        ans = question
        if not ans:
            msg += "No question provided."
            return [], msg
        
        try:
            from duckduckgo_search import DDGS
            with DDGS(timeout=4) as ddgs:
                ddgs_gen = ddgs.text(
                    question,
                    max_results=top_n,
                    timelimit=None,
                    backend="api",
                    region="cn-zh",
                    safesearch="Moderate"
                )
                if ddgs_gen:
                    results = [r for r in ddgs_gen]
            
            result_res = [
                {
                    "url": r["href"],
                    "title": r["title"],
                    "content": r["body"]
                 } for r in results
            ]

            # 获取网页内容详情
            if detail:
                for i in range(len(result_res)):
                    url = result_res[i]['url']
                    if not is_url_reachable(url):
                        continue
                    page_content = self.get_url_content(url)
                    ratio = calculate_chinese_ratio(page_content)
                    if ratio > 0.6 and len(page_content) > len(result_res[i]['content']):
                        result_res[i]['content'] = page_content
            msg += "success"

        except Exception as e:
            msg += f"**ERROR**: {str(e)}"
            debug_logger.error(f"**ERROR**: {str(e)}")
            return [], msg

        return result_res, msg
    

    def get_url_content(self, url):
        loader = AsyncHtmlLoader(url, requests_per_second=3, requests_kwargs={"timeout":2})
        docs = loader.load()
        for doc in docs:
            if doc.page_content == '':
                doc.page_content = doc.metadata.get('description', '')
        docs_transformed = self.html2text.transform_documents(docs)
        return docs_transformed[0].page_content


    
if __name__ == '__main__':
    print(DuckDuckGoSearch.__name__)
    search = DuckDuckGoSearch()
    result = search.run('985大学有哪些?')
    print(json.dumps(result, ensure_ascii=False, indent=4))
else:
    from qanything_kernel.configs.model_config import SUPORT_WEBSEARCH_TOOLS
    if DuckDuckGoSearch.__name__ not in SUPORT_WEBSEARCH_TOOLS:
        SUPORT_WEBSEARCH_TOOLS.append(DuckDuckGoSearch.__name__)
    



