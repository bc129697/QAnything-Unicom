# from chunk_rag import extract_by_html2text_db_nolist,split_text_by_punctuation
# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch
# import json

# class ChunkBackend():
#     def __init__(self, model_name_or_path):
#         device_map = "auto"
#         self.small_tokenizer = AutoTokenizer.from_pretrained(model_name_or_path,trust_remote_code=True)  
#         self.small_model = AutoModelForCausalLM.from_pretrained(model_name_or_path, trust_remote_code=True,device_map=device_map) 
#         self.small_model.eval()        

    
#     # def get_token_probability(self, prompt):
#     #     """
#     #     获取给定提示下特定标记的概率。
        
#     #     :param prompt: 输入的提示文本
#     #     :param token: 要计算概率的标记
#     #     :return: 标记的概率
#     #     """
#     #     payload = {
#     #         "model": self.model_name,  # 替换为你的模型名称
#     #         "prompt": prompt,
#     #         "max_tokens": 50,  # 根据需要调整
#     #         "temperature": 0.5,  # 根据需要调整
#     #         "logprobs": 1,
#     #         "top_p": 1.0,
#     #         "n": 1,
#     #         "stop": ["<|im_end|>"]
#     #     }
        
#     #     # 发送POST请求到模型服务
#     #     response = self.client.completions.create(**payload)
        
#     #     # 检查响应状态码
#     #     if response.status_code != 200:
#     #         print(f"请求失败，状态码: {response.status_code}, 响应: {response.text}")
#     #         return None
        
#     #     return response
    
    
    
#     # def get_prob_subtract(self, sentence1, sentence2, language):
#     #     if language=='zh':
#     #         query='''这是一个文本分块任务.你是一位文本分析专家，请根据提供的句子的逻辑结构和语义内容，从下面两种方案中选择一种分块方式：
#     #         1. 将“{}”分割成“{}”与“{}”两部分；
#     #         2. 将“{}”不进行分割，保持原形式；
#     #         请回答1或2。'''.format(sentence1+sentence2,sentence1,sentence2,sentence1+sentence2)
#     #         prompt="<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n{}<|im_end|>\n<|im_start|>assistant\n".format(query)
#     #     else:
#     #         query='''This is a text chunking task. You are a text analysis expert. Please choose one of the following two options based on the logical structure and semantic content of the provided sentence:
#     #         1. Split "{}" into "{}" and "{}" two parts;
#     #         2. Keep "{}" unsplit in its original form;
#     #         Please answer 1 or 2.'''.format(sentence1+' '+sentence2,sentence1,sentence2,sentence1+' '+sentence2)
#     #         prompt="<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n{}<|im_end|>\n<|im_start|>assistant\n".format(query)
        
#     #     response = self.get_token_probability(prompt)
#     #     decoded_text = response['choices'][0]['text']
#     #     print("decoded_text:", decoded_text)

#     #     # 解析输出
#     #     next_token_logits = response['choices'][0]['logprobs']['token_logprobs']
#     #     token_probs = [float(prob) for prob in next_token_logits]
#     #     print("token_probs:", token_probs)

#     #     # 假设输出是 '1' 或 '2'
#     #     import math
#     #     output_ids = [1 if '1' in decoded_text else 2]
#     #     next_token_prob_0 = math.exp(token_probs[0]) if output_ids[0] == 1 else 0
#     #     next_token_prob_1 = math.exp(token_probs[0]) if output_ids[0] == 2 else 0

#     #     print("next_token_prob_0:", next_token_prob_0)
#     #     print("next_token_prob_1:", next_token_prob_1)
#     #     prob_subtract = next_token_prob_1 - next_token_prob_0
#     #     return prob_subtract


#     def get_prob_subtract(model,tokenizer,sentence1,sentence2,language):
#         if language=='zh':
#             query='''这是一个文本分块任务.你是一位文本分析专家，请根据提供的句子的逻辑结构和语义内容，从下面两种方案中选择一种分块方式：
#             1. 将“{}”分割成“{}”与“{}”两部分；
#             2. 将“{}”不进行分割，保持原形式；
#             请回答1或2。'''.format(sentence1+sentence2,sentence1,sentence2,sentence1+sentence2)
#             prompt="<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n{}<|im_end|>\n<|im_start|>assistant\n".format(query)
            
