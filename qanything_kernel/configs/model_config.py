import os
from dotenv import load_dotenv

# 加载环境变量，获取环境变量GATEWAY_IP
load_dotenv()
GATEWAY_IP = os.getenv("GATEWAY_IP", "localhost")
IMAGE_NGINX_PORT = os.getenv("IMAGE_NGINX_PORT", "1080")
if GATEWAY_IP == "0.0.0.0":
    import socket
    GATEWAY_IP = socket.gethostbyname('host.docker.internal')
IMAGES_PROXY_URL = f"http://{GATEWAY_IP}:{IMAGE_NGINX_PORT}"   # 图片代理服务访问地址

# 设置各个服务的端口号，默认值为8771-8777
EMBEDDING_SERVER_PORT = int(os.getenv("EMBEDDING_SERVER_PORT", 8771))
RERANK_SERVER_PORT    = int(os.getenv("RERANK_SERVER_PORT", 8772))
INSERT_SERVER_PORT    = int(os.getenv("INSERT_SERVER_PORT", 8773))
OCR_SERVER_PORT       = int(os.getenv("OCR_SERVER_PORT", 8774))
PDFPARSER_SERVER_PORT = int(os.getenv("PDFPARSER_SERVER_PORT", 8775))
MILVUS_SERVER_PORT    = int(os.getenv("MILVUS_SERVER_PORT", 8776))
RAG_SERVER_PORT       = int(os.getenv("RAG_SERVER_PORT", 8777))


# 设置各个服务的工作线程数，默认值为1
EMBEDDING_SERVER_WORKERS = 1
RERANK_SERVER_WORKERS    = 1
INSERT_SERVER_WORKERS    = 1
OCR_SERVER_WORKERS       = 1
PDFPARSER_SERVER_WORKERS = 1
MILVUS_SERVER_WORKERS    = 1
RAG_SERVER_WORKERST      = 1



# 获取项目根目录，获取当前脚本的绝对路径，设置模型路径和保存文件路径
current_script_path = os.path.abspath(__file__)
root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))
print(f"root_path: {root_path}")
UPLOAD_ROOT_PATH = os.path.join(root_path, "QANY_DB", "content")
IMAGES_ROOT_PATH = os.path.join(root_path, "QANY_DB", "file_images")
OCR_MODEL_PATH = os.path.join(root_path, "rag_models", "ocr_models")
LOCAL_RERANK_PATH = os.path.join(root_path, "rag_models", "linux_onnx", "rerank_model_configs_v0.0.1")
LOCAL_TORCH_REANK_PATH = os.path.join(root_path, 'rag_models', 'bce-reranker-base_v1')
LOCAL_EMBED_PATH = os.path.join(root_path, "rag_models", "linux_onnx", "embedding_model_configs_v0.0.1")
LOCAL_TORCH_EMBED_PATH = os.path.join(root_path, 'rag_models', 'bce-embedding-base_v1')
PDF_MODEL_PATH = os.path.join(root_path, "rag_models", "pdf_models")
TOKENIZER_PATH = os.path.join(root_path, 'qanything_kernel/connector/llm/tokenizer_files')



