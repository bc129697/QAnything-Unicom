import sys
import os
# 获取当前脚本的绝对路径
current_script_path = os.path.abspath(__file__)

# 获取当前脚本的父目录的路径，即`qanything_server`目录
current_dir = os.path.dirname(current_script_path)

# 获取`qanything_server`目录的父目录，即`qanything_kernel`
parent_dir = os.path.dirname(current_dir)

# 获取根目录：`qanything_kernel`的父目录
root_dir = os.path.dirname(parent_dir)

# 将项目根目录添加到sys.path
sys.path.append(root_dir)


from qanything_kernel.configs.model_config import RAG_SERVER_PORT, RAG_SERVER_WORKERST
from qanything_kernel.utils.general_utils import check_internet_connection
if check_internet_connection():
    print("Internet connection is active.")
else:
    print("No internet connection.")
    # 离线模式，不能连接到互联网
    os.environ["SCARF_NO_ANALYTICS"]="true"
    os.environ["DO_NOT_TRACK"]="true"
    # os.environ["TIKTOKEN_CACHE_DIR"] = "./tiktoken_model"

from handler import *
from qanything_kernel.core.local_doc_qa import LocalDocQA
from qanything_kernel.utils.custom_log import debug_logger, qa_logger
from sanic.worker.manager import WorkerManager
from sanic import Sanic, response
from sanic_ext import Extend
import time



WorkerManager.THRESHOLD = 6000


start_time = time.time()
app = Sanic("QAnything")
app.config.CORS_ORIGINS = "*"
Extend(app)
# 设置请求体最大为 128MB
app.config.REQUEST_MAX_SIZE = 128 * 1024 * 1024

# 将 /qanything 路径映射到 ./dist/qanything 文件夹，并指定路由名称
app.static('/qanything/', 'qanything_kernel/qanything_server/dist/qanything/', name='qanything', index="index.html")


@app.before_server_start
async def init_local_doc_qa(app, loop):
    start = time.time()
    local_doc_qa = LocalDocQA(RAG_SERVER_PORT)
    local_doc_qa.init_cfg()
    end = time.time()
    print(f'init local_doc_qa cost {end - start}s', flush=True)
    app.ctx.local_doc_qa = local_doc_qa
    
@app.after_server_start
async def notify_server_started(app, loop):
    print(f"Server Start Cost {time.time() - start_time} seconds", flush=True)

@app.after_server_start
async def start_server_and_open_browser(app, loop):
    try:
        print(f"Opening browser at http://0.0.0.0:{RAG_SERVER_PORT}/qanything/")
    except Exception as e:
        # 记录或处理任何异常
        print(f"Failed to open browser: {e}")

