# 3.server_stock.py — 실제 외부 API 를 호출하는 원격 MCP 서버 (yfinance 주가 조회)
#
# ── 1.server_simple.py 와의 차이 ────────────────────────────────
#   1.server_simple : add / word_count — 계산만 하는 '장난감' 도구. 전송 방식 학습이 목적.
#   3.server_stock  : yfinance 로 실제 시장 데이터를 가져온다.
#                     LLM 이 절대 알 수 없는 정보(실시간 시세)를 도구가 채워주는,
#                     MCP 를 쓰는 진짜 이유에 해당하는 형태.
#
# ── 여기서도 서버에 LangChain 은 없다 ───────────────────────────
#   도구가 하는 일이 '외부 API 호출' 이든 '계산' 이든, 서버는 그냥 함수를 실행할 뿐이다.
#   LLM 을 부르는 쪽은 클라이언트다. (서버에 LangChain 이 정당해지는 경우는
#   도구 자체가 LLM 파이프라인일 때 — 예: RAG 검색/요약 체인 — 뿐이다.)
#
# ── 도구 설계 메모 ──────────────────────────────────────────────
#   - 에러를 raise 하지 않고 '설명 문자열' 로 돌려준다.
#     에이전트가 그 문장을 읽고 티커를 고쳐 재시도할 수 있기 때문 (예외는 그냥 흐름이 끊긴다).
#   - docstring 이 곧 LLM 이 읽는 도구 설명서다. 한국 주식 티커 형식 같은 힌트를 여기 적어둔다.
#
# 준비:  pip install mcp yfinance
# 실행:  python 3.server_stock.py      → http://127.0.0.1:8001/mcp

from mcp.server.fastmcp import FastMCP

try:
    import yfinance as yf
except ImportError:  # 서버 시작 시점에 바로 알려준다
    raise SystemExit("yfinance 가 없습니다.  pip install yfinance  후 다시 실행하세요.")

# 1.server_simple.py(8000) 와 동시에 띄울 수 있도록 포트를 8001 로 분리
mcp = FastMCP("StockServer", host="127.0.0.1", port=8001)

# yfinance 가 받는 기간 문자열 — LLM 이 엉뚱한 값을 넣는 걸 막기 위해 화이트리스트로 검증
VALID_PERIODS = ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")


def _fmt(value: float) -> str:
    """소수 둘째 자리까지, 천 단위 구분 기호를 넣어 포맷한다."""
    return f"{value:,.2f}"


@mcp.tool()
def get_stock_price(ticker: str) -> str:
    """
    주식/지수의 최근 종가와 전일 대비 등락률을 조회한다.

    Args:
        ticker: 종목 티커. 미국 주식은 'AAPL', 'MSFT' 처럼,
                한국 주식은 '005930.KS'(삼성전자), '035720.KS'(카카오) 처럼 거래소 접미사를 붙인다.

    Returns:
        현재가 · 통화 · 전일 대비 등락률을 담은 한 줄 요약
    """
    symbol = ticker.strip().upper()

    try:
        df = yf.Ticker(symbol).history(period="5d")
    except Exception as e:
        return f"'{symbol}' 조회 중 오류: {type(e).__name__}: {e}"

    if df.empty:
        return (f"'{symbol}' 시세를 찾지 못했습니다. 티커를 확인하세요 "
                f"(한국 주식은 '005930.KS' 형식이 필요합니다).")

    last = float(df["Close"].iloc[-1])
    date = df.index[-1].strftime("%Y-%m-%d")

    # 통화 단위는 부가 정보라, 못 가져와도 조회 자체는 성공시킨다
    try:
        currency = yf.Ticker(symbol).fast_info.get("currency") or ""
    except Exception:
        currency = ""

    line = f"{symbol} 종가({date}): {_fmt(last)} {currency}".rstrip()

    if len(df) >= 2:
        prev = float(df["Close"].iloc[-2])
        diff = last - prev
        pct = (diff / prev * 100) if prev else 0.0
        sign = "+" if diff >= 0 else ""
        line += f" | 전일 대비 {sign}{_fmt(diff)} ({sign}{pct:.2f}%)"

    return line


