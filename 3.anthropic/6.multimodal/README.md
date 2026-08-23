# 6.multimodal — 이미지·문서 입력

Claude에 텍스트가 아닌 입력(이미지, PDF)을 넣어 분석시킵니다. **입력만** 다룹니다 —
Anthropic은 OpenAI(DALL-E/gpt-image)처럼 이미지를 *생성*하는 API를 제공하지 않습니다.

## 순서

| 파일 | 내용 |
|------|------|
| `1.vision.py` | 이미지 입력(비전) — 로컬 파일(base64, 권장) 또는 URL |
| `2.pdf.py` | PDF/문서 입력 — `document` 블록으로 통째로 넣어 질문 |
| `3.citations.py` | Citations — 답변의 각 주장에 원문 근거(정확한 인용문+위치)를 자동으로 붙임 |

## 실행 전 준비

- `1.vision.py`: 같은 폴더에 `image.png`를 두거나 코드의 경로를 바꾸세요.
- `2.pdf.py`: 같은 폴더에 `doc.pdf`를 두거나 경로를 바꾸세요. **PDF 파일은 저장소에 포함돼 있지
  않습니다**(루트 `.gitignore`가 `*.pdf`를 제외). 아무 PDF나 준비해서 폴더에 넣고 실행하세요.
- `3.citations.py`: 별도 파일 불필요 — 문서 내용이 코드에 바로 들어있어 그대로 실행됩니다.

## Citations — 프롬프트로 "출처 알려줘"라고 하는 것과 뭐가 다른가

| | 프롬프트로 요청 | Citations API (`3.citations.py`) |
|---|---|---|
| 인용문 출처 | 모델이 직접 타이핑(환각 가능) | 원문에서 그대로 추출(항상 정확) |
| 출력 토큰 | 인용문만큼 소비 | `cited_text`는 출력 토큰 미소비 |
| 위치 정보 | 없음(텍스트로 설명해야 함) | 문자 인덱스(텍스트) / 페이지 번호(PDF) 구조화 제공 |

`5.prompt_caching`과 함께 쓸 수 있습니다(문서 블록에 `cache_control` 추가) — 문서 청킹이
일정하면 캐시도 함께 재사용됩니다.

## 설치

```bash
pip install anthropic python-dotenv
```

API 키는 `3.anthropic/.env`에 설정합니다: `ANTHROPIC_API_KEY=sk-ant-...`