# LLM 默认服务访问地址
LLM_BASE_URL = "https://maas-api.ai-yuanjing.com/openapi/compatible-mode/v1"
# LLM 模型名称
LLM_MODEL_NAME = "qwen3-235b-a22b"
# LLM 模型最大输入长度
LLM_MAX_LENGTH = 30000
# LLM 模型最大输出长度
LLM_MAX_OUTPUT_LENGTH = 1024
# LLM 模型温度
LLM_TEMPERATURE = 0.7
# LLM 模型 top_p
LLM_TOP_P = 0.9
# LLM API 密钥
LLM_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImE4ZmJlYmFiLTUxNTYtNGI0Ny05OTZmLTA4NTExZmJkNmFjMyIsInRlbmFudElEcyI6bnVsbCwidXNlclR5cGUiOjAsInVzZXJuYW1lIjoiMTU1MjA3Njc5NzAiLCJuaWNrbmFtZSI6IuWUkOWwmuWNjiIsImJ1ZmZlclRpbWUiOjE3NTU3NTE5MDIsImV4cCI6MTc1ODMzNjcwMiwianRpIjoiMjk0MjkzMDk0NzNlNGVlZGFmN2I2YjlhYzNlMWIxYzQiLCJpYXQiOjE3NTU3NDQ0MDIsImlzcyI6ImE4ZmJlYmFiLTUxNTYtNGI0Ny05OTZmLTA4NTExZmJkNmFjMyIsIm5iZiI6MTc1NTc0NDQwMiwic3ViIjoia29uZyJ9.68BghPy9Y0WN5xyfxAko_sij12aNYnz4U1qLZD7ekNg"
# LLM streaming reponse, LLM流式响应
STREAMING = True

SYSTEM = """
You are a helpful assistant. 
You are always a reliable assistant that can answer questions with the help of external documents.
Today's date is {{today_date}}. The current time is {{current_time}}.
"""

INSTRUCTIONS = """
- Answer the question strictly based on the reference information provided between <DOCUMENTS> and </DOCUMENTS>. 
- Do not attempt to modify or adapt unrelated information. If the reference information does not match the person or topic mentioned in the question, respond only with: \"抱歉，检索到的参考信息并未提供任何相关的信息，因此无法回答。\"
- Before generating the answer, please confirm the following (Let's think step by step):
    1. First, check if the reference information directly matches the person or topic mentioned in the question. If no match is found, immediately return: \"抱歉，检索到的参考信息并未提供任何相关的信息，因此无法回答。\"
    2. If a match is found, ensure all required key points or pieces of information from the reference are addressed in the answer.
- Now, answer the following question based on the above retrieved documents:
{{question}}
- Please format your response in a **logical and structured manner** that best fits the question. Follow these guidelines:
    1. **Start with a concise and direct answer to the main question**.
    
    2. **If necessary, provide additional details** in a structured format:
       - Use **appropriate multi-level headings (##, ###, ####)** to separate different parts or aspects of the answer.
       - **Use bullet points (-, *) or numbered lists (1., 2., 3.)** if multiple points need to be highlighted.
       - **Highlight key information using bold or italic text** where necessary.
    
    3. **Tailor the format to the nature of the question**. For example:
       - If the question involves a list or comparison, use bullet points or tables.
       - If the question requires a more narrative answer, structure the response into clear paragraphs.
    4. **Avoid unnecessary or irrelevant sections**. Focus solely on presenting the required information in a clear, concise, and well-structured manner.
- Respond in the same language as the question "{{question}}".
"""
"""
- Please format your response in Markdown with a clear and complete structure:
    1. **Introduction**: Briefly and directly answer the main question.
    2. **Detailed Explanation** (if more relevant details are available):
       - Use **second-level headings (##)** to separate different parts or aspects of the answer.
       - Use **ordered lists** (1., 2.,3.) or **unordered lists** (-, *) to list multiple points or steps.
       - Highlight key information using **bold** or *italic* text where appropriate.
       - If the answer is extensive, conclude with a **brief summary**.
    3. **Notes**:
       - Respond in the **same language** as the question "{{question}}".
       - Avoid including irrelevant information; ensure the answer is related to the retrieved reference information.
       - Ensure the answer is well-structured and easy to understand.
"""

PROMPT_TEMPLATE = """
<SYSTEM>
{{system}}
</SYSTEM>

<INSTRUCTIONS>
{{instructions}}
</INSTRUCTIONS>

<DOCUMENTS>
{{context}}
</DOCUMENTS>
"""

