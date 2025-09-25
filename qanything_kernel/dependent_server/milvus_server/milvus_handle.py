from qanything_kernel.utils.custom_log import milvus_logger
from qanything_kernel.configs.model_config import MILVUS_PORT, MILVUS_HOST_LOCAL
import json
import time
import pymilvus
import numpy as np
from sanic import request, response
from sanic.exceptions import BadRequest
from sanic.request import Request
from sanic.response import json as sanic_json
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection, MilvusClient


__all__ = ["create_collection", "delete_collection", "get_collection_info", "list_collections", "set_collection_index",
           "insert_vectors", "delete_vectors", "search_vectors", "expr_search", "clear_deleted_vectors"]

def safe_get(req: Request, attr: str, default=None):
    try:
        if attr in req.form:
            return req.form.getlist(attr)[0]
        if attr in req.args:
            return req.args[attr]
        if attr in req.json:
            return req.json[attr]
        # if value := req.form.get(attr):
        #     return value
        # if value := req.args.get(attr):
        #     return value
        # """req.json执行时不校验content-type，body字段可能不能被正确解析为json"""
        # if value := req.json.get(attr):
        #     return value
    except BadRequest:
        milvus_logger.warning(f"missing {attr} in request")
    except Exception as e:
        milvus_logger.warning(f"get {attr} from request failed:")
    return default


milvus_logger.info("start connecting to Milvus")
connections.connect("default", host=MILVUS_HOST_LOCAL, port=MILVUS_PORT)
# milvus_client = MilvusClient("http://192.168.5.145:19540")
# connections.connect("default", host="192.168.5.145", port="19540")
for con in connections.list_connections():
    addr = connections.get_connection_addr(con[0])
    milvus_logger.info(f"Connected to Milvus: {addr}")
    # con[0]是该连接的uuid，addr是连接的地址

# 打印请求返回的内容
def return_sanic(return_result):
    data_dumps = json.dumps(return_result, ensure_ascii=False, indent=4)
    milvus_logger.info(f"return_sanic: {data_dumps}\n\n\n")
    return sanic_json(return_result)


def create_collection(req: request):
    collection_name = safe_get(req, "collection_name")
    collection_description = safe_get(req, "collection_description", "")

    if collection_name is None:
        return return_sanic({"code": 2001, "msg": "fail,collection_name is None"})
    
    # 判断字符串是否只包含字母和数字和下划线
    if not collection_name.replace("_", "").isalnum():
        return return_sanic({"code": 2001, "msg": "fail,collection_name must be Letters, numbers, and underscores"})
    if len(collection_name) > 255:
        return return_sanic({"code": 2001, "msg": "fail,collection_name must be less than 255 characters"})

    has = utility.has_collection(collection_name)
    milvus_logger.info(f"Does collection hello_milvus exist in Milvus: {has}")
    if has:
        return return_sanic({"code": 2001, "msg": f"fail,collection_name {collection_name} already exists"})

    fields = safe_get(req, "fields")
    if fields is None:
        return return_sanic({"code": 2001, "msg": "fail,fields is None"})
    
    # 初始化一个空列表来存储 FieldSchema 对象
    field_schemas = []

    # 遍历 fields 列表
    for field in fields:
        # 从字段字典中获取各个属性
        try:
            name = field["name"]
            data_type = field["data_type"]  # 整型
            description = field.get("description", "")  # 可选属性
            kwargs = {k: v for k, v in field.items() if k not in ["name", "data_type", "description"]} # 将fields中其余属性添加到kwargs
        except Exception as e:
            milvus_logger.error(f"fail,invalid field: {field}")
            return return_sanic({"code": 2001, "msg": f"fail,invalid field: {field}，error: {e}"})
        
        # 确认 data_type 是否在 DataType 枚举中
        if data_type is None or data_type not in (item.value for item in DataType):
            return return_sanic({"code": 2001, "msg": f"fail, invalid data_type: {data_type}"})
        # for item in DataType:
        #     if data_type == item.value:
        #         data_type = item
        #         break
        
        field_schema = FieldSchema(name=name, dtype=data_type, description=description, **kwargs)

        # 将创建的 FieldSchema 对象添加到列表中
        field_schemas.append(field_schema)
    
    schema = CollectionSchema(field_schemas, description=collection_description)
    collection = Collection(name=collection_name, schema=schema)
    return return_sanic({"code": 200, "msg": f"success create collection {collection_name}"})


def delete_collection(req: request):
    collection_name = safe_get(req, "collection_name")
    if collection_name is None:
        return return_sanic({"code": 2001, "msg": "fail,collection_name is None"})

    has = utility.has_collection(collection_name)
    milvus_logger.info(f"Does collection hello_milvus exist in Milvus: {has}")
    if not has:
        return return_sanic({"code": 2001, "msg": f"fail,collection_name {collection_name} not exists"})
    utility.drop_collection(collection_name)
    return return_sanic({"code": 200, "msg": f"success delete collection {collection_name}"})
    