#         else:
#             query='''This is a text chunking task. You are a text analysis expert. Please choose one of the following two options based on the logical structure and semantic content of the provided sentence:
#             1. Split "{}" into "{}" and "{}" two parts;
#             2. Keep "{}" unsplit in its original form;
#             Please answer 1 or 2.'''.format(sentence1+' '+sentence2,sentence1,sentence2,sentence1+' '+sentence2)
#             prompt="<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n{}<|im_end|>\n<|im_start|>assistant\n".format(query)
        
#         prompt_ids = tokenizer.encode(prompt, return_tensors='pt').to(model.device)
#         input_ids=prompt_ids
#         output_ids = tokenizer.encode(['1','2'], return_tensors='pt').to(model.device)
#         with torch.no_grad():
#             outputs = model(input_ids)
#             next_token_logits = outputs.logits[:, -1, :]
#             token_probs = torch.nn.functional.softmax(next_token_logits, dim=-1)
#         next_token_id_0 = output_ids[:, 0].unsqueeze(0)
#         next_token_prob_0 = token_probs[:, next_token_id_0].item()      
#         next_token_id_1 = output_ids[:, 1].unsqueeze(0)
#         next_token_prob_1 = token_probs[:, next_token_id_1].item()  
#         prob_subtract=next_token_prob_1-next_token_prob_0
#         return prob_subtract
    
        

    
#     def meta_chunking(self, original_text, base_model, language, ppl_threshold, chunk_length):
#         chunk_length=int(chunk_length)
#         if base_model=='PPL Chunking':
#             final_chunks=extract_by_html2text_db_nolist(original_text,self.small_model, self.small_tokenizer,ppl_threshold,language=language)
#         else:
#             full_segments = split_text_by_punctuation(original_text,language)
#             tmp=''
#             threshold=0
#             threshold_list=[]
#             final_chunks=[]
#             for sentence in full_segments:
#                 if tmp=='':
#                     tmp+=sentence
#                 else:
#                     prob_subtract = self.get_prob_subtract(tmp,sentence,language)
#                     threshold_list.append(prob_subtract)
#                     if prob_subtract>threshold:
#                         tmp+=' '+sentence
#                     else:
#                         final_chunks.append(tmp)
#                         tmp=sentence
#                 if len(threshold_list)>=5:
#                     last_ten = threshold_list[-5:]  
#                     avg = sum(last_ten) / len(last_ten)
#                     threshold=avg
#             if tmp!='':
#                 final_chunks.append(tmp)
                
#         merged_paragraphs = []
#         current_paragraph = ""
#         if language=='zh':
#             for paragraph in final_chunks:  
#                 if len(current_paragraph) + len(paragraph) <= chunk_length:  
#                     current_paragraph +=paragraph  
#                 else:  
#                     merged_paragraphs.append(current_paragraph)  
#                     current_paragraph = paragraph    
#         else:
#             for paragraph in final_chunks:  
#                 if len(current_paragraph.split()) + len(paragraph.split()) <= chunk_length:  
#                     current_paragraph +=' '+paragraph  
#                 else:  
#                     merged_paragraphs.append(current_paragraph)   
#                     current_paragraph = paragraph 
#         if current_paragraph:  
#             merged_paragraphs.append(current_paragraph) 
#         # final_text='\n\n'.join(merged_paragraphs)
#         # return final_text
#         return merged_paragraphs
    
import jieba
import math
from openai import OpenAI
from nltk.tokenize import sent_tokenize


def split_text_by_punctuation(text,language): 
    if language=='zh': 
        sentences = jieba.cut(text, cut_all=False)
        sentences_list = list(sentences)
        sentences = []  
        temp_sentence = ""  
        for word in sentences_list:
            if word in ["。", "！", "？","；"]:
                sentences.append(temp_sentence.strip()+word)
                temp_sentence = ""
            else:
                temp_sentence += word
        if temp_sentence:
            sentences.append(temp_sentence.strip())
        
        return sentences
    else:
        full_segments = sent_tokenize(text)
        ret = []
        for item in full_segments:
            item_l = item.strip().split(' ')
            if len(item_l) > 512:
                if len(item_l) > 1024:
                    item = ' '.join(item_l[:256]) + "..."
                else:
                    item = ' '.join(item_l[:512]) + "..."
            ret.append(item)
        return ret
    
    
