from dotenv import load_dotenv

from langchain_openai import OpenAI
from langchain.chains import ConversationChain


load_dotenv(dotenv_path='../.env')

llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.1)

conversation = ConversationChain(llm=llm, verbose=True)

# print(conversation.predict(input="Hello"))
conversation.predict(input="Hello")
conversation.predict(input="Can we talk about the sports?")
print(conversation.predict(input="What's a good sport to play outdoor?"))