CUSTOM_PROMPT_TEMPLATE = """
<USER_INSTRUCTIONS>
{{custom_prompt}}
</USER_INSTRUCTIONS>

<DOCUMENTS>
{{context}}
</DOCUMENTS>

<INSTRUCTIONS>
- All contents between <DOCUMENTS> and </DOCUMENTS> are reference information retrieved from an external knowledge base.
- Now, answer the following question based on the above retrieved documents(Let's think step by step):
{{question}}
</INSTRUCTIONS>
"""


SIMPLE_PROMPT_TEMPLATE = """
- You are a helpful assistant. You can help me by answering my questions. You can also ask me questions.
- Today's date is {{today}}. The current time is {{now}}.
- User's custom instructions: {{custom_prompt}}
- Before answering, confirm the number of key points or pieces of information required, ensuring nothing is overlooked.
- Now, answer the following question:
{{question}}
Return your answer in Markdown formatting, and in the same language as the question "{{question}}". 
"""



QUERY_REWRITE_SYSTEM_PROMPT = """
假设你是极其专业的英语和汉语语言专家。你的任务是：给定一个聊天历史记录和一个可能涉及此聊天历史的用户最新的对话，请构造一个不需要聊天历史就能理解的独立且语义完整的句子。

你可以假设这个问题是在用户与聊天机器人对话的背景下。

instructions:
- 请始终记住，你的任务是生成独立内容，而不是直接回答用户的最新对话输入！
- 根据用户的最新对话输入和聊天历史记录，判断最新对话输入是否已经是独立且语义完整的。如果最新对话输入已经独立且完整，直接输出最新的对话输入，无需任何改动；否则，你需要对最新对话输入进行改写，使其成为不需要知道聊天历史就能理解的独立语句内容。
- 确保输出内容在重新构造前后语种保持一致。
- 确保输出内容在重新构造前后意思保持一致。
- 在构建独立输出内容时，尽可能将代词（如"她"、"他们"、"它"等）替换为聊天历史记录中对应的具体的名词或实体引用，以提高输出内容的明确性和易理解性。
- 打招呼、礼貌用语等请直接输出，无需改写。
- 输出内容仅为改写后的内容，禁止输出其他分析内容
```
Example input:
HumanMessage: `北京明天出门需要带伞吗？`
AIMessage: `今天北京的天气是全天阴，气温19摄氏度到27摄氏度，因此不需要带伞噢。`
新输入: `那后天呢？`  # 输入query与上文有关，不独立且语义不完整，需要改写
Example output: `北京后天出门需要带伞吗？`  # 根据聊天历史改写新对话输入，使其独立


Example input:
HumanMessage: `明天北京的天气是多云转晴，适合出门野炊吗？`
AIMessage: `当然可以，这样的天气非常适合出门野炊呢！不过在出门前最好还是要做好防晒措施噢~`
新输入: `那北京哪里适合野炊呢？`  # 问题已经是独立且语义完整的，不需要改写
Example output: `那北京哪里适合野炊呢？` # 直接返回新对话输入，不需要改写
```
"""


OUTLINE_EXTRACT_SYSTEM_PROMPT = """
<instruction>
你需要提取输入文本内容的大纲，大纲格式请按markdown格式进行输出，且仅输出文本大纲

<instructions>
1. 仔细阅读输入的文本内容。
2. 确定文本的主要部分或章节，提取章节名称。
3. 使用markdown格式整理大纲，确保大纲条理清晰，逻辑连贯。
4. 确保输出的大纲与输入文本内容紧密相关，不遗漏主要信息点。
5. 保持输出简洁，避免冗余描述。
</instructions>
</instruction>
"""

SUMMARY_EXTRACT_SYSTEM_PROMPT = """
<instruction>
你是一个摘要总结助手，你需要输入文本内容进行一段话总结，并输出总结摘要
<instructions>
1. 仔细阅读输入的文本内容。
2. 确定文本的主要部分或章节，提取文章的摘要信息。
3. 保持输出简洁，避免冗余描述。
</instructions>
</instruction>
"""




