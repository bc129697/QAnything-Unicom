from typing import Union, Tuple, Dict
from qanything_kernel.connector.database.mysql.mysql_client import KnowledgeBaseManager
from sanic.request import File
from qanything_kernel.configs.model_config import UPLOAD_ROOT_PATH
import uuid
import os
from qanything_kernel.utils.custom_log import debug_logger
from qanything_kernel.utils.loader import UnstructuredPaddlePDFLoader
from qanything_kernel.utils.loader.csv_loader import CSVLoader
from langchain.docstore.document import Document
from langchain_community.document_loaders import UnstructuredFileLoader, TextLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
import pandas as pd
import docx2txt

class LocalFile:
    def __init__(self, user_id, kb_id, file: Union[File, str, Dict], file_name, file_id=None):
        self.user_id = user_id
        self.kb_id = kb_id
        self.file_id = uuid.uuid4().hex if file_id is None else file_id
        self.file_name = file_name
        self.file_url = ''
        if isinstance(file, Dict):
            self.file_location = "FAQ"
            self.file_content = b''
        elif isinstance(file, str):
            self.file_location = "URL"
            self.file_content = b''
            self.file_url = file
        else:
            self.file_content = file.body
            # nos_key = construct_nos_key_for_local_file(user_id, kb_id, self.file_id, self.file_name)
            # debug_logger.info(f'file nos_key: {self.file_id}, {self.file_name}, {nos_key}')
            # self.file_location = nos_key
            # upload_res = upload_nos_file_bytes_or_str_retry(nos_key, self.file_content)
            # if 'failed' in upload_res:
            #     debug_logger.error(f'failed init localfile {self.file_name}, {upload_res}')
            # else:
            #     debug_logger.info(f'success init localfile {self.file_name}, {upload_res}')
            try:
                upload_path = os.path.join(UPLOAD_ROOT_PATH, user_id)
                file_dir = os.path.join(upload_path, self.kb_id, self.file_id)
                os.makedirs(file_dir, exist_ok=True)
                self.file_location = os.path.join(file_dir, self.file_name)
                #  如果文件不存在：
                if not os.path.exists(self.file_location):
                    with open(self.file_location, 'wb') as f:
                        f.write(self.file_content)
                        import time
                        time.sleep(0.5)
                debug_logger.info(f'local file save to {self.file_location}')
            except Exception as e:
                debug_logger.error(f'failed init localfile {self.file_name}, {e}')
    
    def get_document_parser(self):
        debug_logger.info(f"start parser document to docs, file_name: {self.file_name}")
        
        if self.file_location.lower().endswith(".txt"):
            encodings = ['utf-8', 'iso-8859-1', 'windows-1252']
            docs = None
            for encoding in encodings:
                try:
                    loader = TextLoader(self.file_location, encoding=encoding)
                    docs = loader.load()
                    debug_logger.info(f"TextLoader {encoding} success: {self.file_location}")
                    break
                except Exception:
                    debug_logger.warning(f"TextLoader {encoding} error: {self.file_content}")
            
        elif self.file_location.lower().endswith(".pdf"):            
            debug_logger.info(f'use fast PDF parser document parser.')
            loader = UnstructuredPaddlePDFLoader(self.file_location, strategy="fast")
            docs = loader.load()

        elif self.file_location.lower().endswith(".docx"):
            try:
                # 未处理docx文件中的图片，表格也未处理。
                # mode="elements"可以处理表格，但会丢失图片。表格数据'category': 'Table''text_as_html'查看表格html格式。
                loader = UnstructuredWordDocumentLoader(self.file_location, strategy="fast")    
                docs = loader.load()
            except Exception as e:
                debug_logger.warning('Error in Powerful Word parsing, use docx2txt instead.')
                text = docx2txt.process(self.file_location)
                docs = [Document(page_content=text)]
        elif self.file_location.lower().endswith(".xlsx"):
            
            debug_logger.info('Excel parsing, use openpyxl.')
            docs = []
            excel_file = pd.ExcelFile(self.file_location)
            sheet_names = excel_file.sheet_names
            for idx, sheet_name in enumerate(sheet_names):
                xlsx = pd.read_excel(self.file_location, sheet_name=sheet_name, engine='openpyxl')
                xlsx = xlsx.dropna(how='all', axis=1)  # 只删除全为空的列
                xlsx = xlsx.dropna(how='all', axis=0)  # 只删除全为空的行
                csv_file_location = self.file_location[:-5] + f'_{idx}.csv'
                xlsx.to_csv(csv_file_location, index=False)
                debug_logger.info('xlsx2csv: %s', csv_file_location)
                loader = CSVLoader(csv_file_location, autodetect_encoding=True,
                                    csv_args={"delimiter": ",", "quotechar": '"'})
                docs.extend(loader.load())
        elif self.file_location.lower().endswith(".csv"):
            loader = CSVLoader(self.file_location, autodetect_encoding=True, csv_args={"delimiter": ",", "quotechar": '"'})
            docs = loader.load()
        else:
            raise TypeError("文件类型不支持，目前仅支持：[txt,pdf,docx,xlsx,csv]")
        
        return docs[0].page_content
