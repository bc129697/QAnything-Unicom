import concurrent.futures
from dotenv import load_dotenv
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from qanything_kernel.utils.custom_log import debug_logger
from qanything_kernel.configs.model_config import SUPORT_WEBSEARCH_TOOLS
from qanything_kernel.core.tools.bingsearch import BingSearch
from qanything_kernel.core.tools.baidusearch import BaiduSearch
from qanything_kernel.core.tools.baidubaike import BaiduBaike
from qanything_kernel.core.tools.duckduckgosearch import DuckDuckGoSearch
from qanything_kernel.core.tools.wikipediasearch import WikipediaSearch

load_dotenv()
html2text = Html2TextTransformer()

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
        print(f"URL Error: {e.reason}")  
        return False  
    except urllib.error.HTTPError as e:  
        # HTTPError是URLError的子类，用于处理HTTP错误（如404、500等）  
        print(f"HTTP Error: {e.code} {e.reason}")  
        return False  
    except Exception as e:  
        # 捕获其他可能的异常  
        print(f"An error occurred: {e}")  
        return False
    

def duckduckgo_search(query: str, top_k: int):

    # results = api_wrapper.results(query, max_results=top_k)
    try:
        from duckduckgo_search import DDGS
        with DDGS(timeout=4) as ddgs:
            ddgs_gen = ddgs.text(
                query,
                max_results=top_k,
                timelimit=None,
                backend="api",
                region="cn-zh",
                safesearch="Moderate"
            )
            print("ddgs_gen:", ddgs_gen)
            if ddgs_gen:
                results = [r for r in ddgs_gen]
        results = [
                    {"snippet": r["body"], "title": r["title"], "link": r["href"]} for r in results
        ]

        debug_logger.info(f"ddgs search sucess, start AsyncHtmlLoader...{results}")
        urls = [res["link"] for res in results]
        urls_available = []
        for url in urls:
            if is_url_reachable(url):
                urls_available.append(url)

        # loader = AsyncChromiumLoader(urls)
        # AsyncHtmlLoader这个效果不是那么好, 还是要换成AsyncChromiumLoader
        loader = AsyncHtmlLoader(urls_available, requests_per_second=3, requests_kwargs={"timeout":2})
        docs = loader.load()
        for doc in docs:
            if doc.page_content == '':
                doc.page_content = doc.metadata.get('description', '')
        debug_logger.info(f"AsyncHtmlLoader sucess\n")
        #docs_transformed = self.bs_transformer.transform_documents(docs, unwanted_tags=['li','a'],tags_to_extract=["p",'div'])
        docs_transformed = html2text.transform_documents(docs)
        #print(f"################################\n{docs_transformed}")
        #print(res)
        #print(docs_transformed[0].page_content)
        # 这里加上title是不是好一点
        search_contents = []
        for i, doc in enumerate(docs_transformed):
            title_content = results[i]["title"]
            search_contents.append(f">>>>>>>>>>>>>>>>>>>>以下是标题为<h1>{title_content}</h1>的网页内容\n{doc.page_content}\n<<<<<<<<<<<<<<<<<以上是标题为<h1>{title_content}</h1>的网页内容\n")
        return "\n\n".join([doc for doc in search_contents]), docs_transformed
    except Exception as e:
        print(f"ddgs search Error occurred: {e}")
        return "",[]



# def web_search_tool(query, top_k=3, tools=SUPORT_WEBSEARCH_TOOLS):
#     if tools == []:
#         return []
    
#     search_results = []
#     msg_results = ""
#     for tool in tools:
#         print(tool)
#         if tool in SUPORT_WEBSEARCH_TOOLS:
#             # 根据工具类型调用相应的函数
#             function = globals().get(tool)
#             if function:
#                 instance = function()
#                 result, msg = instance.run(query, top_k)
#                 # debug_logger.info(f"web_search_tool {tool} result: {json.dumps(result, ensure_ascii=False, indent=4)}")
#                 search_results.extend(result)
#                 msg_results += msg+"\n "
#                 debug_logger.info(f"web_search_tool {tool} msg: {msg}")

#             else:
#                 debug_logger.warning(f"have no tool: {tool}")
#                 continue
#         else:
#             msg_results += f"Unsupported tool: {tool}" +"\n"
#             debug_logger.warning(f"Unsupported tool: {tool}")
#             continue
    
#     return search_results, msg_results


def web_search_tool(query, top_k=3, tools=SUPORT_WEBSEARCH_TOOLS):
    if tools == []:
        return [], "no tools"
    
    search_results = []
    msg_results = []
    import math
    top_k = math.ceil(top_k/len(tools))

    def search_with_tool(tool):
        result = []
        msg = ""
        if tool in SUPORT_WEBSEARCH_TOOLS:
            # 根据工具类型调用相应的函数
            function = globals().get(tool)
            if function:
                instance = function()
                result, msg = instance.run(query, top_k)
                debug_logger.info(f"web_search_tool {tool} result: {json.dumps(result, ensure_ascii=False, indent=4)}")
            else:
                debug_logger.warning(f"have no tool: {tool}")
        else:
            msg = f"Unsupported tool: {tool}"
            debug_logger.warning(f"Unsupported tool: {tool}")
        return result, msg

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_tool = {executor.submit(search_with_tool, tool): tool for tool in tools}
        for future in concurrent.futures.as_completed(future_to_tool):
            tool = future_to_tool[future]
            try:
                result, msg = future.result()
                search_results.extend(result)
                msg_results.append(msg)
            except Exception as exc:
                debug_logger.error(f'{tool} generated an exception: {exc}')

    return search_results, "\n ".join(msg_results)


if __name__ == "__main__":
    # result = duckduckgo_search("985大学有哪些?",3)
    # result = web_search_tool("985大学有哪些?",3, ["BaiduSearch"])
    result = web_search_tool("985大学",3)
    print(json.dumps(result, ensure_ascii=False, indent=4))
