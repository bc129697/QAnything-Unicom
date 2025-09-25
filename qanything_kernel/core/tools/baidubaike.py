import sys
if __name__ == '__main__':
    sys.path.append('./')
import re
import json
import requests
import html2text
from bs4 import BeautifulSoup
from urllib.parse import unquote, quote
from qanything_kernel.utils.custom_log import debug_logger



def remove_brackets_and_contents(text):
    # 正则表达式匹配中括号及其内部的内容
    pattern = r'\[.*?\]'
    
    # 使用sub函数替换匹配到的内容为空字符串
    result = re.sub(pattern, '', text)

    # 去除HTML标签
    clean_text = re.sub(r'<.*?>', '', result)
    
    # 去除多余空白和换行
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    return clean_text




import csv
def save_to_csv(filename, data):
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow({'Title': data[0], 'Content': data[1]})



class BaiduBaike():
    component_name = "Baidu Baike"

    def fetch_baike_page(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=2)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to retrieve the webpage with status code {response.status_code}")
            return None
    
    def get_polysemant_links(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        polysemant_links = []
        for link in soup.find_all('a', href=True):
            if '/item/' in link['href']:
                polysemant_links.append("https://baike.baidu.com" + link['href'])
        return polysemant_links
    

    def parse_baike_page(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 提取<title>标签的内容
        title = soup.title.string if soup.title else 'No title found'

        content = soup.find('div', class_="lemmaSummary_aDCp0 J-summary").get_text() if soup.find('div', class_="lemmaSummary_aDCp0 J-summary") else soup.find('meta', attrs={'name': 'description'}).get('content')
        
        # 去掉content中所有中括号以及中括号内的内容
        content = remove_brackets_and_contents(content)
        
        # 提取主要内容，假设主要内容在<article>标签内
        # 注意：你需要根据实际的HTML结构调整选择器
        # content = soup.article.get_text() if soup.article else 'No content found'
        # print("Content:", content)

        # 提取description meta标签的内容
        # description_meta = soup.find('meta', attrs={'name': 'description'})
        # og_description_meta = soup.find('meta', attrs={'property': 'og:description'})
        # title = soup.find('h1', class_='lemmaTitle').get_text()
        # content = soup.find('div', class_='lemma-summary').get_text()

        return title, content


    def run(self, question, top_n=3, detail=False):
        msg = "Baidu Baike: "
        ans = question
        if not ans:
            msg += "No question provided."
            return [], msg
        
        baike_res = []
        try:
            url = 'https://baike.baidu.com/item/'+question  # 替换为实际的百度百科词条URL
            html_content = self.fetch_baike_page(url)

            if html_content:
                polysemant_links = self.get_polysemant_links(html_content)
                
                encoded_string = quote(question)
                text_polysemant_links = []
                for link in polysemant_links:
                    if "/"+encoded_string+"/" in link:
                        text_polysemant_links.append(link) 
                    else:
                        continue
                
                if text_polysemant_links:
                    debug_logger.debug("Polysemant Links:", text_polysemant_links)
                    
                    for link in text_polysemant_links:
                        html_content = self.fetch_baike_page(link)
                        if html_content:
                            title, content = self.parse_baike_page(html_content)
                            baike_res.append({
                                "url": link,
                                "title": title,
                                "content": content
                            })
                else:
                    debug_logger.info("No polysemant links found.")
                    title, content = self.parse_baike_page(html_content)
                    baike_res.append({
                        "url": url,
                        "title": title,
                        "content": content
                    })
            else:
                msg += "Failed to fetch the baike webpage."
                debug_logger.error("Failed to fetch the webpage.")
                return [], msg

            msg += "success"

        except Exception as e:
            msg += f"**ERROR**: {str(e)}"
            debug_logger.error(f"**ERROR**: {str(e)}")
            return [], msg

        return baike_res, msg
    






if __name__ == '__main__':
    search_term = sys.argv[1] if len(sys.argv) > 1 else "Python"
    search = BaiduBaike()
    results = search.run(search_term, 10)
    print(json.dumps(results, ensure_ascii=False, indent=4))
else:
    from qanything_kernel.configs.model_config import SUPORT_WEBSEARCH_TOOLS
    if BaiduBaike.__name__ not in SUPORT_WEBSEARCH_TOOLS:
        SUPORT_WEBSEARCH_TOOLS.append(BaiduBaike.__name__)
    