def get_collection_info(req: request):
    collection_name = safe_get(req, "collection_name")
    if collection_name is None:
        return return_sanic({"code": 2001, "msg": "fail,collection_name is None"})

    has = utility.has_collection(collection_name)
    milvus_logger.info(f"Does collection hello_milvus exist in Milvus: {has}")
    if not has:
        return return_sanic({"code": 2001, "msg": f"fail,collection_name {collection_name} not exists"})
    collection = Collection(collection_name)
    return return_sanic({"code": 200, "msg": f"success get collection {collection_name}", 
                         "num_entities": collection.num_entities,
                         "schema": collection.schema.to_dict(),
                         "index_params": collection.index().params if collection.has_index() else None})


def list_collections(req: request):
    collections = utility.list_collections()
    return return_sanic({"code": 200, "msg": f"success list collections", "data": collections})


def set_collection_index(req: request):
    collection_name = safe_get(req, "collection_name")
    if collection_name is None:
        return return_sanic({"code": 2001, "msg": "fail,collection_name is None"})

    has = utility.has_collection(collection_name, timeout=5)
    milvus_logger.info(f"Does collection hello_milvus exist in Milvus: {has}")
    if not has:
        return return_sanic({"code": 2001, "msg": f"fail,collection_name {collection_name} not exists"})
    
    
    filed_name = safe_get(req, "filed_name")
    if filed_name is None:
        return return_sanic({"code": 2001, "msg": "fail,filed_name is None"})

    # 判断filed_name是否在collection中
    collection = Collection(collection_name)
    valid_field_names = [field.name for field in collection.schema.fields]
    if filed_name not in valid_field_names:
        return return_sanic({"code": 2001, "msg": f"fail,filed_name {filed_name} not in collection {collection_name}, valid_field_names: {valid_field_names}"})
    
    index_type = safe_get(req, "index_type", 'IVF_FLAT')
    metric_type = safe_get(req, "metric_type", 'L2')
    params = safe_get(req, "params", {"nlist":1024})
    index_params = {
        "index_type": index_type,
        "metric_type": metric_type,
        "params": params
    }
    milvus_logger.info(f"index_params: {index_params}")
    suport_index_type = ["FLAT", "IVF_FLAT", "IVF_SQ8", "IVF_PQ", "IVF_HNSW"]
    suport_metric_type = ["L2", "IP", "Hamming", "Jaccard"]
    if index_type not in suport_index_type:
        return return_sanic({"code": 2001, "msg": f"fail,index_type {index_type} not support. valid index_type: {suport_index_type}"})
    if metric_type not in suport_metric_type:
        return return_sanic({"code": 2001, "msg": f"fail,metric_type {metric_type} not support. valid metric_type: {suport_metric_type}"})
    
    collection.create_index(filed_name, index_params, timeout=5)
    return return_sanic({"code": 200, "msg": f"success set collection {collection_name} index {index_params}"})


def insert_vectors(req: request):
    collection_name = safe_get(req, "collection_name")
    if collection_name is None:
        return return_sanic({"code": 2001, "msg": "fail,collection_name is None"})

    has = utility.has_collection(collection_name)
    milvus_logger.info(f"Does collection hello_milvus exist in Milvus: {has}")
    if not has:
        return return_sanic({"code": 2001, "msg": f"fail,collection_name {collection_name} not exists"})
    
    vectors = safe_get(req, "vectors", None)
    if vectors is None:
        return return_sanic({"code": 2001, "msg": "fail,vectors is None"})
    
    col = Collection(collection_name)
    milvus_logger.info(f"Number of entities in Milvus: {col.num_entities}")  # check the num_entities
    milvus_logger.info("Start inserting entities")
    
    try:
        insert_result = col.insert(vectors)
        milvus_logger.info(f"Milvus insert result: {insert_result}")
        col.flush()
    except Exception as e:
        milvus_logger.error(f"fail,insert vectors error: {e}")
        return return_sanic({"code": 2001, "msg": f"fail,insert vectors error: {e}"})
    milvus_logger.info(f"After insert Number of entities in Milvus: {col.num_entities}")  # check the num_entities
    return return_sanic({"code": 200, "msg": f"success insert vectors {insert_result}"})


