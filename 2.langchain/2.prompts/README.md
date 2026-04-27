# 프롬프트 템플릿

LangChain의 `PromptTemplate`과 `ChatPromptTemplate`을 활용한 다양한 태스크별 프롬프트 예제입니다.

## 핵심 개념

### PromptTemplate vs ChatPromptTemplate
- **PromptTemplate**: 단일 문자열 프롬프트 (completion 모델용)
- **ChatPromptTemplate**: system/user/assistant 역할 기반 프롬프트 (chat 모델용)

### LCEL (LangChain Expression Language)
```python
chain = prompt | llm | StrOutputParser()
result = chain.invoke({"variable": "value"})
```

## 예제 목록

### 기본 템플릿 (1.x)
| 파일 | 설명 |
|------|------|
| `1.1_template.py` | PromptTemplate 기본 사용법 |
| `1.2_template_invoke.py` | invoke() 호출 방식 |
| `1.3_template_invoke_userinput.py` | 사용자 입력 처리 |
| `1.4_template_postprocess.py` | 후처리 파이프라인 |

### 체이닝 (2.x)
| 파일 | 설명 |
|------|------|
| `2.1_template_chaining.py` | 기본 체이닝 |
| `2.2_template_chaining2_lambda.py` | Lambda 활용 체이닝 |
| `2.3_template_chaining3_customfunc.py` | 커스텀 함수 체이닝 |

### 채팅 템플릿 (3.x)
| 파일 | 설명 |
|------|------|
| `3.1_template_chat.py` | ChatPromptTemplate 기본 |
| `3.2_template_chat_chaining.py` | 채팅 템플릿 체이닝 |

### 태스크별 예제 (4.x) — instruct/chat 쌍
| 파일 | 설명 |
|------|------|
| `4.1/4.2` | 텍스트 요약 (instruct / chat) |
| `4.3/4.4` | 번역 (instruct / chat) |
| `4.5/4.6` | 이메일 생성 (instruct / chat) |
| `4.7/4.8` | SQL 생성 (instruct / chat) |

### 이미지 (5.x)
| 파일 | 설명 |
|------|------|
| `5.1_chat_with_image.py` | 이미지 포함 채팅 |

## 실행

```bash
pip install langchain langchain-openai python-dotenv
python 1.1_template.py
```