# app.add_route(lambda req: response.redirect('/api/docs'), '/')
# tags=["新建知识库"]
# app.add_route(document, "/api/docs", methods=['GET'])
# app.add_route(health_check, "/api/health_check", methods=['GET'])  # tags=["健康检查"]
# app.add_route(new_knowledge_base, "/api/local_doc_qa/new_knowledge_base", methods=['POST'])  # tags=["新建知识库"]
# app.add_route(upload_weblink, "/api/local_doc_qa/upload_weblink", methods=['POST'])  # tags=["上传网页链接"]
# app.add_route(upload_files, "/api/local_doc_qa/upload_files", methods=['POST'])  # tags=["上传文件"]
# app.add_route(upload_faqs, "/api/local_doc_qa/upload_faqs", methods=['POST'])  # tags=["上传FAQ"]
# app.add_route(local_doc_chat, "/api/local_doc_qa/local_doc_chat", methods=['POST'])  # tags=["问答接口"] 
# app.add_route(list_kbs, "/api/local_doc_qa/list_knowledge_base", methods=['POST'])  # tags=["知识库列表"] 
# app.add_route(list_docs, "/api/local_doc_qa/list_files", methods=['POST'])  # tags=["文件列表"]
# app.add_route(get_total_status, "/api/local_doc_qa/get_total_status", methods=['POST'])  # tags=["获取所有知识库状态数据库"]
# app.add_route(clean_files_by_status, "/api/local_doc_qa/clean_files_by_status", methods=['POST'])  # tags=["清理数据库"]
# app.add_route(delete_docs, "/api/local_doc_qa/delete_files", methods=['POST'])  # tags=["删除文件"] 
# app.add_route(delete_knowledge_base, "/api/local_doc_qa/delete_knowledge_base", methods=['POST'])  # tags=["删除知识库"] 
# app.add_route(rename_knowledge_base, "/api/local_doc_qa/rename_knowledge_base", methods=['POST'])  # tags=["重命名知识库"]
# app.add_route(get_doc_completed, "/api/local_doc_qa/get_doc_completed", methods=['POST'])  # tags=["获取文档完整解析内容"]
# app.add_route(get_qa_info, "/api/local_doc_qa/get_qa_info", methods=['POST'])  # tags=["获取QA信息"]
# app.add_route(get_user_id, "/api/local_doc_qa/get_user_id", methods=['POST'])  # tags=["获取用户ID"]
# app.add_route(get_doc, "/api/local_doc_qa/get_doc", methods=['POST'])  # tags=["获取doc详细内容"]
# app.add_route(get_rerank_results, "/api/local_doc_qa/get_rerank_results", methods=['POST'])  # tags=["获取rerank结果"]
# app.add_route(get_user_status, "/api/local_doc_qa/get_user_status", methods=['POST'])  # tags=["获取用户状态"]
# app.add_route(get_random_qa, "/api/local_doc_qa/get_random_qa", methods=['POST'])  # tags=["获取随机QA"]
# app.add_route(get_related_qa, "/api/local_doc_qa/get_related_qa", methods=['POST'])  # tags=["获取相关QA"]
# app.add_route(new_bot, "/api/local_doc_qa/new_bot", methods=['POST'])  # tags=["新建Bot"]
# app.add_route(delete_bot, "/api/local_doc_qa/delete_bot", methods=['POST'])  # tags=["删除Bot"]
# app.add_route(update_bot, "/api/local_doc_qa/update_bot", methods=['POST'])  # tags=["更新Bot"]
# app.add_route(get_bot_info, "/api/local_doc_qa/get_bot_info", methods=['POST'])  # tags=["获取Bot信息"]
# app.add_route(update_chunks, "/api/local_doc_qa/update_chunks", methods=['POST'])  # tags=["更新chunk"]
# app.add_route(get_file_base64, "/api/local_doc_qa/get_file_base64", methods=['POST'])  # tags=["从知识库获取原文件"]




# 基础功能接口
app.add_route(lambda req: response.redirect('/api/docs'), '/')
app.add_route(document, "/api/docs", methods=['GET'])
app.add_route(new_knowledge_base, "/api/rag/new_knowledge_base", methods=['POST'])             # tags=["新建知识库"]
app.add_route(delete_knowledge_base, "/api/rag/delete_knowledge_base", methods=['POST'])       # tags=["删除知识库"]
app.add_route(rename_knowledge_base, "/api/rag/rename_knowledge_base", methods=['POST'])       # tags=["重命名知识库"]
app.add_route(list_kbs, "/api/rag/list_knowledge_base", methods=['POST'])                      # tags=["获取某用户知识库列表"]
app.add_route(list_docs, "/api/rag/list_files", methods=['POST'])                              # tags=["获取知识库中文件列表"]
app.add_route(get_files_statu, "/api/rag/get_files_statu", methods=['POST'])                   # tags=["获取某些指定文件的解析状态"]
app.add_route(get_total_status, "/api/rag/get_total_status", methods=['POST'])                 # tags=["获取某用户所有知识库文件解析状态数量"]
app.add_route(get_doc_completed, "/api/rag/get_doc_completed", methods=['POST'])               # tags=["获取指定文件的切片内容，包含切片的所有kwargs信息"]
app.add_route(upload_files, "/api/rag/upload_files", methods=['POST'])                         # tags=["上传文件进行切片和embedding，可选提取摘要和大纲"]
app.add_route(upload_chunks, "/api/rag/chunk_embedding", methods=['POST'])                     # tags=["上传切片数据，进行embedding保存"]
app.add_route(upload_faqs, "/api/rag/upload_faqs", methods=['POST'])                           # tags=["上传FAQ"]
app.add_route(upload_weblink, "/api/rag/upload_weblink", methods=['POST'])                     # tags=["上传网页链接"]
app.add_route(update_chunks, "/api/rag/update_chunks", methods=['POST'])                       # tags=["修改指定切片的文本内容，同时更新embeding和向量数据库"]
app.add_route(update_qa, "/api/rag/update_qa", methods=['POST'])                               # tags=["修改指定QA的内容，同时更新embeding和向量数据库"]
app.add_route(delete_docs, "/api/rag/delete_files", methods=['POST'])                          # tags=["删除文件"] 
app.add_route(question_rag_search, "/api/rag/question_rag_search", methods=['POST'])           # tags=["问答接口，不区分doc和qa"]
app.add_route(question_qa_search, "/api/rag/question_qa_search", methods=['POST'])             # tags=["问答接口，区分doc和qa"]
app.add_route(document_parser, "/api/rag/document_parser", methods=['POST'])                   # tags=["获取文档文本内容，仅支持[txt,pdf,docx,xlsx,csv]"]
app.add_route(get_file_base64, "/api/rag/get_file_base64", methods=['POST'])                   # tags=["获取原文件"]
app.add_route(query_rewrite, "/api/rag/query_rewrite", methods=['POST'])                       # tags=["根据history实现query改写"]
app.add_route(local_doc_chat, "/api/rag/local_doc_chat", methods=['POST'])                     # tags=["问答接口，根据配置模型进行问答"]
app.add_route(delete_chunks, "/api/rag/delete_chunks", methods=['POST'])                       # tags=["删除指定切片"]
app.add_route(move_file, "/api/rag/move_file", methods=['POST'])                               # tags=["移动文件到另外的知识库"]