class ChunkBackend:
    def __init__(self, base_url, api_key, model_name):
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)

    def get_token_probability(self, prompt):
        """
        获取给定提示下特定标记的概率。
        
        :param prompt: 输入的提示文本
        :param token: 要计算概率的标记
        :return: 标记的概率
        """
        payload = {
            "model": self.model_name,  # 替换为你的模型名称
            "prompt": prompt,
            "temperature":0.0, 
            "logprobs":10
        }
        
        # 发送POST请求到模型服务
        try:
            response = self.client.completions.create(**payload)
            return response
        except Exception as e:
            print(f"请求失败，错误信息: {e}")
            return None
        

    def get_prob_subtract(self, sentence1, sentence2, language):
        if language=='zh':
            query='''这是一个文本分块任务.你是一位文本分析专家，请根据提供的句子的逻辑结构和语义内容，并判断是否是一句连贯的语句，从下面两种方案中选择一种分块方式：
            1. 将“{}”分割成“{}”与“{}”两部分；
            2. 将“{}”不进行分割，保持原形式；
            请回答1或2。'''.format(sentence1+sentence2,sentence1,sentence2,sentence1+sentence2)
            prompt="<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n{}<|im_end|>\n<|im_start|>assistant\n".format(query)
        else:
            query='''This is a text chunking task. You are a text analysis expert. Please choose one of the following two options based on the logical structure and semantic content of the provided sentence:
            1. Split "{}" into "{}" and "{}" two parts;
            2. Keep "{}" unsplit in its original form;
            Please answer 1 or 2.'''.format(sentence1+' '+sentence2,sentence1,sentence2,sentence1+' '+sentence2)
            prompt="<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n{}<|im_end|>\n<|im_start|>assistant\n".format(query)
        
        response = self.get_token_probability(prompt)
        # print("response:", response)
        # decoded_text = response.choices[0].text
        # print("decoded_text:", decoded_text)

        
        top_logprobs = response.choices[0].logprobs.top_logprobs[0]
        probs = {token: math.exp(log_prob) for token, log_prob in top_logprobs.items()}

        # 计算所有概率的总和
        total_prob = sum(probs.values())

        # 归一化概率
        normalized_probs = {token: prob / total_prob for token, prob in probs.items()}
        # print("normalized_probs:", normalized_probs)
        prob_split = normalized_probs.get('1', 0)
        prob_keep = normalized_probs.get('2', 0)
        prob_subtract = prob_keep - prob_split
        # print("prob_split:", prob_split)
        # print("prob_keep:", prob_keep)
        # print("prob_subtract:", prob_subtract)
        return prob_subtract

    def meta_chunking(self, original_text, language, chunk_length):
        chunk_length=int(chunk_length)
        full_segments = split_text_by_punctuation(original_text,language)
        tmp=''
        threshold=0
        threshold_list=[]
        final_chunks=[]
        for sentence in full_segments:
            if tmp=='':
                tmp+=sentence
            else:
                prob_subtract = self.get_prob_subtract(tmp,sentence,language)
                threshold_list.append(prob_subtract)
                if prob_subtract>threshold:
                    tmp+=' '+sentence
                else:
                    final_chunks.append(tmp)
                    tmp=sentence
            if len(threshold_list)>=5:
                last_ten = threshold_list[-5:]  
                avg = sum(last_ten) / len(last_ten)
                threshold=avg
        if tmp!='':
            final_chunks.append(tmp)
                
        merged_paragraphs = []
        current_paragraph = ""
        if language=='zh':
            for paragraph in final_chunks:  
                if len(current_paragraph) + len(paragraph) <= chunk_length:  
                    current_paragraph +=paragraph  
                else:  
                    merged_paragraphs.append(current_paragraph)  
                    current_paragraph = paragraph    
        else:
            for paragraph in final_chunks:  
                if len(current_paragraph.split()) + len(paragraph.split()) <= chunk_length:  
                    current_paragraph +=' '+paragraph  
                else:  
                    merged_paragraphs.append(current_paragraph)   
                    current_paragraph = paragraph 
        if current_paragraph:  
            merged_paragraphs.append(current_paragraph) 
        
        return merged_paragraphs

