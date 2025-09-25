import re
import os
import time
import uuid
import json
import base64
import shutil
import aiohttp
import asyncio
import urllib.parse
from typing import List
from datetime import datetime
from sanic import request, response
from collections import Counter
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from langchain.schema import Document
from sanic.response import ResponseStream
from sanic.response import json as sanic_json
from sanic.response import text as sanic_text
from qanything_kernel.core.retriever.parent_retriever import ParentRetriever
from qanything_kernel.core.retriever.vectorstore import VectorStoreMilvusClient
from qanything_kernel.core.local_file import LocalFile
from qanything_kernel.utils.custom_log import debug_logger, qa_logger
from qanything_kernel.core.local_doc_qa import LocalDocQA
from qanything_kernel.utils.general_utils import *
from qanything_kernel.utils.model_utils import *
from qanything_kernel.configs.model_config import (BOT_DESC, BOT_IMAGE, BOT_PROMPT, BOT_WELCOME,
                                                   DEFAULT_PARENT_CHUNK_SIZE, MAX_CHARS, VECTOR_SEARCH_TOP_K,
                                                   UPLOAD_ROOT_PATH, IMAGES_ROOT_PATH, QUESTION_MIN_LENGTH,
                                                   SUPORT_WEBSEARCH_TOOLS, RAG_SERVER_PORT, LLM_BASE_URL, LLM_API_KEY, 
                                                   LLM_MODEL_NAME, LLM_MAX_LENGTH, LLM_TEMPERATURE, LLM_TOP_P)







__all__ = ["new_knowledge_base", "upload_files", "list_kbs", "list_docs", "delete_knowledge_base", "delete_docs",
           "rename_knowledge_base", "get_total_status", "clean_files_by_status", "upload_weblink", "local_doc_chat",
           "document", "upload_faqs", "get_doc_completed", "get_qa_info", "get_user_id", "get_doc",
           "get_user_status", "health_check", "update_chunks", "get_file_base64",
           "get_random_qa", "get_related_qa", "new_bot", "delete_bot", "update_bot", "get_bot_info", 
           "document_parser", "query_rewrite", "get_files_statu", "upload_chunks", "question_rag_search", 
           "question_qa_search", "get_websearch_tools", "chunk_summary", "modify_chunk_kwargs", "update_kb_metadata",
           "update_file_metadata", "file_extract_outline", "file_extract_summary", "delete_chunk_metadata",
           "dify_rag_search", "update_qa", "delete_chunks", "move_file"]

INVALID_USER_ID = f"fail, Invalid user_id: . user_id 必须只含有字母，数字和下划线且字母开头"

# 获取环境变量GATEWAY_IP
GATEWAY_IP = os.getenv("GATEWAY_IP", "localhost")
debug_logger.info(f"GATEWAY_IP: {GATEWAY_IP}")

# 异步包装器，用于在后台执行带有参数的同步函数
async def run_in_background(func, *args):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=4) as pool:
        await loop.run_in_executor(pool, func, *args)


# 使用aiohttp异步请求另一个API
async def fetch(session, url, input_json):
    headers = {'Content-Type': 'application/json'}
    async with session.post(url, json=input_json, headers=headers) as response:
        return await response.json()


# 定义一个需要参数的同步函数
def sync_function_with_args(arg1, arg2):
    # 模拟耗时操作
    import time
    time.sleep(5)
    print(f"同步函数执行完毕，参数值：arg1={arg1}, arg2={arg2}")


# 打印请求返回的内容
def return_sanic(return_result):
    data_dumps = json.dumps(return_result, ensure_ascii=False, indent=4)
    debug_logger.info(f"return_sanic: {data_dumps}\n\n\n")
    return sanic_json(return_result)


@get_time_async
async def new_knowledge_base(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("new_knowledge_base %s", user_id)
    kb_name = safe_get(req, 'kb_name')
    debug_logger.info("kb_name: %s", kb_name)
    default_kb_id = 'KB' + uuid.uuid4().hex
    kb_id = safe_get(req, 'kb_id', default_kb_id)
    kb_id = correct_kb_id(kb_id)

    # is_quick = safe_get(req, 'quick', False)
    # if is_quick:
    #     kb_id += "_QUICK"

    if kb_id[:2] != 'KB':
        return return_sanic({"code": 400, "msg": "fail, kb_id must start with 'KB'"})
    not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, [kb_id])
    if not not_exist_kb_ids:
        return return_sanic({"code": 400, "msg": "fail, knowledge Base {} already exist".format(kb_id)})
    elif not_exist_kb_ids[0][1] != "not_exist": # 说明知识库已经存在，但是属于其他用户
        return return_sanic({"code": 400, "msg": f"fail, knowledge Base {kb_id} already exist, {not_exist_kb_ids[0][1]}"})

    # 新增解析配置
    from qanything_kernel.configs.model_config import LOCAL_EMBED_SERVICE_URL, EMBEDDING_MODEL_NAME, EMBEDDING_API_KEY, SEPARATORS
    parser_config = {}
    parser_config['embedding_base_url'] = safe_get(req, 'embedding_base_url',  LOCAL_EMBED_SERVICE_URL)
    parser_config['embedding_model_name'] = safe_get(req, 'embedding_model_name',  EMBEDDING_MODEL_NAME)
    parser_config['embedding_api_key'] = safe_get(req, 'embedding_api_key',  EMBEDDING_API_KEY)
    parser_config['separators'] = safe_get(req, 'separators',  SEPARATORS)
    parser_config['chunk_size'] = safe_get(req, 'chunk_size',  DEFAULT_PARENT_CHUNK_SIZE)
    
    # local_doc_qa.create_milvus_collection(user_id, kb_id, kb_name)
    local_doc_qa.milvus_summary.new_milvus_base(kb_id, user_id, kb_name, parser_config)
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M")
    return return_sanic({"code": 200, "msg": "success create knowledge base {}".format(kb_id),
                       "data": {"kb_id": kb_id, "kb_name": kb_name, "timestamp": timestamp}})


@get_time_async
async def upload_weblink(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("upload_weblink %s", user_id)
    debug_logger.info("user_info %s", user_info)
    kb_id = safe_get(req, 'kb_id')
    kb_id = correct_kb_id(kb_id)
    not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, [kb_id])
    if not_exist_kb_ids:
        msg = "invalid kb_id: {}, please check...".format(not_exist_kb_ids)
        return return_sanic({"code": 400, "msg": msg, "data": [{}]})

    url = safe_get(req, 'url')
    if url:
        urls = [url]
        # 如果URL以/结尾，先去除这个/
        if url.endswith('/'):
            url = url[:-1]
        titles = [safe_get(req, 'title', url.split('/')[-1]) + '.web']
    else:
        urls = safe_get(req, 'urls')
        titles = safe_get(req, 'titles')
        if len(urls) != len(titles):
            return return_sanic({"code": 400, "msg": "fail, urls and titles length not equal"})

    for url in urls:
        # url 需要以http开头
        if not url.startswith('http'):
            return return_sanic({"code": 400, "msg": "fail, url must start with 'http'"})
        # url 长度不能超过2048
        if len(url) > 2048:
            return return_sanic({"code": 400, "msg": f"fail, url too long, max length is 2048."})

    file_names = []
    for title in titles:
        debug_logger.info('ori name: %s', title)
        file_name = re.sub(r'[\uFF01-\uFF5E\u3000-\u303F]', '', title)
        debug_logger.info('cleaned name: %s', file_name)
        file_name = truncate_filename(file_name, max_length=200)
        file_names.append(file_name)

    mode = safe_get(req, 'mode', default='soft')  # soft代表不上传同名文件，strong表示强制上传同名文件
    debug_logger.info("mode: %s", mode)
    chunk_size = safe_get(req, 'chunk_size', default=DEFAULT_PARENT_CHUNK_SIZE)
    debug_logger.info("chunk_size: %s", chunk_size)

    exist_file_names = []
    if mode == 'soft':
        exist_files = local_doc_qa.milvus_summary.check_file_exist_by_name(user_id, kb_id, file_names)
        exist_file_names = [f[1] for f in exist_files]
        for exist_file in exist_files:
            file_id, file_name, file_size, status = exist_file
            debug_logger.info(f"{url}, {status}, existed files, skip upload")
            # await post_data(user_id, -1, file_id, status, msg='existed files, skip upload')
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M")

    data = []
    for url, file_name in zip(urls, file_names):
        if file_name in exist_file_names:
            continue
        local_file = LocalFile(user_id, kb_id, url, file_name)
        file_id = local_file.file_id
        file_size = len(local_file.file_content)
        file_location = local_file.file_location
        msg = local_doc_qa.milvus_summary.add_file(file_id, user_id, kb_id, file_name, file_size, file_location,
                                                   chunk_size, timestamp, url)
        debug_logger.info(f"{url}, {file_name}, {file_id}, {msg}")
        data.append({"file_id": file_id, "file_name": file_name, "file_url": url, "status": "gray", "bytes": 0,
                     "timestamp": timestamp})
        # asyncio.create_task(local_doc_qa.insert_files_to_milvus(user_id, kb_id, [local_file]))
    if exist_file_names:
        msg = f'warning，当前的mode是soft，无法上传同名文件{exist_file_names}，如果想强制上传同名文件，请设置mode：strong'
    else:
        msg = "success，后台正在飞速上传文件，请耐心等待"
    return return_sanic({"code": 200, "msg": msg, "data": data})


@get_time_async
async def upload_files(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("upload_files %s", user_id)
    debug_logger.info("user_info %s", user_info)
    kb_id = safe_get(req, 'kb_id')
    kb_id = correct_kb_id(kb_id)
    debug_logger.info("kb_id %s", kb_id)
    mode = safe_get(req, 'mode', default='soft')  # soft代表不上传同名文件，strong表示强制上传同名文件
    debug_logger.info("mode: %s", mode)
    files = req.files.getlist('files')
    debug_logger.info(f"{user_id} upload files number: {len(files)}")
    file_ids = safe_get(req, 'file_ids', None)
    if not file_ids is None:
        file_ids = file_ids.split(',') if file_ids else []
        debug_logger.info("file_ids: %s", file_ids)
        # 判断file_ids与files是否匹配，数量是否一致
        if len(file_ids) != len(files):
            msg = "file_ids与files数量不一致，请检查！"
            debug_logger.info("%s", msg)
            return return_sanic({"code": 400, "msg": msg})
        # 检查file_ids是否已经存在
        exist_file_ids = local_doc_qa.milvus_summary.check_file_exist(user_id, kb_id, file_ids)
        if len(exist_file_ids)>0:
            msg = f"file_ids {exist_file_ids} 已经存在，请检查！"
            debug_logger.info("%s", msg)
            return return_sanic({"code": 400, "msg": msg})
    else:
        file_ids = []
        for file in files:
            file_ids.append(uuid.uuid4().hex)

    
    
    not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, [kb_id])
    if not_exist_kb_ids and not_exist_kb_ids[0][1] == "not_exist": # 说明知识库不存在
        debug_logger.info(f"invalid kb_id: {not_exist_kb_ids} new knowledge base")
        # kb_id不存在则直接创建一个，kb_name直接使用kb_id
        # kb_name = safe_get(req, 'kb_name', kb_id)
        # local_doc_qa.milvus_summary.new_milvus_base(kb_id, user_id, kb_name)
        # debug_logger.info(f"new knowledge base kb_id: {kb_id} kb_name: {kb_name} sucess!!!")
        return return_sanic({"code": 400, "msg": f"fail, knowledge Base {kb_id} not exist, please create first."})
    elif not_exist_kb_ids and not_exist_kb_ids[0][1] != "not_exist": # 说明知识库已经存在，但是属于其他用户
        return return_sanic({"code": 400, "msg": f"fail, knowledge Base {kb_id} already exist, {not_exist_kb_ids[0][1]}"})
        
    exist_files = local_doc_qa.milvus_summary.get_files_count(user_id, kb_id)[0][0]
    if exist_files + len(files) > 10000:
        return return_sanic({"code": 400,
                           "msg": f"fail, exist files is {len(exist_files)}, upload files is {len(files)}, total files is {len(exist_files) + len(files)}, max length is 10000."})


    kb_chunk_size = local_doc_qa.milvus_summary.get_kb_parser_config(kb_id).get('chunk_size', DEFAULT_PARENT_CHUNK_SIZE)
    chunk_size = safe_get(req, 'chunk_size', kb_chunk_size)
    debug_logger.info("chunk_size: %s", chunk_size)
    
    parser_outline = safe_get(req, 'parser_outline', False)
    parser_summary = safe_get(req, 'parser_summary', False)
    debug_logger.info(f"parser_outline: {parser_outline}, parser_summary: {parser_summary}")



    data = []
    local_files = []
    file_names = []
    for file in files:
        if isinstance(file, str):
            file_name = os.path.basename(file)
        else:
            debug_logger.info('ori name: %s', file.name)
            file_name = urllib.parse.unquote(file.name, encoding='UTF-8')
            debug_logger.info('decode name: %s', file_name)
        # # 使用正则表达式替换以%开头的字符串
        # file_name = re.sub(r'%\w+', '', file_name)
        # 删除掉全角字符, 删掉空格
        # file_name = re.sub(r'[\uFF01-\uFF5E\u3000-\u303F]', '', file_name)
        file_name = re.sub(r' ', '', file_name) # 删除空格
        debug_logger.info('cleaned name: %s', file_name)
        # max_length = 255 - len(construct_qanything_local_file_nos_key_prefix(file_id)) == 188
        file_name = truncate_filename(file_name, max_length=200)
        file_names.append(file_name)

    exist_file_names = []
    if mode == 'soft':
        exist_files = local_doc_qa.milvus_summary.check_file_exist_by_name(user_id, kb_id, file_names)
        exist_file_names = [f[1] for f in exist_files]
        for exist_file in exist_files:
            file_id, file_name, file_size, status = exist_file
            debug_logger.info(f"{file_name}, {status}, existed files, skip upload")
            # await post_data(user_id, -1, file_id, status, msg='existed files, skip upload')

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M")

    failed_files = []
    for file, file_name, file_id in zip(files, file_names, file_ids):
        if file_name in exist_file_names:
            continue
        local_file = LocalFile(user_id, kb_id, file, file_name, file_id)
        time.sleep(0.1)  # 确保文件被正确写入磁盘
        chars = fast_estimate_file_char_count(local_file.file_location)
        debug_logger.info(f"{file_name} char_size: {chars}")
        if chars and chars > MAX_CHARS:
            debug_logger.warning(f"fail, file {file_name} chars is {chars}, max length is {MAX_CHARS}.")
            # return return_sanic({"code": 2003, "msg": f"fail, file {file_name} chars is too much, max length is {MAX_CHARS}."})
            failed_files.append(file_name)
            continue
        file_id = local_file.file_id
        file_size = len(local_file.file_content)
        file_location = local_file.file_location
        local_files.append(local_file)
        msg = local_doc_qa.milvus_summary.add_file(file_id, user_id, kb_id, file_name, file_size, file_location,
                                                   chunk_size, timestamp)
        upload_infos = {
            "parser_outline": parser_outline,
            "parser_summary": parser_summary
        }
        # 更新文件上传信息
        local_doc_qa.milvus_summary.update_file_upload_infos(file_id, upload_infos)
        debug_logger.info(f"{file_name}, {file_id}, {msg}")
        data.append(
            {"file_id": file_id, "file_name": file_name, "status": "gray", "bytes": len(local_file.file_content),
             "timestamp": timestamp, "estimated_chars": chars})

    # asyncio.create_task(local_doc_qa.insert_files_to_milvus(user_id, kb_id, local_files))
    if exist_file_names:
        msg = f'warning，当前的mode是soft，无法上传同名文件{exist_file_names}，如果想强制上传同名文件，请设置mode：strong'
    elif failed_files:
        msg = f"warning, {failed_files} chars is too much, max characters length is {MAX_CHARS}, skip upload."
    else:
        msg = "success，后台正在飞速上传文件，请耐心等待"
    return return_sanic({"code": 200, "msg": msg, "data": data})


