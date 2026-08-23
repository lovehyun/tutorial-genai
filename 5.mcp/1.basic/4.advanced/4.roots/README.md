# 4.roots — 클라이언트가 서버에 '작업 허용 경로' 알려주기

**Roots** 는 클라이언트가 서버에 "너는 이 폴더들 안에서만 일해" 라고 알려주는 목록이다
(예: IDE 에 열린 워크스페이스 폴더). 서버는 `ctx.session.list_roots()` 로 물어본다.

```
서버 ── roots/list ──▶ 클라이언트
서버 ◀── [file:///workspace, ...] ── 클라이언트   ← list_roots_callback 이 응답
```

filesystem 류 서버가 **허용 범위 밖 접근을 거부**할 때 쓴다(화이트리스트).

## 파일
| 파일 | 무엇을 |
|---|---|
| `server.py` | `show_roots`(목록 조회) + `is_allowed`(경로가 root 하위인지 검사) |
| `client.py` | `ClientSession(..., list_roots_callback=...)` 로 root 2개 제공 |

## 실행
```bash
pip install mcp
cd 5.mcp/1.basic/4.advanced/4.roots
python client.py
```

## 관전 포인트
- `Root.uri` 는 **`file://` 로 시작해야 한다**(현행 스펙 제약, `FileUrl` 로 검증).
- roots 는 sampling/elicit 과 **방향은 같지만(서버→클라 요청) 성격이 다르다** — LLM 도 사람도 아닌 **컨텍스트(설정)** 를 받아오는 것.
- 서버는 이 목록을 접근통제에 활용할 수 있다 → `is_allowed` 가 그 예시(범위 밖 `/etc/passwd` 차단).
- 실제 filesystem 서버 연동은 [`../../../9.projects/1.local/1.filesystem/`](../../../9.projects/1.local/1.filesystem/) 과 묶어 생각하면 좋다.

## 다음
- 상위 [`../README.md`](../README.md) 로 돌아가 4개 심화 패턴 정리 보기
- 원격 서버 **인증**: [`../../../9.projects/2.remote/2.oauth/`](../../../9.projects/2.remote/2.oauth/)
