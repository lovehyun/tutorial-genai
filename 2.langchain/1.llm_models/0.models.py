# https://platform.openai.com/docs/api-reference/models
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path='../.env')
client = OpenAI(
    api_key = os.getenv('OPENAI_API_KEY'),  # this is also the default, it can be omitted
)

model_list = client.models.list()
for m in model_list:
    print(m.id)

# ------------------------------------------------------------
# 모델 한눈에 보기 (자세한 설명은 README.md 참고)
# ------------------------------------------------------------
# | 모델 이름                   | Chat (/v1/chat/completions) | Legacy Completion (/v1/completions) | 비고                                   |
# | -------------------------- | --------------------------- | ----------------------------------- | -------------------------------------- |
# | gpt-4o                     | ✅                          | ❌                                  | 최신 멀티모달 Chat Model               |
# | gpt-4o-mini                | ✅                          | ❌                                  | 경량 Chat Model                        |
# | gpt-4                      | ✅                          | ❌                                  | Chat Model                             |
# | gpt-3.5-turbo              | ✅                          | ❌                                  | Chat Model                             |
# | gpt-3.5-turbo-instruct     | ❌                          | ✅                                  | 현재 유일하게 살아있는 Instruct 모델   |
# | text-davinci-003           | ❌                          | (deprecated)                        | 2024년 1월 사용 중단                   |
#
# 핵심 요약:
#   - 새 프로젝트는 거의 다 Chat Completions API ( /v1/chat/completions ) 사용
#   - Legacy Completions API ( /v1/completions )는 gpt-3.5-turbo-instruct 전용으로 거의 남음
#   - "Instruct" = instruction-tuned 결과물을 가리키는 말 (학습 대상 모델 아님)
#   - 자세한 비교, 헷갈리기 쉬운 부분 정리, 파인튜닝과의 관계는 README.md 참조
#
# ============================================================
# ⚠️ 자주 헷갈리는 포인트들 (반드시 짚고 가기)
# ============================================================
#
# [혼동 1] "Completions"는 두 개의 다른 API 이름이다
# ------------------------------------------------------------
# OpenAI에는 이름에 "completions"가 들어가는 엔드포인트가 두 개 있습니다.
# 같은 것으로 오해하면 설명이 완전히 꼬입니다.
#
#  (A) Chat Completions API   →  POST /v1/chat/completions
#      - **현역/표준 API.** 새 프로젝트는 거의 다 이걸 사용.
#      - 입력: messages=[{"role":..., "content":...}, ...]
#      - 지원 모델: gpt-4o, gpt-4o-mini, gpt-4, gpt-3.5-turbo, o1 시리즈 등 거의 전부
#      - tool calling, vision, structured output, JSON mode 등 최신 기능 전부 여기에 있음
#      - LangChain 래퍼: ChatOpenAI
#
#  (B) (Legacy) Completions API  →  POST /v1/completions
#      - 옛날 방식. OpenAI가 공식적으로 "legacy"로 분류.
#      - 입력: prompt="..."  (단일 문자열)
#      - 현재 지원되는 모델은 사실상 gpt-3.5-turbo-instruct **하나뿐**
#      - gpt-4o, gpt-4o-mini 등 신형 모델은 이 엔드포인트로 호출 **불가**
#      - LangChain 래퍼: OpenAI (langchain_openai.OpenAI)
#
# 헷갈렸던 질문들에 다시 답하면:
#   Q. "Completions API 많이 쓰지 않나요?"
#      → 맞습니다. 단, 그건 (A) Chat Completions 얘기입니다.
#   Q. "gpt-4o-mini도 completions에서 쓰지 않나요?"
#      → 맞습니다. (A)에서는 씁니다. (B) 레거시에서는 못 씁니다.
#   Q. "Completion 모델 거의 안 쓴다는 건?"
#      → (B) 레거시 엔드포인트와 거기에 묶인 Instruct 모델 얘기입니다.
#
# [혼동 2] "Instruct 모델 = 파인튜닝용 베이스 모델"이 아니다
# ------------------------------------------------------------
# - "Instruct"는 instruction-tuning(지시를 따르도록 RLHF/SFT로 후처리)된
#   **결과물**을 가리키는 말입니다. 학습의 산출물이지, "학습 대상이 되는 베이스"가 아님.
#   ChatGPT 계열(gpt-3.5-turbo, gpt-4o 등)도 모두 instruction-tuned 상태입니다.
#
# - "옛날엔 completion 모델로 파인튜닝했었지" 하는 기억이 남는 이유:
#     · 초창기 OpenAI 파인튜닝은 davinci/curie/babbage/ada 같은
#       **base completion 모델**을 대상으로 했기 때문.
#     · 그래서 "completion 모델 = 파인튜닝 대상"이라는 인상이 굳어진 것.
#
# - 현재(2026)의 파인튜닝:
#     · 대상이 **Chat 모델**로 이동 → gpt-4o-mini, gpt-3.5-turbo 등을 파인튜닝
#     · 엔드포인트: /v1/fine_tuning/jobs  (Chat 메시지 형식의 jsonl을 업로드)
#     · 반대로 gpt-3.5-turbo-instruct(legacy)는 **파인튜닝 자체가 불가능**
#
# ============================================================
# 결론 정리 (다시 깔끔하게)
# ============================================================
#  - Chat Completions API ( /v1/chat/completions )  → ✅ 매우 활발히 사용 (표준)
#  - Legacy Completions API ( /v1/completions )     → ⚠️ 거의 안 씀, 사실상 gpt-3.5-turbo-instruct 전용
#
# 레거시 엔드포인트가 그래도 살아남아 있는 이유 / 여전히 쓰이는 경우:
#   (1) 기존 레거시 코드/시스템 유지보수
#   (2) 코드 자동완성 등 "대화 구조"가 오히려 방해되는 작업
#   (3) logprobs, echo, suffix(중간 채우기) 등 Chat API엔 없는 옛 옵션이 필요한 경우
#   (4) gpt-3.5-turbo-instruct의 저렴한 단가로 대량 배치 처리할 때
#
# 새 프로젝트의 기본 선택:
#   → ChatOpenAI + gpt-4o / gpt-4o-mini  (즉 Chat Completions API)
#
# 이 튜토리얼의 LangChain 예제도 모두 ChatOpenAI 기준으로 진행됩니다.
# langchain_openai.OpenAI (legacy completion 래퍼)는 "이런 게 있다" 정도만 알아두면 OK.
