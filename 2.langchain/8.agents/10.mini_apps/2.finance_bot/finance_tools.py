"""
금융 조회 도구 모음 — 뉴스 / 기업정보 / 환율 / 주가.
모두 @tool 로 정의되어 create_agent 에 그대로 꽂힌다 (2.custom_tools 패턴).

  - 키 불필요 : 환율(open.er-api.com), 주가(yfinance)
  - 키 필요   : 뉴스(NAVER_CLIENT_ID/SECRET), 기업정보(SERPER_API_KEY)
                → 키 없으면 도구가 '안내 메시지' 를 반환 (앱은 계속 동작)

  ※ pip install requests yfinance
"""

import os
import re
import requests
from langchain_core.tools import tool


@tool
def get_news(query: str) -> str:
    """네이버 뉴스에서 키워드로 최신 기사 제목/링크를 검색한다."""
    cid, secret = os.getenv("NAVER_CLIENT_ID"), os.getenv("NAVER_CLIENT_SECRET")
    if not (cid and secret):
        return "네이버 뉴스 키(NAVER_CLIENT_ID/SECRET) 미설정 — 뉴스 검색 불가"
    r = requests.get(
        "https://openapi.naver.com/v1/search/news.json",
        params={"query": query, "display": 5, "sort": "date"},
        headers={"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": secret},
        timeout=10,
    )
    items = r.json().get("items", [])
    if not items:
        return f"'{query}' 관련 뉴스 없음"
    return "\n".join(f"- {re.sub(r'<[^>]+>', '', it['title'])} ({it['link']})" for it in items)


@tool
def get_company_info(company: str) -> str:
    """구글 검색(Serper)으로 기업 개요/최근 정보를 조회한다."""
    key = os.getenv("SERPER_API_KEY")
    if not key:
        return "SERPER_API_KEY 미설정 — 기업 정보 검색 불가"
    r = requests.post(
        "https://google.serper.dev/search",
        json={"q": f"{company} 기업 정보", "gl": "kr", "hl": "ko"},
        headers={"X-API-KEY": key, "Content-Type": "application/json"},
        timeout=10,
    )
    data = r.json()
    parts = []
    kg = data.get("knowledgeGraph")
    if kg:
        parts.append(f"{kg.get('title', '')} — {kg.get('description', '')}")
    for o in data.get("organic", [])[:3]:
        parts.append(f"- {o.get('title')}: {o.get('snippet', '')}")
    return "\n".join(parts) or "정보 없음"


@tool
def get_exchange_rate(base: str = "USD", target: str = "KRW") -> str:
    """환율을 조회한다. 예: base=USD, target=KRW → 1달러 = ?원. (무료 API, 키 불필요)"""
    r = requests.get(f"https://open.er-api.com/v6/latest/{base.upper()}", timeout=10)
    rate = r.json().get("rates", {}).get(target.upper())
    if rate is None:
        return f"{base}->{target} 환율 조회 실패"
    return f"1 {base.upper()} = {rate} {target.upper()}"


@tool
def get_stock_price(ticker: str) -> str:
    """yfinance 로 주식/지수 현재가를 조회한다. 예: 'AAPL', '005930.KS'(삼성전자)."""
    import yfinance as yf

    data = yf.Ticker(ticker).history(period="1d")
    if data.empty:
        return f"'{ticker}' 시세 조회 실패 (티커 확인 — 한국 주식은 '005930.KS' 형식)"
    return f"{ticker} 현재가: {round(float(data['Close'].iloc[-1]), 2)}"


TOOLS = [get_news, get_company_info, get_exchange_rate, get_stock_price]
