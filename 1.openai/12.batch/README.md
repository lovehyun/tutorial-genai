# 12.batch — Batch API (대량·저비용 비동기 처리)

즉시 응답 대신 **대량 작업을 절반 비용**으로 처리하는 API (완료 기한 최대 24h).
대량 분류·요약·번역·**임베딩(RAG 인덱싱)** 처럼 급하지 않은 작업에 적합하다.

## 흐름 (5단계)
```
① 요청들을 JSONL 로 작성 (한 줄 = 한 요청, custom_id 로 식별)
② files.create(purpose='batch') 로 업로드
③ batches.create(input_file_id, endpoint, completion_window='24h')
④ batches.retrieve 로 상태 폴링 (validating→in_progress→completed)
⑤ files.content(output_file_id) 로 결과 JSONL 다운로드 (custom_id 로 매칭)
```

## 파일 (기본 → 실용)
| 파일 | 내용 |
|------|------|
| `1.batch_basic.py` | chat 요청 여러 개를 배치로 제출 → 폴링 → 결과 |
| `2.batch_embeddings.py` | **실용** — 대량 임베딩(RAG 인덱싱)을 50% 비용으로. endpoint 만 `/v1/embeddings` |

## 실행
```bash
cd 1.openai/12.batch
pip install openai python-dotenv
# 1.openai/.env 에 OPENAI_API_KEY

python 1.batch_basic.py        # batch_input.jsonl 생성 → 제출 → 결과
python 2.batch_embeddings.py
```
> ⚠️ 배치는 **즉시 완료가 아닙니다** — 적은 양도 수 분 걸릴 수 있고, 최대 24h. 스크립트는 15초 간격 폴링.
> 생성되는 `*.jsonl`(입력/결과)은 `.gitignore` 처리됨.

## 언제 쓰나
- ✅ 대량 + 급하지 않음 + 비용 절감 (오프라인 인덱싱, 야간 배치 분류)
- ❌ 실시간 응답이 필요한 챗봇/UI → 일반 `chat.completions` 사용