@get_time_async
async def upload_chunks(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("upload_chunks %s", user_id)
    debug_logger.info("user_info %s", user_info)
    kb_id = safe_get(req, 'kb_id')
    kb_id = correct_kb_id(kb_id)
    debug_logger.info("kb_id %s", kb_id)

    file_id = safe_get(req, 'file_id', uuid.uuid4().hex)
    file_name = safe_get(req, 'file_name', file_id+".txt")
    debug_logger.info("file_id %s", file_id)
    debug_logger.info("file_name %s", file_name)
    chunk_datas = safe_get(req, 'chunk_datas')
    if not isinstance(chunk_datas, list):
        return return_sanic({"code": 400, "msg": f'输入chunk格式非法！请检查！'})
    debug_logger.info(f"chunk_datas size {len(chunk_datas)}")

    not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, [kb_id])
    if not_exist_kb_ids and not_exist_kb_ids[0][1] == "not_exist": # 说明知识库不存在
        debug_logger.info(f"invalid kb_id: {not_exist_kb_ids} new knowledge base")
        # kb_id不存在则直接创建一个，kb_name直接使用kb_id
        # kb_name = safe_get(req, 'kb_name', kb_id)
        # local_doc_qa.milvus_summary.new_milvus_base(kb_id, user_id, kb_name)
        # debug_logger.info(f"new knowledge base kb_id: {kb_id} kb_name: {kb_name} sucess!!!")
        return return_sanic({"code": 400, "msg": f"fail, knowledge Base {kb_id} not exist, please create first."})
    elif not_exist_kb_ids and not_exist_kb_ids[0][1] != "not_exist": # 说明知识库已经存在，但是属于其他用户
        return return_sanic({"code": 400, "msg": f"fail, knowledge Base {kb_id} already exist, {not_exist_kb_ids[0][1]}"})
        
    exist_files = local_doc_qa.milvus_summary.check_file_exist(user_id, kb_id, [file_id])
    if exist_files:
        debug_logger.info(f"{file_id}, existed files, skip upload")
        return return_sanic({"code": 400, "msg": f'输入file_id:{file_id}已存在，请检查！'})

    exist_files = local_doc_qa.milvus_summary.get_files_count(user_id, kb_id)[0][0]
    if exist_files + 1 > 10000:
        return return_sanic({"code": 401,
                        "msg": f"fail, exist files is {len(exist_files)}, upload files is 1, max length is 10000."})

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M")

    
    file_str_save = "\n[chunk-split]\n".join(chunk_datas)   #.encode('utf-8')
    file_str_save += "\n[chunk-split]\n"


    from qanything_kernel.configs.model_config import UPLOAD_ROOT_PATH
    upload_path = os.path.join(UPLOAD_ROOT_PATH, user_id)
    file_dir = os.path.join(upload_path, kb_id, file_id)
    os.makedirs(file_dir, exist_ok=True)
    file_location = os.path.join(file_dir, file_name)
    debug_logger.info(f"file_location: {file_location}")
    with open(file_location, 'w') as f:
        f.write(file_str_save)
                

    file_size = len(file_str_save)
    
    
    msg = local_doc_qa.milvus_summary.add_file(file_id, user_id, kb_id, file_name, file_size, file_location, DEFAULT_PARENT_CHUNK_SIZE, timestamp)
    debug_logger.info(f"{file_name}, {file_id}, {msg}")
    data=[ {"file_id": file_id, "file_name": file_name, "status": "gray", "bytes": file_size, "timestamp": timestamp}]

    
    msg = "success，后台正在飞速上传文件，请耐心等待"
    return return_sanic({"code": 200, "msg": msg, "data": data})


@get_time_async
async def upload_faqs(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("upload_faqs %s", user_id)
    debug_logger.info("user_info %s", user_info)
    kb_id = safe_get(req, 'kb_id')
    kb_id = correct_kb_id(kb_id)
    debug_logger.info("kb_id %s", kb_id)
    faqs = safe_get(req, 'faqs')
    # if faqs is None or len(faqs) == 0:
    #     return return_sanic({"code": 2001, "msg": "faqs is empty"})
    
    # 增加上传文件的功能和上传文件的检查解析
    file_status = {}
    if faqs is None:
        files = req.files.getlist('files')
        faqs = []
        for file in files:
            debug_logger.info('ori name: %s', file.name)
            file_name = urllib.parse.unquote(file.name, encoding='UTF-8')
            debug_logger.info('decode name: %s', file_name)
            # 删除掉全角字符
            # file_name = re.sub(r'[\uFF01-\uFF5E\u3000-\u303F]', '', file_name)
            file_name = file_name.replace("/", "_")
            debug_logger.info('cleaned name: %s', file_name)
            file_name = truncate_filename(file_name)
            file_faqs = check_and_transform_excel(file.body)
            if isinstance(file_faqs, str):
                file_status[file_name] = file_faqs
                debug_logger.error(f"file_name: {file_name}, file_faqs: {file_faqs}")
                return return_sanic({"code": 400, "msg": f"file_name: {file_name}, {file_faqs}"})
            else:
                faqs.extend(file_faqs)
                file_status[file_name] = "success"

    
    debug_logger.info(f"faqs size: {len(faqs)}")
    file_ids = safe_get(req, 'file_ids', [])
    if len(file_ids)>0 and len(file_ids) != len(faqs):
        return return_sanic({"code": 400, "msg": "file_ids and faqs length not equal"})
    if len(file_ids) == 0:
        for i in range(len(faqs)):
            file_ids.append(uuid.uuid4().hex)
    else:
        # 判断file_id是否合法存在
        exist_file_id = local_doc_qa.milvus_summary.check_file_exist(user_id, kb_id, file_ids)
        if exist_file_id:
            return return_sanic({"code": 400, "msg": f"file_id {exist_file_id} exist"})


    chunk_size = safe_get(req, 'chunk_size', default=DEFAULT_PARENT_CHUNK_SIZE)
    debug_logger.info("chunk_size: %s", chunk_size)


    if len(faqs) > 10000:
        return return_sanic({"code": 401, "msg": f"fail, faqs too many, max length is 10000."})

    not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, [kb_id])
    if not_exist_kb_ids and not_exist_kb_ids[0][1] == "not_exist": # 说明知识库不存在
        debug_logger.info(f"invalid kb_id: {not_exist_kb_ids} new knowledge base")
        # kb_id不存在则直接创建一个，kb_name直接使用kb_id
        # kb_name = safe_get(req, 'kb_name', kb_id)
        # local_doc_qa.milvus_summary.new_milvus_base(kb_id, user_id, kb_name)
        # debug_logger.info(f"new knowledge base kb_id: {kb_id} kb_name: {kb_name} sucess!!!")
        return return_sanic({"code": 400, "msg": f"fail, knowledge Base {kb_id} not exist, please create first."})
    elif not_exist_kb_ids and not_exist_kb_ids[0][1] != "not_exist": # 说明知识库已经存在，但是属于其他用户
        return return_sanic({"code": 400, "msg": f"fail, knowledge Base {kb_id} already exist, {not_exist_kb_ids[0][1]}"})

    data = []
    data_skip = []
    local_files = []
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M")
    debug_logger.info(f"start insert {len(faqs)} faqs to mysql, user_id: {user_id}, kb_id: {kb_id}")
    for faq,file_id in zip(faqs, file_ids):
        ques = faq['question']
        if len(ques) > 512 or len(faq['answer']) > 8000:
            return return_sanic(
                {"code": 400, "msg": f"fail, faq too long, max length of question is 512, answer is 8000."})
        file_name = f"FAQ_{ques}.faq"
        file_name = file_name.replace("/", "_").replace(":", "_")  # 文件名中的/和：会导致写入时出错
        # file_name = simplify_filename(file_name)
        file_size = len(ques) + len(faq['answer'])
        faq_id = local_doc_qa.milvus_summary.get_faq_by_question(ques, kb_id)
        if faq_id:
            debug_logger.info(f"faq question {ques} already exist, skip")
            data_skip.append({
                "file_id": faq_id,
                "file_name": file_name,
                "status": "green",
                "length": file_size,
                "timestamp": local_doc_qa.milvus_summary.get_file_timestamp(faq_id),
                "msg": "faq question already exist, skip"
            })
            continue
        local_file = LocalFile(user_id, kb_id, faq, file_name, file_id)
        file_location = local_file.file_location
        local_files.append(local_file)
        local_doc_qa.milvus_summary.add_faq(file_id, user_id, kb_id, faq['question'], faq['answer'], faq.get('nos_keys', ''))
        local_doc_qa.milvus_summary.add_file(file_id, user_id, kb_id, file_name, file_size, file_location,
                                             chunk_size, timestamp)
        # debug_logger.info(f"{file_name}, {file_id}, {msg}, {faq}")
        data.append(
            {"file_id": file_id, "file_name": file_name, "status": "gray", "length": file_size,
             "timestamp": timestamp})
    debug_logger.info(f"end insert {len(faqs)} faqs to mysql, user_id: {user_id}, kb_id: {kb_id}")

    msg = "success，后台正在飞速上传文件，请耐心等待"
    return return_sanic({"code": 200, "msg": msg, "data": data, "data_skip": data_skip})



@get_time_async
async def document_parser(req: request):
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    
    file = req.files.get('file')
    debug_logger.info('ori name: %s', file.name)
    file_name = urllib.parse.unquote(file.name, encoding='UTF-8')
    debug_logger.info('decode name: %s', file_name)
    # file_name = re.sub(r'[\uFF01-\uFF5E\u3000-\u303F]', '', file_name)
    file_name = file_name.replace("/", "_")
    debug_logger.info('cleaned name: %s', file_name)
    file_name = truncate_filename(file_name)
    debug_logger.info('truncated name: %s', file_name)

    local_file = LocalFile(user_id, "KBdocumentparser", file, file_name)
    docs =  local_file.get_document_parser()
    return return_sanic({"code": 200, "msg": "success", "data": docs})
    


