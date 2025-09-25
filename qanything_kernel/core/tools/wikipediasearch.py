if __name__=='__main__':
    import sys
    sys.path.append('./')
from abc import ABC
import wikipedia
import requests
import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from qanything_kernel.utils.custom_log import debug_logger


def check_valid_value(language):                    
    return language in ['af', 'pl', 'ar', 'ast', 'az', 'bg', 'nan', 'bn', 'be', 'ca', 'cs', 'cy', 'da', 'de',
                                'et', 'el', 'en', 'es', 'eo', 'eu', 'fa', 'fr', 'gl', 'ko', 'hy', 'hi', 'hr', 'id',
                                'it', 'he', 'ka', 'lld', 'la', 'lv', 'lt', 'hu', 'mk', 'arz', 'ms', 'min', 'my', 'nl',
                                'ja', 'nb', 'nn', 'ce', 'uz', 'pt', 'kk', 'ro', 'ru', 'ceb', 'sk', 'sl', 'sr', 'sh',
                                'fi', 'sv', 'ta', 'tt', 'th', 'tg', 'azb', 'tr', 'uk', 'ur', 'vi', 'war', 'zh', 'yue']

def wikipediasearch(question, top_n=3, timeout_seconds=5, suggestion=False):
    search_params = {
        'list': 'search',
        'srprop': '',
        'srlimit': top_n,
        'limit': top_n,
        'srsearch': question,
        'format': 'json',
        'action': 'query'
    }

    headers = {
        'User-Agent': wikipedia.USER_AGENT
    }

    r = requests.get(wikipedia.API_URL, params=search_params, headers=headers, timeout=timeout_seconds)
    raw_results = r.json()

    if 'error' in raw_results:
        if raw_results['error']['info'] in ('HTTP request timed out.', 'Pool queue is full'):
            debug_logger.error("Wikipedia search timed out")
            return []
        else:
            debug_logger.error(raw_results['error']['info'])
            return []

    search_results = (d['title'] for d in raw_results['query']['search'])

    if suggestion:
        if raw_results['query'].get('searchinfo'):
            return list(search_results), raw_results['query']['searchinfo']['suggestion']
        else:
            return list(search_results), None

    return list(search_results)








class WikipediaSearch(ABC):
    component_name = "Wikipedia Search"
    language='zh'

    def run(self, question, top_n=3, detail=True, timeout_seconds=5):
        msg = "Wikipedia Search: "
        ans = question
        if not ans or not check_valid_value(self.language):
            msg += "Invalid question or language"
            return [], msg

        try:
            wiki_res = []
            wikipedia.set_lang(self.language)
            wiki_engine = wikipedia
            for wiki_key in wikipediasearch(question, top_n, timeout_seconds):
                page = wiki_engine.page(title=wiki_key, auto_suggest=False)
                wiki_res.append({
                    "url": page.url,
                    "title": page.title,
                    "content": page.content if detail else page.summary})
            msg += "sucess"
            return wiki_res, msg
        except Exception as e:
            msg += f"Error occurred while searching Wikipedia: {e}"
            debug_logger.error(f"Error occurred while searching Wikipedia: {e}")
            return [], msg
    



if __name__ == '__main__':
    search = WikipediaSearch()
    print(json.dumps(search.run('985大学'), ensure_ascii=False, indent=4))
else:
    from qanything_kernel.configs.model_config import SUPORT_WEBSEARCH_TOOLS
    if WikipediaSearch.__name__ not in SUPORT_WEBSEARCH_TOOLS:
        SUPORT_WEBSEARCH_TOOLS.append(WikipediaSearch.__name__)
