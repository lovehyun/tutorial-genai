# use-case: 분류 (티켓 라우팅 / 인텐트)

문의를 **고정 카테고리**(배송·환불·계정·결제·기타)로 분류하도록 파인튜닝.
**대량 분류**에서 작은 ft 모델이 큰 모델 프롬프팅보다 **싸고 빠르고 일관적** — 가장 흔한 실전 용도.

## 데이터 형태 (핵심)
`assistant` 응답이 **라벨 한 단어**뿐:
```json
{"messages":[
  {"role":"system","content":"...다음 중 하나로 분류... 라벨만 출력"},
  {"role":"user","content":"택배가 아직 안 왔어요"},
  {"role":"assistant","content":"배송"}
]}
```

## 실행
```bash
cd 1.openai/13.finetuning/usecase_classify
pip install openai python-dotenv          # .env 는 1.openai/.env (../../.env)
python 1.prepare_data.py                  # train.jsonl
python 2.create_job.py                    # ⚠️ 과금·시간 → ft 모델 ID
FT_MODEL=ft:... python 3.use_finetuned.py # 분류 + 베이스 비교
```
> 개념·주의·언제 쓰나는 상위 [`../README.md`](../README.md) 참고.