@get_time_async
async def list_kbs(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("list_kbs %s", user_id)
    kb_infos = local_doc_qa.milvus_summary.get_knowledge_bases(user_id)
    kb_name = safe_get(req, 'kb_name')  # 用于查询指定的知识库信息
    debug_logger.info("kb_name: %s", kb_name)

    try:
        kb_id = safe_get(req, 'kb_id')  # 用于查询指定的知识库信息
        if kb_id:
            kb_id = correct_kb_id(kb_id)

        data = []
        for kb in kb_infos:
            if kb_name and kb_name not in kb[1]:
                continue
            if kb_id and kb[0] != kb_id:
                continue

            file_count = local_doc_qa.milvus_summary.get_files_count(user_id, kb[0])[0][0]
            kb_info = {
                "kb_id": kb[0], 
                "kb_name": kb[1], 
                "file_count": file_count,
                "creation_time": kb[2].strftime("%Y%m%d%H%M") if kb[2] else None,
                "parser_config": json.loads(kb[3]) if kb[3] else {}, 
                "kb_metadata": json.loads(kb[4]) if kb[4] else {}}
            debug_logger.info("kb infos: {}".format(kb_info))
            data.append(kb_info)
    
        return return_sanic({"code": 200, "data": data})
    except Exception as e:
        debug_logger.error("list_kbs error: %s", str(e))
        return return_sanic({"code": 500, "msg": str(e)})


@get_time_async
async def list_docs(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("list_docs %s", user_id)
    kb_id = safe_get(req, 'kb_id')
    kb_id = correct_kb_id(kb_id)
    debug_logger.info("kb_id: {}".format(kb_id))
    not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, [kb_id])
    if not_exist_kb_ids:
        return return_sanic({"code": 400, "msg": "fail, knowledge Base {} not found".format(not_exist_kb_ids)})

    file_id = safe_get(req, 'file_id')  # 用于查询指定的文件信息
    file_name = safe_get(req, 'file_name')  # 用于查询指定的文件信息
    file_status = safe_get(req, 'status')  # green, red, yellow, gray，用于查询指定状态的文件信息
    if not file_status:
        file_status = None
    debug_logger.info("file_id: {}, file_name: {}, status: {}".format(file_id, file_name, file_status))
    
    # 分页参数
    page_id = safe_get(req, 'page_id', 1)  # 默认为第一页
    page_limit = safe_get(req, 'page_limit', 10)  # 默认每页显示10条记录
    data = []
    data_red = []
    if file_id is None:
        # file_infos = local_doc_qa.milvus_summary.get_files(user_id, kb_id)
        file_count = local_doc_qa.milvus_summary.get_files_count(user_id, kb_id)[0][0]
        green_file_count = local_doc_qa.milvus_summary.get_files_count(user_id, kb_id, 'green')[0][0]
        debug_logger.info(f"file_count: {file_count}, green_file_count: {green_file_count}")

        red_file_count = local_doc_qa.milvus_summary.get_files_count(user_id, kb_id, 'red')[0][0]
        yellow_file_count = local_doc_qa.milvus_summary.get_files_count(user_id, kb_id, 'yellow')[0][0]
        gray_file_count = local_doc_qa.milvus_summary.get_files_count(user_id, kb_id, 'gray')[0][0]
        status_count = {
            'green': green_file_count,      # "上传成功"
            'red': red_file_count,          # "上传出错，请删除后重试或联系工作人员"
            'yellow': yellow_file_count,    # "已进入上传队列，请耐心等待"
            'gray': gray_file_count         # "已上传到服务器，进入上传等待队列"
        }
        debug_logger.info(f"file_count: {file_count}, status_count: {status_count}")

        # 计算总记录数, 计算总页数
        total_count = file_count
        total_pages = (total_count + page_limit - 1) // page_limit
        if page_id > total_pages and total_count != 0:
            return return_sanic({"code": 400, "msg": f'输入非法！page_id超过最大值，page_id: {page_id}，最大值：{total_pages}，请检查！'})
        # 计算当前页的起始和结束索引
        start_index = (page_id - 1) * page_limit
        current_page_data = local_doc_qa.milvus_summary.get_files(user_id, kb_id, file_name=file_name, status=file_status, limit=page_limit, offset=start_index)
        data = []
        for file_info in current_page_data:
            data.append({"file_id": file_info[0], "file_name": file_info[1], "status": file_info[2], "bytes": file_info[3],
                     "content_length": file_info[4], "timestamp": file_info[5], "file_location": file_info[6],
                     "file_url": file_info[7], "chunks_number": file_info[8], "msg": file_info[9], "file_metadata": file_info[10]})
            if file_info[1].endswith('.faq'):
                faq_info = local_doc_qa.milvus_summary.get_faq(file_info[0])
                user_id, kb_id, question, answer, nos_keys = faq_info
                data[-1]['question'] = question
                data[-1]['answer'] = answer

        data_red = []
        data_red_infos = local_doc_qa.milvus_summary.get_files(user_id, kb_id, status='red')
        for file_info in data_red_infos:
            data_red.append({"file_id": file_info[0], "file_name": file_info[1], "status": file_info[2], "bytes": file_info[3],
                             "content_length": file_info[4], "timestamp": file_info[5], "file_location": file_info[6], 
                             "file_url": file_info[7], "chunks_number": file_info[8], "msg": file_info[9], "file_metadata": file_info[10]})
        
        return return_sanic({
            "code": 200,
            "msg": "success",
            "data": {
                'total_page': total_pages,  # 总页数
                "total": total_count,  # 总文件数
                "status_count": status_count,  # 各状态的文件数
                "details": data,  # 当前页码下的文件目录
                "page_id": page_id,  # 当前页码,
                "page_limit": page_limit,  # 每页显示的文件数
                "data_red": data_red
            }
        })

    else:
        file_info = local_doc_qa.milvus_summary.get_files(user_id, kb_id, file_id)[0]
        data = [{"file_id": file_info[0], "file_name": file_info[1], "status": file_info[2], "bytes": file_info[3],
                             "content_length": file_info[4], "timestamp": file_info[5], "file_location": file_info[6], 
                             "file_url": file_info[7], "chunks_number": file_info[8], "msg": file_info[9]}]
        if file_info[1].endswith('.faq'):
            faq_info = local_doc_qa.milvus_summary.get_faq(file_info[0])
            user_id, kb_id, question, answer, nos_keys = faq_info
            data[-1]['question'] = question
            data[-1]['answer'] = answer
        return return_sanic({"code": 200, "msg": "success", "data": data})


@get_time_async
async def get_files_statu(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("get_files_statu %s", user_id)

    file_ids = safe_get(req, 'file_ids')
    debug_logger.info("get_files_statu %s", file_ids)
    data = []
    status_count = {}
    if file_ids is None or len(file_ids) == 0:
        return return_sanic({"code": 400, "msg": "fail, file_ids is None"})
    else:
        for file_id in file_ids:
            kb_id = local_doc_qa.milvus_summary.get_kbid_by_fileid(file_id)
            if kb_id is None:
                # return return_sanic({"code": 2003, "msg": "fail, file_id {} not found".format(file_id)})
                data.append({"file_id": file_id, "file_name": "", "status": "red", "bytes": 0, "timestamp": "0", "msg": "fail, file_id {} not found".format(file_id)})
                if "red" not in status_count:
                    status_count["red"] = 1
                else:
                    status_count["red"] += 1
                continue
            file_info = local_doc_qa.milvus_summary.get_files(user_id, kb_id, file_id)
            if not file_info:
                # return return_sanic({"code": 2003, "msg": "fail, file_id {} not found".format(file_id)})
                data.append({"file_id": file_id, "file_name": "", "status": "red", "bytes": 0, "timestamp": "0", "msg": "fail, file_id {} not found".format(file_id)})
                if "red" not in status_count:
                    status_count["red"] = 1
                else:
                    status_count["red"] += 1
            else:
                file_info = file_info[0]
                status = file_info[2]
                if status not in status_count:
                    status_count[status] = 1
                else:
                    status_count[status] += 1
                data.append({"file_id": file_info[0], "file_name": file_info[1], "status": file_info[2], "bytes": file_info[3],
                            "content_length": file_info[4], "timestamp": file_info[5], "file_location": file_info[6],
                            "file_url": file_info[7], "chunks_number": file_info[8], "msg": file_info[9], "file_metadata": file_info[10]})
                if file_info[1].endswith('.faq'):
                    faq_info = local_doc_qa.milvus_summary.get_faq(file_info[0])
                    user_id, kb_id, question, answer, nos_keys = faq_info
                    data[-1]['question'] = question
                    data[-1]['answer'] = answer
    
    # msg_map = {'gray': "已上传到服务器，进入上传等待队列",
    #            'red': "上传出错，请删除后重试或联系工作人员",
    #            'yellow': "已进入上传队列，请耐心等待", 'green': "上传成功"}
    
    data = sorted(data, key=lambda x: int(x['timestamp']), reverse=True)

    return return_sanic({
        "code": 200,
        "msg": "success",
        "data": {
            "total": status_count,  # 各状态的文件数
            "details": data,  # 当前页码下的文件目录
        }
    })


@get_time_async
async def delete_knowledge_base(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    # TODO: 确认是否支持批量删除知识库
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("delete_knowledge_base %s", user_id)
    kb_ids = safe_get(req, 'kb_id')
    if kb_ids is None or len(kb_ids) == 0:
        kb_ids = safe_get(req, 'kb_ids')
        kb_ids = [correct_kb_id(kb_id) for kb_id in kb_ids]
    else:
        kb_ids = [correct_kb_id(kb_ids)]
    not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, kb_ids)
    if not_exist_kb_ids:
        return return_sanic({"code": 400, "msg": "fail, knowledge Base {} not found".format(not_exist_kb_ids)})
    
    
    # 添加file_ids，支持删除知识库中的一个或多个文件
    del_file_ids = safe_get(req, "file_ids", None)
    
    for kb_id in kb_ids:
        file_infos = []
        if del_file_ids is not None:
            valid_file_infos = local_doc_qa.milvus_summary.check_file_exist(user_id, kb_id, del_file_ids)
            if len(valid_file_infos) == 0:
                return return_sanic({"code": 400, "msg": "fail, files {} not found".format(del_file_ids)})
            for file_id in del_file_ids:
                file_info = local_doc_qa.milvus_summary.get_files(user_id, kb_id, file_id)
                file_infos.extend(file_info)
        else:
            file_count = local_doc_qa.milvus_summary.get_files_count(user_id, kb_id)[0][0]
            file_infos = local_doc_qa.milvus_summary.get_files(user_id, kb_id, limit=file_count)  # 如果太长特别耗时
        file_ids = [file_info[0] for file_info in file_infos]
        file_chunks = [file_info[8] for file_info in file_infos]
        
        # 删除es中的记录
        asyncio.create_task(run_in_background(local_doc_qa.es_client.delete_files, file_ids, file_chunks))
        
        # 删除milvus中的记录
        expr = f"""kb_id == "{kb_id}" and file_id in {file_ids}"""
        parser_config = local_doc_qa.milvus_summary.get_kb_parser_config(kb_id)
        milvus_kb = VectorStoreMilvusClient(parser_config)
        asyncio.create_task(run_in_background(milvus_kb.delete_expr, expr))
        
        # 删除mysql中的文件对应记录
        local_doc_qa.milvus_summary.delete_documents(file_ids)
        local_doc_qa.milvus_summary.delete_faqs(file_ids)
        local_doc_qa.milvus_summary.delete_files(kb_id, file_ids)
        
        # 删除本地对应的文件
        for file_info in file_infos:
            file_location = os.path.join(UPLOAD_ROOT_PATH, user_id, kb_id, file_info[0])
            if file_location is not None and os.path.exists(file_location):
                shutil.rmtree(os.path.abspath(file_location))
                debug_logger.info("delete_docs file_dir %s", os.path.abspath(file_location))
            
            images_dir = os.path.join(IMAGES_ROOT_PATH, file_info[0])
            if os.path.exists(images_dir):
                shutil.rmtree(images_dir)
                debug_logger.info("delete_docs images_dir %s", images_dir)
        if del_file_ids is None:
            kb_location = os.path.join(UPLOAD_ROOT_PATH, user_id, kb_id)
            if os.path.exists(kb_location):
                shutil.rmtree(os.path.abspath(kb_location))
                debug_logger.info("delete_docs kb_location %s", os.path.abspath(kb_location))

    if del_file_ids is not None:
        debug_logger.info(f"""delete knowledge base {kb_ids}'s files {file_ids} success""")
        return return_sanic({"code": 200, "msg": "Knowledge Base {}'s files {} delete success".format(kb_ids, file_ids)})
    
    
    # 如果是删除知识库，则删除知识库对应的文件夹，一级mysql中对应的知识库表
    local_doc_qa.milvus_summary.delete_knowledge_base(user_id, kb_ids)
    debug_logger.info(f"""delete knowledge base {kb_ids} success""")
    return return_sanic({"code": 200, "msg": "Knowledge Base {} delete success".format(kb_ids)})


@get_time_async
async def rename_knowledge_base(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("rename_knowledge_base %s", user_id)
    kb_id = safe_get(req, 'kb_id')
    kb_id = correct_kb_id(kb_id)
    new_kb_name = safe_get(req, 'new_kb_name')
    not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, [kb_id])
    if not_exist_kb_ids:
        return return_sanic({"code": 400, "msg": "fail, knowledge Base {} not found".format(not_exist_kb_ids[0])})
    local_doc_qa.milvus_summary.rename_knowledge_base(user_id, kb_id, new_kb_name)
    return return_sanic({"code": 200, "msg": "Knowledge Base {} rename success".format(kb_id)})


@get_time_async
async def delete_docs(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("delete_docs %s", user_id)
    kb_id = safe_get(req, 'kb_id')
    kb_id = correct_kb_id(kb_id)
    file_ids = safe_get(req, "file_ids")
    not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, [kb_id])
    if not_exist_kb_ids:
        return return_sanic({"code": 400, "msg": "fail, knowledge Base {} not found".format(not_exist_kb_ids[0])})
    valid_file_infos = local_doc_qa.milvus_summary.check_file_exist(user_id, kb_id, file_ids)
    if len(valid_file_infos) == 0:
        return return_sanic({"code": 400, "msg": "fail, files {} not found".format(file_ids)})
    valid_file_ids = [file_info[0] for file_info in valid_file_infos]
    
    # 删除milvus中记录
    # milvus_kb = local_doc_qa.match_milvus_kb(user_id, [kb_id])
    # milvus_kb.delete_files(file_ids)
    expr = f"""kb_id == "{kb_id}" and file_id in {valid_file_ids}"""  # 删除数据库中的记录
    parser_config = local_doc_qa.milvus_summary.get_kb_parser_config(kb_id)
    milvus_kb = VectorStoreMilvusClient(parser_config)
    asyncio.create_task(run_in_background(milvus_kb.delete_expr, expr))
    # local_doc_qa.milvus_kb.delete_expr(expr)
    
    # 删除es中记录
    file_chunks = local_doc_qa.milvus_summary.get_chunk_size(valid_file_ids)
    asyncio.create_task(run_in_background(local_doc_qa.es_client.delete_files, valid_file_ids, file_chunks))

    # 删除mysql中记录
    local_doc_qa.milvus_summary.delete_files(kb_id, valid_file_ids)
    local_doc_qa.milvus_summary.delete_documents(valid_file_ids)
    local_doc_qa.milvus_summary.delete_faqs(valid_file_ids)

    # 删除本地对应的文件
    for file_info in valid_file_infos:
        file_location = os.path.join(UPLOAD_ROOT_PATH, user_id, kb_id, file_info[0])    # 可能存在的问题，其他user_id在删除的时候，该目录会找不到哦
        if file_location is not None and os.path.exists(file_location):
            shutil.rmtree(os.path.abspath(file_location))
            debug_logger.info("delete_docs file_dir %s", os.path.abspath(file_location))
        
        images_dir = os.path.join(IMAGES_ROOT_PATH, file_info[0])
        if os.path.exists(images_dir):
            shutil.rmtree(images_dir)
            debug_logger.info("delete_docs images_dir %s", images_dir)

    debug_logger.info(f"""delete knowledge base {kb_id}'s files {valid_file_ids} success""")
    return return_sanic({"code": 200, "msg": "documents {} delete success".format(valid_file_ids)})


@get_time_async
async def get_total_status(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info('get_total_status %s', user_id)
    res={}
    res[user_id] = {}
    kbs = local_doc_qa.milvus_summary.get_knowledge_bases(user_id)
    for kb_info in kbs:
        kb_id, kb_name = kb_info[0], kb_info[1]
        # gray_file_infos = local_doc_qa.milvus_summary.get_file_by_status([kb_id], 'gray')
        # red_file_infos = local_doc_qa.milvus_summary.get_file_by_status([kb_id], 'red')
        # yellow_file_infos = local_doc_qa.milvus_summary.get_file_by_status([kb_id], 'yellow')
        # green_file_infos = local_doc_qa.milvus_summary.get_file_by_status([kb_id], 'green')
        red_file_count = local_doc_qa.milvus_summary.get_files_count(user_id, kb_id, 'red')[0][0]
        yellow_file_count = local_doc_qa.milvus_summary.get_files_count(user_id, kb_id, 'yellow')[0][0]
        gray_file_count = local_doc_qa.milvus_summary.get_files_count(user_id, kb_id, 'gray')[0][0]
        green_file_count = local_doc_qa.milvus_summary.get_files_count(user_id, kb_id, 'green')[0][0]
        res[user_id][kb_id] = {'green': green_file_count, 
                                'yellow': yellow_file_count,
                                'red': red_file_count,
                                'gray': gray_file_count}

    return return_sanic({"code": 200, "status": res})


@get_time_async
async def clean_files_by_status(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info('clean_files_by_status %s', user_id)
    status = safe_get(req, 'status', default='gray')
    if status not in ['gray', 'red', 'yellow']:
        return return_sanic({"code": 400, "msg": "fail, status {} must be in ['gray', 'red', 'yellow']".format(status)})
    kb_ids = safe_get(req, 'kb_ids')
    kb_ids = [correct_kb_id(kb_id) for kb_id in kb_ids]
    if not kb_ids:
        kbs = local_doc_qa.milvus_summary.get_knowledge_bases(user_id)
        kb_ids = [kb[0] for kb in kbs]
    else:
        not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, kb_ids)
        if not_exist_kb_ids:
            return return_sanic({"code": 400, "msg": "fail, knowledge Base {} not found".format(not_exist_kb_ids)})

    gray_file_infos = local_doc_qa.milvus_summary.get_file_by_status(kb_ids, status)
    gray_file_ids = [f[0] for f in gray_file_infos]
    gray_file_names = [f[1] for f in gray_file_infos]
    debug_logger.info(f'{status} files number: {len(gray_file_names)}')
    # 删除milvus中的file
    if gray_file_ids:
        # expr = f"file_id in \"{gray_file_ids}\""
        # asyncio.create_task(run_in_background(local_doc_qa.milvus_kb.delete_expr, expr))
        for kb_id in kb_ids:
            local_doc_qa.milvus_summary.delete_files(kb_id, gray_file_ids)
    return return_sanic({"code": 200, "msg": f"delete {status} files success", "data": gray_file_names})


@get_time_async
async def question_rag_search(req: request):
    preprocess_start = time.perf_counter()
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa

    # 检查用户id和user_info是否合法
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info('question_rag_search %s', user_id)
    debug_logger.info('user_info %s', user_info)
    
    # 检查知识库是否存在，解析配置是否一致，获取知识库的parser_config
    kb_ids = safe_get(req, 'kb_ids', [])
    kb_ids = [correct_kb_id(kb_id) for kb_id in kb_ids]
    ignore_file_error = safe_get(req, 'ignore_file_error', False) # 新增参数，用于忽略文件不存在或未审核的错误
    parser_config = {}      # 判断每个知识库的parser_config是否一致
    valid_files_num = 0  # 统计知识库中可用的文件数量
    if kb_ids:
        not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, kb_ids)
        if not_exist_kb_ids:
            if ignore_file_error:
                msg += f"warnning, kb_ids {not_exist_kb_ids}."
            else:
                return return_sanic({"code": 400, "msg": "fail, knowledge Base {}".format(not_exist_kb_ids)})
        not_exist_kb_ids = [x[0] for x in not_exist_kb_ids]
        kb_ids = [kb for kb in kb_ids if kb not in not_exist_kb_ids]
        if kb_ids:
            parser_config = local_doc_qa.milvus_summary.get_kb_parser_config(kb_ids[0])
            valid_files_num += local_doc_qa.milvus_summary.get_files_count(user_id, kb_ids[0], status='green')[0][0]
            for kb_id in kb_ids[1:]:
                # 继续检查parser_config中的embeding模型是否一致
                tmp_parser_config = local_doc_qa.milvus_summary.get_kb_parser_config(kb_id)
                if tmp_parser_config['embedding_model_name'] != parser_config['embedding_model_name']:
                    return return_sanic({"code": 400, "msg": "fail, knowledge Base {}'s parser_config not same".format(kb_ids)})
                valid_files_num += local_doc_qa.milvus_summary.get_files_count(user_id, kb_id, status='green')[0][0]
        
    # 检查输入的file_ids是否合法，增加一个file_ids参数，用于指定需要查询的文件，默认为空，与kb_ids同时存在，两个取并集
    file_ids = safe_get(req, 'file_ids', [])
    valid_file_ids = []
    if len(file_ids) > 0:
        valid_file_infos = local_doc_qa.milvus_summary.check_file_exist_byuserid(user_id, file_ids)
        if len(valid_file_infos) != len(file_ids):
            notexist_file_ids = list(set(file_ids) - set([file_info[0] for file_info in valid_file_infos]))
            if ignore_file_error:
                msg += f"warnning, files {notexist_file_ids} not found.\n"
            else:
                return return_sanic({"code": 400, "msg": "fail, files {} not found".format(notexist_file_ids)})
        unvalid_file_ids = [file_info[0] for file_info in valid_file_infos if file_info[1] != 'green']
        valid_file_ids = [file_info[0] for file_info in valid_file_infos if file_info[1] == 'green']
        # 获取文件信息，判断知识库解析参数是否一致
        for tmp_file_id in valid_file_ids:
            tmp_kb_id = local_doc_qa.milvus_summary.get_kbid_by_fileid(tmp_file_id)
            tmp_parser_config = local_doc_qa.milvus_summary.get_kb_parser_config(tmp_kb_id)
            if not parser_config:
                parser_config = tmp_parser_config
            elif tmp_parser_config['embedding_model_name'] != parser_config['embedding_model_name']:
                return return_sanic({"code": 400, "msg": "fail, files {}'s parser_config not same".format(file_ids)})
        valid_files_num += len(valid_file_ids)
        if len(unvalid_file_ids) > 0:
            if ignore_file_error:
                msg += f"wanrnning, files {unvalid_file_ids} not green.\n"
            else:
                return return_sanic({"code": 400, "msg": "fail, files {} not green".format(unvalid_file_ids)})
    
    # 判断输入的所有检索参数是否有可用检索对象
    if valid_files_num == 0 and not need_web_search:
        debug_logger.info("valid_files is empty, use only chat mode.")
        return return_sanic({
            "code": 200, 
            "msg": "当前知识库没有可用文档，且不需要联网检索，请上传文件或等待文件解析完毕", 
            "question": question,
            "retrieval_documents": []})

    # 读取并处理history，用于query改写
    history = safe_get(req, 'history', None)
    try:
        if isinstance(history, str):
            messages = json.loads(history)["messages"]
            history = []
            for message in messages:
                if message["role"] == "user":
                    history.append([message["content"]])
                elif message["role"] == "assistant":
                    history[-1].append(message["content"])
                else:
                    continue
            if len(history[-1]) != 2:
                history.pop()
        elif isinstance(history, list):  # 只检查是否是列表
            # 然后可以进一步检查列表内容
            if all(isinstance(item, list) for item in history):
                if all(isinstance(subitem, str) for item in history for subitem in item):
                    # 符合 List[List[str]] 的结构
                    pass
                else:
                    debug_logger.error("history is list but not List[List[str]]")
                    return return_sanic({"code": 400, "msg": "fail, history is list but not List[List[str]]"})
            else:
                debug_logger.error("history is list but not List[List[str]]")
                return return_sanic({"code": 400, "msg": "fail, history is list but not List[List[str]]"})
        elif history is None:
            debug_logger.info("history is None")
        else:
            debug_logger.error("history is not str or None")
            return return_sanic({"code": 400, "msg": "fail, history is not str or None"})
    except Exception as e:
        debug_logger.error(f"history parser error: {e}")
        return return_sanic({"code": 500, "msg": "fail, history parser error {}".format(e)})

    # 读取rerank参数
    rerank = safe_get(req, 'rerank', default=True)
    if rerank:
        debug_logger.info("rerank is True")
        from qanything_kernel.configs.model_config import LOCAL_RERANK_SERVICE_URL, RERANK_MODEL_NAME, RERANK_API_KEY
        from qanything_kernel.connector.rerank.rerank_for_online_client import GeneralRerank
        rerank_url = safe_get(req, 'rerank_url', default=LOCAL_RERANK_SERVICE_URL)
        rerank_model_name = safe_get(req, 'rerank_model_name', default=RERANK_MODEL_NAME)
        rerank_api_key = safe_get(req, 'rerank_api_key', default=RERANK_API_KEY)
        rerank = GeneralRerank(rerank_url, rerank_model_name, rerank_api_key)
    else:
        debug_logger.info("rerank is False")
        rerank = None

    
    
    # 读取其他检索参数
    question = safe_get(req, 'question')
    merge = safe_get(req, 'merge', True) # 是否合并检索结果，将来自于相同文件的chunk内容合并在一起
    need_web_search = safe_get(req, 'networking', False)
    web_search_tools = safe_get(req, 'web_search_tools', ["BaiduSearch"])
    hybrid_search = safe_get(req, 'hybrid_search', True)
    web_chunk_size = safe_get(req, 'web_chunk_size', DEFAULT_PARENT_CHUNK_SIZE) # 网页内容的分块大小
    top_k = safe_get(req, 'top_k', 5)
    score_threshold = safe_get(req, 'score_threshold', 0.5)
    debug_logger.info("kb_ids: %s", kb_ids)
    debug_logger.info("user_id: %s", user_id)
    debug_logger.info("question: %s", question)
    debug_logger.info("hybrid_search: %s", hybrid_search)
    debug_logger.info('rerank %s', rerank)
    debug_logger.info("web_chunk_size: %s", web_chunk_size)
    debug_logger.info("top_k: %s", top_k)
    debug_logger.info("networking: %s", need_web_search)
    debug_logger.info("web_search_tools: %s", web_search_tools)
    debug_logger.info("score_threshold: %s", score_threshold)


    # 判断参数合法性
    if not isinstance(score_threshold, float) or score_threshold<=0 or score_threshold >=1:
        debug_logger.warning(f"score_threshold not met requirements. score_threshold:{score_threshold}")
        return return_sanic({"code": 400, "msg": "fail, score_threshold should be a float between 0 and 1"})
    if len(question) <= QUESTION_MIN_LENGTH:
        msg += f"question length is too short. LENGTH: {len(question)}, return directly"
        debug_logger.info(msg)
        return return_sanic({"code": 200, "msg": msg, "question": question, "retrieval_documents":[]})

    
    time_record = {}
    preprocess_end = time.perf_counter()
    time_record['preprocess'] = round(preprocess_end - preprocess_start, 2)
    qa_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 获取格式为'2021-08-01 00:00:00'的时间戳
    for kb_id in kb_ids:
        local_doc_qa.milvus_summary.update_knowledge_base_latest_qa_time(kb_id, qa_timestamp)
    
    debug_logger.info("get_knowledge_search_answer...")
    kb_ids_file_ids = kb_ids + valid_file_ids
    t1 = time.time()
    try:
        retriever = None
        if parser_config:
            milvus_kb = VectorStoreMilvusClient(parser_config)
            retriever = ParentRetriever(milvus_kb, local_doc_qa.milvus_summary, local_doc_qa.es_client, parser_config['separators'], parser_config['chunk_overlap'], parser_config['chunk_size'])
        resp, search_msg = await local_doc_qa.get_knowledge_search_answer(
                                                        kb_ids=kb_ids_file_ids,
                                                        query=question,
                                                        retriever=retriever,
                                                        time_record=time_record,
                                                        top_k=top_k,
                                                        rerank=rerank,                                                        
                                                        need_web_search=need_web_search,
                                                        web_search_tools=web_search_tools,
                                                        web_chunk_size=web_chunk_size,
                                                        hybrid_search=hybrid_search,                                                        
                                                        score_threshold=score_threshold,
                                                        history=history
                                                    )
    except Exception as e:
        debug_logger.error(f"get_knowledge_search_answer error: {e}")
        return return_sanic({"code": 500, "message": "get_knowledge_search_answer error"})

    retrieval_documents, retrieval_web_documents = format_source_documents_v1(resp)
    if merge:
        retrieval_documents = merge_source_documents(retrieval_documents)
        retrieval_web_documents = merge_source_documents(retrieval_web_documents)


    return_result = {
        "code": 200, 
        "msg": msg+"success chat\n"+search_msg, 
        "question": question, 
        "retrieval_documents": retrieval_documents, 
        "retrieval_web_documents": retrieval_web_documents
    }
    qa_logger.info("chat_data: %s", return_result)

    
    from qanything_kernel.qanything_server.save_apicsv import save_api_call_to_csv
    try:
        t2 = time.time()
        date = datetime.now().strftime("%Y-%m-%d")
        debug_logger.info("save_api_call_to_csv...")
        save_api_call_to_csv(date, "question_rag_search", req.json, return_result, t2-t1)
        return return_sanic(return_result)
    except Exception as e:
        debug_logger.warning(f"save api 失败，异常信息：{e}")
    
    return return_sanic(return_result)


@get_time_async
async def question_qa_search(req: request):
    preprocess_start = time.perf_counter()
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa

    # 检查用户id和user_info是否合法
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info('question_qa_search %s', user_id)
    debug_logger.info('user_info %s', user_info)
    
    # 检查知识库是否存在，解析配置是否一致，获取知识库的parser_config
    kb_ids = safe_get(req, 'kb_ids', [])
    kb_ids = [correct_kb_id(kb_id) for kb_id in kb_ids]
    ignore_file_error = safe_get(req, 'ignore_file_error', False) # 新增参数，用于忽略文件不存在或未审核的错误
    parser_config = {}      # 判断每个知识库的parser_config是否一致
    valid_files_num = 0  # 统计知识库中可用的文件数量
    if kb_ids:
        not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, kb_ids)
        if not_exist_kb_ids:
            if ignore_file_error:
                msg += f"warnning, kb_ids {not_exist_kb_ids}."
            else:
                return return_sanic({"code": 400, "msg": "fail, knowledge Base {}".format(not_exist_kb_ids)})
        not_exist_kb_ids = [x[0] for x in not_exist_kb_ids]
        kb_ids = [kb for kb in kb_ids if kb not in not_exist_kb_ids]
        if kb_ids:
            parser_config = local_doc_qa.milvus_summary.get_kb_parser_config(kb_ids[0])
            valid_files_num += local_doc_qa.milvus_summary.get_files_count(user_id, kb_ids[0], status='green')[0][0]
            for kb_id in kb_ids[1:]:
                # 继续检查parser_config中的embeding模型是否一致
                tmp_parser_config = local_doc_qa.milvus_summary.get_kb_parser_config(kb_id)
                if tmp_parser_config['embedding_model_name'] != parser_config['embedding_model_name']:
                    return return_sanic({"code": 400, "msg": "fail, knowledge Base {}'s parser_config not same".format(kb_ids)})
                valid_files_num += local_doc_qa.milvus_summary.get_files_count(user_id, kb_id, status='green')[0][0]
        
    # 检查输入的file_ids是否合法，增加一个file_ids参数，用于指定需要查询的文件，默认为空，与kb_ids同时存在，两个取并集
    file_ids = safe_get(req, 'file_ids', [])
    valid_file_ids = []
    if len(file_ids) > 0:
        valid_file_infos = local_doc_qa.milvus_summary.check_file_exist_byuserid(user_id, file_ids)
        if len(valid_file_infos) != len(file_ids):
            notexist_file_ids = list(set(file_ids) - set([file_info[0] for file_info in valid_file_infos]))
            if ignore_file_error:
                msg += f"warnning, files {notexist_file_ids} not found.\n"
            else:
                return return_sanic({"code": 400, "msg": "fail, files {} not found".format(notexist_file_ids)})
        unvalid_file_ids = [file_info[0] for file_info in valid_file_infos if file_info[1] != 'green']
        valid_file_ids = [file_info[0] for file_info in valid_file_infos if file_info[1] == 'green']
        # 获取文件信息，判断知识库解析参数是否一致
        for tmp_file_id in valid_file_ids:
            tmp_kb_id = local_doc_qa.milvus_summary.get_kbid_by_fileid(tmp_file_id)
            tmp_parser_config = local_doc_qa.milvus_summary.get_kb_parser_config(tmp_kb_id)
            if not parser_config:
                parser_config = tmp_parser_config
            elif tmp_parser_config['embedding_model_name'] != parser_config['embedding_model_name']:
                return return_sanic({"code": 400, "msg": "fail, files {}'s parser_config not same".format(file_ids)})
        valid_files_num += len(valid_file_ids)
        if len(unvalid_file_ids) > 0:
            if ignore_file_error:
                msg += f"wanrnning, files {unvalid_file_ids} not green.\n"
            else:
                return return_sanic({"code": 400, "msg": "fail, files {} not green".format(unvalid_file_ids)})
    
    # 判断输入的所有检索参数是否有可用检索对象
    if valid_files_num == 0 and not need_web_search:
        debug_logger.info("valid_files is empty, use only chat mode.")
        return return_sanic({
            "code": 200, 
            "msg": "当前知识库没有可用文档，且不需要联网检索，请上传文件或等待文件解析完毕", 
            "question": question,
            "retrieval_documents": []})

    # 读取并处理history，用于query改写
    history = safe_get(req, 'history', None)
    try:
        if isinstance(history, str):
            messages = json.loads(history)["messages"]
            history = []
            for message in messages:
                if message["role"] == "user":
                    history.append([message["content"]])
                elif message["role"] == "assistant":
                    history[-1].append(message["content"])
                else:
                    continue
            if len(history[-1]) != 2:
                history.pop()
        elif isinstance(history, list):  # 只检查是否是列表
            # 然后可以进一步检查列表内容
            if all(isinstance(item, list) for item in history):
                if all(isinstance(subitem, str) for item in history for subitem in item):
                    # 符合 List[List[str]] 的结构
                    pass
                else:
                    debug_logger.error("history is list but not List[List[str]]")
                    return return_sanic({"code": 400, "msg": "fail, history is list but not List[List[str]]"})
            else:
                debug_logger.error("history is list but not List[List[str]]")
                return return_sanic({"code": 400, "msg": "fail, history is list but not List[List[str]]"})
        elif history is None:
            debug_logger.info("history is None")
        else:
            debug_logger.error("history is not str or None")
            return return_sanic({"code": 400, "msg": "fail, history is not str or None"})
    except Exception as e:
        debug_logger.error(f"history parser error: {e}")
        return return_sanic({"code": 500, "msg": "fail, history parser error {}".format(e)})
    
    # 读取rerank参数
    rerank = safe_get(req, 'rerank', default=True)
    if rerank:
        debug_logger.info("rerank is True")
        from qanything_kernel.configs.model_config import LOCAL_RERANK_SERVICE_URL, RERANK_MODEL_NAME, RERANK_API_KEY
        from qanything_kernel.connector.rerank.rerank_for_online_client import GeneralRerank
        rerank_url = safe_get(req, 'rerank_url', default=LOCAL_RERANK_SERVICE_URL)
        rerank_model_name = safe_get(req, 'rerank_model_name', default=RERANK_MODEL_NAME)
        rerank_api_key = safe_get(req, 'rerank_api_key', default=RERANK_API_KEY)
        rerank = GeneralRerank(rerank_url, rerank_model_name, rerank_api_key)
    else:
        debug_logger.info("rerank is False")
        rerank = None

    
    
    # 读取其他检索参数
    question = safe_get(req, 'question')
    merge = safe_get(req, 'merge', True) # 是否合并检索结果，将来自于相同文件的chunk内容合并在一起
    need_web_search = safe_get(req, 'networking', False)
    web_search_tools = safe_get(req, 'web_search_tools', ["BaiduSearch"])
    hybrid_search = safe_get(req, 'hybrid_search', True)
    web_chunk_size = safe_get(req, 'web_chunk_size', DEFAULT_PARENT_CHUNK_SIZE) # 网页内容的分块大小
    top_k = safe_get(req, 'top_k', 5)
    score_threshold = safe_get(req, 'score_threshold', 0.5)
    debug_logger.info("kb_ids: %s", kb_ids)
    debug_logger.info("user_id: %s", user_id)
    debug_logger.info("question: %s", question)
    debug_logger.info("hybrid_search: %s", hybrid_search)
    debug_logger.info('rerank %s', rerank)
    debug_logger.info("web_chunk_size: %s", web_chunk_size)
    debug_logger.info("top_k: %s", top_k)
    debug_logger.info("networking: %s", need_web_search)
    debug_logger.info("web_search_tools: %s", web_search_tools)
    debug_logger.info("score_threshold: %s", score_threshold)


    # 判断参数合法性
    if not isinstance(score_threshold, float) or score_threshold<=0 or score_threshold >=1:
        debug_logger.warning(f"score_threshold not met requirements. score_threshold:{score_threshold}")
        return return_sanic({"code": 400, "msg": "fail, score_threshold should be a float between 0 and 1"})
    if len(question) <= QUESTION_MIN_LENGTH:
        msg += f"question length is too short. LENGTH: {len(question)}, return directly"
        debug_logger.info(msg)
        return return_sanic({"code": 200, "msg": msg, "question": question, "retrieval_documents":[]})

    
    time_record = {}
    preprocess_end = time.perf_counter()
    time_record['preprocess'] = round(preprocess_end - preprocess_start, 2)
    qa_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 获取格式为'2021-08-01 00:00:00'的时间戳
    for kb_id in kb_ids:
        local_doc_qa.milvus_summary.update_knowledge_base_latest_qa_time(kb_id, qa_timestamp)
    
    debug_logger.info("get_knowledge_search_answer...")
    kb_ids_file_ids = kb_ids + valid_file_ids
    t1 = time.time()
    try:
        retriever = None
        if parser_config:
            milvus_kb = VectorStoreMilvusClient(parser_config)
            retriever = ParentRetriever(milvus_kb, local_doc_qa.milvus_summary, local_doc_qa.es_client, parser_config['separators'], parser_config['chunk_size'])
        resp, search_msg = await local_doc_qa.get_knowledge_search_answer(
                                                        kb_ids=kb_ids_file_ids,
                                                        query=question,
                                                        retriever=retriever,
                                                        time_record=time_record,
                                                        top_k=top_k,
                                                        rerank=rerank,                                                        
                                                        need_web_search=need_web_search,
                                                        web_search_tools=web_search_tools,
                                                        web_chunk_size=web_chunk_size,
                                                        hybrid_search=hybrid_search,                                                        
                                                        score_threshold=score_threshold,
                                                        history=history
                                                    )
    except Exception as e:
        debug_logger.error(f"get_knowledge_search_answer error: {e}")
        return return_sanic({"code": 500, "message": "get_knowledge_search_answer error"})
    
    source_doc_documents, source_qa_documents, source_web_docuements = format_source_documents_v2(resp)
    merge = safe_get(req, 'merge', True)
    if merge:
        source_doc_documents = merge_source_documents(source_doc_documents)
        source_qa_documents = merge_source_documents(source_qa_documents)
        source_web_docuements = merge_source_documents(source_web_docuements)

    return_result = {
        "code": 200, 
        "msg": msg+"success chat\n"+search_msg, 
        "question": question, 
        "retrieval_doc_documents": source_doc_documents, 
        "retrieval_qa_documents": source_qa_documents, 
        "retrieval_web_documents": source_web_docuements
    }
    qa_logger.info("chat_data: %s", return_result)
    
    from qanything_kernel.qanything_server.save_apicsv import save_api_call_to_csv
    try:
        t2 = time.time()
        date = datetime.now().strftime("%Y-%m-%d")
        debug_logger.info("save_api_call_to_csv...")
        save_api_call_to_csv(date, "question_rag_search", req.json, return_result, t2-t1)
        return return_sanic(return_result)
    except Exception as e:
        debug_logger.warning(f"save api 失败，异常信息：{e}")
    
    return return_sanic(return_result)



@get_time_async
async def local_doc_chat(req: request):
    # 输出所有请求参数
    debug_logger.info("local_doc_chat %s", req.json)
    debug_logger.info("local_doc_chat %s", req.headers)

    preprocess_start = time.perf_counter()
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return sanic_json({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info('local_doc_chat %s', user_id)
    debug_logger.info('user_info %s', user_info)
    bot_id = safe_get(req, 'bot_id')
    if bot_id:
        if not local_doc_qa.milvus_summary.check_bot_is_exist(bot_id):
            return sanic_json({"code": 400, "msg": "fail, Bot {} not found".format(bot_id)})
        bot_info = local_doc_qa.milvus_summary.get_bot(None, bot_id)[0]
        bot_id, bot_name, desc, image, prompt, welcome, kb_ids_str, upload_time, user_id, llm_setting = bot_info
        kb_ids = kb_ids_str.split(',')
        if not kb_ids:
            return sanic_json({"code": 400, "msg": "fail, Bot {} unbound knowledge base.".format(bot_id)})
        custom_prompt = prompt
        if not llm_setting:
            return sanic_json({"code": 400, "msg": "fail, Bot {} llm_setting is empty.".format(bot_id)})
        llm_setting = json.loads(llm_setting)
        rerank = llm_setting.get('rerank', True)
        only_need_search_results = llm_setting.get('only_need_search_results', False)
        need_web_search = llm_setting.get('networking', False)
        api_base = llm_setting.get('api_base', '')
        api_key = llm_setting.get('api_key', 'ollama')
        api_context_length = llm_setting.get('api_context_length', 4096)
        top_p = llm_setting.get('top_p', 0.99)
        temperature = llm_setting.get('temperature', 0.5)
        top_k = llm_setting.get('top_k', VECTOR_SEARCH_TOP_K)
        model = llm_setting.get('model', 'gpt-4o-mini')
        max_token = llm_setting.get('max_token')
        hybrid_search = llm_setting.get('hybrid_search', False)
        chunk_size = llm_setting.get('chunk_size', DEFAULT_PARENT_CHUNK_SIZE)
    else:
        kb_ids = safe_get(req, 'kb_ids')
        custom_prompt = safe_get(req, 'custom_prompt', None)
        rerank = safe_get(req, 'rerank', default=True)
        only_need_search_results = safe_get(req, 'only_need_search_results', False)
        need_web_search = safe_get(req, 'networking', False)
        api_base = safe_get(req, 'api_base', LLM_BASE_URL)
        # 如果api_base中包含0.0.0.0或127.0.0.1或localhost，替换为GATEWAY_IP
        api_base = api_base.replace('0.0.0.0', GATEWAY_IP).replace('127.0.0.1', GATEWAY_IP).replace('localhost', GATEWAY_IP)
        api_key = safe_get(req, 'api_key', LLM_API_KEY)
        api_context_length = safe_get(req, 'api_context_length', LLM_MAX_LENGTH)
        top_p = safe_get(req, 'top_p', LLM_TOP_P)
        temperature = safe_get(req, 'temperature', LLM_TEMPERATURE)
        top_k = safe_get(req, 'top_k', VECTOR_SEARCH_TOP_K)

        model = safe_get(req, 'model', LLM_MODEL_NAME)
        max_token = safe_get(req, 'max_token', LLM_MAX_LENGTH)

        hybrid_search = safe_get(req, 'hybrid_search', False)
        chunk_size = safe_get(req, 'chunk_size', DEFAULT_PARENT_CHUNK_SIZE)

    if rerank:
        debug_logger.info("rerank is True")
        from qanything_kernel.configs.model_config import LOCAL_RERANK_SERVICE_URL, RERANK_MODEL_NAME, RERANK_API_KEY
        from qanything_kernel.connector.rerank.rerank_for_online_client import GeneralRerank
        rerank_url = safe_get(req, 'rerank_url', default=LOCAL_RERANK_SERVICE_URL)
        rerank_model_name = safe_get(req, 'rerank_model_name', default=RERANK_MODEL_NAME)
        rerank_api_key = safe_get(req, 'rerank_api_key', default=RERANK_API_KEY)
        rerank = GeneralRerank(rerank_url, rerank_model_name, rerank_api_key)
    else:
        debug_logger.info("rerank is False")
        rerank = None
    rerank_score = safe_get(req, 'rerank_score', 0.5)
    debug_logger.info("rerank_score: %s", rerank_score)

    if len(kb_ids) > 40:
        return sanic_json({"code": 400, "msg": "fail, kb_ids length should less than or equal to 40"})
    kb_ids = [correct_kb_id(kb_id) for kb_id in kb_ids]
    question = safe_get(req, 'question')
    streaming = safe_get(req, 'streaming', False)
    history = safe_get(req, 'history', [])

    if top_k > 100:
        return sanic_json({"code": 400, "msg": "fail, top_k should less than or equal to 100"})

    missing_params = []
    if not api_base:
        missing_params.append('api_base')
    if not api_key:
        missing_params.append('api_key')
    if not api_context_length:
        missing_params.append('api_context_length')
    if not top_p:
        missing_params.append('top_p')
    if not top_k:
        missing_params.append('top_k')
    if top_p == 1.0:
        top_p = 0.99
    if not temperature:
        missing_params.append('temperature')

    if missing_params:
        missing_params_str = " and ".join(missing_params) if len(missing_params) > 1 else missing_params[0]
        return sanic_json({"code": 400, "msg": f"fail, {missing_params_str} is required"})

    if only_need_search_results and streaming:
        return sanic_json(
            {"code": 400, "msg": "fail, only_need_search_results and streaming can't be True at the same time"})
    request_source = safe_get(req, 'source', 'unknown')

    debug_logger.info("history: %s ", history)
    debug_logger.info("question: %s", question)
    debug_logger.info("kb_ids: %s", kb_ids)
    debug_logger.info("user_id: %s", user_id)
    debug_logger.info("custom_prompt: %s", custom_prompt)
    debug_logger.info("model: %s", model)
    debug_logger.info("max_token: %s", max_token)
    debug_logger.info("request_source: %s", request_source)
    debug_logger.info("only_need_search_results: %s", only_need_search_results)
    debug_logger.info("bot_id: %s", bot_id)
    debug_logger.info("need_web_search: %s", need_web_search)
    debug_logger.info("api_base: %s", api_base)
    debug_logger.info("api_key: %s", api_key)
    debug_logger.info("api_context_length: %s", api_context_length)
    debug_logger.info("top_p: %s", top_p)
    debug_logger.info("top_k: %s", top_k)
    debug_logger.info("temperature: %s", temperature)
    debug_logger.info("hybrid_search: %s", hybrid_search)
    debug_logger.info("chunk_size: %s", chunk_size)

    time_record = {}
    if kb_ids:
        not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, kb_ids)
        if not_exist_kb_ids:
            return sanic_json({"code": 400, "msg": "fail, knowledge Base {} not found".format(not_exist_kb_ids)})
        faq_kb_ids = [kb + '_FAQ' for kb in kb_ids]
        not_exist_faq_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, faq_kb_ids)
        not_exist_faq_kb_ids = [x[0] for x in not_exist_faq_kb_ids]
        exist_faq_kb_ids = [kb for kb in faq_kb_ids if kb not in not_exist_faq_kb_ids]
        debug_logger.info("exist_faq_kb_ids: %s", exist_faq_kb_ids)
        kb_ids += exist_faq_kb_ids

    valid_files_num = 0
    for kb_id in kb_ids:
        valid_files_num += local_doc_qa.milvus_summary.get_files_count(user_id, kb_id, status='green')[0][0]
    if valid_files_num == 0:
        debug_logger.info("valid_files is empty, use only chat mode.")
        kb_ids = []
    preprocess_end = time.perf_counter()
    time_record['preprocess'] = round(preprocess_end - preprocess_start, 2)
    # 获取格式为'2021-08-01 00:00:00'的时间戳
    qa_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    for kb_id in kb_ids:
        local_doc_qa.milvus_summary.update_knowledge_base_latest_qa_time(kb_id, qa_timestamp)
    
    parser_config = local_doc_qa.milvus_summary.get_kb_parser_config(kb_ids[0]) # 同一个用户的知识库的parser_config是一样的
    milvus_kb = VectorStoreMilvusClient(parser_config)
    retriever = ParentRetriever(milvus_kb, local_doc_qa.milvus_summary, local_doc_qa.es_client, parser_config['separators'], parser_config['chunk_size'])
    debug_logger.info("streaming: %s", streaming)
    if streaming:
        debug_logger.info("start generate answer")

        async def generate_answer(response):
            debug_logger.info("start generate...")
            async for resp, next_history in local_doc_qa.get_knowledge_based_answer(model=model,
                                                                                    max_token=max_token,
                                                                                    kb_ids=kb_ids,
                                                                                    query=question,
                                                                                    retriever=retriever,
                                                                                    chat_history=history,
                                                                                    streaming=True,
                                                                                    rerank=rerank,
                                                                                    custom_prompt=custom_prompt,
                                                                                    time_record=time_record,
                                                                                    need_web_search=need_web_search,
                                                                                    hybrid_search=hybrid_search,
                                                                                    web_chunk_size=chunk_size,
                                                                                    temperature=temperature,
                                                                                    api_base=api_base,
                                                                                    api_key=api_key,
                                                                                    api_context_length=api_context_length,
                                                                                    top_p=top_p,
                                                                                    top_k=top_k
                                                                                    ):
                chunk_data = resp["result"]
                if not chunk_data:
                    continue
                chunk_str = chunk_data[6:]
                if chunk_str.startswith("[DONE]"):
                    retrieval_documents = format_source_documents(resp["retrieval_documents"])
                    source_documents = format_source_documents(resp["source_documents"])
                    result = next_history[-1][1]
                    # result = resp['result']
                    time_record['chat_completed'] = round(time.perf_counter() - preprocess_start, 2)
                    if time_record.get('llm_completed', 0) > 0:
                        time_record['tokens_per_second'] = round(
                            len(result) / time_record['llm_completed'], 2)
                    formatted_time_record = format_time_record(time_record)
                    chat_data = {'user_id': user_id, 'kb_ids': kb_ids, 'query': question, "model": model,
                                 "product_source": request_source, 'time_record': formatted_time_record,
                                 'history': history,
                                 'condense_question': resp['condense_question'], 'prompt': resp['prompt'],
                                 'result': result, 'retrieval_documents': retrieval_documents,
                                 'source_documents': source_documents, 'bot_id': bot_id}
                    local_doc_qa.milvus_summary.add_qalog(**chat_data)
                    qa_logger.info("chat_data: %s", chat_data)
                    debug_logger.info("response: %s", chat_data['result'])
                    stream_res = {
                        "code": 200,
                        "msg": "success stream chat",
                        "question": question,
                        "response": result,
                        "model": model,
                        "history": next_history,
                        "condense_question": resp['condense_question'],
                        "source_documents": source_documents,
                        "retrieval_documents": retrieval_documents,
                        "time_record": formatted_time_record,
                        "show_images": resp.get('show_images', [])
                    }
                else:
                    time_record['rollback_length'] = resp.get('rollback_length', 0)
                    if 'first_return' not in time_record:
                        time_record['first_return'] = round(time.perf_counter() - preprocess_start, 2)
                    chunk_js = json.loads(chunk_str)
                    delta_answer = chunk_js["answer"]
                    stream_res = {
                        "code": 200,
                        "msg": "success",
                        "question": "",
                        "response": delta_answer,
                        "history": [],
                        "source_documents": [],
                        "retrieval_documents": [],
                        "time_record": format_time_record(time_record),
                    }
                await response.write(f"data: {json.dumps(stream_res, ensure_ascii=False)}\n\n")
                if chunk_str.startswith("[DONE]"):
                    await response.eof()
                await asyncio.sleep(0.001)

        response_stream = ResponseStream(generate_answer, content_type='text/event-stream')
        return response_stream

    else:
        async for resp, history in local_doc_qa.get_knowledge_based_answer(model=model,
                                                                           max_token=max_token,
                                                                           kb_ids=kb_ids,
                                                                           query=question,
                                                                           retriever=retriever,
                                                                           chat_history=history, streaming=False,
                                                                           rerank=rerank,
                                                                           custom_prompt=custom_prompt,
                                                                           time_record=time_record,
                                                                           only_need_search_results=only_need_search_results,
                                                                           need_web_search=need_web_search,
                                                                           hybrid_search=hybrid_search,
                                                                           web_chunk_size=chunk_size,
                                                                           temperature=temperature,
                                                                           api_base=api_base,
                                                                           api_key=api_key,
                                                                           api_context_length=api_context_length,
                                                                           top_p=top_p,
                                                                           top_k=top_k,
                                                                           score_threshold=rerank_score
                                                                           ):
            pass
        if only_need_search_results:
            return sanic_json(
                {"code": 200, "question": question, "source_documents": format_source_documents(resp)})
        retrieval_documents = format_source_documents(resp["retrieval_documents"])
        source_documents = format_source_documents(resp["source_documents"])
        formatted_time_record = format_time_record(time_record)
        chat_data = {'user_id': user_id, 'kb_ids': kb_ids, 'query': question, 'time_record': formatted_time_record,
                     'history': history, "condense_question": resp['condense_question'], "model": model,
                     "product_source": request_source,
                     'retrieval_documents': retrieval_documents, 'prompt': resp['prompt'], 'result': resp['result'],
                     'source_documents': source_documents, 'bot_id': bot_id}
        local_doc_qa.milvus_summary.add_qalog(**chat_data)
        qa_logger.info("chat_data: %s", chat_data)
        debug_logger.info("response: %s", chat_data['result'])
        return sanic_json({"code": 200, "msg": "success no stream chat", "question": question,
                           "response": resp["result"], "model": model,
                           "history": history, "condense_question": resp['condense_question'],
                           "source_documents": source_documents, "retrieval_documents": retrieval_documents,
                           "time_record": formatted_time_record})




@get_time_async
async def document(req: request):
    description = """
# RAG 文档问答接口

您的任何格式的本地文件都可以往里扔，即可获得准确、快速、靠谱的问答体验。
**目前已支持格式:**
* PDF
* Word(docx)
* PPT
* TXT
* Markdown
* Excel(xlsx)
* CSV
* 图片(jpg/jpeg/png)
* 网页链接
* ...更多格式，敬请期待

# API 调用指南
"""
    with open('api使用说明.md', 'r') as f:
        api_des = f.read().strip()
    description += api_des
    return sanic_text(description)


@get_time_async
async def get_websearch_tools(req: request):
    return return_sanic({"code": 200, "web_search_tools": SUPORT_WEBSEARCH_TOOLS})


@get_time_async
async def get_doc_completed(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("get_doc_completed %s", user_id)
    file_id = safe_get(req, 'file_id')
    if not file_id:
        return return_sanic({"code": 400, "msg": "fail, file_id is None"})
    debug_logger.info("file_id: {}".format(file_id))
    page_id = safe_get(req, 'page_id', 1)  # 默认为第一页
    page_limit = safe_get(req, 'page_limit', 10)  # 默认每页显示10条记录

    
    kb_id = local_doc_qa.milvus_summary.get_kbid_by_fileid(file_id)
    if not kb_id:
        return return_sanic({"code": 400, "msg": "fail, file_id {} not found".format(file_id)})
    file_info = local_doc_qa.milvus_summary.get_files(user_id, kb_id, file_id)
    if not file_info:
        return return_sanic({"code": 400, "msg": "fail, file_id {} not found".format(file_id)})
    debug_logger.info("file_info: {}".format(file_info))
    if file_info[0][2] != 'green':
        return return_sanic({"code": 400, "msg": "fail, file_id {} not completed".format(file_id)})
    

    try:
        sorted_json_datas = local_doc_qa.milvus_summary.get_document_by_file_id(file_id)
        chunks = [json_data['kwargs'] for json_data in sorted_json_datas]

        # 计算总记录数
        total_count = len(chunks)
        # 计算总页数
        total_pages = (total_count + page_limit - 1) // page_limit
        if page_id > total_pages and total_count != 0:
            return return_sanic({"code": 400, "msg": f'输入非法！page_id超过最大值，page_id: {page_id}，最大值：{total_pages}，请检查！'})
        # 计算当前页的起始和结束索引
        start_index = (page_id - 1) * page_limit
        end_index = start_index + page_limit
        # 截取当前页的数据
        current_page_chunks = chunks[start_index:end_index]
        for chunk in current_page_chunks:
            chunk['page_content'] = replace_image_references(chunk['page_content'], file_id)

        return return_sanic({"code": 200, "msg": "success", "chunks": current_page_chunks, 
                        "page_id": page_id, "page_limit": page_limit, "total_count": total_count})

    except Exception as e:
        debug_logger.error("get_doc_chunks error: {}".format(e))
        return return_sanic({"code": 500, "msg": "fail, get_doc_chunks error: {}".format(e)})


@get_time_async
async def get_qa_info(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    any_kb_id = safe_get(req, 'any_kb_id')
    user_id = safe_get(req, 'user_id')
    if user_id is None and not any_kb_id:
        return return_sanic({"code": 400, "msg": "fail, user_id and any_kb_id is None"})
    if any_kb_id:
        any_kb_id = correct_kb_id(any_kb_id)
        debug_logger.info("get_qa_info %s", any_kb_id)
    if user_id:
        user_info = safe_get(req, 'user_info', "1234")
        passed, msg = check_user_id_and_user_info(user_id, user_info)
        if not passed:
            return return_sanic({"code": 400, "msg": msg})
        user_id = user_id + '__' + user_info
        debug_logger.info("get_qa_info %s", user_id)
    query = safe_get(req, 'query')
    bot_id = safe_get(req, 'bot_id')
    qa_ids = safe_get(req, "qa_ids")
    time_start = safe_get(req, 'time_start')
    time_end = safe_get(req, 'time_end')
    time_range = get_time_range(time_start, time_end)
    if not time_range:
        return {"code": 400, "msg": f'输入非法！time_start格式错误，time_start: {time_start}，示例：2024-10-05，请检查！'}
    only_need_count = safe_get(req, 'only_need_count', False)
    debug_logger.info(f"only_need_count: {only_need_count}")
    if only_need_count:
        need_info = ["timestamp"]
        qa_infos = local_doc_qa.milvus_summary.get_qalog_by_filter(need_info=need_info, user_id=user_id, time_range=time_range)
        # timestamp = now.strftime("%Y%m%d%H%M")
        # 按照timestamp，按照天数进行统计，比如20240628，20240629，20240630，计算每天的问答数量
        qa_infos = sorted(qa_infos, key=lambda x: x['timestamp'])
        qa_infos = [qa_info['timestamp'] for qa_info in qa_infos]
        qa_infos = [qa_info[:10] for qa_info in qa_infos]
        qa_infos_by_day = dict(Counter(qa_infos))
        return return_sanic({"code": 200, "msg": "success", "qa_infos_by_day": qa_infos_by_day})

    page_id = safe_get(req, 'page_id', 1)
    page_limit = safe_get(req, 'page_limit', 10)
    default_need_info = ["qa_id", "user_id", "bot_id", "kb_ids", "query", "model", "product_source", "time_record",
                         "history", "condense_question", "prompt", "result", "retrieval_documents", "source_documents",
                         "timestamp"]
    need_info = safe_get(req, 'need_info', default_need_info)
    save_to_excel = safe_get(req, 'save_to_excel', False)
    qa_infos = local_doc_qa.milvus_summary.get_qalog_by_filter(need_info=need_info, user_id=user_id, query=query,
                                                               bot_id=bot_id, time_range=time_range,
                                                               any_kb_id=any_kb_id, qa_ids=qa_ids)
    if save_to_excel:
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        file_name = f"QAnything_QA_{timestamp}.xlsx"
        file_path = export_qalogs_to_excel(qa_infos, need_info, file_name)
        return await response.file(file_path, filename=file_name,
                                   mime_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                   headers={'Content-Disposition': f'attachment; filename="{file_name}"'})

    # 计算总记录数
    total_count = len(qa_infos)
    # 计算总页数
    total_pages = (total_count + page_limit - 1) // page_limit
    if page_id > total_pages and total_count != 0:
        return return_sanic(
            {"code": 400, "msg": f'输入非法！page_id超过最大值，page_id: {page_id}，最大值：{total_pages}，请检查！'})
    # 计算当前页的起始和结束索引
    start_index = (page_id - 1) * page_limit
    end_index = start_index + page_limit
    # 截取当前页的数据
    current_qa_infos = qa_infos[start_index:end_index]
    msg = f"检测到的Log总数为{total_count}, 本次返回page_id为{page_id}的数据，每页显示{page_limit}条"

    # if len(qa_infos) > 100:
    #     pages = math.ceil(len(qa_infos) // 100)
    #     if page_id is None:
    #         msg = f"检索到的Log数超过100，需要分页返回，总数为{len(qa_infos)}, 请使用page_id参数获取某一页数据，参数范围：[0, {pages - 1}], 本次返回page_id为0的数据"
    #         qa_infos = qa_infos[:100]
    #         page_id = 0
    #     elif page_id >= pages:
    #         return return_sanic(
    #             {"code": 2002, "msg": f'输入非法！page_id超过最大值，page_id: {page_id}，最大值：{pages - 1}，请检查！'})
    #     else:
    #         msg = f"检索到的Log数超过100，需要分页返回，总数为{len(qa_infos)}, page范围：[0, {pages - 1}], 本次返回page_id为{page_id}的数据"
    #         qa_infos = qa_infos[page_id * 100:(page_id + 1) * 100]
    # else:
    #     msg = f"检索到的Log数为{len(qa_infos)}，一次返回所有数据"
    #     page_id = 0
    return return_sanic({"code": 200, "msg": msg, "page_id": page_id, "page_limit": page_limit, "qa_infos": current_qa_infos, "total_count": total_count})


@get_time_async
async def get_random_qa(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    limit = safe_get(req, 'limit', 10)
    time_start = safe_get(req, 'time_start')
    time_end = safe_get(req, 'time_end')
    need_info = safe_get(req, 'need_info')
    time_range = get_time_range(time_start, time_end)
    if not time_range:
        return {"code": 400, "msg": f'输入非法！time_start格式错误，time_start: {time_start}，示例：2024-10-05，请检查！'}

    debug_logger.info(f"get_random_qa limit: {limit}, time_range: {time_range}")
    qa_infos = local_doc_qa.milvus_summary.get_random_qa_infos(limit=limit, time_range=time_range, need_info=need_info)

    counts = local_doc_qa.milvus_summary.get_statistic(time_range=time_range)
    return return_sanic({"code": 200, "msg": "success", "total_users": counts["total_users"],
                       "total_queries": counts["total_queries"], "qa_infos": qa_infos})


@get_time_async
async def get_related_qa(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    qa_id = safe_get(req, 'qa_id')
    if not qa_id:
        return return_sanic({"code": 400, "msg": "fail, qa_id is None"})
    need_info = safe_get(req, 'need_info')
    need_more = safe_get(req, 'need_more', False)
    debug_logger.info("get_related_qa %s", qa_id)
    qa_log, recent_logs, older_logs = local_doc_qa.milvus_summary.get_related_qa_infos(qa_id, need_info, need_more)
    # 按kb_ids划分sections
    recent_sections = defaultdict(list)
    for log in recent_logs:
        recent_sections[log['kb_ids']].append(log)
    # 把recent_sections的key改为自增的正整数，且每个log都新增kb_name
    for i, kb_ids in enumerate(list(recent_sections.keys())):
        kb_names = local_doc_qa.milvus_summary.get_knowledge_base_name(json.loads(kb_ids))
        kb_names = [kb_name for user_id, kb_id, kb_name in kb_names]
        kb_names = ','.join(kb_names)
        recent_sections[i] = recent_sections.pop(kb_ids)
        for log in recent_sections[i]:
            log['kb_names'] = kb_names

    older_sections = defaultdict(list)
    for log in older_logs:
        older_sections[log['kb_ids']].append(log)
    # 把older_sections的key改为自增的正整数，且每个log都新增kb_name
    for i, kb_ids in enumerate(list(older_sections.keys())):
        kb_names = local_doc_qa.milvus_summary.get_knowledge_base_name(json.loads(kb_ids))
        kb_names = [kb_name for user_id, kb_id, kb_name in kb_names]
        kb_names = ','.join(kb_names)
        older_sections[i] = older_sections.pop(kb_ids)
        for log in older_sections[i]:
            log['kb_names'] = kb_names

    return return_sanic({"code": 200, "msg": "success", "qa_info": qa_log, "recent_sections": recent_sections,
                       "older_sections": older_sections})


@get_time_async
async def get_user_id(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    kb_id = safe_get(req, 'kb_id')
    kb_id = correct_kb_id(kb_id)
    debug_logger.info("kb_id: {}".format(kb_id))
    user_id = local_doc_qa.milvus_summary.get_user_by_kb_id(kb_id)
    if not user_id:
        return return_sanic({"code": 400, "msg": "fail, knowledge Base {} not found".format(kb_id)})
    else:
        return return_sanic({"code": 200, "msg": "success", "user_id": user_id})


@get_time_async
async def get_doc(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    doc_id = safe_get(req, 'doc_id')
    debug_logger.info("get_doc %s", doc_id)
    if not doc_id:
        return return_sanic({"code": 400, "msg": "fail, doc_id is None"})
    doc_json_data = local_doc_qa.milvus_summary.get_document_by_doc_id(doc_id)
    return return_sanic({"code": 200, "msg": "success", "doc_text": doc_json_data['kwargs']})



@get_time_async
async def get_user_status(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("get_user_status %s", user_id)
    user_status = local_doc_qa.milvus_summary.get_user_status(user_id)
    if user_status is None:
        return return_sanic({"code": 400, "msg": "fail, user {} not found".format(user_id)})
    if user_status == 0:
        status = 'green'
    else:
        status = 'red'
    return return_sanic({"code": 200, "msg": "success", "status": status})


@get_time_async
async def health_check(req: request):
    # 实现一个服务健康检查的逻辑，正常就返回200，不正常就返回500
    return return_sanic({"code": 200, "msg": "success"})


@get_time_async
async def get_bot_info(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    bot_id = safe_get(req, 'bot_id')
    if bot_id:
        if not local_doc_qa.milvus_summary.check_bot_is_exist(bot_id):
            return return_sanic({"code": 400, "msg": "fail, Bot {} not found".format(bot_id)})
    debug_logger.info("get_bot_info %s", user_id)
    bot_infos = local_doc_qa.milvus_summary.get_bot(user_id, bot_id)
    data = []
    for bot_info in bot_infos:
        if bot_info[6] != "":
            kb_ids = bot_info[6].split(',')
            kb_infos = local_doc_qa.milvus_summary.get_knowledge_base_name(kb_ids)
            kb_names = []
            for kb_id in kb_ids:
                for kb_info in kb_infos:
                    if kb_id == kb_info[1]:
                        kb_names.append(kb_info[2])
                        break
        else:
            kb_ids = []
            kb_names = []
        info = {"bot_id": bot_info[0], "user_id": user_id, "bot_name": bot_info[1], "description": bot_info[2],
                "head_image": bot_info[3], "prompt_setting": bot_info[4], "welcome_message": bot_info[5],
                "kb_ids": kb_ids, "kb_names": kb_names,
                "update_time": bot_info[7].strftime("%Y-%m-%d %H:%M:%S"), "llm_setting": bot_info[9]}
        data.append(info)
    return return_sanic({"code": 200, "msg": "success", "data": data})


@get_time_async
async def new_bot(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    bot_name = safe_get(req, "bot_name")
    desc = safe_get(req, "description", BOT_DESC)
    head_image = safe_get(req, "head_image", BOT_IMAGE)
    prompt_setting = safe_get(req, "prompt_setting", BOT_PROMPT)
    welcome_message = safe_get(req, "welcome_message", BOT_WELCOME)
    kb_ids = safe_get(req, "kb_ids", [])
    kb_ids_str = ",".join(kb_ids)

    not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, kb_ids)
    if not_exist_kb_ids:
        msg = "invalid kb_id: {}, please check...".format(not_exist_kb_ids)
        return return_sanic({"code": 400, "msg": msg, "data": [{}]})
    debug_logger.info("new_bot %s", user_id)
    bot_id = 'BOT' + uuid.uuid4().hex
    local_doc_qa.milvus_summary.new_qanything_bot(bot_id, user_id, bot_name, desc, head_image, prompt_setting,
                                                  welcome_message, kb_ids_str)
    create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return return_sanic({"code": 200, "msg": "success create qanything bot {}".format(bot_id),
                       "data": {"bot_id": bot_id, "bot_name": bot_name, "create_time": create_time}})


@get_time_async
async def delete_bot(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("delete_bot %s", user_id)
    bot_id = safe_get(req, 'bot_id')
    if not local_doc_qa.milvus_summary.check_bot_is_exist(bot_id):
        return return_sanic({"code": 400, "msg": "fail, Bot {} not found".format(bot_id)})
    local_doc_qa.milvus_summary.delete_bot(user_id, bot_id)
    return return_sanic({"code": 200, "msg": "Bot {} delete success".format(bot_id)})


@get_time_async
async def update_bot(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("update_bot %s", user_id)
    bot_id = safe_get(req, 'bot_id')
    if not local_doc_qa.milvus_summary.check_bot_is_exist(bot_id):
        return return_sanic({"code": 400, "msg": "fail, Bot {} not found".format(bot_id)})
    bot_info = local_doc_qa.milvus_summary.get_bot(user_id, bot_id)[0]
    bot_name = safe_get(req, "bot_name", bot_info[1])
    description = safe_get(req, "description", bot_info[2])
    head_image = safe_get(req, "head_image", bot_info[3])
    prompt_setting = safe_get(req, "prompt_setting", bot_info[4])
    welcome_message = safe_get(req, "welcome_message", bot_info[5])
    kb_ids = safe_get(req, "kb_ids")
    if kb_ids is not None:
        not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, kb_ids)
        if not_exist_kb_ids:
            msg = "invalid kb_id: {}, please check...".format(not_exist_kb_ids)
            return return_sanic({"code": 400, "msg": msg, "data": [{}]})
        kb_ids_str = ",".join(kb_ids)
    else:
        kb_ids_str = bot_info[6]
    

    llm_setting = json.loads(bot_info[9])
    if api_base := safe_get(req, "api_base"):
        llm_setting["api_base"] = api_base
    if api_key := safe_get(req, "api_key"):
        llm_setting["api_key"] = api_key
    if api_context_length := safe_get(req, "api_context_length"):
        llm_setting["api_context_length"] = api_context_length
    if top_p := safe_get(req, "top_p"):
        llm_setting["top_p"] = top_p
    if top_k := safe_get(req, "top_k"):
        llm_setting["top_k"] = top_k
    if chunk_size := safe_get(req, "chunk_size"):
        llm_setting["chunk_size"] = chunk_size
    if temperature := safe_get(req, "temperature"):
        llm_setting["temperature"] = temperature
    if model := safe_get(req, "model"):
        llm_setting["model"] = model
    if max_token := safe_get(req, "max_token"):
        llm_setting["max_token"] = max_token
    # 如果rerank不是None，赋值，false也可以
    rerank = safe_get(req, "rerank")
    if rerank is not None:
        llm_setting["rerank"] = rerank
    hybrid_search = safe_get(req, "hybrid_search")
    if hybrid_search is not None:
        llm_setting["hybrid_search"] = hybrid_search
    networking = safe_get(req, "networking")
    if networking is not None:
        llm_setting["networking"] = networking
    only_need_search_results = safe_get(req, "only_need_search_results")
    if only_need_search_results is not None:
        llm_setting["only_need_search_results"] = only_need_search_results

    debug_logger.info(f"update llm_setting: {llm_setting}")


    # 判断哪些项修改了
    if bot_name != bot_info[1]:
        debug_logger.info(f"update bot name from {bot_info[1]} to {bot_name}")
    if description != bot_info[2]:
        debug_logger.info(f"update bot description from {bot_info[2]} to {description}")
    if head_image != bot_info[3]:
        debug_logger.info(f"update bot head_image from {bot_info[3]} to {head_image}")
    if prompt_setting != bot_info[4]:
        debug_logger.info(f"update bot prompt_setting from {bot_info[4]} to {prompt_setting}")
    if welcome_message != bot_info[5]:
        debug_logger.info(f"update bot welcome_message from {bot_info[5]} to {welcome_message}")
    if kb_ids_str != bot_info[6]:
        debug_logger.info(f"update bot kb_ids from {bot_info[6]} to {kb_ids_str}")
    #  update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP 根据这个mysql的格式获取现在的时间
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    debug_logger.info(f"update_time: {update_time}")
    local_doc_qa.milvus_summary.update_bot(user_id, bot_id, bot_name, description, head_image, prompt_setting,
                                           welcome_message, kb_ids_str, update_time, llm_setting)
    return return_sanic({"code": 200, "msg": "Bot {} update success".format(bot_id)})


@get_time_async
async def update_chunks(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("update_chunks %s", user_id)
    doc_id = safe_get(req, 'doc_id')
    debug_logger.info(f"doc_id: {doc_id}")
    # yellow_files = local_doc_qa.milvus_summary.get_files_by_status("yellow")
    # if len(yellow_files) > 0:
    #     return return_sanic({"code": 2002, "msg": f"fail, currently, there are {len(yellow_files)} files being parsed, please wait for all files to finish parsing before updating the chunk."})
    update_content = safe_get(req, 'update_content')
    debug_logger.info(f"update_content: {update_content}")
    chunk_size = safe_get(req, 'chunk_size', DEFAULT_PARENT_CHUNK_SIZE)
    # chunk_size = int(chunk_size)*2  # 乘以2是为了在修改切片时有足够的空间，避免切片过长
    # debug_logger.info(f"chunk_size: {chunk_size}")
    # update_content_tokens = num_tokens_embed(update_content)
    # if update_content_tokens > chunk_size:
    #     return return_sanic({"code": 2003, "msg": f"fail, update_content too long, please reduce the length, "
    #                                             f"your update_content tokens is {update_content_tokens}, "
    #                                             f"the max tokens is {chunk_size}"})
    doc_json = local_doc_qa.milvus_summary.get_document_by_doc_id(doc_id)
    if not doc_json:
        return return_sanic({"code": 400, "msg": "fail, DocId {} not found".format(doc_id)})
    doc = Document(page_content=update_content, metadata=doc_json['kwargs']['metadata'])
    doc.metadata['doc_id'] = doc_id
    local_doc_qa.milvus_summary.update_document(doc_id, update_content)
    expr = f'doc_id == "{doc_id}"'

    # 根据doc_id获取kb_id
    kb_id = doc_json['kwargs']['metadata']['kb_id']
    parser_config = local_doc_qa.milvus_summary.get_kb_parser_config(kb_id)
    milvus_kb = VectorStoreMilvusClient(parser_config)
    milvus_kb.delete_expr(expr)
    local_doc_qa.es_client.delete(doc_id)

    # 删除后重新插入
    retriever = ParentRetriever(milvus_kb, local_doc_qa.milvus_summary, local_doc_qa.es_client, parser_config['separators'], parser_config['chunk_size'])
    await retriever.insert_documents([doc], chunk_size, True)
    return return_sanic({"code": 200, "msg": "success update doc_id {}".format(doc_id)})



@get_time_async
async def delete_chunks(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("delete_chunks %s", user_id)
    doc_ids = safe_get(req, 'doc_ids')
    debug_logger.info(f"doc_ids: {doc_ids}")
    try:
        # 删除milvus中的数据
        expr = f'doc_id in {doc_ids}'
        doc_json = local_doc_qa.milvus_summary.get_document_by_doc_id(doc_ids[0])
        kb_id = doc_json['kwargs']['metadata']['kb_id']
        parser_config = local_doc_qa.milvus_summary.get_kb_parser_config(kb_id)
        milvus_kb = VectorStoreMilvusClient(parser_config)
        milvus_kb.delete_expr(expr)

        # 删除es中的数据
        local_doc_qa.es_client.delete(doc_ids)
        
        # 删除mysql中的数据
        local_doc_qa.milvus_summary.delete_docs(doc_ids)
        return return_sanic({"code": 200, "msg": "success delete doc_ids {}".format(doc_ids)})
    except Exception as e:
        debug_logger.error(f"delete_chunks error: {e}")
        return return_sanic({"code": 500, "msg": f"fail, delete_chunks error: {e}"})



@get_time_async
async def update_qa(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("update_qa %s", user_id)
    file_id = safe_get(req, 'file_id')
    doc_id = file_id + '_0'
    debug_logger.info(f"doc_id: {doc_id}")
    yellow_files = local_doc_qa.milvus_summary.get_files_by_status("yellow")
    if len(yellow_files) > 0:
        return return_sanic({"code": 400, "msg": f"fail, currently, there are {len(yellow_files)} files being parsed, please wait for all files to finish parsing before updating the chunk."})
    question = safe_get(req, 'question')
    answer = safe_get(req, 'answer')
    debug_logger.info(f"question: {question}")
    debug_logger.info(f"answer: {answer}")
    
    
    doc_json = local_doc_qa.milvus_summary.get_document_by_doc_id(doc_id)
    if not doc_json:
        return return_sanic({"code": 400, "msg": "fail, DocId {} not found".format(doc_id)})
    doc = Document(page_content=question, metadata=doc_json['kwargs']['metadata'])
    doc.metadata['doc_id'] = doc_id
    faq_dict = {"question": question, "answer": answer, "nos_keys": doc_json['kwargs']['metadata']['faq_dict']['nos_keys']}
    doc.metadata['faq_dict'] = faq_dict

    # 更新mysql中的faq相关信息
    local_doc_qa.milvus_summary.update_document(doc_id, question, faq_dict)
    local_doc_qa.milvus_summary.update_faq(user_id, file_id, question, answer)
    

    # 先删除再插入
    expr = f'doc_id == "{doc_id}"'
    kb_id = local_doc_qa.milvus_summary.get_kbid_by_fileid(file_id)
    parser_config = local_doc_qa.milvus_summary.get_kb_parser_config(kb_id)
    milvus_kb = VectorStoreMilvusClient(parser_config)
    milvus_kb.delete_expr(expr)

    retriever = ParentRetriever(milvus_kb, local_doc_qa.milvus_summary, local_doc_qa.es_client, parser_config['separators'], parser_config['chunk_size'])
    await retriever.insert_documents([doc], DEFAULT_PARENT_CHUNK_SIZE, True)
    return return_sanic({"code": 200, "msg": "success update faq {}".format(file_id)})


@get_time_async
async def get_file_base64(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    file_id = safe_get(req, 'file_id')
    debug_logger.info("get_file_base64 %s", file_id)
    file_location = local_doc_qa.milvus_summary.get_file_location(file_id)
    # file_location = '/home/liujx/Downloads/2021-08-01 00:00:00.pdf'
    if not file_location:
        return return_sanic({"code": 400, "msg": "fail, file_id is Invalid"})
    with open(file_location, "rb") as f:
        file_base64 = base64.b64encode(f.read()).decode()
    return return_sanic({"code": 200, "msg": "success", "file_base64": file_base64})


@get_time_async
async def query_rewrite(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    query = safe_get(req, 'query')
    debug_logger.info("query_rewrite %s", query)

    history = safe_get(req, 'history', [])
    api_base = safe_get(req, 'api_base', LLM_BASE_URL)
    # 如果api_base中包含0.0.0.0或127.0.0.1或localhost，替换为GATEWAY_IP
    api_base = api_base.replace('0.0.0.0', GATEWAY_IP).replace('127.0.0.1', GATEWAY_IP).replace('localhost', GATEWAY_IP)
    api_key = safe_get(req, 'api_key', LLM_API_KEY)
    model_name = safe_get(req, 'model_name', LLM_MODEL_NAME)
    api_context_length = safe_get(req, 'api_context_length', LLM_MAX_LENGTH)
    

    missing_params = []
    if not api_base:
        missing_params.append('api_base')
    if not api_key:
        missing_params.append('api_key')
    if not api_context_length:
        missing_params.append('api_context_length')
    
    if missing_params:
        missing_params_str = " and ".join(missing_params) if len(missing_params) > 1 else missing_params[0]
        return return_sanic({"code": 400, "msg": f"fail, {missing_params_str} is required"})
    
    status, rewrite_result = local_doc_qa.query_rewrite(query, history, api_base, api_key, model_name, api_context_length)
    if status:
        result ={"code": 200, "msg": "success", "rewrite_query": rewrite_result}
    else:
        result ={"code": 400, "msg": f"query_rewrite error: {rewrite_result}", "rewrite_query": query}
    return return_sanic(result)


@get_time_async
async def chunk_summary(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("chunk_summary %s", user_id)

    api_base = safe_get(req, 'api_base', LLM_BASE_URL)    # 如果api_base中包含0.0.0.0或127.0.0.1或localhost，替换为GATEWAY_IP
    api_base = api_base.replace('0.0.0.0', GATEWAY_IP).replace('127.0.0.1', GATEWAY_IP).replace('localhost', GATEWAY_IP).replace("/chat/completions", "")
    api_key = safe_get(req, 'api_key', LLM_API_KEY)
    model = safe_get(req, 'model_name', LLM_MODEL_NAME)
    top_p = safe_get(req, 'top_p', LLM_TOP_P)
    temperature = safe_get(req, 'temperature', LLM_TEMPERATURE)
    max_tokens = safe_get(req, 'max_token', LLM_MAX_LENGTH)
    
    keywords_num = safe_get(req, 'keywords_num', 2)
    qa_num  = safe_get(req, 'qa_num', 2)
    save_summary = safe_get(req, 'save_summary', False)
    

    missing_params = []
    if not api_base:
        missing_params.append('api_base')
    if not model:
        missing_params.append('model_name')
    
    if missing_params:
        missing_params_str = " and ".join(missing_params) if len(missing_params) > 1 else missing_params[0]
        return return_sanic({"code": 400, "msg": f"fail, {missing_params_str} is required"})

    file_id = safe_get(req, 'file_id', None)  #接口只处理一个文件，用与速读文件
    if not file_id:
        return return_sanic({"code": 400, "msg": "fail, file_id is required"})
    elif not isinstance(file_id, str):
        return return_sanic({"code": 400, "msg": "fail, file_id should be a string"})
    else:
        # 检查file_ids是否已经存在
        kb_id = local_doc_qa.milvus_summary.get_kbid_by_fileid(file_id)
        if not kb_id:
            return return_sanic({"code": 400, "msg": f"fail, file_id {file_id} not found"})
        exist_file_ids = local_doc_qa.milvus_summary.check_file_exist(user_id, kb_id, [file_id])

        if len(exist_file_ids) == 0:
            msg = f"file_id {file_id} 不存在，请检查！"
            debug_logger.info("%s", msg)
            return return_sanic({"code": 400, "msg": msg})
        elif exist_file_ids[0][1] != 'green':
            msg = f"file_id {file_id} 未完成，请等待处理完成后再进行摘要提取！"
            debug_logger.info("%s", msg)
            return return_sanic({"code": 400, "msg": msg})
    
    try:
        sorted_json_datas = local_doc_qa.milvus_summary.get_document_by_file_id(file_id)    
        debug_logger.info("sorted_json_datas %s", sorted_json_datas)
        completed_text = ""
        chunk_datas=[]
        for json_data in sorted_json_datas:
            doc_id = json_data['kwargs']['chunk_id']
            chunk = json_data['kwargs']
            page_content = re.sub(r'^\[headers]\(.*?\)\n', '', chunk['page_content'])
            completed_text += page_content + '\n'

            summary_chunk = local_doc_qa.query_summary(chunk['page_content'], api_base, api_key, model, top_p=top_p, temperature=temperature, max_tokens=max_tokens)
            json_data['kwargs']["summary"] = summary_chunk

            keywords_chunk = local_doc_qa.query_extract_keywords(chunk['page_content'], api_base, api_key, model, top_p=top_p, temperature=temperature, max_tokens=max_tokens, keywords_num=keywords_num)
            json_data['kwargs']["keywords"] = keywords_chunk

            qa_chunk = local_doc_qa.query_extract_qa(chunk['page_content'], api_base, api_key, model, top_p=top_p, temperature=temperature, max_tokens=max_tokens, qa_num=qa_num)
            json_data['kwargs']["qa"] = qa_chunk
            chunk_datas.append(json_data['kwargs'])

            if save_summary:
                local_doc_qa.milvus_summary.update_jsondata( doc_id, json_data)

    except Exception as e:
        debug_logger.error("chunk_summary error: %s", e)
        return return_sanic({"code": 500, "msg": f"fail, {e}"})

    
    return return_sanic({"code": 200, "msg": "success", "chunk_result": chunk_datas, "completed_text": completed_text})


@get_time_async
async def file_extract_outline(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    
    # 基本参数检查
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    if not local_doc_qa.milvus_summary.check_user_exist_(user_id):
        return return_sanic({"code": 400, "msg": "user_id not exist"})
    debug_logger.info("file_extract_outline %s", user_id)

    # 模型参数检查
    api_base = safe_get(req, 'api_base', LLM_BASE_URL)    # 如果api_base中包含0.0.0.0或127.0.0.1或localhost，替换为GATEWAY_IP
    api_base = api_base.replace('0.0.0.0', GATEWAY_IP).replace('127.0.0.1', GATEWAY_IP).replace('localhost', GATEWAY_IP).replace("/chat/completions", "")
    api_key = safe_get(req, 'api_key', LLM_API_KEY)
    model = safe_get(req, 'model_name', LLM_MODEL_NAME)
    top_p = safe_get(req, 'top_p', LLM_TOP_P)
    temperature = safe_get(req, 'temperature', LLM_TEMPERATURE)
    max_tokens = safe_get(req, 'max_token', LLM_MAX_LENGTH)

    # 处理文件检查
    file_id = safe_get(req, 'file_id', None)  #接口只处理一个文件，用与速读文件
    if not file_id:
        return return_sanic({"code": 400, "msg": "fail, file_id is required"})
    elif not isinstance(file_id, str):
        return return_sanic({"code": 400, "msg": "fail, file_id should be a string"})
    elif file_id.endswith("_outline"):
        return return_sanic({"code": 400, "msg": "该文件为大纲文件，不再提取大纲。"})
    else:
        # 检查file_ids是否已经存在
        kb_id = local_doc_qa.milvus_summary.get_kbid_by_fileid(file_id)
        if not kb_id:
            return return_sanic({"code": 400, "msg": f"fail, file_id {file_id} not found"})
        exist_file_ids = local_doc_qa.milvus_summary.check_file_exist(user_id, kb_id, [file_id])

        if len(exist_file_ids) == 0:
            msg = f"file_id {file_id} 不存在，请检查！"
            debug_logger.info("%s", msg)
            return return_sanic({"code": 400, "msg": msg})
        elif exist_file_ids[0][1] != 'green':
            msg = f"file_id {file_id} 未完成，请等待处理完成后再进行摘要提取！"
            debug_logger.info("%s", msg)
            return return_sanic({"code": 400, "msg": msg})
    
    outline_kbid = kb_id
    outline_fileid = file_id + "_outline"
    if local_doc_qa.milvus_summary.check_file_exist(user_id, outline_kbid, [outline_fileid]):
        msg = f"file_id {outline_fileid} 大纲已经存在，请检查！"
        debug_logger.info("%s", msg)
        return return_sanic({"code": 200, "msg": msg})

    # 大纲提取
    try:
        # 直接用python-docx读取文件内容大纲
        file_path = local_doc_qa.milvus_summary.get_file_location(file_id)
        toc = ""
        if file_path.endswith('.docx'):
            toc = get_docx_toc(file_path)
        if len(toc) > 50:
            debug_logger.info(f"直接获取到文件目录内容，长度为{len(toc)}，直接使用该内容作为大纲。\n{toc}")
            file_outline = toc
        else:
            # 如果直接获取到的目录内容长度小于50，则使用llm生成大纲
            debug_logger.info(f"直接获取到文件文本内容，使用llm生成大纲。")
            sorted_json_datas = local_doc_qa.milvus_summary.get_document_by_file_id(file_id)
            completed_text = ""
            for json_data in sorted_json_datas:
                chunk = json_data['kwargs']
                page_content = re.sub(r'^\[headers]\(.*?\)\n', '', chunk['page_content'])
                completed_text += page_content + '\n'
            
            file_outline = local_doc_qa.file_outline(completed_text, api_base, api_key, model, top_p=top_p, temperature=temperature, max_tokens=max_tokens)
        kb_name = local_doc_qa.milvus_summary.get_knowledge_base_name([kb_id])[0][2]  # 获取知识库名称
        file_name = local_doc_qa.milvus_summary.get_file_name(file_id)
        data = {"user_id": user_id.split('__')[0],
                "user_info": user_id.split('__')[1],
                "kb_id": kb_id,
                "kb_name": kb_name,
                "file_id": file_id+"_outline",
                "file_name": file_name.split('.')[0] + "_大纲.txt",
                "chunk_datas": [file_outline]}
        headers = {"content-type": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"http://127.0.0.1:{RAG_SERVER_PORT}/api/rag/chunk_embedding", json=data, headers=headers) as response:
                if response.status == 200 and (await response.json())['code'] == 200:
                    debug_logger.info(f'outline request success')
                else:
                    msg = f'outline request failed with status {response.status}'
                    debug_logger.error(f'{msg}')
                    return return_sanic({"code": 400, "msg": f"fail, file_id {file_id} {msg}"})
        return return_sanic({"code": 200, "msg": "success", "file_outline": file_outline})
    
    except Exception as e:
        debug_logger.error("outline extract error: %s", e)
        return return_sanic({"code": 500, "msg": f"fail, {e}"})


@get_time_async
async def file_extract_summary(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    
    # 基本参数检查
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    if not local_doc_qa.milvus_summary.check_user_exist_(user_id):
        return return_sanic({"code": 400, "msg": "user_id not exist"})
    debug_logger.info("file_extract_summary %s", user_id)

    # 模型参数检查
    api_base = safe_get(req, 'api_base', LLM_BASE_URL)    # 如果api_base中包含0.0.0.0或127.0.0.1或localhost，替换为GATEWAY_IP
    api_base = api_base.replace('0.0.0.0', GATEWAY_IP).replace('127.0.0.1', GATEWAY_IP).replace('localhost', GATEWAY_IP).replace("/chat/completions", "")
    api_key = safe_get(req, 'api_key', LLM_API_KEY)
    model = safe_get(req, 'model_name', LLM_MODEL_NAME)
    top_p = safe_get(req, 'top_p', LLM_TOP_P)
    temperature = safe_get(req, 'temperature', LLM_TEMPERATURE)
    max_tokens = safe_get(req, 'max_token', LLM_MAX_LENGTH)

    # 处理文件检查
    file_id = safe_get(req, 'file_id', None)  #接口只处理一个文件，用与速读文件
    if not file_id:
        return return_sanic({"code": 400, "msg": "fail, file_id is required"})
    elif not isinstance(file_id, str):
        return return_sanic({"code": 400, "msg": "fail, file_id should be a string"})
    elif file_id.endswith("_summary"):
        return return_sanic({"code": 400, "msg": "该文件为摘要文件，不再单独生成摘要。"})
    else:
        # 检查file_ids是否已经存在
        kb_id = local_doc_qa.milvus_summary.get_kbid_by_fileid(file_id)
        if not kb_id:
            return return_sanic({"code": 400, "msg": f"fail, file_id {file_id} not found"})
        exist_file_ids = local_doc_qa.milvus_summary.check_file_exist(user_id, kb_id, [file_id])

        if len(exist_file_ids) == 0:
            msg = f"file_id {file_id} 不存在，请检查！"
            debug_logger.info("%s", msg)
            return return_sanic({"code": 400, "msg": msg})
        elif exist_file_ids[0][1] != 'green':
            msg = f"file_id {file_id} 未完成，请等待处理完成后再进行摘要提取！"
            debug_logger.info("%s", msg)
            return return_sanic({"code": 400, "msg": msg})
    
    summary_kbid = kb_id
    summary_fileid = file_id + "_summary"
    if local_doc_qa.milvus_summary.check_file_exist(user_id, summary_kbid, [summary_fileid]):
        msg = f"file_id {summary_fileid} 摘要已存在，请检查！"
        debug_logger.info("%s", msg)
        return return_sanic({"code": 200, "msg": msg})

    # 大纲提取
    try:
        sorted_json_datas = local_doc_qa.milvus_summary.get_document_by_file_id(file_id)
        completed_text = ""
        for json_data in sorted_json_datas:
            chunk = json_data['kwargs']
            page_content = re.sub(r'^\[headers]\(.*?\)\n', '', chunk['page_content'])
            completed_text += page_content + '\n'
        
        file_summary = local_doc_qa.file_summary(completed_text, api_base, api_key, model, top_p=top_p, temperature=temperature, max_tokens=max_tokens)
        kb_name = local_doc_qa.milvus_summary.get_knowledge_base_name([kb_id])[0][2]  # 获取知识库名称
        file_name = local_doc_qa.milvus_summary.get_file_name(file_id)
        data = {"user_id": user_id.split('__')[0],
                "user_info": user_id.split('__')[1],
                "kb_id": kb_id,
                "kb_name": kb_name,
                "file_id": file_id+"_summary",
                "file_name": file_name.split('.')[0] + "_摘要.txt",
                "chunk_datas": [file_summary]}
        headers = {"content-type": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"http://127.0.0.1:{RAG_SERVER_PORT}/api/rag/chunk_embedding", json=data, headers=headers) as response:
                if response.status == 200 and (await response.json())['code'] == 200:
                    debug_logger.info(f'summary request success')
                else:
                    msg = f'summary request failed with status {response.status}'
                    debug_logger.error(f'{msg}')
                    return return_sanic({"code": 2003, "msg": f"fail, file_id {file_id} {msg}"})
        return return_sanic({"code": 200, "msg": "success", "file_summary": file_summary})
    
    except Exception as e:
        debug_logger.error("summary extract error: %s", e)
        return return_sanic({"code": 500, "msg": f"fail, {e}"})
    

    

async def modify_chunk_kwargs(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("modify_chunk_kwargs %s", user_id)
    
    doc_id = safe_get(req, 'doc_id', None)
    if not doc_id:
        return return_sanic({"code": 400, "msg": "fail, doc_id is required"})
    elif not isinstance(doc_id, str):
        return return_sanic({"code": 400, "msg": "fail, doc_id should be a string"})
    
    kwargs = safe_get(req, 'kwargs', None)
    if kwargs:
        try:
            kwargs = json.loads(kwargs)
        except Exception as e:
            return return_sanic({"code": 400, "msg": f"fail, kwargs should be a json string"})
    else:
        return_sanic({"code": 400, "msg": f"fail, kwargs is required"})


    # 获取文件信息
    json_data = local_doc_qa.milvus_summary.get_document_by_doc_id(doc_id)
    if json_data is None:
        return return_sanic({"code": 400, "msg": f"fail, doc_id {doc_id} 不存在，请检查！"})
    debug_logger.info(f"{doc_id} json_data %s", json_data)
    for key, value in kwargs.items():
        json_data['kwargs'][key] = value
    
    debug_logger.info(f"after modify {doc_id} json_data %s", json_data)
    local_doc_qa.milvus_summary.update_jsondata(doc_id, json_data)
    return return_sanic({"code": 200, "msg": "success"})



async def delete_chunk_metadata(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("delete_chunk_metadata %s", user_id)
    
    doc_id = safe_get(req, 'doc_id', None)
    if not doc_id:
        return return_sanic({"code": 400, "msg": "fail, doc_id is required"})
    elif not isinstance(doc_id, str):
        return return_sanic({"code": 400, "msg": "fail, doc_id should be a string"})
    
    delete_keys = safe_get(req, 'delete_keys', None)
    if not delete_keys:
        return_sanic({"code": 400, "msg": f"fail, delete_keys is required"})


    # 获取文件信息
    json_data = local_doc_qa.milvus_summary.get_document_by_doc_id(doc_id)
    if json_data is None:
        return return_sanic({"code": 400, "msg": f"fail, doc_id {doc_id} 不存在，请检查！"})
    debug_logger.info(f"{doc_id} json_data %s", json_data)
    for key in delete_keys:
        if key in json_data['kwargs']:
            del json_data['kwargs'][key]
        else:
            debug_logger.info(f"key {key} not exist in {doc_id} json_data %s", json_data)
    
    debug_logger.info(f"after modify {doc_id} json_data %s", json_data)
    local_doc_qa.milvus_summary.update_jsondata(doc_id, json_data)
    return return_sanic({"code": 200, "msg": "success"})



async def update_kb_metadata(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("update_kb_metadata %s", user_id)

    kb_id = safe_get(req, 'kb_id')
    kb_id = correct_kb_id(kb_id)
    debug_logger.info("kb_id %s", kb_id)
    not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, [kb_id])
    if not_exist_kb_ids:
        debug_logger.info(f"invalid kb_id: {not_exist_kb_ids} new knowledge base")
        msg = "invalid kb_id: {}, please check...".format(not_exist_kb_ids)
        return return_sanic({"code": 400, "msg": msg})
    
    add_metadata = safe_get(req, 'metadata', None)
    if not add_metadata:
        return return_sanic({"code": 400, "msg": "fail, metadata is required"})
    elif not isinstance(add_metadata, str):
        return return_sanic({"code": 400, "msg": "fail, metadata should be a json string"})
    try:
        add_metadata = json.loads(add_metadata)
    except Exception as e:
        return return_sanic({"code": 400, "msg": f"fail, metadata should be a json string, error:{e}"})
    
    debug_logger.info("add_metadata %s", add_metadata)

    local_doc_qa.milvus_summary.update_kb_metadata(user_id, kb_id, add_metadata)   # 注意该接口为直接替换，非增量更新或者变更，方便删除、更改、新增等操作
    return return_sanic({"code": 200, "msg": "success"})




async def update_file_metadata(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("update_file_metadata %s", user_id)

    file_id = safe_get(req, 'file_id')
    exist_file_ids = local_doc_qa.milvus_summary.check_file_exist_byuserid(user_id, [file_id])
    if not exist_file_ids:
        debug_logger.info(f"invalid file_id: {file_id}")
        msg = "invalid file_id: {}, please check...".format(file_id)
        return return_sanic({"code": 400, "msg": msg})
    
    add_metadata = safe_get(req, 'metadata', None)
    if not add_metadata:
        return return_sanic({"code": 400, "msg": "fail, metadata is required"})
    elif not isinstance(add_metadata, str):
        return return_sanic({"code": 400, "msg": "fail, metadata should be a json string"})
    try:
        add_metadata = json.loads(add_metadata)
    except Exception as e:
        return return_sanic({"code": 400, "msg": f"fail, metadata should be a json string, error:{e}"})
    
    debug_logger.info("add_metadata %s", add_metadata)

    local_doc_qa.milvus_summary.update_file_metadata(user_id, file_id, add_metadata)   # 注意该接口为直接替换，非增量更新或者变更，方便删除、更改、新增等操作
    return return_sanic({"code": 200, "msg": "success"})



@get_time_async
async def dify_rag_search(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    knowledge_id = safe_get(req, 'knowledge_id')
    question = safe_get(req, 'query')
    retrieval_setting = safe_get(req, 'retrieval_setting')
    metadata_condition = safe_get(req, 'metadata_condition')
    
    debug_logger.info("dify_rag_search %s", knowledge_id)
    debug_logger.info("query %s", question)
    debug_logger.info("retrieval_setting %s", retrieval_setting)
    debug_logger.info("metadata_condition %s", metadata_condition)

    user_id = safe_get(req, 'user_id', "user")
    user_info = safe_get(req, 'user_info', "1234")
    user_id = user_id + '__' + user_info
    debug_logger.info('user_info %s', user_info)
    
    # kb_infos = local_doc_qa.milvus_summary.get_knowledge_bases(user_id)
    # kb_ids = [kb_info['0'] for kb_info in kb_infos]
    # if not kb_ids:
    #     return return_sanic({"error_code": 2001, "error_msg": "fail, no knowledge base found"})
    kb_ids = [knowledge_id]
    kb_ids = [correct_kb_id(kb_id) for kb_id in kb_ids]
    not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, kb_ids)
    if not_exist_kb_ids:
        debug_logger.info(f"invalid kb_id: {not_exist_kb_ids} new knowledge base")
        return return_sanic({"error_code": 400, "error_msg": "fail, no knowledge base found"})

    
    rerank = safe_get(req, 'rerank', default=True)
    need_web_search = safe_get(req, 'networking', False)
    web_search_tools = safe_get(req, 'web_search_tools', ["BaiduSearch"])
    hybrid_search = safe_get(req, 'hybrid_search', False)
    web_chunk_size = safe_get(req, 'web_chunk_size', DEFAULT_PARENT_CHUNK_SIZE)
    
    top_k = retrieval_setting.get('top_k', 5) if retrieval_setting else 5
    score_threshold = retrieval_setting.get('score_threshold', 0.5) if retrieval_setting else 0.5
    if not isinstance(score_threshold, float) or score_threshold<0 or score_threshold >1:
        debug_logger.warning(f"score_threshold not met requirements. score_threshold:{score_threshold}, use default value 0.5")
        score_threshold = 0.5

    qa_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    for kb_id in kb_ids:
        local_doc_qa.milvus_summary.update_knowledge_base_latest_qa_time(kb_id, qa_timestamp)
    
    
    debug_logger.info("get_knowledge_search_answer...")
    t1 = time.time()
    time_record = {}
    try:
        parser_config = local_doc_qa.milvus_summary.get_kb_parser_config(kb_ids[0]) # 同一个用户的知识库的parser_config是一样的
        milvus_kb = VectorStoreMilvusClient(parser_config)
        retriever = ParentRetriever(milvus_kb, local_doc_qa.milvus_summary, local_doc_qa.es_client, parser_config['separators'], parser_config['chunk_size'])
        resp, search_msg = await local_doc_qa.get_knowledge_search_answer(
                                                        kb_ids=kb_ids,
                                                        query=question,
                                                        retriever=retriever,
                                                        top_k=top_k,
                                                        rerank=rerank,
                                                        time_record=time_record,
                                                        need_web_search=need_web_search,
                                                        web_search_tools=web_search_tools,
                                                        hybrid_search=hybrid_search,
                                                        web_chunk_size=web_chunk_size,
                                                        score_threshold=score_threshold
                                                        )
    except Exception as e:
        debug_logger.error(f"get_knowledge_search_answer error: {e}")
        return return_sanic({"code": 500, "message": "get_knowledge_search_answer error"})
    
    try:
        result = []
        logical_operator = metadata_condition.get('logical_operator', 'and') if metadata_condition else 'and'
        conditions = metadata_condition.get('conditions', []) if metadata_condition else []
        kbs_info = local_doc_qa.milvus_summary.get_knowledge_bases(user_id)
        kbs_metadata = {
            kb_info[0]: json.loads(kb_info[-1]) if kb_info[-1] else {}
            for kb_info in kbs_info
            if kb_info[0] in kb_ids
        }
        debug_logger.info(f"kb_ids:{kb_ids}, kbs_metadata:{kbs_metadata}")
        

        def compare_metadata(doc_value, condition_value, comparison_operator):
            """
            根据指定的比较操作符，比较文档值 (doc_value) 和条件值 (condition_value)。

            参数:
                doc_value: 文档中的值（可以是字符串、数字或日期等）。
                condition_value: 条件值（可以是字符串、数字或日期等）。
                comparison_operator: 比较操作符（如 'contains', '==', '>', '<=' 等）。

            返回:
                布尔值，表示比较结果是否为真。
            """
            # 字符串相关的操作符
            if comparison_operator == 'contains':
                return str(condition_value) in str(doc_value)
            elif comparison_operator == 'not contains':
                return str(condition_value) not in str(doc_value)
            elif comparison_operator == 'start with':
                return str(doc_value).startswith(str(condition_value))
            elif comparison_operator == 'end with':
                return str(doc_value).endswith(str(condition_value))

            # 等值和不等值操作符
            elif comparison_operator == 'is':
                return doc_value == condition_value
            elif comparison_operator == 'is not':
                return doc_value != condition_value
            elif comparison_operator == '==':
                return doc_value == condition_value
            elif comparison_operator == '!=':
                return doc_value != condition_value

            # 数值大小比较操作符
            elif comparison_operator == '>':
                return doc_value > condition_value
            elif comparison_operator == '<':
                return doc_value < condition_value
            elif comparison_operator == '>=':
                return doc_value >= condition_value
            elif comparison_operator == '<=':
                return doc_value <= condition_value

            # 空值判断操作符
            elif comparison_operator == 'empty':
                return doc_value is None or doc_value == ''
            elif comparison_operator == 'not empty':
                return doc_value is not None and doc_value != ''

            # 日期相关操作符
            elif comparison_operator == 'before':
                return doc_value < condition_value
            elif comparison_operator == 'after':
                return doc_value > condition_value

            # 如果传入的操作符无效，抛出异常
            else:
                raise ValueError(f"Unsupported comparison operator: {comparison_operator}")

        file_metadatas = {}
        for doc in resp:
            kb_id = doc.metadata.get('kb_id')
            file_id = doc.metadata.get('file_id')
            if file_id not in file_metadatas:
                tmp_metadata = local_doc_qa.milvus_summary.get_files(user_id, kb_id, file_id)[0][10] 
                file_metadatas[file_id] = tmp_metadata if tmp_metadata else {}
            file_metadata = file_metadatas[file_id]

            doc_return = {
                "metadata": file_metadata,
                "score": doc.metadata.get('score'),
                "title": doc.metadata.get('file_name'),
                "content": doc.page_content
            }

            
            if conditions:
                if logical_operator == 'and':
                    if all([condition['name'] in file_metadata and compare_metadata(file_metadata[condition['name']], condition['value'], condition['comparison_operator']) for condition in conditions]):
                        result.append(doc_return)
                elif logical_operator == 'or':
                    if any([condition['name'] in file_metadata and compare_metadata(file_metadata[condition['name']], condition['value'], condition['comparison_operator']) for condition in conditions]):
                        result.append(doc_return)
            else:
                result.append(doc_return)

        return_result = {
            "records": result
        }
        return return_sanic(return_result)
    except Exception as e:
        return return_sanic({"error_code": 400, "error_msg": str(e)})
    



@get_time_async
async def move_file(req: request):
    local_doc_qa: LocalDocQA = req.app.ctx.local_doc_qa
    user_id = safe_get(req, 'user_id')
    user_info = safe_get(req, 'user_info', "1234")
    passed, msg = check_user_id_and_user_info(user_id, user_info)
    if not passed:
        return return_sanic({"code": 400, "msg": msg})
    user_id = user_id + '__' + user_info
    debug_logger.info("get_doc_completed %s", user_id)
    
    target_kb_id = safe_get(req, 'target_kb_id')  # 移动到的目标知识库，只能在当前用户下，不能跨用户
    if not target_kb_id:
        return return_sanic({"code": 400, "msg": "fail, target_kb_id is None"})
    
    # 检查目标知识库是否存在
    target_kb_id = correct_kb_id(target_kb_id)
    debug_logger.info("target_kb_id: {}".format(target_kb_id))
    not_exist_kb_ids = local_doc_qa.milvus_summary.check_kb_exist(user_id, [target_kb_id])
    if not_exist_kb_ids:
        debug_logger.info(f"invalid target_kb_id: {not_exist_kb_ids}")
        msg = "invalid target_kb_id: {}, please check...".format(not_exist_kb_ids)
        return return_sanic({"code": 400, "msg": msg})
    
    # 检查文件是否存在
    file_id = safe_get(req, 'file_id')
    if not file_id:
        return return_sanic({"code": 400, "msg": "fail, file_id is None"})
    debug_logger.info("file_id: {}".format(file_id))
    origin_kb_id = local_doc_qa.milvus_summary.get_kbid_by_fileid(file_id)
    if not origin_kb_id:
        return return_sanic({"code": 400, "msg": "fail, file_id {} not found".format(file_id)})
    if origin_kb_id == target_kb_id:
        return return_sanic({"code": 200, "msg": "success, origin_kb_id is same as target_kb_id, no need to move"})
    
    # 判断两个知识库的embedding模型，解析参数是否一致
    
    origin_parser_config = local_doc_qa.milvus_summary.get_kb_parser_config(origin_kb_id)
    target_parser_config = local_doc_qa.milvus_summary.get_kb_parser_config(target_kb_id)
    if origin_parser_config != target_parser_config:
        return return_sanic({"code": 400, "msg": "fail, origin_kb_id and target_kb_id have different parser config, can not move file"})

    
    try:
        # 移动对应的文件到新的知识库目录
        file_location = os.path.join(UPLOAD_ROOT_PATH, user_id, origin_kb_id, file_id)
        new_file_location = os.path.join(UPLOAD_ROOT_PATH, user_id, target_kb_id, file_id)
        shutil.move(file_location, new_file_location)
        debug_logger.info("move file from {} to {}".format(file_location, new_file_location))

        # 更改数据库记录
        local_doc_qa.milvus_summary.move_file(user_id, file_id, target_kb_id)

        # 更新向量索引中的kb_id
        milvus_kb = VectorStoreMilvusClient(origin_parser_config)
        milvus_kb.local_vectorstore.update_kb_id_for_file_id(file_id, target_kb_id)
        local_doc_qa.es_client.update_kb_id_for_file_id(file_id, target_kb_id)
        return return_sanic({"code": 200, "msg": "success move file {} from kb {} to kb {}".format(file_id, origin_kb_id, target_kb_id)})

    except Exception as e:
        debug_logger.error("get_doc_chunks error: {}".format(e))
        return return_sanic({"code": 500, "msg": "fail, get_doc_chunks error: {}".format(e)})
    
