# use-case: 구조화 추출 (텍스트 → 고정 JSON)

자유 형식 텍스트(주문/인보이스/이력서 등)에서 **항상 같은 키의 JSON**을 뽑도록 파인튜닝.
복잡한 포맷일수록 프롬프트보다 안정적이고, 후처리 파이프라인이 단순해진다.

## 데이터 형태 (핵심)
`assistant` 응답이 **고정 스키마 JSON 문자열**:
```json
{"messages":[
  {"role":"system","content":"...키는 item, quantity, price, date. JSON만 출력"},
  {"role":"user","content":"어제 사과 3개 4500원에 샀어요 (2026-06-01)"},
  {"role":"assistant","content":"{\"item\":\"사과\",\"quantity\":3,\"price\":4500,\"date\":\"2026-06-01\"}"}
]}
```

## 실행
```bash
cd 1.openai/13.finetuning/usecase_extract
pip install openai python-dotenv          # .env 는 1.openai/.env (../../.env)
python 1.prepare_data.py                  # train.jsonl
python 2.create_job.py                    # ⚠️ 과금·시간 → ft 모델 ID
FT_MODEL=ft:... python 3.use_finetuned.py # 추출 + JSON 파싱
```
> 더 강한 형식 보장은 `response_format`(json_schema)·`with_structured_output` 과 병행 가능.
> 개념은 상위 [`../README.md`](../README.md) 참고.