@mcp.tool()
def get_stock_history(ticker: str, period: str = "1mo") -> str:
    """
    일정 기간의 주가 흐름을 요약한다(시작가·종가·최고·최저·평균·기간 변동률).

    Args:
        ticker: 종목 티커 (예: 'AAPL', '005930.KS')
        period: 조회 기간. 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max 중 하나. 기본값 1mo

    Returns:
        기간 요약 통계 문자열
    """
    symbol = ticker.strip().upper()
    period = period.strip().lower()

    if period not in VALID_PERIODS:
        return f"'{period}' 는 지원하지 않는 기간입니다. 다음 중 하나를 쓰세요: {', '.join(VALID_PERIODS)}"

    try:
        df = yf.Ticker(symbol).history(period=period)
    except Exception as e:
        return f"'{symbol}' 조회 중 오류: {type(e).__name__}: {e}"

    if df.empty:
        return f"'{symbol}' 의 {period} 기간 데이터를 찾지 못했습니다. 티커를 확인하세요."

    close = df["Close"]
    first, last = float(close.iloc[0]), float(close.iloc[-1])
    pct = ((last - first) / first * 100) if first else 0.0
    sign = "+" if pct >= 0 else ""

    return (
        f"{symbol} 최근 {period} ({df.index[0]:%Y-%m-%d} ~ {df.index[-1]:%Y-%m-%d}, {len(df)}거래일)\n"
        f"  시작가: {_fmt(first)}\n"
        f"  종가:   {_fmt(last)}\n"
        f"  최고가: {_fmt(float(close.max()))}\n"
        f"  최저가: {_fmt(float(close.min()))}\n"
        f"  평균:   {_fmt(float(close.mean()))}\n"
        f"  기간 변동률: {sign}{pct:.2f}%"
    )


@mcp.tool()
def get_company_info(ticker: str) -> str:
    """
    종목의 기업 개요를 조회한다(회사명·거래소·섹터·산업·시가총액).

    Args:
        ticker: 종목 티커 (예: 'AAPL', '005930.KS')

    Returns:
        기업 개요 요약 문자열
    """
    symbol = ticker.strip().upper()

    try:
        info = yf.Ticker(symbol).info or {}
    except Exception as e:
        return f"'{symbol}' 기업 정보 조회 실패: {type(e).__name__}: {e}"

    # yfinance 의 .info 는 티커가 틀려도 예외 대신 빈/부실한 dict 를 주는 경우가 있다
    name = info.get("longName") or info.get("shortName")
    if not name:
        return f"'{symbol}' 기업 정보를 찾지 못했습니다. 티커를 확인하세요."

    lines = [f"{name} ({symbol})"]
    if info.get("exchange"):
        lines.append(f"  거래소: {info['exchange']}")
    if info.get("sector"):
        lines.append(f"  섹터:   {info['sector']}")
    if info.get("industry"):
        lines.append(f"  산업:   {info['industry']}")

    cap, cur = info.get("marketCap"), info.get("currency", "")
    if cap:
        lines.append(f"  시가총액: {cap:,} {cur}".rstrip())

    return "\n".join(lines)


if __name__ == "__main__":
    print("=" * 60)
    print("StockServer MCP 서버 (streamable-http)")
    print("  주소: http://127.0.0.1:8001/mcp")
    print("  도구: get_stock_price / get_stock_history / get_company_info")
    print("  종료: Ctrl+C")
    print("=" * 60)

    mcp.run(transport="streamable-http")


# ── 참고 ────────────────────────────────────────────────────────
#   - yfinance 는 야후 파이낸스를 비공식 스크래핑한다. 무료·키 불필요지만
#     호출이 잦으면 일시적으로 막힐 수 있고, 시세는 실시간이 아니라 지연 데이터다.
#     (학습·데모용. 실제 매매 판단에 쓰지 말 것)
#   - 같은 서버를 Claude Desktop 에 붙이려면 stdio 로 바꾸기만 하면 된다:
#       mcp.run()   ← transport 인자 없이. 도구 코드는 손대지 않는다.
