# pip install transformers torch

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# 모델 이름 (로컬 캐시에 다운로드됨)
model_name = "gpt2"

# 토크나이저 및 모델 불러오기
# AutoModel	기본 모델 구조 (예: BERT의 Encoder만)
# AutoModelForSequenceClassification	문장 분류 (감성 분석 등)
# AutoModelForTokenClassification	    토큰 단위 태깅 (NER 등)
# AutoModelForQuestionAnswering	        질문/답변
# AutoModelForCausalLM	                GPT류 모델 (텍스트 생성)
# AutoModelForSeq2SeqLM	                번역/요약 등 (Encoder-Decoder 구조)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)


# pipeline()에서 사용 가능한 주요 태스크 목록
# 태스크 이름 (task)	    설명	                    예시 모델
# "text-generation"	        텍스트 이어쓰기	            GPT2, GPT-Neo, Mistral
# "text2text-generation"	입력 → 출력 (질문→답, 번역 등)	T5, FLAN-T5, BART
# "text-classification"	    감성 분석, 문장 분류	    BERT, RoBERTa
# "token-classification"	NER (이름, 장소 등 태깅)	BERT
# "question-answering"	    주어진 문서 내 질의응답	    DistilBERT, RoBERTa
# "translation"	            기계 번역	                MarianMT, Helsinki-NLP
# "summarization"	        문서 요약	                BART, T5
# "zero-shot-classification"	레이블 없이 분류	    BART, RoBERTa
# "conversation"	        챗봇 형태	                DialoGPT, BlenderBot
# "fill-mask"	            [MASK]에 단어 채우기	    BERT
# "image-classification"	이미지 분류	                ViT, ResNet
# "automatic-speech-recognition"	음성 → 텍스트	    Whisper, Wav2Vec2
# "feature-extraction"	    임베딩 추출	                BERT, Sentence-BERT

# LLM에서 "샘플링 모드"란, 텍스트 생성 시 가장 확률이 높은 단어만 고르지 않고, 확률 분포에 따라 적절히 섞어서 단어를 선택하는 방식을 말합니다.
# 1. Greedy Search (기본 모드): 매 단계에서 가장 확률이 높은 토큰 1개만 선택. 결과는 항상 같고, 정확하지만 창의성 부족.
# 2. Sampling (샘플링 모드): 매 단계에서 확률 분포를 따라 무작위로 선택 (가중치 있음). 결과가 매번 조금씩 달라짐, 더 자연스럽고 창의적
# | 항목      | Greedy Search (`do_sample=False`) | Sampling (`do_sample=True`)   |
# | --------- | --------------------------------- | ----------------------------- |
# | 선택 방식  | 확률이 가장 높은 1개만 선택        | 확률 분포에서 무작위로 선택      |
# | 연산량     | 적음 (1개 선택)                   | 많음 (여러 후보 중 선택)        |
# | 메모리 사용 | 낮음                             | 높음 (분포 계산 및 저장 필요)   |
# | 속도       | 빠름                             | 느림 (top-k, top-p, 확률 누적 연산 등) |
# | 창의성     | 낮음 (일관성 있음)                | 높음 (다양한 응답 가능)         |
# | 사용 예시  | 분류, 요약                       | 스토리 생성, 대화, 코딩         |

# 텍스트 생성 파이프라인 생성
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=128, # 출력 토큰 수만 제한
    temperature=0.7,
    # repetition_penalty=1.2,        # 반복 억제
    # no_repeat_ngram_size=3,        # 3단어 이상 반복 금지
    pad_token_id=tokenizer.eos_token_id,  # gpt2는 pad_token 없음, 중간 오류 방지
    do_sample=True
)
# do_sample=True              # 샘플링 모드 ON
# temperature=0.7             # 확률 분포 평탄화 (0.7~1.0 추천)
# top_k=50                    # 상위 K개 중에서만 샘플링 (선택 제한)
# top_p=0.95                  # 누적 확률 상위 P% 이내만 선택

# 질문 프롬프트
prompt = "What are good fitness tips?"

# 텍스트 생성
result = generator(prompt)[0]["generated_text"]

# result = generator(prompt, max_new_tokens=128, temperature=0.5)
# pipeline(...)은 내부적으로 **kwargs를 저장하고,
# generator(...) 호출 시 전달되는 값이 있으면 그 값을 우선 적용

# 출력
print(f"Prompt: {prompt}")
print(f"Answer: {result}")
