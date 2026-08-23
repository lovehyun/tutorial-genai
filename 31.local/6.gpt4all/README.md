# 6.gpt4all — GPT4All 로 로컬 LLM

[GPT4All](https://gpt4all.io)은 GGUF 포맷 모델을 CPU에서도 돌리는 로컬 런타임이다. `10.ollama/`가
이미 로컬 LLM 실행의 사실상 표준을 다루므로(그래서 번호도 이 폴더보다 뒤다), 여기는
**대안 런타임**으로서 API 자체(`GPT4All` 클래스)에 집중한다.

## 순서

| 파일 | 내용 |
|---|---|
| `1.intro.py` | 최소 예제 — 모델 로드 + `generate()` 한 번 |
| `2.basic_qa.py` | 단답형 질의응답 |
| `3.conversation.py` | `chat_session()`으로 대화 맥락 유지 |
| `4.system_prompt.py` | 시스템 프롬프트로 역할/톤 지정 |
| `5.temperature.py` | `temp` 파라미터로 창의성 조절 |
| `6.fileprocessing.py` | 텍스트 파일(`document1.txt`) 내용을 프롬프트에 넣어 분석 |
| `7.largeoutput.py` | `max_tokens` 늘려 긴 답변 생성 + 소요 시간 측정 |
| `8.local_docs.py` | 로컬 문서 여러 개(`document1.txt`, `document2.txt`)를 근거로 답변 |
| `9.local_large_docs.py` | 큰 문서를 청크로 나눠 처리(`large_document1/2.txt`) |
| `9.local_large_docs2_debug.py` | 위 + 디버그 로그(청크별 처리 과정 출력) |
| `9.local_large_docs3_multiproc.py` | 위 + `multiprocessing`으로 청크 병렬 처리 |
| `10.promptengineering.py` | 같은 요청을 여러 프롬프트 스타일로 비교 |
| `11.externalapi.py` / `11.externalapi2_req.py` | 외부 REST API(날씨/유저 데이터) 응답을 모델에게 요약시킴 |
| `11.externalapi3_req.py` | 주가(yfinance)·번역(googletrans) 등 여러 외부 소스를 결합 |

## 설치

```bash
pip install gpt4all
```
```bash
# CLI 버전
wget https://raw.githubusercontent.com/nomic-ai/gpt4all/main/gpt4all-bindings/cli/app.py
# GUI 버전(Linux 예시)
wget https://gpt4all.io/installers/gpt4all-installer-linux.run
chmod +x gpt4all-installer-linux.run
./gpt4all-installer-linux
```

모든 예제가 `GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")`를 쓴다 — 처음 실행 시 자동으로
모델(약 4.7GB)을 다운로드한다.

> ⚠️ 이 폴더는 모델 다운로드 용량이 커서(약 4.7GB) 이 세션에서 라이브 실행 검증은 하지 못했다.
> `6.fileprocessing.py`의 `open("/path/to/file.txt")`(존재하지 않는 플레이스홀더 경로 —
> 실행하면 바로 `FileNotFoundError`)는 실제 버그로 확인되어 `document1.txt`를 가리키도록
> 고쳤다. 나머지 파일은 코드 리뷰로 로직 오류는 없는 것을 확인했다.

## 다음 단계
- 사실상 표준 로컬 런타임(더 활발히 유지보수됨) → [`../10.ollama/`](../10.ollama/)
