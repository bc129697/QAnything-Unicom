# API接口说明文档

以下是所有API接口的快速索引表，点击接口名称可跳转到详细说明：

## 基础功能接口

| 序号 | 接口名称                     | 路径                                        | 方法  | 功能描述                         |
|------|------------------------------|---------------------------------------------|-------|----------------------------------|
| 1    | [获取API文档](#获取API文档) | `/api/docs`                                 | GET   | 获取API文档信息                  |
| 2    | [新建知识库](#新建知识库)   | `/api/rag/new_knowledge_base`         | POST  | 创建新的知识库                   |
| 3    | [删除知识库](#删除知识库)   | `/api/rag/delete_knowledge_base`      | POST  | 删除指定知识库                   |
| 4    | [重命名知识库](#重命名知识库) | `/api/rag/rename_knowledge_base`      | POST  | 重命名知识库                     |
| 5    | [获取知识库列表](#获取知识库列表) | `/api/rag/list_knowledge_base`        | POST  | 获取用户知识库列表               |
| 6    | [获取文件列表](#获取文件列表) | `/api/rag/list_files`                 | POST  | 获取知识库中文件列表             |
| 7    | [获取文件解析状态](#获取文件解析状态) | `/api/rag/get_files_statu`            | POST  | 获取指定文件的解析状态           |
| 8    | [获取解析状态统计](#获取解析状态统计) | `/api/rag/get_total_status`           | POST  | 获取用户所有文件解析状态数量     |
| 9    | [获取文件切片内容](#获取文件切片内容) | `/api/rag/get_doc_completed`          | POST  | 获取文件的详细切片内容           |
| 10   | [上传解析文件](#上传解析文件) | `/api/rag/upload_files`               | POST  | 上传文件进行解析和向量化         |
| 11   | [上传切片数据](#上传切片数据) | `/api/rag/chunk_embedding`            | POST  | 上传切片数据并生成向量           |
| 12   | [上传FAQ](#上传FAQ)         | `/api/rag/upload_faqs`                | POST  | 上传常见问题数据                 |
| 13   | [上传weblink](#上传weblink) | `/api/rag/upload_weblink`                | POST  | 上传网页链接                 |
| 14   | [更新切片内容](#更新切片内容) | `/api/rag/update_chunks`              | POST  | 更新切片文本并重新生成向量       |
| 15   | [修改问答对](#修改问答对)    | `/api/rag/update_qa`                            | POST  | 修改qa内容               |
| 16   | [删除文件](#删除文件)       | `/api/rag/delete_files`               | POST  | 删除知识库中的文件               |
| 17   | [通用问答接口](#通用问答接口) | `/api/rag/question_rag_search`        | POST  | 不区分文档类型的问答             |
| 18   | [区分文档问答](#区分文档问答) | `/api/rag/question_qa_search`         | POST  | 区分文档和FAQ的问答              |
| 19   | [文档内容解析](#文档内容解析) | `/api/rag/document_parser`            | POST  | 提取文档文本内容                 |
| 20   | [获取原文件](#获取原文件)   | `/api/rag/get_file_base64`            | POST  | 获取Base64编码的原文件           |
| 21   | [查询改写](#查询改写)       | `/api/rag/query_rewrite`              | POST  | 根据对话历史改写查询             |
| 22   | [本地文档问答](#本地文档问答) | `/api/rag/local_doc_chat`             | POST  | 基于配置模型的文档问答           |
| 23   | [删除切片](#删除切片)       | `/api/rag/delete_chunks`               | POST  |  删除切片                     |
| 24   | [文件移动](#文件移动)       | `/api/rag/move_file`                  | POST  |  移动文件到其他知识库            |

## 新开发通用接口

| 序号 | 接口名称                     | 路径                                        | 方法  | 功能描述                         |
|------|------------------------------|---------------------------------------------|-------|----------------------------------|
| 1   | [修改切片元数据](#修改切片元数据) | `/api/modify_chunk_kwargs`                  | POST  | 修改切片的元数据信息             |
| 2   | [删除切片元数据](#删除切片元数据) | `/api/delete_chunk_metadata`                | POST  | 删除切片的指定元数据字段         |
| 3   | [更新知识库元数据](#更新知识库元数据) | `/api/update_kb_metadata`                | POST  | 修改知识库元数据                 |
| 4   | [更新文件元数据](#更新文件元数据) | `/api/update_file_metadata`                 | POST  | 修改文件的元数据                 |
| 5   | [获取联网检索工具](#获取联网检索工具) | `/api/get_websearch_tools`               | GET   | 获取可用的联网检索工具           |
| 6   | [切片摘要生成](#切片摘要生成) | `/api/chunk_summary`                        | POST  | 生成切片内容的摘要               |
| 7   | [文件大纲提取](#文件大纲提取) | `/api/file_extract_outline`                 | POST  | 提取文件内容大纲                 |
| 8   | [文件摘要提取](#文件摘要提取) | `/api/file_extract_summary`                 | POST  | 提取文件内容摘要                 |



## 机器人问答
| 序号 | 接口名称         | 路径                     | 方法  | 功能描述         |
|------|------------------|--------------------------|-------|------------------|
| 1   | [新建Bot](#新建Bot) | `/api/rag/new_bot`      | POST  | 创建新的机器人   |
| 2   | [删除Bot](#删除Bot) | `/api/rag/delete_bot`   | POST  | 删除指定机器人   |
| 3   | [更新Bot](#更新Bot) | `/api/rag/update_bot`   | POST  | 更新机器人信息   |
| 4   | [获取Bot信息](#获取Bot信息) | `/api/rag/get_bot_info` | POST  | 获取机器人详细信息 |

---

## 基础功能接口详细说明

### <a id="获取API文档"></a> 获取API文档
**接口路径**: `/api/docs`  
**请求方法**: GET  
**功能描述**: 获取API文档信息  
**请求示例**:
```bash
curl -X GET "http://localhost:8777/api/docs"
```

**返回示例**:
```json
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
...
```

---

### <a id="新建知识库"></a> 新建知识库
**接口路径**: `/api/rag/new_knowledge_base`  
**请求方法**: POST  
**功能描述**: 创建新的知识库  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| kb_name   | string | 是 | 知识库名称 |
| kb_id     | string | 否 | 知识库id，不输入则自动生成，格式为"KB"+uuid.uuid4().hex，输入kb_id必须以"KB"开头，且输入的kb_id与系统中已存在的不相同 |
| embedding_base_url   | string | 否 | embedding_base_url |
| embedding_model_name | string | 否 | embedding_model_name |
| embedding_api_key    | string | 否 | embedding_api_key |
| separators   | List[string] | 否 | 块分隔符，默认值["\n\n", "\n", "。", "，", ",", ".", ""] |
| chunk_size   | int          | 否 | 父块大小，最大token数 |


**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int    | 200表示成功，其他表示失败 |
| msg  | string | 返回结果说明     |
| data | dict   | 知识库相关信息   |

**请求示例**:
```bash
curl -X POST -H "Content-Type: application/json" http://{ip}:{port}/api/rag/new_knowledge_base \
-d '{"user_id": "zzp", "kb_id": "KB6dae785cdd5d47a997e890521acbe1c5", "kb_name": "rag1"}'
```

**返回示例**:
```json
{
    "code":200,
    "msg":"success create knowledge base KB6dae785cdd5d47a997e890521acbe1c5",
    "data":{
        "kb_id":"KB6dae785cdd5d47a997e890521acbe1c5",
        "kb_name":"rag1",
        "timestamp":"202406121408"
    }
}
```

---

### <a id="删除知识库"></a> 删除知识库
**接口路径**: `/api/rag/delete_knowledge_base`  
**请求方法**: POST  
**功能描述**: 删除指定知识库  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| kb_id     | string | 是 | 需要删除的知识库id |
| kb_ids    | []string | 是 | kb_id和kb_ids二选一 |
| file_ids  | []string | 否 | 与kb_id绑定，需要删除的知识库中文件id，不输入则删除该知识库 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| ----- | --- | --- |
| code | int    | 200表示成功，其他表示失败 |
| msg  | string | 返回结果说明 |


**请求示例**:
```bash
curl -X POST -H "Content-Type: application/json" http://{ip}:{port}/api/rag/delete_knowledge_base -d '{"user_id": "123456", "kb_id": "KB123456789"}'
```

**返回示例**:
```json
{
    "code":200,
    "msg":"Knowledge Base KB6dae785cdd5d47a997e890521acbe1c5 delete success"
}
```

---

### <a id="重命名知识库"></a> 重命名知识库
**接口路径**: `/api/rag/rename_knowledge_base`  
**请求方法**: POST  
**功能描述**: 重命名知识库  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| kb_id     | string | 是 | 需要重命名的知识库id |
| new_kb_name  | string | 是 | 新的知识库名称 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int    | 200表示成功，其他表示失败 |
| msg  | string | 返回结果说明 |

**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/rag/new_knowledge_base' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "user",
    "kb_id": "KB123456666",
    "new_kb_name": "内蒙FAQ"
}'
```

**返回示例**:
```json
{
    "code": 200, 
    "msg": "Knowledge Base KB123456666 rename success"
}
```

---

### <a id="获取知识库列表"></a> 获取知识库列表
**接口路径**: `/api/rag/list_knowledge_base`  
**请求方法**: POST  
**功能描述**: 获取用户的所有知识库列表  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| kb_id     | string | 否 | 查询条件，指定kb_id，只查询该知识库id对应的相关信息 |
| kb_name   | string | 否 | 查询条件，指定知识库名称包含的部分名字内容 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| ----- | --- | --- |
| code | int    | 200表示成功，其他表示失败 |
| data | List | 知识库列表 |

**请求示例**:
```bash
curl -X POST -H "Content-Type: application/json" http://{ip}:{port}/api/rag/list_knowledge_base \
    -d '{"user_id": "123456"}'
```

**返回示例**:
```json
{
    "code": 200,
    "data": [
        {
            "kb_id": "KB8cf34692b44f4eafb78b7c5203c3d5bc",
            "kb_name": "写作知识",
            "file_count": 10,
            "creation_time": "202506201019",
            "parser_config": {},
            "kb_metadata": {}
        },
        {
            "kb_id": "KB8cf34692b44f4eafb78b7c5203c3d5bc_outline",
            "kb_name": "写作知识_大纲",
            "file_count": 10,
            "creation_time": "202506201310",
            "parser_config": {},
            "kb_metadata": {}
        },
        {
            "kb_id": "KB8cf34692b44f4eafb78b7c5203c3d5bc_summary",
            "kb_name": "写作知识_摘要",
            "file_count": 10,
            "creation_time": "202506201310",
            "parser_config": {},
            "kb_metadata": {}
        }
    ]
}
```

---

### <a id="获取文件列表"></a> 获取文件列表
**接口路径**: `/api/rag/list_files`  
**请求方法**: POST  
**功能描述**: 获取知识库中的文件列表  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| kb_id     | string | 是 | 需要获取知识库文件列表的知识库id |
| file_id   | string | 否 | 需要获取的知识库中文件id，不输入则获取该知识库所有文件 |
| page_id   | int    | 否 | 分页查询，默认值为1，从1开始 |
| page_limit| int    | 否 | 分页查询，默认值为10 |
| status    | string | 否 | 查询条件，筛选指定知识库状态，green、red、yellow、gray四种状态 |
| file_name | string | 否 | 查询条件，指定筛选文件名称包含的内容 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| ----- | --- | --- |
| code | int    | 200表示成功，其他表示失败 |
| msg  | string | 返回结果说明 |
| data | dict   | 知识库文件列表详情 |

**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/rag/list_files' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "user",
    "kb_id": "KB9ca1fb4e288f4adcaa6aff7b1818c1d1"
    
}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "total_page": 1,
        "total": 2,
        "status_count": {
            "green": 2,
            "red": 0,
            "yellow": 0,
            "gray": 0
        },
        "details": [
            {
                "file_id": "6866d1a2a0b9492092116c7980b9159a",
                "file_name": "城乡居民参保.jpg",
                "status": "green",
                "bytes": 565395,
                "content_length": 250,
                "timestamp": "202506040925",
                "file_location": "/workspace/QAnything/QANY_DB/content/user__1234/KB9ca1fb4e288f4adcaa6aff7b1818c1d1/6866d1a2a0b9492092116c7980b9159a/城乡居民参保.jpg",
                "file_url": "",
                "chunks_number": 1,
                "msg": "{\"parse_time\": 4.12, \"split_time\": 0.0, \"milvus_embedding_time\": 0.17, \"milvus_insert_time\": 0.01, \"es_insert_time\": 0.17, \"upload_total_time\": 4.48}",
                "file_metadata": null
            },
            {
                "file_id": "82be47b21b524382a7d0285c07f88d06",
                "file_name": "5-6级伤残待遇.png",
                "status": "green",
                "bytes": 96166,
                "content_length": 489,
                "timestamp": "202506040928",
                "file_location": "/workspace/QAnything/QANY_DB/content/user__1234/KB9ca1fb4e288f4adcaa6aff7b1818c1d1/82be47b21b524382a7d0285c07f88d06/5-6级伤残待遇.png",
                "file_url": "",
                "chunks_number": 3,
                "msg": "{\"parse_time\": 3.61, \"split_time\": 0.01, \"milvus_embedding_time\": 0.02, \"milvus_insert_time\": 0.0, \"es_insert_time\": 0.02, \"upload_total_time\": 3.68}",
                "file_metadata": null
            }
        ],
        "page_id": 1,
        "page_limit": 10,
        "data_red": []
    }
}
```

---

### <a id="获取文件解析状态"></a> 获取文件解析状态
**接口路径**: `/api/rag/get_files_statu`  
**请求方法**: POST  
**功能描述**: 获取指定文件的解析状态  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string   | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| file_ids  | []string | 否 | 检索的文件id列表 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code   | int  | 200表示成功，其他表示失败 |
| msg   | string | 返回结果说明 |
| data  | dict | 知识库文件列表详情 |

**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/rag/get_files_statu' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "user",
    "kb_id": "KB8cf34692b44f4eafb78b7c5203c3d5bc",
    "file_ids": [
        "efcac3d8150e4fa89ca9a485ada89d9b",
        "2642a6b3518f496c92e00fae97b63557"
    ]
}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "total": {
            "red": 1,
            "green": 1
        },
        "details": [
            {
                "file_id": "2642a6b3518f496c92e00fae97b63557",
                "file_name": "成都市党建引领信托物业服务指导手册.txt",
                "status": "green",
                "bytes": 53857,
                "content_length": 18116,
                "timestamp": "202506201310",
                "file_location": "/workspace/QAnything/QANY_DB/content/user__1234/KB8cf34692b44f4eafb78b7c5203c3d5bc/2642a6b3518f496c92e00fae97b63557/成都市党建引领信托物业服务指导手册.txt",
                "file_url": "",
                "chunks_number": 47,
                "msg": "{\"parse_time\": 0.0, \"parse_outline\": 29.66, \"parse_summary\": 9.34, \"split_time\": 0.1, \"milvus_embedding_time\": 0.4, \"milvus_insert_time\": 0.01, \"es_insert_time\": 0.12, \"upload_total_time\": 39.74}",
                "file_metadata": null
            },
            {
                "file_id": "efcac3d8150e4fa89ca9a485ada89d9b",
                "file_name": "",
                "status": "red",
                "bytes": 0,
                "timestamp": "0",
                "msg": "fail, file_id efcac3d8150e4fa89ca9a485ada89d9b not found"
            }
        ]
    }
}
```

---

### <a id="获取解析状态统计"></a> 获取解析状态统计
**接口路径**: `/api/rag/get_total_status`  
**请求方法**: POST  
**功能描述**: 获取用户所有文件的解析状态统计  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string   | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| ----- | --- | --- |
| code | int    | 200表示成功，其他表示失败 |
| status | dict   | 知识库文件列表详情 |


**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/rag/get_total_status' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "user"
}'
```

**返回示例**:
```json
{
    "code": 200,
    "status": {
        "user__1234": {
            "KB8cf34692b44f4eafb78b7c5203c3d5bc_summary": {
                "green": 3,
                "yellow": 0,
                "red": 0,
                "gray": 0
            }
        }
    }
}
```

---

### <a id="获取文件切片内容"></a> 获取文件切片内容
**接口路径**: `/api/rag/get_doc_completed`  
**请求方法**: POST  
**功能描述**: 获取文件的详细切片内容  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string   | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| file_id   | string   | 是 | 文件id |
| page_id   | int    | 否 | 分页查询页码，默认值为1，从1开始 |
| page_limit| int    | 否 | 分页查询每页数量，默认值为10 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code        | int    | 200表示成功，其他表示失败 |
| msg         | string | 结果说明 |
| chunks      | list[Obj]   | 结果说明 |
| page_id     | int    | 分页查询 |
| page_limit  | int    | 结果说明 |
| total_count | int    | 当前文档的总共切片数量 |



**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/rag/get_doc_completed' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "user",
    "file_id": "afe868a91f4848b2896517003e2504bd"
}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success",
    "chunks": [
        {
            "page_content": "[headers]({'知识库名': 'pic', '文件名': '1-4级伤残待遇.png'})\n级\n27个月的本人工资\n《工伤保险条例》（国务院\n令第586号）第三十五条\n政策\n二级\n25个月的本人工资\n一次性伤\n依据\n残补助金\n三级\n23个月的本人工资\n四级\n21个月的本人工资\n保留劳动关系，\n退出工作岗位\n劳动\n级\n本人工资的90%\n关系\n二级\n本人工资的85%\n伤残\n津贴\n三级\n本人工资的80%\n鉴定次月开\n始享受待遇\n级至四级伤残\n四级\n本人工资的75%\n每月20日\n伤残津贴\n职工工伤待遇\n前到账\n拨付规定\n职工因工致残被鉴定为一级\n至四级伤残的，由用人单位\n和职工个人以伤残津贴为基\n报销缴\n数，缴纳基本医疗保险费。\n每年按省市文\n件规定统调\n伤残津\n纳规定\n贴调整\n工伤职工达到退休年龄并办理退休手续\n每年六月通过静默认证平台、\n后，停发伤残津贴，按照国家有关规定\n享受基本养老保险待遇。基本养老保险\n微信认证\n资格\n待遇低于伤残津贴的，由工伤保险基金\n认证\n退休衔\n补足差额。\n接规定",
            "metadata": {
                "user_id": "user__1234",
                "kb_id": "KBc79eac5884ee41ea98e7fc168b31dcab",
                "file_id": "afe868a91f4848b2896517003e2504bd",
                "file_name": "1-4级伤残待遇.png",
                "nos_key": "/workspace/QAnything/QANY_DB/content/user__1234/KBc79eac5884ee41ea98e7fc168b31dcab/afe868a91f4848b2896517003e2504bd/1-4级伤残待遇.png",
                "file_url": "",
                "title_lst": [],
                "has_table": false,
                "images": [],
                "page_id": 0,
                "bboxes": [],
                "single_parent": false,
                "headers": {
                    "知识库名": "pic",
                    "文件名": "1-4级伤残待遇.png"
                },
                "faq_dict": {}
            },
            "chunk_id": "afe868a91f4848b2896517003e2504bd_0"
        }
    ],
    "page_id": 1,
    "page_limit": 10,
    "total_count": 1
}
```

---

### <a id="上传解析文件"></a> 上传解析文件
**接口路径**: `/api/rag/upload_files`  
**请求方法**: POST  
**功能描述**: 上传文件进行解析和向量化  
* 上传对应的知识库当前单个知识库最大支持文件数为10000，单次上传的文件总大小不超过128M
* 单个文件最大字符数1000000，超过此字符数将上传失败
* 上传文件目前仅支持：[md,txt,pdf,jpg,png,jpeg,docx,xlsx,pptx,eml,csv]
* 切片后的chunk会加上header。示例： [headers]({'知识库名': '新津文档', '文件名': '成都市新津区关于推动数字赋能政策申报攻略.docx'})
* 支持设置提取文章摘要，文章大纲，默认不提取

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| kb_id     | string | 是 | 知识库id |
| chunk_size| int    | 否 | 分块大小，默认值为对应知识库的分块大小，单位为token，单个文件可以继续自定义分块大小 |
| mode      | string | 否 | "soft"代表不上传同名文件，"strong"表示强制上传同名文件，默认"soft" |
| files     | []files| 是 | 待解析文档，支持上传多个，[('files', open('/home/darren/文档/repiBench.pdf','rb')),] |
| file_ids  | string | 否 | 文件id列表，与files中文件顺序相同,多个文件id中间用逗号隔开，如果未提供，则随机生成file_id |
| parser_outline | bool | 否 | 默认为Fasle，是否提取文章大纲保存到kbid_outline库，对应文件fileid_outline |
| parser_summary | bool | 否 | 默认为Fasle，是否提取文章摘要保存到kbid_outline库，对应文件fileid_outline |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int | 200表示成功，其他表示失败 |
| msg | string | 返回结果说明 |
| data | List | 每个文件的保存详细情况，其中，status表示文件的处理状态，gray表示后台处理中，还未处理完成（可能出现处理失败的情况，需要后台自行查询） |


**请求示例**:
```bash
curl -X POST "http://{ip}:{port}/api/rag/upload_files"  -d '{"user_id": "zzp", "kb_id":"kb_id", "file_ids":"file_id1,file_id2", "mode":"soft"}' -F "files=@/home/darren/文档/repiBench.pdf" -F "files=@/home/darren/文档/repiBench2.pdf"
```

**返回示例**:
```json
{
    "code":200,
    "msg":"success，后台正在飞速上传文件，请耐心等待",
    "data":[
        {
            "file_id":"124",
            "file_name":"repiBench.pdf",
            "status":"gray",
            "bytes":2614844,
            "timestamp":"202406121655",
            "estimated_chars": 655
        }
    ]
}
```

---

### <a id="上传切片数据"></a> 上传切片数据
**接口路径**: `/api/rag/chunk_embedding`  
**请求方法**: POST  
**功能描述**: 上传切片数据并生成向量  
  * 默认不再对切片进行切分，适用于手动切片后上传，复杂文件


**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id | string | 是 | 用户id |
| kb_id   | string | 是 | 知识库id |
| file_id | string | 否 | 文件id，默认uuid.uuid4().hex |
| file_name | string | 否 | 文件名称，默认为file_id+".txt" |
| chunk_datas | []string | 是 | 切片后的文本数据 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int | 200表示成功，其他表示失败 |
| msg | string | 返回结果说明 |
| data | dict | 文本的保存详细情况，其中，status表示文件的处理状态，gray表示后台处理中，还未处理完成（可能出现处理失败的情况，需要后台自行查询） |


**请求示例**:
```bash
curl -X POST "http://<your_host>:<your_port>/api/rag/upload_files"  -d '{"user_id": "zzp", "kb_id":"kb_id", "file_id":"file_id", "file_name":"xxx.txt", "chunk_datas": ["切片文本1","切片文本2"] }'
```

**返回示例**:
```json
{
    "code":200,
    "msg":"success，后台正在飞速上传文件，请耐心等待",
    "data":[
        {
            "file_id":"file_id",
            "file_name":"xxx.txt",
            "status":"gray",
            "status": "gray",
            "bytes": 50,
            "timestamp": "202507151723"
        }
    ]
}
```

---

### <a id="上传FAQ"></a> 上传FAQ
**接口路径**: `/api/rag/upload_faqs`  
**请求方法**: POST  
**功能描述**: 上传常见问题数据  
  * 单次上传FAQ对数量最大支持1000条
  * 单条FAQ，其中question长度需要小于512，answer长度最大支持2048
  * 请求参数和示例

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| kb_id     | string | 是 | 知识库id，如果kb_id不存在则会创建一个 |
| faqs      | list   | 是 | 格式：[{"question": "xxxx", "answer": "xxx"}, ...,{"question": "xxx", "answer": "xxx"}],单次最大支持1000条上传，如果遇到已存在相同问题，则不进行更新，直接跳过 |
| file_ids  | list   | 否 | 格式：["file_id1", ...,"file_idn"],长度需要与faqs长度一致，且每个file_id是唯一的 |
| chunk_size| int    | 否 | 分块大小，默认值800，单位为字 |
| files     | file   | 否 | 按qa模版上传文件，可以多个文件，单次总共qa对不超过1000个 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int    | 200表示成功，其他表示失败 |
| msg  | string | 返回结果说明 |
| data | List   | 每个上传QA对的状态 |



**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/rag/upload_faqs' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "user",
    "kb_id": "KB9ca1fb4e288f4adcaa6aff7b1818c1d1",
    "faqs": [{"question": "如何使用python", "answer": "xxx"}]
}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success，后台正在飞速上传文件，请耐心等待",
    "data": [
        {
            "file_id": "d312d66cb7b842ff9b8925b0f7b24c6f",
            "file_name": "FAQ_如何使用python.faq",
            "status": "gray",
            "length": 13,
            "timestamp": "202507151730"
        }
    ],
    "data_skip": []
}
```

---


### <a id="上传weblink"></a> 上传weblink
**接口路径**: `/api/rag/upload_weblink`  
**请求方法**: POST  
**功能描述**: 上传网页链接，解析网页链接获取文本内容  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| kb_id     | string | 是 | 知识库id，如果kb_id不存在则会创建一个 |
| url       | string | 是 | 网页链接 |
| title     | string | 否 | 网页名称 |
| urls      | []string | 否 | 多个网页链接，url和urls二选一 |
| title     | []string | 否 | 多个网页链接对应的名称，长度需要与urls一致 |
| chunk_size| int    | 否 | 分块大小，默认值800，单位为字 |
| mode      | string | 否 | "soft"代表不上传同名文件，"strong"表示强制上传同名文件，默认"soft" |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int    | 200表示成功，其他表示失败 |
| msg  | string | 返回结果说明 |
| data | List   | 每个上传url的状态 |



**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/rag/upload_weblink' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "user",
    "kb_id": "KB9ca1fb4e288f4adcaa6aff7b1818c1d1",
    "url": "https://news.sina.com.cn/gov/xlxw/2025-09-02/doc-infpanvn0329752.shtml"
}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success，后台正在飞速上传文件，请耐心等待",
    "data": [
        {
            "file_id": "d4453e85f40b4fcd9450c1513449e23b",
            "file_name": "doc-infpanvn0329752.shtml.web",
            "file_url": "https://news.sina.com.cn/gov/xlxw/2025-09-02/doc-infpanvn0329752.shtml",
            "status": "gray",
            "bytes": 0,
            "timestamp": "202509021440"
        }
    ]
}

```

---

### <a id="更新切片内容"></a> 更新切片内容
**接口路径**: `/api/rag/update_chunks`  
**请求方法**: POST  
**功能描述**: 更新切片文本并重新生成向量  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id       | string   | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info     | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| doc_id        | string   | 是 | 文档切片的id，该部分由“get_doc_completed”接口获取文档后返回内容中获得 |
| update_content| string   | 是 | 修改后的切片内容 |


**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code        | int    | 200表示成功，其他表示失败 |
| msg         | string | 结果说明 |

**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/rag/update_chunks' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "user",
    "doc_id": "2642a6b3518f496c92e00fae97b63557_0",
    "update_content": "修改后内容"
}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success update doc_id 2642a6b3518f496c92e00fae97b63557_0"
}
```

---



### <a id="修改问答对"></a> 修改问答对
**接口路径**: `/api/rag/update_qa`  
**请求方法**: POST  
**功能描述**: 修改问答对内容，包括问题和答案 

**请求参数**:
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string   | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| file_id   | string   | 是 | 修改的qa的file_id |
| question  | string   | 是 | 修改后的question |
| answer    | string   | 是 | 修改后的答案 |


**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int | 200表示成功，其他表示失败 |
| msg | string | 返回结果说明 |



**请求示例**:
```bash
curl --location 'http://ip:port/api/rag/update_qa' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "user",
    "file_id": "949954d639404f33b470430d9cbf3f0a",
    "question": "如何使用JAVA",
    "answer": "java使用教程：xxx"
}'
```

**返回示例**:
```json
{
    "code": 200, 
    "msg": "success update faq 949954d639404f33b470430d9cbf3f0a"
}
```


### <a id="删除文件"></a> 删除文件
**接口路径**: `/api/rag/delete_files`  
**请求方法**: POST  
**功能描述**: 删除知识库中的文件  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string   | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| kb_id     | string   | 是 | 知识库id |
| file_ids  | []string | 是 | 文件id列表 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int | 200表示成功，其他表示失败 |
| msg | string | 返回结果说明 |

**请求示例**:
```bash
curl -X POST "http://<your_host>:<your_port>/api/rag/delete_files"  -d '{"user_id": "zzp", "kb_id":"kb_id", "file_ids":["file_id1,file_id2"]}'
```

**返回示例**:
```json
{
    "code":200,
    "msg":"documents ['124'] delete success"
}
```

---

### <a id="通用问答接口"></a> 通用问答接口
**接口路径**: `/api/rag/question_rag_search`  
**请求方法**: POST  
**功能描述**: 不区分文档类型的问答  
  * 不联网检索时，file_ids和kb_ids必须有一个不为空

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string   | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| kb_ids    | []string | 否 | 检索的知识库id列表 |
| file_ids  | []string | 否 | 检索的文件id列表 |
| question  | string   | 是 | 待检索问题 |
| rerank    | bool     | 否 | 是否对检索结果进行重排序，默认值True |
| - rerank_url        | string   | 否 | 自定义重排序接口地址 |
| - rerank_model_name | string   | 否 | 自定义重排序接口名称 |
| - rerank_api_key    | string   | 否 | 自定义重排序接口密钥 |
| networking       | bool     | 否 | 是否使用网络检索，默认值False |
| web_search_tools | []string | 否 | 网络检索工具列表，默认值["BaiduSearch"] |
| hybrid_search    | bool     | 否 | 是否使用混合检索，默认值False |
| web_chunk_size   | int      | 否 | 网络检索时，每个chunk的大小，默认值800 |
| top_k            | int      | 否 | 返回最多检索数量，默认值30 |
| score_threshold  | float    | 否 | 检索结果得分阈值，默认值0.5 |
| merge | bool     | 否 | 是否合并检索源于同一个文件的结果，默认值True |
| history | string或者list | 否 | 问答历史，格式为json字符串或者list，如果传了则用作query改写 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int | 200表示成功，其他表示失败 |
| msg | string | 返回结果说明 |
| question | string | 检索问题 |
| retrieval_documents | List | 知识库检索结果 |
| retrieval_web_documents | List | 网页检索结果 |

**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/rag/question_rag_search' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "user",
    "kb_ids": ["KB9ca1fb4e288f4adcaa6aff7b1818c1d1"],
    "top_k": 4,
    "question": "劳动者到新单位后多久签订劳动合同？",
    "networking": false
    
}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success chat\nKBdatabase search sucess.\n",
    "question": "劳动者到新单位后多久签订劳动合同？",
    "retrieval_documents": [
        {
            "page_content": "该参考内容由多个片段组成，片段内容如下：\n\n***片段[18]：*** 劳动者到新单位后多久签订劳动合同？\n问题id:0d117c05-77e0-4199-8970-e25952743f19\n\n***片段[133]：*** 事业单位公开招聘时，新聘用人员的合同签订一般为多长时间？\n问题id:543575dc-5737-421e-9884-d7029f3b41a8\n\n***片段[137]：*** 劳务派遣单位与被派遣劳动者订立的劳动合同的期限应当如何约定？\n问题id:566bc91c-7a77-4428-8ae7-7d7e3974c301\n\n***片段[291]：*** 用人单位自用工之日起超过一个月不与劳动者签订劳动合同的，如何处理？\n问题id:ade11da2-9024-4519-b6b4-62fc9a70ff46",
            "metadata": {
                "kb_id": "KB9ca1fb4e288f4adcaa6aff7b1818c1d1",
                "file_id": "903c96ab508c4809a9d51aa52b21d0aa",
                "file_name": "相关问题_1.txt",
                "retrieval_query": "劳动者到新单位后多久签订劳动合同？",
                "file_url": "",
                "score": 0.83,
                "retrieval_source": "milvus",
                "headers": {
                    "知识库名": "test",
                    "文件名": "相关问题_1.txt"
                },
                "page_id": 0
            }
        }
    ],
    "retrieval_web_documents": []
}
```

---

### <a id="区分文档问答"></a> 区分文档问答
**接口路径**: `/api/rag/question_qa_search`  
**请求方法**: POST  
**功能描述**: 区分文档和FAQ的问答接口  
  * 不联网检索时，file_ids和kb_ids必须有一个不为空

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string   | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| kb_ids    | []string | 否 | 检索的知识库id列表 |
| file_ids  | []string | 否 | 检索的文件id列表 |
| question  | string   | 是 | 待检索问题 |
| rerank    | bool     | 否 | 是否对检索结果进行重排序，默认值True |
| - rerank_url        | string   | 否 | 自定义重排序接口地址 |
| - rerank_model_name | string   | 否 | 自定义重排序接口名称 |
| - rerank_api_key    | string   | 否 | 自定义重排序接口密钥 |
| networking       | bool     | 否 | 是否使用网络检索，默认值False |
| web_search_tools | []string | 否 | 网络检索工具列表，默认值["BaiduSearch"] |
| hybrid_search    | bool     | 否 | 是否使用混合检索，默认值False |
| web_chunk_size   | int      | 否 | 网络检索时，每个chunk的大小，默认值800 |
| top_k            | int      | 否 | 返回最多检索数量，默认值30 |
| score_threshold  | float    | 否 | 检索结果得分阈值，默认值0.5 |
| merge | bool     | 否 | 是否合并检索源于同一个文件的结果，默认值True |
| history | string或者list | 否 | 问答历史，格式为json字符串或者list，如果传了则用作query改写 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int | 200表示成功，其他表示失败 |
| msg | string | 返回结果说明 |
| question | string | 检索问题 |
| retrieval_doc_documents | List | 检索doc结果 |
| retrieval_qa_documents | List | 检索qa结果 |
| retrieval_web_documents | List | 网页检索结果 |


**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/rag/question_qa_search' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "user",
    "kb_ids": ["KB9ca1fb4e288f4adcaa6aff7b1818c1d1"],
    "top_k": 4,
    "question": "劳动者到新单位后多久签订劳动合同？",
    "networking": false
    
}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success chat\nKBdatabase search sucess.\n",
    "question": "劳动者到新单位后多久签订劳动合同？",
    "retrieval_doc_documents": [
        {
            "page_content": "该参考内容由多个片段组成，片段内容如下：\n\n***片段[18]：*** 劳动者到新单位后多久签订劳动合同？\n问题id:0d117c05-77e0-4199-8970-e25952743f19\n\n***片段[133]：*** 事业单位公开招聘时，新聘用人员的合同签订一般为多长时间？\n问题id:543575dc-5737-421e-9884-d7029f3b41a8\n\n***片段[137]：*** 劳务派遣单位与被派遣劳动者订立的劳动合同的期限应当如何约定？\n问题id:566bc91c-7a77-4428-8ae7-7d7e3974c301\n\n***片段[291]：*** 用人单位自用工之日起超过一个月不与劳动者签订劳动合同的，如何处理？\n问题id:ade11da2-9024-4519-b6b4-62fc9a70ff46",
            "metadata": {
                "kb_id": "KB9ca1fb4e288f4adcaa6aff7b1818c1d1",
                "file_id": "903c96ab508c4809a9d51aa52b21d0aa",
                "file_name": "相关问题_1.txt",
                "retrieval_query": "劳动者到新单位后多久签订劳动合同？",
                "file_url": "",
                "score": 0.83,
                "retrieval_source": "milvus",
                "headers": {
                    "知识库名": "test",
                    "文件名": "相关问题_1.txt"
                },
                "page_id": 0
            }
        }
    ],
    "retrieval_qa_documents": [],
    "retrieval_web_documents": []
}
```

---

### <a id="文档内容解析"></a> 文档内容解析
**接口路径**: `/api/rag/document_parser`  
**请求方法**: POST  
**功能描述**: 提取文档文本内容  
  * 仅支持[txt,pdf,docx,xlsx,csv]

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| files | 文件 | 是 | 待解析文档，只能上传一个，[('file', open('/home/darren/文档/repiBench.pdf','rb'))] |

**返回参数**:
| 参数名 | 类型 | 说明 |
| ----- | --- | --- |
| code | int    | 200表示成功，其他表示失败 |
| msg  | string | 返回结果说明 |
| docs | string | 文档解析结果 |

**请求示例**:
```bash
curl -X POST "http://<your_host>:<your_port>/api/rag/document_parser"  -d '{"user_id": "zzp"}' -F "file=@/home/darren/文档/repiBench.pdf"
```

**返回示例**:
```json
{
    "code":200,
    "msg":"document parser success",
    "docs":"RepoBench: Benchmarking Repository-Level Code\nAuto-Completion ........ McAuley\nUniversity of California."
}
```

---

### <a id="获取原文件"></a> 获取原文件
**接口路径**: `/api/rag/get_file_base64`  
**请求方法**: POST  
**功能描述**: 获取Base64编码的原文件  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| file_id | string  | 是 | 获取文件的id |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code        | int    | 200表示成功，其他表示失败 |
| msg         | string | 结果说明 |
| file_base64 | string | 文件base64编码 |

**请求示例**:
```bash
curl -X POST -H "Content-Type: application/json" http://{ip}:{port}/api/rag/get_file_base64 \
    -d '{"file_id": "filezzp"}'
```

**返回示例**:
```json
{
    "code": 200, 
    "msg": "success",
    "file_base64": ""
}
```

---

### <a id="查询改写"></a> 查询改写
**接口路径**: `/api/rag/query_rewrite`  
**请求方法**: POST  
**功能描述**: 根据对话历史改写查询  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| query         | string   | 是 | 用户问题 |
| history       | list     | 是 | 对话历史记录，[["human","ai"],["human","ai"]] |
| api_base      | string   | 否 | LLM模型访问接口地址 |
| api_key       | string   | 否 | LLM模型访问api_key |
| api_context_length | int | 否 | 模型的最大输入token数 |
| model_name    | string   | 否 | LLM模型名称，默认从api_base获取可以模型的第一个 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code        | int    | 200表示成功，其他表示失败 |
| msg         | string | 结果说明 |
| rewrite_query | string | 改写后的查询 |

**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/rag/query_rewrite' \
--header 'Content-Type: application/json' \
--data '{
    "query": "那后天呢？",
    "history": [
        ["北京明天出门需要带伞吗？","今天北京的天气是全天阴，气温19摄氏度到27摄氏度，因此不需要带伞噢。"]
    ],
    "api_base": "http://192.168.5.177:8000/v1", 
    "api_key": "sk-b155e575ea1542cba4f4a0ea28075236",
    "model_name": "Qwen2.5-7B-Instruct"   
}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "sucess",
    "rewrite_query": "北京后天出门需要带伞吗？"
}
```

---

### <a id="本地文档问答"></a> 本地文档问答
**接口路径**: `/api/rag/local_doc_chat`  
**请求方法**: POST  
**功能描述**: 基于配置模型的文档问答  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string   | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| question  | string   | 是 | 待检索问题 |
| streaming  | bool   | 否 | 是否采用流式输出，默认false |
| bot_id | string | 否 | 是否为特定机器人问答，如果采用机器人问答，则相关参数自动加载机器人相关配置参数 |
| kb_ids    | []string | 否 | 检索的知识库id列表 |
| rerank    | bool     | 否 | 是否对检索结果进行重排序，默认值True |
| only_need_search_results    | bool     | 否 | 是否只输出检索结果 |
| networking| bool     | 否 | 是否使用网络检索，默认值False |
| hybrid_search    | bool     | 否 | 是否使用混合检索，默认值False |
| top_k            | int      | 否 | 返回最多检索数量，默认值30 |
| score_threshold  | float    | 否 | 检索结果得分阈值，默认值0.5 |
| history | string或者list | 否 | 问答历史，格式为json字符串或者list，如果传了则用作query改写 |
| api_base | string | 否 | 大模型地址 |
| api_key | string | 否 | 大模型密钥 |
| api_context_length | string | 否 | 上下文长度 |
| top_p | string | 否 |  |
| top_k | string | 否 |  |
| chunk_size | string | 否 |  |
| temperature | string | 否 |  |
| model | string | 否 | 模型名称 |
| max_token | string | 否 | 最大输出token |


流式返回
```
{
    "code": 200,
    "msg": "success",
    "question": "",
    "response": delta_answer,
    "history": [],
    "source_documents": [],
    "retrieval_documents": [],
    "time_record": format_time_record(time_record),
}
[DONE]
{
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
```

非流式返回
```

{
    "code": 200, 
    "msg": "success no stream chat", 
    "question": question,                       
    "response": resp["result"], 
    "model": model,
    "history": history, 
    "condense_question": resp['condense_question'],
    "source_documents": source_documents, 
    "retrieval_documents": retrieval_documents,
    "time_record": formatted_time_record
}
```

---


### <a id="删除切片"></a> 删除切片
**接口路径**: `/api/rag/delete_chunks`  
**请求方法**: POST  
**功能描述**: 删除指定切片

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id       | string   | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info     | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| doc_ids       | List[string]  | 是 | 待删除的切片的所有id，切片应属于同一个文档 |


**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code        | int    | 200表示成功，其他表示失败 |
| msg         | string | 结果说明 |

**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/rag/delete_chunks' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "user",
    "doc_ids": [
        "0a7d97c82d464d5fb5bdbb8baa680985_0",
        "0a7d97c82d464d5fb5bdbb8baa680985_1"
    ]
}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success delete doc_ids ['0a7d97c82d464d5fb5bdbb8baa680985_0', '0a7d97c82d464d5fb5bdbb8baa680985_1']"
}
```

---



### <a id="文件移动"></a> 文件移动
**接口路径**: `/api/rag/move_file`
**请求方法**: POST  
**功能描述**: 文件移动

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id       | string   | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info     | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| target_kb_id  | string   | 是 | 目标知识库id，移动后的知识库和源知识库必须为同一个用户，且知识库的解析方式，embedding模型必须相同 |
| file_id       | string   | 是 | 待移动的文件id |


**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code        | int    | 200表示成功，其他表示失败 |
| msg         | string | 结果说明 |

**请求示例**:
```bash
curl --location 'http://192.168.2.201:8777/api/rag/move_file' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "user",
    "file_id": "0f0d77f76fd7423ab3ca329039d16ae8",
    "target_kb_id": "KB71b72474e7384e0b8254a4f0ebb19c1f"
}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success move file 0f0d77f76fd7423ab3ca329039d16ae8 from kb KB3fac3c38217642d1b084c4c2e9fb0f09 to kb KB71b72474e7384e0b8254a4f0ebb19c1f"
}
```

---




## 新开发通用接口

### <a id="修改切片元数据"></a> 修改切片元数据
**接口路径**: `/api/modify_chunk_kwargs`
**请求方法**: POST  
**功能描述**: 修改切片的元数据信息  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| doc_id | string  | 是 | 切片id |
| kwargs | string | 是 | 需要修改的元数据信息,dict json转string |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code        | int    | 200表示成功，其他表示失败 |
| msg         | string | 结果说明 |


**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/modify_chunk_kwargs' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "user",
    "doc_id": "2642a6b3518f496c92e00fae97b63557_0",
    "kwargs": "{\"arg1\": \"20250716\"}"
}'

```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success"
}
```

---

### <a id="删除切片元数据"></a> 删除切片元数据
**接口路径**: `/api/delete_chunk_metadata`  
**请求方法**: POST  
**功能描述**: 删除切片的指定元数据字段  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| doc_id | string  | 是 | 切片id |
| delete_keys | list | 是 | 需要修改的元数据信息 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code        | int    | 200表示成功，其他表示失败 |
| msg         | string | 结果说明 |

**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/delete_chunk_metadata' \
--header 'Content-Type: text/plain' \
--data '{
    "user_id": "user",
    "doc_id": "2642a6b3518f496c92e00fae97b63557_0",
    "delete_keys": ["arg1"]
}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success"
}
```

---

### <a id="更新知识库元数据"></a> 更新知识库元数据
**接口路径**: `/api/update_kb_metadata`  
**请求方法**: POST  
**功能描述**: 修改知识库元数据  
  * 该接口直接为用上传的元数据替换现有的元数据，请注意使用

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| kb_id | string  | 是 | 需要更新元数据的知识库id |
| metadata | string | 是 | json转str的元数据信息 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code        | int    | 200表示成功，其他表示失败 |
| msg         | string | 结果说明 |

**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/update_kb_metadata' \
--header 'Content-Type: text/plain' \
--data '{
    "user_id": "user",
    "kb_id": "KB9ca1fb4e288f4adcaa6aff7b1818c1d1",
    "metadata": "{\"arg1\": \"20250716\"}"
}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success"
}
```

---

### <a id="更新文件元数据"></a> 更新文件元数据
**接口路径**: `/api/update_file_metadata`  
**请求方法**: POST  
**功能描述**: 修改文件的元数据  
  * 该接口直接为用上传的元数据替换现有的元数据，请注意使用

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| file_id | string  | 是 | 需要更新元数据的知识库id |
| metadata | string | 是 | json转str的元数据信息 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code        | int    | 200表示成功，其他表示失败 |
| msg         | string | 结果说明 |

**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/update_file_metadata' \
--header 'Content-Type: text/plain' \
--data '{
    "user_id": "user",
    "file_id": "2642a6b3518f496c92e00fae97b63557",
    "metadata": "{\"arg1\": \"20250716\"}"
}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success"
}
```

---

### <a id="获取联网检索工具"></a> 获取联网检索工具
**接口路径**: `/api/get_websearch_tools`  
**请求方法**: GET  
**功能描述**: 获取可用的联网检索工具  
**请求示例**:
```bash
curl --location 'http://{ip}:{port}/api/get_websearch_tools'
```
**返回示例**:
```json
{
    "code": 200,
    "web_search_tools": [
        "BingSearch",
        "BaiduSearch",
        "BaiduBaike",
        "DuckDuckGoSearch",
        "WikipediaSearch"
    ]
}
```

---

### <a id="切片摘要生成"></a> 切片摘要生成
**接口路径**: `/api/chunk_summary`  
**请求方法**: POST  
**功能描述**: 生成切片内容的摘要  

**请求参数**：
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string   | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| api_base      | string   | 否 | LLM模型访问接口地址 |
| api_key       | string   | 否 | LLM模型访问api_key |
| model_name    | string   | 否 | LLM模型名称 |
| top_p         | float    | 否 | 0.7，默认值0.7，用于控制生成文本的多样性 |
| temperature   | float    | 否 | 0.95，默认值0.95，用于控制生成文本的随机性 |
| max_tokens    | int      | 否 | 4096，默认值4096，用于控制生成文本的最大长度 |
| file_id       | string   | 是 | 检索的文件id |
| keywords_num  | int      | 否 | 2，默认值2，用于控制生成关键词的数量 |
| qa_num        | int      | 否 | 2，默认值2，用于控制生成问答对的数量 |
| save_summary  | int      | 否 | 默认值False，用于控制是否将生成结果保存到Document数据表存储 |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int | 200表示成功，其他表示失败 |
| msg | string | 返回结果说明 |
| chunk_result | List | 每个切片内容详情，包括关键词、总结、qa提取结果 |
| completed_text | string | 文件的完整文本内容 |

**请求示例**:
```bash
curl -X POST -H "Content-Type: application/json" http://ip:port/api/chunk_summary \
    -d '{"user_id": "zzp", "file_id": "8591b31075194422b011993e3b75ae15", "api_base": "http://192.168.5.177:8000/v1", "api_key": "sk-b155e575ea1542cba4f4a0ea28075236", "model_name": "Qwen2.5-7B-Instruct", "keywords_num": 2, "qa_num": 2, "save_summary": true}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success",
    "chunk_result": [
        {
            "page_content": "[headers]({'知识库名': '唐尚华测试', '文件名': '关于修订河南联通省公司部门中心员工薪酬分配办法的通知.pdf'})\n##中国联合网络通信有限公司河南省分公司文件\n\n豫联通〔2023〕209 号\n\n##关于修订《河南联通省公司部门（中心）员工薪酬分配办法》的通知\n\n省公司各部门（中心）：\n为充分调动省公司部门（中心）员工工作积极性、强化员工争先意识，通过业绩考核结果与绩效薪酬分配强关联，合理拉开绩效薪酬分配差距，发挥薪酬分配的激励作用，省公司修订了《河南联通省公司部门（中心）员工薪酬分配办法》，业经2023年9月9 日省公司党委会研究通过，现印发给你们，请遵照执行。\n![figure](1-figure-0.jpg \"\")\n\n##河南联通省公司部门（中心）员工薪酬分配办法\n\n（二级制度，V4.0）\n本办法适用于河南联通省公司部门（中心）专业序列员工，不含直聘专家、省级转非人员、河南机动通信分局员工和联通（河南）产业互联网有限公司专业序列员工。",
            "metadata": {
                "user_id": "zzp__1234",
                "kb_id": "KBzzp_test",
                "file_id": "8591b31075194422b011993e3b75ae15",
                "file_name": "关于修订河南联通省公司部门中心员工薪酬分配办法的通知.pdf",
                "nos_key": "/workspace/QAnything/QANY_DB/content/zzp__1234/KBzzp_test/8591b31075194422b011993e3b75ae15/关于修订河南联通省公司部门中心员工薪酬分配办法的通知.pdf",
                "file_url": "",
                "title_lst": [
                    "中国联合网络通信有限公司河南省分公司文件",
                    "关于修订《河南联通省公司部门（中心）员工薪酬分配办法》的通知",
                    "河南联通省公司部门（中心）员工薪酬分配办法"
                ],
                "has_table": false,
                "images": [
                    "![figure](1-figure-0.jpg \"\")"
                ],
                "page_id": 1,
                "bboxes": [
                    [
                        109.0,
                        492.0,
                        211.33333333333334,
                        246.66666666666666,
                        1
                    ],
                    [
                        216.33333333333334,
                        373.3333333333333,
                        314.0,
                        329.0,
                        1
                    ]
                ],
                "headers": {
                    "知识库名": "唐尚华测试",
                    "文件名": "关于修订河南联通省公司部门中心员工薪酬分配办法的通知.pdf"
                },
                "faq_dict": {}
            },
            "chunk_id": "8591b31075194422b011993e3b75ae15_0",
            "keywords": [
                "修订的薪酬分配办法",
                "适用范围"
            ],
            "qa": [
                [
                    "本办法适用于哪些员工？",
                    "河南联通省公司部门（中心）专业序列员工，不含直聘专家、省级转非人员、河南机动通信分局员工和联通（河南）产业互联网有限公司专业序列员工。"
                ],
                [
                    "修订《河南联通省公司部门（中心）员工薪酬分配办法》的原因是什么？",
                    "为充分调动省公司部门（中心）员工工作积极性、强化员工争先意识，通过业绩考核结果与绩效薪酬分配强关联，合理拉开绩效薪酬分配差距，发挥薪酬分配的激励作用。"
                ]
            ]
        },
        ...
    ],
    "completed_text": "##中国联合网络通信有限公司河南省分公司文件\n\n豫联通〔2023〕209 号\n\n.........",
    "summary": "### 摘要\n\n中国联合网络通信有限公司河南省分公司发布了新的《河南联通省公司部门（中心）员工薪酬分配办法》，旨在通过业绩考核结果与绩效薪酬分配的强关联，激励员工提升工作积极性，合理拉开薪酬差距。该办法适用于省公司部门（中心）的专业序列员工，并明确了薪酬结构、绩效薪酬计算方法及发放流程。绩效薪酬由基本薪酬和绩效薪酬组成，其中绩效薪酬又分为日常绩效薪酬和年终绩效薪酬。各部门可以根据实际情况自主分配绩效薪酬，但需确保考评等级为“优秀”和“良好”的员工年终绩效薪酬兑现均值不低于“称职”员工的相应均值的1.2倍和1.1倍。该办法自2023年1月1日起在政企BG执行，其他部门（中心）自2023年10月1日起执行。"
}
```

---

### <a id="文件大纲提取"></a> 文件大纲提取
**接口路径**: `/api/file_extract_outline`  
**请求方法**: POST  
**功能描述**: 提取文件内容大纲  

**请求参数**:
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string   | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| api_base      | string   | 否 | LLM模型访问接口地址 |
| api_key       | string   | 否 | LLM模型访问api_key |
| model_name    | string   | 否 | LLM模型名称 |
| top_p         | float    | 否 | 0.7，默认值0.7，用于控制生成文本的多样性 |
| temperature   | float    | 否 | 0.95，默认值0.95，用于控制生成文本的随机性 |
| max_tokens    | int      | 否 | 4096，默认值4096，用于控制生成文本的最大长度 |
| file_id       | string   | 是 | 检索的文件id |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int | 200表示成功，其他表示失败 |
| msg | string | 返回结果说明 |
| file_outline | string | 文件大纲内容 |


**请求示例**:
```bash
curl -X POST -H "Content-Type: application/json" http://ip:port/api/file_extract_outline \
    -d '{"user_id": "zzp", "file_id": "8591b31075194422b011993e3b75ae15", "api_base": "http://192.168.5.177:8000/v1", "api_key": "sk-b155e575ea1542cba4f4a0ea28075236", "model_name": "Qwen2.5-7B-Instruct"}'
```

**返回示例**:
```json
{
    "code": 200, 
    "msg": "success", 
    "file_outline": "file_outline"
}
```

---

### <a id="文件摘要提取"></a> 文件摘要提取
**接口路径**: `/api/file_extract_summary`  
**请求方法**: POST  
**功能描述**: 提取文件内容摘要  

**请求参数**:
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id   | string   | 是 | 用户id，user_id 长度必须小于64，且必须只含有字母，数字和下划线且字母开头 |
| user_info | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| api_base      | string   | 否 | LLM模型访问接口地址 |
| api_key       | string   | 否 | LLM模型访问api_key |
| model_name    | string   | 否 | LLM模型名称 |
| top_p         | float    | 否 | 0.7，默认值0.7，用于控制生成文本的多样性 |
| temperature   | float    | 否 | 0.95，默认值0.95，用于控制生成文本的随机性 |
| max_tokens    | int      | 否 | 4096，默认值4096，用于控制生成文本的最大长度 |
| file_id       | string   | 是 | 检索的文件id |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int | 200表示成功，其他表示失败 |
| msg | string | 返回结果说明 |
| file_summary | string | 文件大纲内容 |


**请求示例**:
```bash
curl -X POST -H "Content-Type: application/json" http://ip:port/api/file_extract_summary \
    -d '{"user_id": "zzp", "file_id": "8591b31075194422b011993e3b75ae15", "api_base": "http://192.168.5.177:8000/v1", "api_key": "sk-b155e575ea1542cba4f4a0ea28075236", "model_name": "Qwen2.5-7B-Instruct"}'
```

**返回示例**:
```json
{
    "code": 200, 
    "msg": "success", 
    "file_summary": "file_summary"
}
```


## 机器人问答

### <a id="新建Bot"></a> 新建Bot
**接口路径**: `/api/rag/new_bot`  
**请求方法**: POST  
**功能描述**: 创建新的机器人  

**请求参数**:
| 参数名             | 示例参数值                           | 是否必填 | 参数类型         | 描述说明                  |
| --------------- | ------------------------------- | ---- | ------------ | --------------------- |
| user_id         | "zzp"                           | 是    | String       | 用户 id                 |
| user_info       | "1234"                          | 否    | string | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| bot_name        | "测试"                            | 是    | String       | Bot名字                 |
| description     | "这是一个测试Bot"                     | 否    | String       | Bot简介                 |
| head_image      | "zhiyun/xxx"                    | 否    | String       | 头像nos地址               |
| prompt_setting  | "你是一个耐心、友好、专业的机器人，能够回答用户的各种问题。" | 否    | String       | Bot角色设定               |
| welcome_message | "您好，我是您的专属机器人，请问有什么可以帮您呢？"      | 否    | String       | Bot欢迎语                |
| kb_ids          | ["KB_xxx", KB_xxx", "KB_xxx"]      | 否    | List[String] | Bot关联的知识库id列表         |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int | 200表示成功，其他表示失败 |
| msg  | string | 返回结果说明 |
| data | list   | 新创建的机器人的详细信息 |

**请求示例**:
```bash
curl -X POST -H "Content-Type: application/json" http://ip:port/api/rag/new_bot \
    -d '{"user_id": "test_user", "bot_name": "客服机器人", "description": "用于客户服务", "knowledge_base_ids": ["kb1", "kb2"]}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success create qanything bot BOT042f88dc5e474772bf2acd0f81b6c071",
    "data": {
        "bot_id": "BOT042f88dc5e474772bf2acd0f81b6c071",
        "bot_name": "客服机器人",
        "create_time": "2025-09-02 15:05:53"
    }
}
```

### <a id="删除Bot"></a> 删除Bot
**接口路径**: `/api/rag/delete_bot`  
**请求方法**: POST  
**功能描述**: 删除指定机器人  

**请求参数**:
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id | string | 是 | 用户id |
| user_info | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| bot_id  | string | 是 | 要删除的机器人ID |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int | 200表示成功，其他表示失败 |
| msg | string | 返回结果说明 |

**请求示例**:
```bash
curl -X POST -H "Content-Type: application/json" http://ip:port/api/rag/delete_bot \
    -d '{"user_id": "test_user", "bot_id": "bot_BOT042f88dc5e474772bf2acd0f81b6c071123456"}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "Bot BOT042f88dc5e474772bf2acd0f81b6c071 delete success"
}
```

### <a id="更新Bot"></a> 更新Bot
**接口路径**: `/api/rag/update_bot`  
**请求方法**: POST  
**功能描述**: 更新机器人信息  

**请求参数**:
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id | string | 是 | 用户id |
| user_info | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| bot_id  | string | 是 | 要更新的机器人ID |
| bot_name | string | 否 | 新的机器人名称 |
| description | string | 否 | 新的机器人描述 |
| head_image  | string | 否 | 新的机器人图 |
| prompt_setting | string | 否 | 新的机器人提示词 |
| welcome_message | string | 否 | 新的机器人欢迎词 |
| kb_ids | List[string] | 否 | 新的机器人绑定的知识库id |
| api_base | string | 否 | 大模型地址 |
| api_key | string | 否 | 大模型密钥 |
| api_context_length | string | 否 | 上下文长度 |
| top_p | string | 否 |  |
| top_k | string | 否 |  |
| chunk_size | string | 否 |  |
| temperature | string | 否 |  |
| model | string | 否 | 模型名称 |
| max_token | string | 否 | 最大输出token |
| rerank | string | 否 | 检索结果是否重排 |
| hybrid_search | string | 否 | 是否采用混合检索 |
| networking | string | 否 | 是否采用联网检索 |
| only_need_search_results | string | 否 | 是否只输出检索结果 |



**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int | 200表示成功，其他表示失败 |
| msg | string | 返回结果说明 |

**请求示例**:
```bash
curl -X POST -H "Content-Type: application/json" http://ip:port/api/rag/update_bot \
    -d '{"user_id": "test_user", "bot_id": "BOT042f88dc5e474772bf2acd0f81b6c071", "bot_name": "新客服机器人", "description": "更新后的描述"}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "Bot BOT042f88dc5e474772bf2acd0f81b6c071 update success"
}
```

### <a id="获取Bot信息"></a> 获取Bot信息
**接口路径**: `/api/rag/get_bot_info`  
**请求方法**: POST  
**功能描述**: 获取机器人详细信息  

**请求参数**:
| 参数名 | 类型 | 是否必须 | 说明 |
| --- | --- | --- | --- |
| user_id | string | 是 | 用户id |
| user_info | string   | 否 | 用户信息，必须为纯数字，默认值“1234”，其作用是用于同一个user_id可以用多个账号 |
| bot_id  | string | 是 | 要查询的机器人ID |

**返回参数**:
| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int | 200表示成功，其他表示失败 |
| msg | string | 返回结果说明 |
| bot_info | object | 机器人详细信息，包含名称、描述、关联知识库等 |

**请求示例**:
```bash
curl -X POST -H "Content-Type: application/json" http://ip:port/api/rag/get_bot_info \
    -d '{"user_id": "test_user", "bot_id": "BOT042f88dc5e474772bf2acd0f81b6c071"}'
```

**返回示例**:
```json
{
    "code": 200,
    "msg": "success",
    "data": [
        {
            "bot_id": "BOT042f88dc5e474772bf2acd0f81b6c071",
            "user_id": "user__1234",
            "bot_name": "测试bot",
            "description": "测试bot",
            "head_image": "",
            "prompt_setting": "\n- 你是一个耐心、友好、专业的机器人，能够回答用户的各种问题。\n- 根据知识库内的检索结果，以清晰简洁的表达方式回答问题。\n- 不要编造答案，如果答案不在经核实的资料中或无法从经核实的资料中得出，请回答“我无法回答您的问题。”（或者您可以修改为：如果给定的检索结果无法回答问题，可以利用你的知识尽可能回答用户的问题。)\n",
            "welcome_message": "您好，我是您的专属机器人，请问有什么可以帮您呢？",
            "kb_ids": [
                "KBddfa934b8e524c0f82ea69590b7dcc37",
                "KBddfa934b8e524c0f82ea69590b7dcc37_summary"
            ],
            "kb_names": [
                "测试",
                "测试_摘要"
            ],
            "update_time": "2025-09-02 15:22:10",
            "llm_setting": "{\"api_base\": \"http://192.168.5.177:8000/v1/\", \"api_key\": \"xxxxx\", \"api_context_length\": 4096, \"top_p\": 1, \"top_k\": 30, \"chunk_size\": 800, \"temperature\": 0.5, \"model\": \"Qwen3-30B-3B\", \"max_token\": 512, \"networking\": false, \"only_need_search_results\": true}"
        }
    ]
}
```





## 使用说明
1. 所有POST请求需使用`application/json`格式
2. 文件上传接口使用`multipart/form-data`格式
3. 返回状态码说明：
   - 200：请求成功
   - 400：请求参数错误
   - 401: 超过知识限制
   - 500：服务器内部错误
4. 返回结果说明：
   - `code`：返回状态码
   - `msg`：返回结果说明
   - `data`：返回数据，根据接口不同而不同