SENTENCE_SIZE = 100    # 文本分句长度
DEFAULT_CHILD_CHUNK_SIZE = 400
DEFAULT_PARENT_CHUNK_SIZE = 800
VECTOR_SEARCH_TOP_K = 30   # 知识库检索时返回的匹配内容条数
VECTOR_SEARCH_SCORE_THRESHOLD = 1.2  # 向量检索部分的阈值，使用L2距离，则阈值越小越严格
SEPARATORS = ["\n\n", "\n", "。", "，", ",", ".", ""]
MAX_CHARS = 10000000  # 单个文件最大字符数，超过此字符数将上传失败，改大可能会导致解析超时
QUESTION_MIN_LENGTH=1   # 问题最小长度，如果小于等于此长度，则不进行检索，直接返回空
SUPORT_WEBSEARCH_TOOLS=[] #"WikipediaSearch","DuckDuckGoSearch","BaiduSearch","BingSearch



KB_SUFFIX = "" #'_240625'
MILVUS_HOST_LOCAL = "standalone" #GATEWAY_IP
MILVUS_PORT = 19530
MILVUS_COLLECTION_NAME = 'qanything_collection' + KB_SUFFIX


ES_URL = 'http://elasticsearch:9200/' #f'http://{GATEWAY_IP}:9210/'
ES_USER = None
ES_PASSWORD = None
ES_TOP_K = 30
ES_INDEX_NAME = 'qanything_es_index' + KB_SUFFIX

MYSQL_HOST_LOCAL = "mysql" #GATEWAY_IP
MYSQL_PORT_LOCAL = 3306
MYSQL_USER_LOCAL = 'root'
MYSQL_PASSWORD_LOCAL = '123456'
MYSQL_DATABASE_LOCAL = 'qanything'


LOCAL_OCR_SERVICE_URL = f"rag_local:{OCR_SERVER_PORT}"
LOCAL_PDF_PARSER_SERVICE_URL = f"rag_local:{PDFPARSER_SERVER_PORT}"


RERANK_MODEL_NAME = ""
RERANK_API_KEY = ""
LOCAL_RERANK_SERVICE_URL = f"http://localhost:{RERANK_SERVER_PORT}/general_rerank"
LOCAL_RERANK_MODEL_NAME = 'rerank'
LOCAL_RERANK_MAX_LENGTH = 512
LOCAL_RERANK_BATCH = 4
LOCAL_RERANK_THREADS = 1
LOCAL_RERANK_MODEL_PATH = os.path.join(LOCAL_RERANK_PATH, "rerank.onnx")

EMBEDDING_DIM = 768
EMBEDDING_MODEL_NAME = "bce-embedding-base_v1"
EMBEDDING_API_KEY = ""
LOCAL_EMBED_SERVICE_URL = f"http://localhost:{EMBEDDING_SERVER_PORT}/general_embedding"
LOCAL_EMBED_MODEL_NAME = 'embed'
LOCAL_EMBED_MAX_LENGTH = 512
LOCAL_EMBED_BATCH = 4
LOCAL_EMBED_THREADS = 1
LOCAL_EMBED_MODEL_PATH = os.path.join(LOCAL_EMBED_PATH, "embed.onnx")




# Bot
BOT_DESC = "一个简单的问答机器人"
BOT_IMAGE = ""
BOT_PROMPT = """
- 你是一个耐心、友好、专业的机器人，能够回答用户的各种问题。
- 根据知识库内的检索结果，以清晰简洁的表达方式回答问题。
- 不要编造答案，如果答案不在经核实的资料中或无法从经核实的资料中得出，请回答“我无法回答您的问题。”（或者您可以修改为：如果给定的检索结果无法回答问题，可以利用你的知识尽可能回答用户的问题。)
"""
BOT_WELCOME = "您好，我是您的专属机器人，请问有什么可以帮您呢？"