def delete_vectors(req: request):
    collection_name = safe_get(req, "collection_name")
    if collection_name is None:
        return return_sanic({"code": 2001, "msg": "fail, collection_name is None"})

    has = utility.has_collection(collection_name)
    milvus_logger.info(f"Does collection hello_milvus exist in Milvus: {has}")
    if not has:
        return return_sanic({"code": 2001, "msg": f"fail, collection_name {collection_name} not exists"})
    expr = safe_get(req, "expr", None)
    compact = safe_get(req, "compact", False)
    if expr is None:
        return return_sanic({"code": 2001, "msg": "fail, delete expr is None"})
    milvus_logger.info(f"Start deleting entities with expr: {expr}")
    
    collection = Collection(collection_name)
    milvus_logger.info(f"Number of entities in Milvus: {collection.num_entities}")
    try:
        res = collection.delete(expr)
        milvus_logger.info(f"Milvus delete result: {res}")
        collection.flush()
        if compact:
            collection.compact()
        milvus_logger.info(f"After delete Number of entities in Milvus: {collection.num_entities}")
    except Exception as e:
        milvus_logger.error(f"fail,delete vectors error: {e}")
        return return_sanic({"code": 2001, "msg": f"fail,delete vectors error: {e}"})
    return return_sanic({"code": 200, "msg": f"success delete vectors {res}"})



def search_vectors(req: request):
    collection_name = safe_get(req, "collection_name")
    if collection_name is None:
        return return_sanic({"code": 2001, "msg": "fail, collection_name is None"})

    has = utility.has_collection(collection_name)
    milvus_logger.info(f"Does collection hello_milvus exist in Milvus: {has}")
    if not has:
        return return_sanic({"code": 2001, "msg": f"fail, collection_name {collection_name} not exists"})
    
    vectors = safe_get(req, "vectors")  # 格式为[vector1, ... , vectorn]
    if vectors is None:
        return return_sanic({"code": 2001, "msg": "fail, vectors is None"})
    
    # 检索相关参数
    
    anns_field = safe_get(req, "anns_field")
    param = safe_get(req, "param", {"metric_type": "L2","params": {"nprobe": 12}})
    limit = safe_get(req, "limit", 10)
    expr = safe_get(req, "expr", None)
    partition_names = safe_get(req, "partition_names", None)
    output_fields = safe_get(req, "output_fields", None)
    timeout = safe_get(req, "timeout", None)
    round_decimal = safe_get(req, "round_decimal", -1)


    collection = Collection(collection_name)
    if collection.has_index():
        collection.load()
    else:
        return return_sanic({"code": 2001, "msg": f"fail, collection_name {collection_name} has no index"})
    try:
        result = collection.search(vectors, anns_field, param, limit, expr, partition_names, output_fields, timeout, round_decimal)
    except Exception as e:
        milvus_logger.error(f"fail,search vectors error: {e}")
        return return_sanic({"code": 2001, "msg": f"fail,search vectors error: {e}"})
    
    milvus_logger.info(f"Search result: {result}")

    
    # 将result中的numpy元素转换为json可序列化的格式
    for i in range(len(result)):
        for j in range(len(result[i])):
            result[i][j] = str(result[i][j])
    
    return return_sanic({"code": 200, "msg": "success search vectors", "search_result":result})


def expr_search(req: request):
    collection_name = safe_get(req, "collection_name")
    if collection_name is None:
        return return_sanic({"code": 2001, "msg": "fail, collection_name is None"})

    has = utility.has_collection(collection_name)
    milvus_logger.info(f"Does collection hello_milvus exist in Milvus: {has}")
    if not has:
        return return_sanic({"code": 2001, "msg": f"fail, collection_name {collection_name} not exists"})

    expr = safe_get(req, "expr", None)  # "random > 0.5"
    if expr is None:
        return return_sanic({"code": 2001, "msg": "fail, delete expr is None"})
    
    output_fields = safe_get(req, "output_fields", None) #["random", "embeddings"]

    collection = Collection(collection_name)
    if collection.has_index():
        collection.load()
    else:
        return return_sanic({"code": 2001, "msg": f"fail, collection_name {collection_name} has no index"})
    result = collection.query(expr=expr, output_fields=output_fields)
    milvus_logger.info(f"success expr search, result: {result}")
    # 将result中的numpy元素转换为json可序列化的格式
    for i in range(len(result)):
        for key in result[i].keys():
            if isinstance(result[i][key], np.ndarray):
                result[i][key] = result[i][key].tolist()
            
            try:
                json.dumps(result[i][key])
            except Exception as e:
                result[i][key] = str(result[i][key])

    return return_sanic({"code": 200, "msg": "success expr search", "data": result})


def clear_deleted_vectors(req: request):
    collection_name = safe_get(req, "collection_name")
    if collection_name is None:
        return return_sanic({"code": 2001, "msg": "fail, collection_name is None"})

    has = utility.has_collection(collection_name)
    milvus_logger.info(f"Does collection hello_milvus exist in Milvus: {has}")
    if not has:
        return return_sanic({"code": 2001, "msg": f"fail, collection_name {collection_name} not exists"})

    collection = Collection(collection_name)
    milvus_logger.info(f"Number of entities in Milvus: {collection.num_entities}")
    collection.compact()
    milvus_logger.info(f"After delete Number of entities in Milvus: {collection.num_entities}")
    return return_sanic({"code": 200, "msg": "success clear deleted vectors"})