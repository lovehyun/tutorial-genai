# pip install -U langchain langchain-openai requests beautifulsoup4 python-dotenv

import os, re, time, random, urllib.parse, html
from typing import List, Dict, Tuple
from dataclasses import dataclass

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage

from langchain_core.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.tools import StructuredTool
from pydantic import BaseModel


load_dotenv()


# =========================
# 0) 검색어(별도 변수로 관리)
# =========================
SEARCH_QUERY = "LangChain OpenAI 최신 변경점"


# =========================
# 1) 공통 유틸 (세션/리다이렉트 정리/중복 제거)
# =========================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

def _wrap_timeout(request_func, timeout: float):
    def inner(method, url, **kwargs):
        kwargs.setdefault("timeout", timeout)
        return request_func(method, url, **kwargs)
    return inner

def build_session(timeout: float = 10.0) -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=3, connect=3, read=3,
        backoff_factor=0.6,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"]),
        raise_on_status=False,
    )
    s.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    s.request = _wrap_timeout(s.request, timeout)
    return s

def norm_url(u: str) -> str:
    if not u:
        return ""
    u = html.unescape(u.strip())
    # Google 리다이렉트 /url?q= 처리
    if u.startswith("/url?"):
        try:
            q = urllib.parse.parse_qs(urllib.parse.urlparse(u).query).get("q", [""])[0]
            if q:
                return q
        except Exception:
            pass
    parsed = urllib.parse.urlsplit(u)
    if not parsed.scheme:
        return u
    qs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    qs = [(k, v) for (k, v) in qs if k.lower() not in {
        "utm_source","utm_medium","utm_campaign","utm_term","utm_content","gclid"
    }]
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(qs), ""))

def is_http(u: str) -> bool:
    return u.startswith("http://") or u.startswith("https://")

