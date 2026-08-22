# 7. Google Gemini

Google Gemini API 활용 예제

## 구조

```
1.basic/                  # Gemini SDK 기본
  1.intro.py              # 텍스트 생성 (google-genai)
  2.chat.py               # 멀티턴 대화
  3.params.py             # 파라미터 제어 (temperature, top_p, top_k)
  4.stream.py             # 스트리밍 응답
  5.structured_output.py  # JSON 구조화 출력 (Pydantic)

2.multimodal/             # 멀티모달
  1.vision.py             # 이미지 분석 (URL / 로컬)
  2.image_gen.py          # Imagen 3 이미지 생성

3.langchain/              # LangChain 연동
  1.intro.py              # ChatGoogleGenerativeAI 기본
  2.chain.py              # LCEL 체인 (prompt | llm | parser)
  3.structured_output.py  # with_structured_output
```

## 필요 패키지

```bash
pip install google-genai langchain-google-genai python-dotenv Pillow
```

## 환경 변수

```
GOOGLE_API_KEY=your_google_api_key
```
