# 9.files_api — Files API (beta)

파일을 한 번 업로드하고 `file_id`로 여러 번 재사용합니다. 같은 문서에 질문을 여러 번 할 때
매번 새로 업로드하지 않아도 됩니다.

## 파일

| 파일 | 내용 |
|------|------|
| `1.files_api.py` | 업로드 → `file_id` 재사용 |

## 실행 전 준비

같은 폴더에 `doc.pdf`를 두거나 코드의 경로를 바꾸세요. **PDF 파일은 저장소에 포함돼 있지
않습니다**(루트 `.gitignore`가 `*.pdf`를 제외) — 아무 PDF나 준비해서 넣으면 됩니다.

## 참고

`6.multimodal/2.pdf.py`와 비슷해 보이지만 다릅니다 — `2.pdf.py`는 매 호출마다 PDF를 통째로
같이 보내고, 여기서는 한 번 업로드해두고 `file_id`만 계속 재사용합니다(같은 문서를 여러 번
물어볼 때 더 효율적).

## 설치

```bash
pip install anthropic python-dotenv
```

API 키는 `3.anthropic/.env`에 설정합니다: `ANTHROPIC_API_KEY=sk-ant-...`
