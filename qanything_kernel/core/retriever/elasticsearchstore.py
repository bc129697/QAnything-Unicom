from qanything_kernel.utils.custom_log import debug_logger, insert_logger
from qanything_kernel.configs.model_config import ES_USER, ES_PASSWORD, ES_URL, ES_INDEX_NAME
from langchain_elasticsearch import ElasticsearchStore


class StoreElasticSearchClient:
    def __init__(self):
        self.es_store = ElasticsearchStore(
            es_url=ES_URL,
            index_name=ES_INDEX_NAME,
            es_user=ES_USER,
            es_password=ES_PASSWORD,
            strategy=ElasticsearchStore.BM25RetrievalStrategy()
        )
        debug_logger.info(f"Init ElasticSearchStore with index_name: {ES_INDEX_NAME}")

    def delete(self, docs_ids):
        try:
            res = self.es_store.delete(docs_ids, timeout=60)
            debug_logger.info(f"Delete ES document with number: {len(docs_ids)}, {docs_ids[0]}, res: {res}")
        except Exception as e:
            debug_logger.error(f"Delete ES document failed with error: {e}")

    def delete_files(self, file_ids, file_chunks):
        docs_ids = []
        for file_id, file_chunk in zip(file_ids, file_chunks):
            # doc_id 是file_id + '_' + i，其中i是range(file_chunk)
            docs_ids.extend([file_id + '_' + str(i) for i in range(file_chunk)])
        if docs_ids:
            self.delete(docs_ids)

    def update_kb_id_for_file_id(self, file_id, target_kb_id):
        """
        简化版本：使用_update_by_query API更新
        
        Args:
            file_id (str): 要更新的文件ID
            target_kb_id (str): 目标KB ID
        """
        try:
            # 使用_update_by_query API直接更新所有匹配的文档
            update_query = {
                "query": {
                    "term": {
                        "file_id": file_id
                    }
                },
                "script": {
                    "source": "ctx._source.kb_id = params.target_kb_id",
                    "params": {
                        "target_kb_id": target_kb_id
                    }
                }
            }
            
            response = self.es_store.client.update_by_query(
                index=ES_INDEX_NAME,
                body=update_query,
                refresh=True  # 立即刷新
            )


            
            debug_logger.info(f"Update by query response: {response}")
            debug_logger.info(f"Updated documents for file_id {file_id} with kb_id {target_kb_id}")
            
        except Exception as e:
            debug_logger.error(f"Error updating kb_id for file_id {file_id}: {e}")
