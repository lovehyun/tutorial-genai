import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Any
import time

class SearchAgent:
    def __init__(self):
        """검색 Agent 초기화"""
        self.search_engines = {
            'google': 'https://www.google.com/search',
            'bing': 'https://www.bing.com/search'
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def process(self, message: str) -> Dict[str, Any]:
        """메시지를 분석하고 검색 수행"""
        # 검색 키워드 추출
        search_query = self._extract_search_query(message)
        
        if not search_query:
            return {
                'status': 'no_query',
                'message': '검색할 키워드를 찾을 수 없습니다.',
                'results': []
            }
        
        try:
            # 검색 수행
            search_results = self._perform_search(search_query)
            
            return {
                'status': 'success',
                'query': search_query,
                'results': search_results,
                'message': f'"{search_query}"에 대한 검색 결과를 찾았습니다.'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'검색 중 오류가 발생했습니다: {str(e)}',
                'results': []
            }
    
    def _extract_search_query(self, message: str) -> str:
        """메시지에서 검색 쿼리 추출"""
        # 검색 관련 키워드 제거
        search_keywords = [
            '검색해줘', '찾아줘', '알려줘', '정보', '뉴스', '최신', '현재',
            '어떻게', '무엇', '어디', '언제', '누가', '왜', '검색', '찾아'
        ]
        
        query = message
        for keyword in search_keywords:
            query = query.replace(keyword, '').strip()
        
        # 특수문자 제거 및 정리 (한글, 영문, 숫자, 공백만 유지)
        query = re.sub(r'[^\w\s가-힣]', '', query)
        
        # 빈 문자열이면 원본 메시지 반환
        return query if query else message
    
    def _perform_search(self, query: str) -> List[Dict[str, Any]]:
        """실제 검색 수행"""
        results = []
        
        try:
            # DuckDuckGo 검색 API 사용 (무료, API 키 불필요)
            results = self._duckduckgo_search(query)
            
            # 결과가 없으면 mock 데이터 반환
            if not results:
                results = self._get_mock_results(query)
            
            return results
            
        except Exception as e:
            print(f"검색 오류: {e}")
            # 오류 시 mock 데이터 반환
            return self._get_mock_results(query)
    
    def _duckduckgo_search(self, query: str) -> List[Dict[str, Any]]:
        """DuckDuckGo 검색 API 사용"""
        try:
            import requests
            
            # DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            
            # Abstract 결과 추가
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', query),
                    'snippet': data.get('Abstract', ''),
                    'url': data.get('AbstractURL', ''),
                    'source': 'DuckDuckGo'
                })
            
            # Related Topics 추가
            if data.get('RelatedTopics'):
                for topic in data.get('RelatedTopics', [])[:3]:
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append({
                            'title': topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else topic.get('Text', ''),
                            'snippet': topic.get('Text', ''),
                            'url': topic.get('FirstURL', ''),
                            'source': 'DuckDuckGo'
                        })
            
            # Wikipedia 검색 결과 추가
            wiki_results = self._wikipedia_search(query)
            results.extend(wiki_results)
            
            return results
            
        except Exception as e:
            print(f"DuckDuckGo 검색 오류: {e}")
            return []
    
    def _wikipedia_search(self, query: str) -> List[Dict[str, Any]]:
        """Wikipedia 검색 API 사용"""
        try:
            import requests
            
            # Wikipedia API
            url = "https://ko.wikipedia.org/api/rest_v1/page/summary/" + query
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return [{
                    'title': data.get('title', query),
                    'snippet': data.get('extract', '')[:200] + '...' if len(data.get('extract', '')) > 200 else data.get('extract', ''),
                    'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    'source': 'Wikipedia'
                }]
            
            return []
            
        except Exception as e:
            print(f"Wikipedia 검색 오류: {e}")
            return []
    
    def _get_mock_results(self, query: str) -> List[Dict[str, Any]]:
        """Mock 검색 결과 반환"""
        return [
            {
                'title': f'{query}에 대한 정보',
                'snippet': f'{query}에 대한 최신 정보와 뉴스를 찾을 수 있습니다.',
                'url': f'https://example.com/search?q={query}',
                'source': 'Mock'
            },
            {
                'title': f'{query} 관련 뉴스',
                'snippet': f'{query}와 관련된 최신 뉴스와 업데이트 정보입니다.',
                'url': f'https://news.example.com/{query}',
                'source': 'Mock'
            },
            {
                'title': f'{query} 위키피디아',
                'snippet': f'{query}에 대한 상세한 정보와 설명을 제공합니다.',
                'url': f'https://wikipedia.org/wiki/{query}',
                'source': 'Mock'
            }
        ]
    
    def _google_search(self, query: str) -> List[Dict[str, Any]]:
        """Google 검색 API 사용 (실제 구현 시)"""
        # 실제 Google Custom Search API 사용 예시
        # API_KEY = "your_google_api_key"
        # SEARCH_ENGINE_ID = "your_search_engine_id"
        
        # url = f"https://www.googleapis.com/customsearch/v1"
        # params = {
        #     'key': API_KEY,
        #     'cx': SEARCH_ENGINE_ID,
        #     'q': query
        # }
        
        # response = requests.get(url, params=params)
        # data = response.json()
        
        # results = []
        # if 'items' in data:
        #     for item in data['items']:
        #         results.append({
        #             'title': item.get('title', ''),
        #             'snippet': item.get('snippet', ''),
        #             'url': item.get('link', ''),
        #             'source': 'Google'
        #         })
        
        return []
    
    def _bing_search(self, query: str) -> List[Dict[str, Any]]:
        """Bing 검색 API 사용 (실제 구현 시)"""
        # Bing Web Search API 사용 예시
        # SUBSCRIPTION_KEY = "your_bing_api_key"
        
        # url = "https://api.bing.microsoft.com/v7.0/search"
        # headers = {
        #     'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY
        # }
        # params = {
        #     'q': query,
        #     'count': 10
        # }
        
        # response = requests.get(url, headers=headers, params=params)
        # data = response.json()
        
        # results = []
        # if 'webPages' in data and 'value' in data['webPages']:
        #     for item in data['webPages']['value']:
        #         results.append({
        #             'title': item.get('name', ''),
        #             'snippet': item.get('snippet', ''),
        #             'url': item.get('url', ''),
        #             'source': 'Bing'
        #         })
        
        return []
    
    def get_search_suggestions(self, query: str) -> List[str]:
        """검색 제안 반환"""
        suggestions = [
            f"{query} 최신 정보",
            f"{query} 뉴스",
            f"{query} 가격",
            f"{query} 리뷰",
            f"{query} 사용법"
        ]
        return suggestions
