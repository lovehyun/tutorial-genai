# 4.langchain/3.tools_safety — 에이전트 도구 범위 제한(안전 가드레일)

에이전트가 **정해진 도구만** 쓰고, 범위를 벗어난 요청은 깔끔히 거절하도록 프롬프트로 가드레일을 건다.

## 파일
- `server.py` — hello, add, now
- `1.client.py` — 기본: 도구는 동작하나 범위 밖 요청에 예측 불가 동작 가능
- `2.client2_restrict.py` — 엄격 프롬프트 + `early_stopping` → 범위 밖이면 "죄송합니다…" 고정 응답

## 실행
```bash
cd 8.mcp/4.langchain/3.tools_safety
pip install mcp langchain langchain-openai langchain-core python-dotenv
# .env 에 OPENAI_API_KEY

python 1.client.py
python 2.client2_restrict.py
```
> `server.py` stdio **자동 실행**.

## 관전 포인트
- **프롬프트 가드레일**: 같은 도구라도 시스템 프롬프트로 '사용 가능 도구 화이트리스트'를 강제.
- `1`(유연·불확실) vs `2`(엄격·예측가능) 비교 → 프로덕션은 `2` 형태.
- 도구 자체가 아니라 **에이전트의 행동 범위**를 제어한다는 점(서버는 동일).

## 추천 순서
`1.client` → `2.client2_restrict`
