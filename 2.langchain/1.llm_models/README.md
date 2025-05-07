# LLM 모델 비교 및 Instruct Fine-tuning 정리

## Instruct Fine-tuning이란?

**Instruct Fine-tuning**은 기본 언어 모델을 “명령을 이해하고 수행하는 대화형 모델”로 만드는 학습 기법입니다.

- 목적: 명령(instruction)에 반응하여 정답형 응답을 하도록 튜닝
- 데이터 형식:
    ```json
    {
      "instruction": "Translate to French.",
      "input": "Hello, world.",
      "output": "Bonjour, le monde."
    }
    ```
- 효과:
  - 명령형 프롬프트에 잘 반응함 ("Summarize", "List", "Explain" 등)
  - 일반 LLM 대비 명확하고 목적 지향적인 응답 생성

---

## 🔷 모델별 특징 비교

| 항목 | GPT-2 | GPT-Neo-2.7B | Mistral-7B-Instruct-v0.3 |
|------|-------|---------------|---------------------------|
| 출시 시기 | 2019 | 2021 | 2023 |
| 파라미터 수 | 1.5B | 2.7B | 7.3B |
| 구조 | GPT-2 (Decoder-only) | GPT-3 유사 구조 | 효율적인 GQA 구조 |
| 주요 기술 | 기본 Attention | GPT-3 모사 | GQA + Sliding Window |
| 학습 데이터 | OpenWebText | Pile (800GB+) | 비공개 (고품질 정제) |
| Instruct 튜닝 | ❌ 없음 | ❌ 없음 | ✅ 있음 |
| 명령 이해 | 매우 낮음 | 낮음 | 매우 높음 |
| 생성 품질 | 낮음 | 중간 | 매우 우수 |
| 지원 토큰 길이 | 1024 | 2048 | 8K 이상 |
| 메모리 요구 | 낮음 | 높음 (10GB+) | 높음 (8~12GB VRAM) |
| 라이선스 | MIT | Apache 2.0 | Apache 2.0 |

---

## Instruct 튜닝된 모델 예시

- `text-davinci-003`: OpenAI instruct 대표 모델
- `Mistral-7B-Instruct-v0.3`: 오픈소스 기반 최고 수준
- `LLaMA2-Chat`, `Alpaca`, `OpenAssistant`: 커뮤니티 기반 instruct 모델

---

## 요약 추천

| 목적 | 추천 모델 |
|------|------------|
| 빠른 테스트 / 데모 | GPT-2 |
| 무료 LLM 연구용 | GPT-Neo-2.7B |
| 실제 챗봇/요약/코딩 | Mistral-7B-Instruct-v0.3 |

---

## Instruct 튜닝 확인용 추천 테스트 프롬프트

명령 수행 능력을 테스트하려면 아래와 같은 프롬프트를 각 모델에 넣고 응답을 비교해보세요.

| 테스트 목적     | 프롬프트 예시                                                                 |
|----------------|------------------------------------------------------------------------------|
| SQL 생성     | `Write a SQL query to get top 5 customers by purchase amount in 2023.`       |
| 요약         | `Summarize the following article: [본문]`                                     |
| 번역         | `Translate this to Korean: "The product was well-received by customers."`     |
| 이메일 작성  | `Write a formal email to request a meeting with the marketing team.`          |
| 코드 작성     | `Write a Python function to calculate factorial recursively.`                 |
| JSON 변환     | `Convert the following data into JSON format: name: Alice, age: 30, city: Paris` |

> **비교 팁:** 같은 프롬프트를 GPT-2, GPT-Neo-2.7B, Mistral-7B-Instruct 등에 동일하게 입력해보면,
> Instruct 튜닝 여부에 따라 얼마나 다른 결과를 내는지 명확히 알 수 있습니다.
