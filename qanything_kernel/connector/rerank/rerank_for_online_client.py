import sys
import os

# 获取当前脚本的绝对路径，将项目根目录添加到sys.path
current_script_path = os.path.abspath(__file__)
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_script_path))))

sys.path.append(root_dir)
print(root_dir)


import asyncio
import aiohttp
from typing import List
from qanything_kernel.utils.custom_log import debug_logger
from qanything_kernel.utils.general_utils import get_time_async
from qanything_kernel.utils.model_utils import num_tokens_rerank, get_vllm_model_length
from qanything_kernel.configs.model_config import LOCAL_RERANK_BATCH, SEPARATORS
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import traceback


# 针对rerank的query token超长的问题，进行切分处理
def tokenize_passage_preproc(passages: List[str], chunk_size=1024, chunk_overlap=None):
    if chunk_overlap is None:
        chunk_overlap = int(chunk_size * 0.1)
    query_splitter = RecursiveCharacterTextSplitter(
                separators=SEPARATORS,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=num_tokens_rerank)
    
    split_texts = []
    split_counts = []
    for passage in passages:
        # 先将 passage 分词
        passage_chunks = query_splitter.split_text(passage)
        
        split_texts.extend(passage_chunks)
        split_counts.append(len(passage_chunks))

    return split_texts, split_counts







class GeneralRerank:
    def __init__(self, base_url, model_name, api_key):
        self.model_version = model_name
        self.url = base_url
        self.model_name = model_name
        self.api_key = api_key
        self.max_length = get_vllm_model_length(base_url, model_name)


    async def _get_rerank_res(self, query, passages):
        new_passages = []
        query_num = []
        new_passages, query_num = tokenize_passage_preproc(passages, self.max_length)
        # debug_logger.info(f"rerank query num: {query_num}, rerank passages : {new_passages}")

        data = {
            "model": self.model_name,
            'query': query,
            'documents': new_passages
        }
        headers = {"content-type": "application/json",
                   "Authorization": f"Bearer {self.api_key}"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, json=data, headers=headers) as response:
                    if response.status == 200:
                        scores = [0 for _ in range(len(passages))]
                        results = await response.json()
                        # debug_logger.info(f"results: {results}")
                        # for i, result in enumerate(results["results"]):
                        #     scores[result["index"]] = result["relevance_score"]
                        start_index = 0
                        for i in range(len(passages)):
                            end_index = start_index + query_num[i]
                            # 获取切片范围内的结果, 提取relevance_score 并找到最大值
                            slice_results = results["results"][start_index:end_index]
                            scores[i] = max(result["relevance_score"] for result in slice_results)
                            start_index = end_index
                        return scores
                    else:
                        debug_logger.error(f'Rerank request failed with status {response.status}')
                        return None
        except Exception as e:
            debug_logger.info(f'rerank query: {query}, rerank passages length: {len(passages)}')
            debug_logger.error(f'rerank error: {traceback.format_exc()}')
            return None

    @get_time_async
    async def arerank_documents(self, query: str, source_documents: List[Document]) -> List[Document]:
        """Embed search docs using async calls, maintaining the original order."""
        batch_size = LOCAL_RERANK_BATCH  # 增大客户端批处理大小
        all_scores = [0 for _ in range(len(source_documents))]
        # passages = [doc.page_content for doc in source_documents]
        passages = [ doc.metadata["faq_dict"]["question"] if doc.metadata.get("file_name","").endswith('.faq') else doc.page_content for doc in source_documents]

        
        tasks = []
        for i in range(0, len(passages), batch_size):
            task = asyncio.create_task(self._get_rerank_res(query, passages[i:i + batch_size]))
            tasks.append((i, task))

        for start_index, task in tasks:
            res = await task
            if res is None:
                return source_documents
            all_scores[start_index:start_index + batch_size] = res

        for idx, score in enumerate(all_scores):
            source_documents[idx].metadata['score'] = round(float(score), 2)
        source_documents = sorted(source_documents, key=lambda x: x.metadata['score'], reverse=True)

        return source_documents




# 使用示例
# async def main():
#     reranker = GeneralRerank()
#     query = "Your query here"
#     documents = [Document(page_content="content1"), Document(page_content="content2")]  # 示例文档
#     reranked_docs = await reranker.arerank_documents(query, documents)
#     return reranked_docs


# # 运行异步主函数
# if __name__ == "__main__":
#     reranked_docs = asyncio.run(main())
#     print("reranked_docs", reranked_docs)
