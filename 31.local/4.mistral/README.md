# 4.mistral — Mistral 7B 를 로컬에서

`mistralai/Mistral-7B-Instruct-v0.3`(비-게이트, 승인 없이 바로 다운로드됨)를 순수
`transformers`만으로 로드해 텍스트를 생성한다. `1.transformers/`가 GPT-2/BERT급 작은 모델로
구조를 익히는 자리였다면, 여기는 실전에서 실제로 쓰이는 7B급 오픈 모델을 다룬다.

## 파일

| 파일 | 내용 |
|---|---|
| `1.local_mistral.py` | 기본형 — `pipeline("text-generation")`으로 한 줄 생성. Greedy vs Sampling 표·주요 태스크 목록 등 참고 주석이 풍부함 |
| `1.local2_mistral_langchain.py` | 같은 모델을 `HuggingFacePipeline`으로 감싸 LangChain 프롬프트 템플릿과 연결 |
| `1.local3_mistral_flask.py` | 같은 모델을 Flask로 REST 서빙(서버 시작 시 1회 로드 → 요청마다 재사용) |

## ⚠️ 실행 전 확인할 것

- **7B 모델**이라 다운로드 용량이 크고(bfloat16 기준 약 14GB), **CPU로 돌리면 매우 느리다**(응답
  하나에 수 분 걸릴 수 있음). GPU(VRAM 16GB 권장)가 없다면 실행 자체보다 **코드를 읽고 구조를
  이해하는 용도**로 먼저 접근할 것.
- 비-게이트 모델이라 별도 라이선스 승인은 필요 없다(`huggingface_hub.model_info`로 직접 확인함).
- 이 저장소 환경(CPU-only)에서는 다운로드·추론 시간이 커서 라이브 실행 검증을 하지 못했다 —
  코드 문법·API 사용은 확인했지만 실제 출력은 직접 GPU 환경에서 확인 필요.

## 설치
```bash
pip install transformers protobuf sentencepiece torch python-dotenv
# 2번 파일은 추가로: pip install langchain-huggingface langchain-core
# 3번 파일은 추가로: pip install flask
```

## 다음 단계
- 작은 모델로 구조부터 다시 보고 싶다면 → [`../1.transformers/`](../1.transformers/)
- 같은 걸 Llama 계열로 → [`../5.llama/`](../5.llama/)
- CPU에서도 가볍게 돌아가는 대안(양자화된 형식) → [`../10.ollama/`](../10.ollama/)
