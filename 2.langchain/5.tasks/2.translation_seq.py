from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
parser = StrOutputParser()

base_prompt = ChatPromptTemplate.from_messages([
    ("system", "Translate English to {language}. Only return the translation."),
    ("human", "{text}"),
])

text = "Hello, nice to meet you."

chain_ko = base_prompt.partial(language="Korean") | llm | parser
chain_ja = base_prompt.partial(language="Japanese") | llm | parser
chain_fr = base_prompt.partial(language="French") | llm | parser

ko = chain_ko.invoke({"text": text})
ja = chain_ja.invoke({"text": text})
fr = chain_fr.invoke({"text": text})

print("[KO]", ko)
print("[JA]", ja)
print("[FR]", fr)
