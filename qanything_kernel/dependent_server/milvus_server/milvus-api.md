# milvus server 接口文档

- [milvus server 接口文档](#milvus server-接口文档)
  - [创建一个集合（POST）](#创建一个集合post)
    - [URL：http://{your_host}:8778/api/milvus/create_collection ](#create_collection)
    - [创建集合请求参数（Body）](#创建集合请求参数body)
    - [创建集合请求示例](#创建集合请求示例)
    - [创建集合响应示例](#创建集合响应示例)
  - [删除集合（POST）](#删除集合post)
    - [URL：http://{your_host}:8778/api/milvus/delete_collection ](#delete_collection)
    - [删除集合请求参数（Body）](#删除集合请求参数body)
    - [删除集合请求示例](#删除集合请求示例)
    - [删除集合响应示例](#删除集合响应示例)
  - [获取集合信息（POST）](#获取集合信息post)
    - [URL：http://{your_host}:8778/api/milvus/get_collection_info](#get_collection_info)
    - [获取集合信息请求参数（Body）](#获取集合信息请求参数body)
    - [获取集合信息请求示例](#获取集合信息请求示例)
    - [获取集合信息响应示例](#获取集合信息响应示例)
  - [获取所有集合（POST、GET）](#获取所有集合postget)
    - [URL：http://{your_host}:8778/api/milvus/list_collections](#list_collections)
    - [获取所有集合请求示例](#获取所有集合请求示例)
    - [获取所有集合响应示例](#获取所有集合响应示例)
  - [在实体上生成索引（POST）](#在实体上生成索引post)
    - [URL：http://{your_host}:8778/api/milvus/set_collection_index ](#set_collection_index)
    - [在实体上生成索引请求参数（Body）](#在实体上生成索引请求参数body)
    - [在实体上生成索引请求示例](#在实体上生成索引请求示例)
    - [在实体上生成索引响应示例](#在实体上生成索引响应示例)
  - [在集合中插入向量（POST）](#在集合中插入向量post)
    - [URL：http://{your_host}:8778/api/milvus/insert_vectors](#insert_vectors)
    - [在集合中插入向量请求参数（Body）](#在集合中插入向量请求参数body)
    - [在集合中插入向量请求示例](#在集合中插入向量请求示例)
    - [在集合中插入向量响应示例](#在集合中插入向量响应示例)
  - [在集合中删除向量（POST）](#在集合中删除向量post)
    - [URL：http://{your_host}:8778/api/milvus/delete_vectors](#delete_vectors)
    - [在集合中删除向量请求参数（Body）](#在集合中删除向量请求参数body)
    - [在集合中删除向量请求示例](#在集合中删除向量请求示例)
    - [在集合中删除向量响应示例](#在集合中删除向量响应示例)
  - [在集合中搜索向量（POST）](#在集合中搜索向量post)
    - [URL: http://{your_host}:8778/api/milvus/search_vectors](#search_vectors)
    - [在集合中搜索向量请求参数（Body）](#在集合中搜索向量请求参数body)
    - [在集合中搜索向量请求示例](#在集合中搜索向量请求示例)
    - [在集合中搜索向量响应示例](#在集合中搜索向量响应示例)
  - [在集合中查询向量（POST）](#在集合中查询向量post)
    - [URL：http://{your_host}:8778/api/milvus/expr_search](#expr_search)
    - [在集合中查询向量请求参数（Body）](#在集合中查询向量请求参数body)
    - [在集合中查询向量请求示例](#在集合中查询向量请求示例)
    - [在集合中查询向量响应示例](#在集合中查询向量响应示例)
  - [清除删除的向量（POST）](#清除删除的向量post)
    - [URL：http://{your_host}:8778/api/milvus/clear_deleted_vectors](#clear_deleted_vectors)
    - [清除删除的向量请求参数（Body）](#清除删除的向量请求参数body)
    - [清除删除的向量请求示例](#清除删除的向量请求示例)
    - [清除删除的向量响应示例](#清除删除的向量响应示例)


## <h2><p id="创建一个集合post">创建一个集合（POST）</p></h2>

### <h3><p id="create_collection"> 接口地址</p></h3>
* URL：<http://{your_host}:8778/api/milvus/create_collection>

### <h3><p id="创建集合请求参数body">创建集合请求参数（Body）</p></h3>

| 参数名     | 示例参数值                                           | 是否必填 | 参数类型   | 描述说明                     |
| ------- | ----------------------------------------------- | ---- | ------ | ------------------------ |
| collection_name | "testabc_1"                                           | 是    | String | 创建集合名称，仅支持数字+字母+下划线 |
| collection_description | "集合描述"                                       | 否    | String | 集合描述           |
| fields   | [{"name":"pk", "data_type":21, "is_primary": true, "auto_id":false, "max_length":100}, {"name":"random", "data_type":11}, {"name":"embeddings", "data_type":101, "dim":8}] | 否    | List | 集合的FieldSchema     |
```
data_type数据类型，参考DataType
class DataType(IntEnum):
    NONE = 0
    BOOL = 1
    INT8 = 2
    INT16 = 3
    INT32 = 4
    INT64 = 5

    FLOAT = 10
    DOUBLE = 11

    STRING = 20
    VARCHAR = 21
    ARRAY = 22
    JSON = 23

    BINARY_VECTOR = 100
    FLOAT_VECTOR = 101
    FLOAT16_VECTOR = 102
    BFLOAT16_VECTOR = 103
    SPARSE_FLOAT_VECTOR = 104

    UNKNOWN = 999
```


### <h3><p id="创建集合请求示例">创建集合请求示例</p></h3>

```python
import requests
import json

url = "http://{your_host}:8778/api/milvus/create_collection"
headers = {
    "Content-Type": "application/json"
}
data = {
    "collection_name": "testabc_1",
    "collection_description": "测试向量库test",
    "fields": [
        {"name":"pk", "data_type":21, "is_primary": true, "auto_id":false, "max_length":100},
        {"name":"random", "data_type":11},
        {"name":"embeddings", "data_type":101, "dim":8}
    ]
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)
```

### <h3><p id="创建集合响应示例">创建集合响应示例</p></h3>

```json
{
    "code": 200,
    "msg": "success create collection testabc_1"
}
```

## <h2><p id="删除集合post">删除集合（POST）</p></h2>

### <h3><p id="delete_collection"> 接口地址</p></h3>
* URL：<http://{your_host}:8778/api/milvus/delete_collection>

Content-Type: multipart/form-data

### <h3><p id="删除集合请求参数body">删除集合请求参数（Body）</p></h3>

| 参数名           | 参数值          | 是否必填 | 参数类型   | 描述说明     |
| --------------- | -------------- | ------- | -------- | -----------------|
| collection_name | "testabc_1"    | 是      |  String   | 创建集合名称，仅支持数字+字母+下划线 |


### <h3><p id="删除集合请求示例">删除集合请求示例</p></h3>

```python
import os
import requests

url = "http://{your_host}:8778/api/milvus/delete_collection"
data = {
    "collection_name": "testabc_1"
}


response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.text)
```


### <h3><p id="删除集合响应示例">删除集合响应示例</p></h3>

```json
{
    "code": 200,
    "msg": "success delete collection testabc_1"
}
```

## <h2><p id="获取集合信息post">获取集合信息（POST）</p></h2>

### <h3><p id="get_collection_info">请求地址</p></h3>
*URL：<http://{your_host}:8778/api/milvus/get_collection_info>

### <h3><p id="获取集合信息请求参数body">获取集合信息请求参数（Body）</p></h3>

| 参数名           | 参数值          | 是否必填 | 参数类型   | 描述说明     |
| --------------- | -------------- | ------- | -------- | -----------------|
| collection_name | "testabc_1"    | 是      |  String   | 创建集合名称，仅支持数字+字母+下划线 |

### <h3><p id="获取集合信息请求示例">获取集合信息请求示例</p></h3>

```python
import requests
import json

url = "http://{your_host}:8778/api/milvus/get_collection_info"
headers = {
    "Content-Type": "application/json"
}
{
    "collection_name": "testabc_1"
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)
```

### <h3><p id="获取集合信息响应示例">获取集合信息响应示例</p></h3>

```json
{
    "code": 200,
    "msg": "success get collection testabc_1",
    "num_entities": 100,
    "schema": {
        "auto_id": false,
        "description": "测试向量库test",
        "fields": [
            {
                "name": "pk",
                "description": "",
                "type": 21,
                "params": {
                    "max_length": 100
                },
                "is_primary": true,
                "auto_id": false
            },
            {
                "name": "random",
                "description": "",
                "type": 11
            },
            {
                "name": "embeddings",
                "description": "",
                "type": 101,
                "params": {
                    "dim": 8
                }
            }
        ],
        "enable_dynamic_field": false
    },
    "index_params": {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {
            "nlist": 1024
        }
    }
}
```

## <h2><p id="获取所有集合postget">获取所有集合（POST、GET）</p></h2>

### <h3><p id="list_collections">请求地址</p></h3>
* URL：<http://{your_host}:8778/api/milvus/list_collections>

### <h3><p id="获取所有集合请求示例">获取所有集合请求示例</p></h3>

```python
import requests
import json

url = "http://{your_host}:8778/api/milvus/list_collections"
headers = {
    "Content-Type": "application/json"
}

# response = requests.post(url, headers=headers)
response = requests.get(url)

print(response.status_code)
print(response.text)
```

### <h3><p id="获取所有集合响应示例">获取所有集合响应示例</p></h3>

```json
{
    "code": 200,
    "msg": "success list collections",
    "data": [
        "qanything_collection",
        "testabc_1"
    ]
}
```

## <h2><p id="在实体上生成索引post">在实体上生成索引（POST）</p></h2>

### <h3><p id="set_collection_index"> 请求地址 </p></h3>
* URL：<http://{your_host}:8778/api/milvus/set_collection_index>

### <h3><p id="在实体上生成索引请求参数body">在实体上生成索引请求参数（Body）</p></h3>

| 参数名     | 示例参数值                                           | 是否必填 | 参数类型   | 描述说明                     |
| ------- | ----------------------------------------------- | ---- | ------ | ------------------------ |
| collection_name | "testabc_1"    | 是      |  String   | 集合名称，仅支持数字+字母+下划线 |
| filed_name | "embedding"         | 是    | String | 索引属性名称    |
| index_type   | "IVF_FLAT" | 否    | String | 索引类型方法，默认"IVF_FLAT"，可选值["FLAT", "IVF_FLAT", "IVF_SQ8", "IVF_PQ", "IVF_HNSW"]  |
| metric_type   | "L2"                                           | 否    | String   | 相似性度量方法，默认为"L2",可选值为["L2", "IP", "Hamming", "Jaccard"] |
| params   | {"nlist":1024} | 否    | List    | 其他参数，默认为{"nlist":1024} |

### <h3><p id="在实体上生成索引请求示例">在实体上生成索引请求示例</p></h3>

```python
import requests
import json

url = "http://{your_host}:8778/api/milvus/set_collection_index"
headers = {
    "Content-Type": "application/json"
}
data = {
    "collection_name": "testabc_1",
    "filed_name": "embeddings",
    "index_type": "IVF_FLAT",
    "metric_type": "L2"
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)
```

### <h3><p id="在实体上生成索引响应示例">在实体上生成索引响应示例</p></h3>

```json
{
    "code": 200,
    "msg": "success set collection testabc_1 index {'index_type': 'IVF_FLAT', 'metric_type': 'L2', 'params': {'nlist': 1024}}"
}
```





## <h2><p id="在集合中插入向量post">在集合中插入向量（POST）</p></h2>

### <h3><p id="insert_vectors"> 请求地址 </p></h3>
* URL：<http://{your_host}:8778/api/milvus/insert_vectors>

### <h3><p id="在集合中插入向量请求参数body">在集合中插入向量请求参数（Body）</p></h3>

| 参数名     | 参数值    |   是否必填 | 参数类型      | 描述说明          |
| ---------- | --------------- | ---- | --------- | ------------------------------ |
| collection_name | "testabc_1"    | 是      |  String   | 集合名称，仅支持数字+字母+下划线 |
| vectors | [["num1", "num2", "num3"], [0.02, 5.21, 3.33], [[1,2,3,4,5,6,7,8],[2,2,3,4,5,6,7,8],[2,3,4,5,6,7,8,9]]]   | 是    | List | 上传插入的向量    |

### <h3><p id="在集合中插入向量请求示例">在集合中插入向量请求示例</p></h3>

```python
import requests
import json

url = "http://{your_host}:8778/api/milvus/insert_vectors"
headers = {
    "Content-Type": "application/json"
}
data = {
    "collection_name": "testabc_1",
    "vectors": [
        ["num1", "num2", "num3"],
        [0.02, 5.21, 3.33],
        [[1,2,3,4,5,6,7,8],[2,2,3,4,5,6,7,8],[2,3,4,5,6,7,8,9]]
    ]
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)
```

### <h3><p id="在集合中插入向量响应示例">在集合中插入向量响应示例</p></h3>

```json
{
    "code": 200,
    "msg": "success insert vectors (insert count: 3, delete count: 0, upsert count: 0, timestamp: 454390413595246601, success count: 3, err count: 0"
}
```

## <h2><p id="在集合中删除向量post">在集合中删除向量（POST）</p></h2>

### <h3><p id="delete_vectors"> 请求地址 </p></h3>
* URL：<http://{your_host}:8778/api/milvus/delete_vectors>

### <h3><p id="在集合中删除向量请求参数body">在集合中删除向量请求参数（Body）</p></h3>

| 参数名     | 示例参数值 | 是否必填 | 参数类型   | 描述说明  |
| ------- | ----- | ---- | ------ | ----- |
| collection_name | "testabc_1"    | 是      |  String   | 集合名称，仅支持数字+字母+下划线 |
| expr | "pk in [\"num1\",\"num2\"]"    | 是      |  String   | The boolean expression used to filter attribute. |
| compact | false    | 否      |  Bool   | 是否清除所有delete状态的数据，默认为false |

### <h3><p id="在集合中删除向量请求示例">在集合中删除向量请求示例</p></h3>

```python
import requests
import json

url = "http://{your_host}:8778/api/milvus/delete_vectors"
headers = {
    "Content-Type": "application/json"
}
data = {
    "collection_name": "testabc_1",
    "expr":  "pk in [\"num1\",\"num2\"]",
    "compact": false
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)
```

### <h3><p id="在集合中删除向量响应示例">在集合中删除向量响应示例</p></h3>

```json
{
    "code": 200,
    "msg": "success delete vectors (insert count: 0, delete count: 2, upsert count: 0, timestamp: 0, success count: 0, err count: 0"
}
```

## <h2><p id="在集合中搜索向量post">在集合中搜索向量（POST）</p></h2>

### <h3><p id="search_vectors"> 请求地址 </p></h3>
* URL: <http://{your_host}:8778/api/milvus/search_vectors>

### <h3><p id="在集合中搜索向量请求参数body">在集合中搜索向量请求参数（Body）</p></h3>

| 参数名     | 示例参数值 | 是否必填 | 参数类型   | 描述说明  |
| ------- | ----- | ---- | ------ | ----- |
| collection_name | "testabc_1"    | 是      |  String   | 集合名称，仅支持数字+字母+下划线 |
| vectors | [[2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]]    | 是      |  List   | 需要检索的query的向量，可以是多个 |
| anns_field | "embedding"    | 是      |  String   | The name of the vector field used to search of collection. |
| param | {"metric_type": "L2","params": {"nprobe": 12}}   | 否 |  Dict   | The parameters of search. The followings are valid keys of param.   * *metric_type* (``str``)    * *offset* (``int``, optional)  * *params of index: *nprobe*, *ef*, *search_k*, etc |
| limit | 10  | 否      |  Int   | The max number of returned record, also known as `topk`. |
| expr | "pk in [\"num1\",\"num2\"]"    | 否      |  String   | The boolean expression used to filter attribute. |
| partition_names |     | 否      |  String   | The names of partitions to search on. |
| timeout |     | 否      |  float   | A duration of time in seconds to allow for the RPC. |
| round_decimal |     | 否      |  Int   | The specified number of decimal places of returned distance. Defaults to -1 means no round to returned distance. |
| output_fields |     | 否      |  List   | The name of fields to return in the search result.  Can only get scalar fields. |

### <h3><p id="在集合中搜索向量请求示例">在集合中搜索向量请求示例</p></h3>

```python
import requests
import json

url = "http://{your_host}:8778/api/milvus/search_vectors"
headers = {
    "Content-Type": "application/json"
}
data = {
    "collection_name": "testabc_1",
    "vectors": [[2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]],
    "expr":  "pk in [\"num1\",\"num2\",\"num3\"]",
    "output_fields": ["pk", "random", "embeddings"]
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)
```

### <h3><p id="在集合中搜索向量响应示例">在集合中搜索向量响应示例</p></h3>

```json
{
    "code": 200,
    "msg": "success search vectors",
    "search_result": [
        [
            "id: num3, distance: 0.0, entity: {'random': 3.33, 'embeddings': [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0], 'pk': 'num3'}"
        ]
    ]
}
```

## <h2><p id="在集合中查询向量post">在集合中查询向量（POST）</p></h2>

### <h3><p id="expr_search"></p></h3>
* URL：<http://{your_host}:8778/api/milvus/expr_search>

### <h3><p id="在集合中查询向量请求参数body">在集合中查询向量请求参数（Body）</p></h3>

| 参数名     | 示例参数值 | 是否必填 | 参数类型   | 描述说明  |
| ------- | ----- | ---- | ------ | ----- |
| collection_name | "testabc_1"    | 是      |  String   | 集合名称，仅支持数字+字母+下划线 |
| expr | "pk in [\"num1\",\"num2\"]"    | 否      |  String   | The boolean expression used to filter attribute. |
| output_fields |  ["pk", "random", "embeddings"]   | 否      |  List   | The name of fields to return in the search result.  Can only get scalar fields. |

### <h3><p id="在集合中查询向量请求示例">在集合中查询向量请求示例</p></h3>

```python
import requests
import json

url = "http://{your_host}:8778/api/milvus/expr_search"
headers = {
    "Content-Type": "application/json"
}
data = {
    "collection_name": "testabc_1",
    "expr":  "pk in [\"num1\",\"num2\",\"3005\"]",
    "output_fields": ["pk", "random", "embeddings"]
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)
```

### <h3><p id="在集合中查询向量响应示例">在集合中查询向量响应示例</p></h3>

```json
{
    "code": 200,
    "msg": "success expr search",
    "data": [
        {
            "random": 0.02,
            "embeddings": "[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]",
            "pk": "num1"
        },
        {
            "random": 5.21,
            "embeddings": "[2.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]",
            "pk": "num2"
        }
    ]
}
```

## <h2><p id="清除删除的向量post">清除删除的向量（POST）</p></h2>

### <h3><p id="clear_deleted_vectors"> 请求地址 </p></h3>
* URL：<http://{your_host}:8778/api/milvus/clear_deleted_vectors>

### <h3><p id="清除删除的向量请求参数body">清除删除的向量请求参数（Body）</p></h3>

| 参数名     | 示例参数值 | 是否必填 | 参数类型   | 描述说明  |
| ------- | ----- | ---- | ------ | ----- |
| collection_name | "testabc_1"    | 是      |  String   | 集合名称，仅支持数字+字母+下划线 |

### <h3><p id="清除删除的向量请求示例">清除删除的向量请求示例</p></h3>

```python
import requests
import json

url = "http://{your_host}:8778/api/milvus/clear_deleted_vectors"
headers = {
    "Content-Type": "application/json"
}
data = {
    "collection_name": "testabc_1"
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)
```

### <h3><p id="清除删除的向量响应示例">清除删除的向量响应示例</p></h3>

```json
{
    "code": 200,
    "msg": "success clear deleted vectors"
}
```

