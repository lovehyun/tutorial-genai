from langchain_core.prompts import ChatPromptTemplate

# Chat 버전: PromptTemplate 대신 ChatPromptTemplate 사용 (system + user 역할 분리)

# ─────────────────────────────────────────────────────────────
# [참고] ChatPromptTemplate.from_messages 에 메시지를 넘기는 세 가지 형태
#
# (1) 튜플 단축형  ── ("system", "...{var}...")
#     - 가장 짧고 가독성 좋음. 권장 방식.
#
# (2) 메시지 템플릿 객체  ── SystemMessagePromptTemplate.from_template("...{var}...")
#     - (1)번이 내부적으로 변환되는 정식 객체 형태. 동작은 완전히 동일.
#     - import 가 필요해서 길지만 명시적임.
#
# (3) 일반 메시지 객체  ── SystemMessage(content="고정 문장")
#     - 변수 치환 ❌. {var} 못 씀. 고정 문구일 때만 사용 가능.
#     - 예: system prompt 는 고정인데 user 만 변수일 때 섞어 쓸 수 있음.
# ─────────────────────────────────────────────────────────────


# ─── 형태 (1) 튜플 단축형 — 현재 권장 ───
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a naming consultant for new companies."),
    ("user",   "Suggest a name for a company that makes {product}."),
])


# ─── 형태 (2) 메시지 템플릿 객체 — 위와 동작 동일 ───
# from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
# prompt = ChatPromptTemplate.from_messages([
#     SystemMessagePromptTemplate.from_template("You are a naming consultant for new companies."),
#     HumanMessagePromptTemplate.from_template("Suggest a name for a company that makes {product}."),
# ])


# ─── 형태 (3) 일반 메시지 객체 — system 은 고정, user 만 변수 ───
# 주의: SystemMessage 안의 문자열에는 {var} 치환이 안 된다.
# from langchain_core.messages import SystemMessage
# from langchain_core.prompts import HumanMessagePromptTemplate
# prompt = ChatPromptTemplate.from_messages([
#     SystemMessage(content="You are a naming consultant for new companies."),       # 고정
#     HumanMessagePromptTemplate.from_template("Suggest a name for a company that makes {product}."),
# ])


# .format_messages() 는 메시지 리스트(BaseMessage) 를 반환한다 (instruct 의 .format() 은 단일 문자열)
filled_messages = prompt.format_messages(product="robot toys")

print("Prompt 결과:")
for m in filled_messages:
    print(f"  [{m.type}] {m.content}")

# 2. 프롬프트 템플릿 반복 활용
print("\n-----\n")
test_products = [
    "mobile games",
    "robot toys",
    "eco-friendly packaging",
    "language learning platforms",
    "electric bikes"
]

# 3. 프롬프트 확인
for product in test_products:
    msgs = prompt.format_messages(product=product)
    print(f"[{product}]")
    for m in msgs:
        print(f"  [{m.type}] {m.content}")
    print()