# 新开发通用接口
app.add_route(modify_chunk_kwargs, "/api/modify_chunk_kwargs", methods=['POST'])                     # tags=["用于修改和增加切片的kwargs信息"]
app.add_route(delete_chunk_metadata, "/api/delete_chunk_metadata", methods=['POST'])                 # tags=["用于删除切片的kwargs中的某个key"]
app.add_route(update_kb_metadata, "/api/update_kb_metadata", methods=['POST'])                       # tags=["修改知识库的元数据，增删改"]
app.add_route(update_file_metadata, "/api/update_file_metadata", methods=['POST'])                   # tags=["修改知识库的元数据，增删改"]
app.add_route(get_websearch_tools, "/api/get_websearch_tools", methods=['GET'])                      # tags=["获取可用的联网检索工具"] 
app.add_route(chunk_summary, "/api/chunk_summary", methods=['POST'])                                 # tags=["处理上传解析成功的文件，将文件读取其中每个切片内容，并调用大模型进行总结、关键词提取等，将提取的结果保存到切片的元数据"]
app.add_route(file_extract_outline, "/api/file_extract_outline", methods=['POST'])                   # tags=["处理上传解析成功的文件，对文件内容调用大模型进行大纲提取，将提取的结果保存到对应知识库"]
app.add_route(file_extract_summary, "/api/file_extract_summary", methods=['POST'])                   # tags=["处理上传解析成功的文件，将文件内容调用大模型进行摘要提取，将提取的结果保存到对应知识库"]



# 机器人问答
app.add_route(new_bot, "/api/rag/new_bot", methods=['POST'])  # tags=["新建Bot"]
app.add_route(delete_bot, "/api/rag/delete_bot", methods=['POST'])  # tags=["删除Bot"]
app.add_route(update_bot, "/api/rag/update_bot", methods=['POST'])  # tags=["更新Bot"]
app.add_route(get_bot_info, "/api/rag/get_bot_info", methods=['POST'])  # tags=["获取Bot信息"]




# 项目适配接口
app.add_route(dify_rag_search, "/retrieval", methods=['POST'])  # tags=["对应dify的问答接口API"]




# 其他不常用接口，主要用于qanything前端
app.add_route(health_check, "/api/health_check", methods=['GET'])  # tags=["健康检查"]
app.add_route(clean_files_by_status, "/api/rag/clean_files_by_status", methods=['POST'])  # tags=["清理数据库"]
app.add_route(get_qa_info, "/api/rag/get_qa_info", methods=['POST'])  # tags=["获取QA信息"]
app.add_route(get_user_id, "/api/rag/get_user_id", methods=['POST'])  # tags=["获取用户ID"]
app.add_route(get_doc, "/api/rag/get_doc", methods=['POST'])  # tags=["获取doc详细内容"]
app.add_route(get_user_status, "/api/rag/get_user_status", methods=['POST'])  # tags=["获取用户状态"] 不可用
app.add_route(get_random_qa, "/api/rag/get_random_qa", methods=['POST'])  # tags=["获取随机QA"]
app.add_route(get_related_qa, "/api/rag/get_related_qa", methods=['POST'])  # tags=["获取相关QA"]





if __name__ == "__main__":
    app.run(host='0.0.0.0', port=RAG_SERVER_PORT, workers=RAG_SERVER_WORKERST, access_log=False)
