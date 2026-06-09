"""
보안 헬퍼 — 공유 Bearer 토큰 인증 + SSRF 방어.

데모/수업용 최소 보호:
  · 토큰 : 쓰기 API(POST/PUT/DELETE)와 게이트웨이(/mcp)에 단일 공유 Bearer 토큰 요구.
           읽기 GET·페이지는 공개. MARKET_TOKEN 미설정 시 인증 비활성(로컬 개발 편의).
  · SSRF : 등록 endpoint가 사설/내부/메타데이터 IP로 향하면 거부.
           (프록시는 등록자가 준 URL에 '우리 서버가' 접속하므로 SSRF에 노출됨)

환경변수
  MARKET_TOKEN              공유 토큰. 비우면 인증 끔.
  ALLOW_PRIVATE_ENDPOINTS   '1' 이면 사설/루프백 endpoint 허용(로컬 올인원 데모용).
"""

import os
import socket
import secrets
import ipaddress
from urllib.parse import urlparse

TOKEN = os.getenv("MARKET_TOKEN", "").strip()
ALLOW_PRIVATE = os.getenv("ALLOW_PRIVATE_ENDPOINTS", "0") == "1"
# '1' 이면 UI 🔑 버튼이 토큰을 직접 보여준다(데모 편의). 켜면 쓰기는 사실상 공개임에 주의.
SHOW_TOKEN = os.getenv("SHOW_TOKEN_IN_UI", "0") == "1"


def token_hint() -> str | None:
    """UI 노출이 허용된 경우에만 토큰을 돌려준다. 아니면 None."""
    return TOKEN if (SHOW_TOKEN and TOKEN) else None


def auth_enabled() -> bool:
    return bool(TOKEN)


def token_ok(header_value: str | None) -> bool:
    """Authorization 헤더('Bearer xxx' 또는 'xxx')가 유효한지. 미설정이면 항상 통과."""
    if not TOKEN:
        return True
    if not header_value:
        return False
    v = header_value.strip()
    if v.lower().startswith("bearer "):
        v = v[7:].strip()
    return secrets.compare_digest(v, TOKEN)        # 타이밍 공격 방지 상수시간 비교


def check_endpoint(url: str) -> str | None:
    """SSRF 방어. 안전하면 None, 위험하면 사유(문자열) 반환."""
    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        return "scheme 은 http/https 만 허용"
    host = p.hostname
    if not host:
        return "host 가 없는 URL"
    if ALLOW_PRIVATE:                              # 로컬 데모: 사설 허용
        return None
    port = p.port or (443 if p.scheme == "https" else 80)
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except Exception as e:
        return f"호스트 DNS 해석 실패: {e}"
    for info in infos:                             # 호스트가 가리키는 모든 IP 검사
        ip = ipaddress.ip_address(info[4][0])
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            return f"사설/내부/메타데이터 IP 로 향하는 endpoint 는 금지: {ip}"
    return None
