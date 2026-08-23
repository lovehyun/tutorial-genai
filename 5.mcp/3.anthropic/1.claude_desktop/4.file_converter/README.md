# 3.anthropic/1.claude_desktop/4.file_converter — 문서 검색·변환 MCP 서버

Claude Desktop에 등록해 **내 컴퓨터의 문서를 검색·변환**하게 만드는 실전 예제. 강의 중 반복
보완된 4개의 독립적인 서버 버전이 남아있다 — 순서대로 번호가 이어지진 않지만(1→2→9→10),
지운 것 없이 전부 보존했다: 뒤로 갈수록 기능이 늘거나 다른 각도로 단순화한 변형이다.

## 파일

| 파일 | 서버 이름 | 도구 | 특징 |
|---|---|---|---|
| `file_converter_server.py` | `file-converter` | `find` | 기본형 — PDF/TXT 키워드 검색, DOCX→PDF 변환 옵션 |
| `file_converter2_server_errhandler.py` | `file-converter` | (검색+요약) | 1 + **예외 처리 강화**, 검색 결과에 summary/errors 포함, MuPDF 콘솔 오염 방지 |
| `file_converter9_server.py` | `doc-demo` | `convert_to_pdf`, `search_docs` | **의존성 최소화한 단순 데모 버전** — 변환과 검색을 별도 도구로 분리, 실패해도 안 멈춤 |
| `file_converter10_server.py` | `doc-search-agent` | `search_docs` | **가장 완성된 버전** — pdf/docx/pptx/xlsx/txt/md 지원, 정규식·대소문자·확장자 필터까지 파라미터화 |
| `test_fileconverter_client.py` | — | — | `file_converter_server.py`(`find` 도구)를 순수 MCP 클라이언트로 점검 |

## Claude Desktop 등록
아무 버전이나 `claude_desktop_config.json`에 등록해서 비교해볼 수 있다:
```json
{
  "mcpServers": {
    "file-converter": {
      "command": "python",
      "args": ["C:/절대경로/.../4.file_converter/file_converter10_server.py"]
    }
  }
}
```

## 관전 포인트
- **같은 문제(내 문서를 검색하게 하기)를 여러 번 다르게 풀었다** — `9`는 "최대한 단순하게",
  `10`은 "최대한 다양한 포맷을 지원하게"라는 서로 다른 방향의 시도다. 정답은 하나가 아니다.
- `2`에서 `os.environ["MUPDF_DISPLAY_ERRORS"] = "0"`로 PyMuPDF의 자체 콘솔 출력을 끄는 부분을
  눈여겨볼 것 — stdio 서버는 stdout이 JSON-RPC 채널이라, 서드파티 라이브러리가 몰래 stdout에
  뭔가 찍으면 그 자체로 프로토콜이 깨진다(`1.basic/README.md`의 "stdout에 print 금지" 원칙이
  내가 직접 쓴 코드에만 적용되는 게 아니라는 실전 사례).
- `10`의 `search_docs`는 파라미터가 많다(정규식·대소문자·확장자 필터·최대 결과 수) — 도구
  하나가 너무 많은 걸 하게 되면 모델이 인자를 고르기 어려워질 수 있다는 트레이드오프도 함께
  볼 것(`9`처럼 도구를 쪼개는 것과의 설계 선택 비교).

## 설치
```bash
pip install mcp pymupdf python-docx docx2pdf openpyxl
# docx/pptx → PDF 변환은 Windows + Word/PowerPoint 설치 시에만 실제 동작(없으면 자동 건너뜀)
```
