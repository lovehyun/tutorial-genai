# simple_net_server_http.py
# 기능: ping, 주요 포트(22,80,443,3000,5000,8000) 상태, 80/5000 페이지 내용 가져오기
# 주의: stdout에 print() 금지. 로깅은 stderr(프로토콜 분리).
from mcp.server.fastmcp import FastMCP
import asyncio, platform, socket, logging
from typing import Dict, List
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

mcp = FastMCP("simple-net-remote")  # 커넥터에 표시될 서버 이름

COMMON_PORTS: List[int] = [22, 80, 443, 3000, 5000, 8000]

def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))

@mcp.tool()
async def ping_host(host: str, count: int = 3, timeout_sec: int = 3) -> str:
    """
    지정한 host 로 ping 결과 원문을 반환합니다.
    - count: 1~5
    - timeout_sec: 1~5 (패킷 당 타임아웃)
    """
    host = (host or "").strip()
    if not host:
        raise ValueError("host 를 입력하세요.")
    count = _clamp(count, 1, 5)
    timeout_sec = _clamp(timeout_sec, 1, 5)

    if platform.system() == "Windows":
        cmd = ["ping", "-n", str(count), "-w", str(timeout_sec * 1000), host]
    else:
        # -c: count, -W: timeout(sec)
        cmd = ["ping", "-c", str(count), "-W", str(timeout_sec), host]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate()
    text = (out or b"").decode("utf-8", "ignore")
    if not text:
        text = (err or b"").decode("utf-8", "ignore")
    return text

async def _check_one_port(host: str, port: int, timeout_sec: float) -> str:
    try:
        # blocking 콜은 스레드로 돌려 타임아웃 관리
        await asyncio.wait_for(
            asyncio.to_thread(socket.create_connection, (host, port), timeout=timeout_sec),
            timeout=timeout_sec + 0.5,
        )
        return "open"
    except Exception:
        return "closed"

@mcp.tool()
async def check_common_ports(host: str, timeout_sec: int = 1) -> Dict[str, str]:
    """
    host 의 주요 포트(22,80,443,3000,5000,8000)를 빠르게 확인합니다.
    반환: {"22": "open/closed", ...}
    """
    host = (host or "").strip()
    if not host:
        raise ValueError("host 를 입력하세요.")
    timeout_sec = _clamp(timeout_sec, 1, 3)

    tasks = [asyncio.create_task(_check_one_port(host, p, timeout_sec)) for p in COMMON_PORTS]
    results = await asyncio.gather(*tasks)
    return {str(p): status for p, status in zip(COMMON_PORTS, results)}

@mcp.tool()
async def fetch_page(host: str, port: int = 80, path: str = "/", max_bytes: int = 100_000) -> dict:
    """
    간단한 페이지 GET(HTTP) 결과를 반환합니다. (포트 80 또는 5000만 허용)
    - path 는 기본 "/" (간단히 사용)
    - max_bytes 만큼만 본문을 읽어 반환(기본 100KB)
    """
    host = (host or "").strip()
    if not host:
        raise ValueError("host 를 입력하세요.")
    if port not in (80, 5000):
        raise ValueError("이 데모는 port 80 또는 5000 만 허용합니다.")
    path = path or "/"
    if not path.startswith("/"):
        path = "/" + path
    url = f"http://{host}:{port}{quote(path)}"

    req = Request(url, headers={"User-Agent": "simple-net-mcp/1.0", "Accept": "*/*"})

    try:
        # blocking I/O -> thread
        def _do_request():
            with urlopen(req, timeout=5) as resp:
                status = resp.getcode()
                headers = dict(resp.getheaders())
                body = resp.read(max_bytes)  # 안전을 위해 최대 바이트 제한
                # 텍스트로 추정되면 디코딩 시도
                try:
                    text = body.decode("utf-8", errors="replace")
                except Exception:
                    text = None
                return status, headers, body, text

        status, headers, body, text = await asyncio.to_thread(_do_request)
        return {
            "url": url,
            "status_code": status,
            "headers": headers,
            "body_preview_len": len(body),
            "text_preview": text if text is not None else "(binary content)",
            "truncated": len(body) >= max_bytes,
        }
    except HTTPError as e:
        return {"url": url, "error": f"HTTP {e.code}", "reason": str(e)}
    except URLError as e:
        return {"url": url, "error": "URL error", "reason": str(e)}
    except Exception as e:
        return {"url": url, "error": "Unexpected error", "reason": str(e)}

if __name__ == "__main__":
    # 절대 stdout 에 print() 금지. logging 은 stderr 로 출력됨.
    logging.basicConfig(level=logging.INFO)
    # HTTP(스트리머블) 전송. 엔드포인트 path="/mcp"
    mcp.run(transport="http", host="0.0.0.0", port=8888)  # 기본 path는 /mcp (문서 및 예시 기준)
    # mcp.run(transport="http", host="0.0.0.0", port=8888, path="/api/mcp")  # 경로 커스터마이징
