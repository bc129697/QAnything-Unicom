"""Wrapper around YouDao embedding models."""
from typing import List
from qanything_kernel.utils.custom_log import debug_logger, embed_logger
from qanything_kernel.utils.general_utils import get_time_async, get_time
from langchain_core.embeddings import Embeddings
from qanything_kernel.configs.model_config import LOCAL_EMBED_BATCH
import traceback
import aiohttp
import asyncio
import requests


def _process_query(query):
    return '\n'.join([line for line in query.split('\n') if
                      not line.strip().startswith('![figure]') and
                      not line.strip().startswith('![equation]')])


class GeneralEmbeddings(Embeddings):
    def __init__(self, base_url, model_name, api_key):
        self.model_version = model_name
        self.session = requests.Session()
        self.url = base_url
        self.model_name = model_name
        self.api_key = api_key
        super().__init__()

    async def _get_embedding_async(self, session, queries):
        data = {
            "model": self.model_name,
            "input": queries,
            "encoding_format": "float"
        }
        headers = {"content-type": "application/json",
                   "Authorization": f"Bearer {self.api_key}"}
        async with session.post(self.url, json=data, headers=headers) as response:
            results = await response.json()
            result_embedding = [item['embedding'] for item in results["data"]]
            return result_embedding

    @get_time_async
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        batch_size = LOCAL_EMBED_BATCH  # 增大客户端批处理大小
        # 向上取整
        embed_logger.info(f'embedding texts number: {len(texts) / batch_size}')
        all_embeddings = []
        async with aiohttp.ClientSession() as session:
            tasks = [self._get_embedding_async(session, texts[i:i + batch_size])
                     for i in range(0, len(texts), batch_size)]
            results = await asyncio.gather(*tasks)
            for result in results:
                all_embeddings.extend(result)
        debug_logger.info(f'success embedding number: {len(all_embeddings)}')
        return all_embeddings

    async def aembed_query(self, text: str) -> List[float]:
        return (await self.aembed_documents([text]))[0]

    def _get_embedding_sync(self, texts):
        data = {
            "model": self.model_name,
            "input": [_process_query(text) for text in texts],
            "encoding_format": "float"
        }
        headers = {"content-type": "application/json",
                   "Authorization": f"Bearer {self.api_key}"}
        try:
            response = self.session.post(self.url, json=data, headers=headers)
            response.raise_for_status()
            results = response.json()
            result_embedding = [item['embedding'] for item in results["data"]]
            return result_embedding
        except Exception as e:
            debug_logger.error(f'sync embedding error: {traceback.format_exc()}')
            return None

    # @get_time
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._get_embedding_sync(texts)

    @get_time
    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        return self._get_embedding_sync([text])[0]

    @property
    def embed_version(self):
        return self.model_version
    


