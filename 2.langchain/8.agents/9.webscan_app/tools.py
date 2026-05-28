"""
서버 점검 도구 모음 — @tool 데코레이터로 도구화한 시스템 진단 함수들.
이 예제: 옛 `Tool(query: str)` 패턴 대신 현행 `@tool` + 타입 힌트 + Pydantic args.

도구 목록:
  - check_port            : 임의 host:port TCP 연결 확인
  - check_ssl_cert        : HTTPS 인증서 만료일 확인
  - check_website         : URL 의 HTTP 응답 / 응답시간 확인
  - check_system_resources: CPU / 메모리 / 디스크 사용률
  - check_processes       : 주요 서비스 프로세스 실행 여부
  - check_network         : 외부 호스트 연결성 확인

옛 scanapp.py 의 415줄을 ~120줄로 축소 (initialize_agent → create_react_agent + @tool).
"""

import socket
import ssl
import datetime
from typing import Literal

import psutil
import requests
from langchain_core.tools import tool


# ─── 1) 포트 체크 (범용) ────────────────────────────────────
@tool
def check_port(host: str, port: int, service_name: str = "Service") -> str:
    """TCP 포트 연결 가능 여부를 확인한다.
    예: check_port('127.0.0.1', 22, 'SSH'), check_port('db.example.com', 5432, 'PostgreSQL')
    """
    try:
        with socket.create_connection((host, port), timeout=3):
            return f"✅ {service_name} ({host}:{port}) 연결 성공"
    except socket.timeout:
        return f"❌ {service_name} ({host}:{port}) 타임아웃"
    except ConnectionRefusedError:
        return f"❌ {service_name} ({host}:{port}) 연결 거부"
    except Exception as e:
        return f"❌ {service_name} ({host}:{port}) 실패: {e}"


# ─── 2) SSL 인증서 ──────────────────────────────────────────
@tool
def check_ssl_cert(host: str, port: int = 443) -> str:
    """도메인의 HTTPS 인증서 만료까지 남은 일수를 반환한다."""
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
            s.connect((host, port))
            cert = s.getpeercert()
            expire = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
            days_left = (expire - datetime.datetime.now()).days
            mark = "✅" if days_left > 30 else "⚠️" if days_left > 7 else "❌"
            return f"{mark} {host} SSL: 만료 {cert['notAfter']} ({days_left}일 남음)"
    except Exception as e:
        return f"❌ SSL 점검 실패 ({host}): {e}"


# ─── 3) 웹사이트 상태 ───────────────────────────────────────
@tool
def check_website(url: str) -> str:
    """URL 의 HTTP 응답 코드와 응답시간을 확인한다."""
    try:
        r = requests.get(url, timeout=10)
        elapsed = r.elapsed.total_seconds()
        mark = "✅" if r.status_code == 200 else "⚠️"
        return f"{mark} {url} → HTTP {r.status_code} (응답 {elapsed:.2f}s)"
    except Exception as e:
        return f"❌ {url} 실패: {e}"


# ─── 4) 시스템 리소스 ───────────────────────────────────────
@tool
def check_system_resources() -> str:
    """현재 서버의 CPU / 메모리 / 디스크 사용률을 반환한다."""
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    lines = [
        f"CPU 사용률: {cpu}%",
        f"메모리: {mem.percent}% ({mem.used // (1024**3)}/{mem.total // (1024**3)} GB)",
        f"디스크: {disk.percent}% ({disk.used // (1024**3)}/{disk.total // (1024**3)} GB)",
    ]
    warnings = [
        ("⚠️ CPU 사용률 ↑",      cpu > 80),
        ("⚠️ 메모리 사용률 ↑",   mem.percent > 80),
        ("⚠️ 디스크 사용률 ↑",   disk.percent > 80),
    ]
    msg = "\n".join(lines)
    triggered = [w for w, hit in warnings if hit]
    if triggered:
        msg += "\n" + "\n".join(triggered)
    return msg


# ─── 5) 프로세스 ────────────────────────────────────────────
@tool
def check_processes(
    names: list[str] = ["nginx", "apache2", "mysql", "postgres", "redis", "docker"],
) -> str:
    """주어진 이름들의 프로세스가 실행 중인지 확인한다."""
    running_set = {p.name().lower() for p in psutil.process_iter()}
    running, missing = [], []
    for n in names:
        if any(n in r for r in running_set):
            running.append(n)
        else:
            missing.append(n)
    parts = []
    if running: parts.append(f"✅ 실행 중: {', '.join(running)}")
    if missing: parts.append(f"❌ 중지: {', '.join(missing)}")
    return "\n".join(parts) or "(없음)"


# ─── 6) 외부 네트워크 ───────────────────────────────────────
@tool
def check_network() -> str:
    """외부 호스트 (google.com, cloudflare.com, 8.8.8.8) 연결성을 확인한다."""
    targets = [("google.com", 80), ("8.8.8.8", 53), ("cloudflare.com", 80)]
    results = []
    for host, port in targets:
        try:
            with socket.create_connection((host, port), timeout=3):
                results.append(f"✅ {host}:{port}")
        except Exception:
            results.append(f"❌ {host}:{port}")
    return "\n".join(results)


ALL_TOOLS = [
    check_port,
    check_ssl_cert,
    check_website,
    check_system_resources,
    check_processes,
    check_network,
]