def dedup_keep_order(items: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    seen = set(); out = []
    for title, url in items:
        key = norm_url(url)
        if key in seen:
            continue
        seen.add(key)
        out.append((title, key))
    return out


# =========================
# 2) Google / Naver 파서 (웹/뉴스 모두 대응 가능)
# =========================
GOOGLE_BASE = "https://www.google.com/search"
GOOGLE_SELECTORS_WEB = [
    "div#search a h3",
    "a h3",
    "div.yuRUbf > a > h3",
]
GOOGLE_SELECTORS_NEWS = [
    "a.WlydOe",            # 뉴스 카드 링크
    "div.SoaBEf a.WlydOe",
    "div#search a h3",     # 백업
]

def google_search(query: str, max_results: int = 5, vertical: str = "web", lang: str = "ko") -> str:
    """
    Google 검색 상위 결과(제목 - URL) 줄바꿈 텍스트로 반환.
    vertical = "web" | "news"
    """
    s = build_session()
    params = {"q": query, "hl": lang, "num": 10}
    if vertical == "news":
        params["tbm"] = "nws"
    r = s.get(GOOGLE_BASE, params=params)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    selectors = GOOGLE_SELECTORS_NEWS if vertical == "news" else GOOGLE_SELECTORS_WEB
    pairs: List[Tuple[str, str]] = []

    for sel in selectors:
        for node in soup.select(sel):
            a = node if node.name == "a" else node.find_parent("a")
            if not a:
                continue
            title = node.get_text(strip=True)
            href = norm_url(a.get("href") or "")
            if title and is_http(href):
                pairs.append((title, href))
        if len(pairs) >= max_results:
            break

    pairs = dedup_keep_order(pairs)[:max_results]
    return "\n".join([f"{i+1}. {t} - {u}" for i, (t,u) in enumerate(pairs)]) or "구글: 결과를 파싱하지 못했습니다."

NAVER_BASE = "https://search.naver.com/search.naver"
NAVER_SELECTORS_WEB = [
    "a.total_tit",
    "a.news_tit",
    "a.link_tit",
    "a.api_txt_lines",
]
NAVER_SELECTORS_NEWS = [
    "a.news_tit",
    "div.news_area > a",
    "a.total_tit",
]

def naver_search(query: str, max_results: int = 5, vertical: str = "web") -> str:
    """
    Naver 검색 상위 결과(제목 - URL) 줄바꿈 텍스트로 반환.
    vertical = "web" | "news"
    """
    s = build_session()
    params = {"query": query}
    r = s.get(NAVER_BASE, params=params)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    selectors = NAVER_SELECTORS_NEWS if vertical == "news" else NAVER_SELECTORS_WEB
    pairs: List[Tuple[str, str]] = []

    for sel in selectors:
        for a in soup.select(sel):
            title = a.get_text(strip=True)
            href = norm_url(a.get("href") or "")
            if title and is_http(href):
                pairs.append((title, href))
        if len(pairs) >= max_results:
            break

    pairs = dedup_keep_order(pairs)[:max_results]
    return "\n".join([f"{i+1}. {t} - {u}" for i, (t,u) in enumerate(pairs)]) or "네이버: 결과를 파싱하지 못했습니다."


# =========================
# 3) Human & Query 툴
# =========================
def ask_engine(prompt: str) -> str:
    """
    사용자에게 '네이버/구글' 엔진을 택일하도록 요구.
    필요하면 '웹/뉴스' 수직도 물어보도록 확장 가능.
    """
    print(f"\n[에이전트 질문] {prompt}")
    while True:
        choice = input("검색 엔진을 선택하세요 (네이버/구글): ").strip()
        if choice in ("네이버", "구글"):
            return choice
        print("'네이버' 또는 '구글'만 입력해주세요.")

# 1) 검색어 제공 함수: 인자 없음
def get_search_query() -> str:
    return SEARCH_QUERY

# 2) 비어있는 스키마 (인자 0개를 명시)
class _Empty(BaseModel):
    pass

HumanInput = Tool(
    name="HumanInput",
    func=ask_engine,
    description="네이버/구글 중 어떤 엔진으로 검색할지 사용자에게 1회 물어봅니다. 입력은 질문 문자열."
)

GetSearchQuery = StructuredTool.from_function(
    name="GetSearchQuery",
    func=get_search_query,
    args_schema=_Empty,  # 인자 없음
    description="미리 정의된 검색어를 가져옵니다(인자 불필요)."
)

GoogleSearchWeb = Tool(
    name="GoogleSearchWeb",
    func=lambda q: google_search(q, max_results=5, vertical="web", lang="ko"),
    description="구글(웹)에서 질의어를 검색해 상위 결과를 반환합니다. 입력은 '검색어 문자열'."
)
GoogleSearchNews = Tool(
    name="GoogleSearchNews",
    func=lambda q: google_search(q, max_results=5, vertical="news", lang="ko"),
    description="구글(뉴스)에서 질의어를 검색해 상위 결과를 반환합니다. 입력은 '검색어 문자열'."
)

NaverSearchWeb = Tool(
    name="NaverSearchWeb",
    func=lambda q: naver_search(q, max_results=5, vertical="web"),
    description="네이버(웹)에서 질의어를 검색해 상위 결과를 반환합니다. 입력은 '검색어 문자열'."
)
NaverSearchNews = Tool(
    name="NaverSearchNews",
    func=lambda q: naver_search(q, max_results=5, vertical="news"),
    description="네이버(뉴스)에서 질의어를 검색해 상위 결과를 반환합니다. 입력은 '검색어 문자열'."
)


# =========================
# 4) LLM & Agent
# =========================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

rules = SystemMessage(content=
    "한국어로 간결히 답하라. 다음 절차를 반드시 따른다:\n"
    "1) HumanInput 도구로 '네이버' 또는 '구글' 중 하나를 딱 한 번 물어본다.\n"
    "2) GetSearchQuery 도구로 검색어를 가져온다.\n"
    "3) 사용자가 선택한 엔진과 수직(웹 기본)을 기준으로 해당 도구만 호출한다.\n"
    "   - 네이버: NaverSearchWeb (또는 뉴스가 필요하면 NaverSearchNews)\n"
    "   - 구글:  GoogleSearchWeb (또는 뉴스가 필요하면 GoogleSearchNews)\n"
    "4) 상위 결과 5개를 목록으로 보여주고, 핵심 요약을 3줄 이내로 작성한다.\n"
    "5) 추정/지어내기 금지. 검색 결과가 부족하면 그 사실을 명시한다."
)

agent = initialize_agent(
    tools=[HumanInput, GetSearchQuery, GoogleSearchWeb, GoogleSearchNews, NaverSearchWeb, NaverSearchNews],
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={"system_message": rules},
    handle_parsing_errors=True,
    max_iterations=4,
    early_stopping_method="force",
    verbose=True
)


# =========================
# 5) 실행
# =========================
task = (
    "검색어를 조회하고 상위 결과 5개를 목록으로 보여준 뒤, 핵심 요약을 3줄 내로 작성하세요. "
    "반드시 먼저 HumanInput으로 엔진을 선택받고, GetSearchQuery로 검색어를 가져온 다음, "
    "선택된 엔진 전용 Search 도구를 호출하세요. (웹 결과를 기본으로 사용)"
)

final = agent.invoke({"input": task})
print("\n[최종 출력]\n", final["output"])
