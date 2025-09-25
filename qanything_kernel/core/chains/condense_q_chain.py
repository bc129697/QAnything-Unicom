from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import StrOutputParser
from langchain_openai import ChatOpenAI
import tiktoken
from openai import OpenAI
from typing import List, Tuple
from qanything_kernel.configs.model_config import QUERY_REWRITE_SYSTEM_PROMPT
from qanything_kernel.utils.custom_log import debug_logger
from qanything_kernel.utils.general_utils import remove_think_tags


class RewriteQuestionChain:
    def __init__(self, model_name, openai_api_key, openai_api_base):
        self.chat_model = ChatOpenAI(model_name=model_name, openai_api_key=openai_api_key, openai_api_base=openai_api_base,
                                     temperature=0, model_kwargs={"top_p": 0.01, "seed": 1234})
        self.condense_q_system_prompt = QUERY_REWRITE_SYSTEM_PROMPT
        self.condense_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.condense_q_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "新问题:{question}\n请构造不需要聊天历史就能理解的独立且语义完整的问题。\n独立问题:"),
            ]
        )

        self.condense_q_chain = self.condense_q_prompt | self.chat_model | StrOutputParser()




class RewriteQuestion:
    def __init__(self, llm_api_base, llm_api_key, model_name="gpt-3.5-turbo-0613", max_context_tokens=4096):
        self.llm_api_base = llm_api_base
        self.llm_api_key = llm_api_key
        self.model_name = model_name
        self.max_context_tokens = max_context_tokens
        self.client = OpenAI(
            api_key=llm_api_key,
            base_url=llm_api_base,
        )
        
        self.condense_q_system_prompt = QUERY_REWRITE_SYSTEM_PROMPT
        try:
            self.enc = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # 如果模型不在 tiktoken 内置列表，退化为 gpt-3.5-turbo 的编码
            debug_logger.warning(f"{model_name} not found in tiktoken, using cl100k_base!")
            self.enc = tiktoken.get_encoding("cl100k_base")


    
    def _build_messages(self,
                        history: List[List[str]],
                        query: str) -> List[dict]:
        # 系统
        messages = [{"role": "system", "content": self.condense_q_system_prompt}]

        # 先全部扁平化，方便统一截断
        flat: List[Tuple[str, str]] = []
        for turn in history:
            if len(turn) >= 2:
                flat.append(("user", turn[0]))
                flat.append(("assistant", turn[1]))

        # 从最新一轮开始往前加，直到 token 超限
        budget = self.max_context_tokens - self._token_len(messages)
        selected = []
        for role, text in reversed(flat):
            turn_msg = {"role": role, "content": text}
            needed = self._token_len([turn_msg])
            if budget - needed < 0:
                break
            selected.append(turn_msg)
            budget -= needed
        selected.reverse()
        messages.extend(selected)

        # 最后追加当前 query
        modify_query = f"新输入:{query}\n请构造不需要聊天历史就能理解的独立且语义完整的对话输入。\n独立输入:"
        messages.append({"role": "user", "content": modify_query})
        return messages

    
    def _token_len(self, msgs: List[dict]) -> int:
        """openai 官方格式 token 计算（含每 message 3 个额外 token）"""
        try:
            return sum(
                len(self.enc.encode(m["content"])) + 3
                for m in msgs
            ) + 3  # 每调用再加 3
        except Exception:
            # 降级：按字符长度估算，1 汉字 ≈ 2 token
            return sum(len(m["content"]) * 2 + 3 for m in msgs) + 3


    # -------------------- 唯一对外接口 --------------------
    def rewrite(self,
                history: List[List[str]],
                query: str) -> str:
        """
        history: [[user1, assistant1], [user2, assistant2], ...]
        query  : 当前用户问题
        return : 改写后的独立检索式问题
        """
        messages = self._build_messages(history, query)
        debug_logger.info(f"[Rewrite] final messages length: {len(messages)}")
        # debug_logger.info(f"[Rewrite] final messages: {messages}")
        resp = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.0,
            top_p=0.01,
            max_tokens=256
        )
        rewritten = resp.choices[0].message.content.strip()
        rewritten = remove_think_tags(rewritten)  # 去除思考标签
        debug_logger.info(f"[Rewrite] origin: {query} -> rewritten: {rewritten}")
        return rewritten