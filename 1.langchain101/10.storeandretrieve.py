from dotenv import load_dotenv

from langchain_openai import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.schema import messages_from_dict, messages_to_dict

load_dotenv()

history = ChatMessageHistory()
history.add_user_message("Hello, Let's talk about giraffes")
history.add_ai_message("Hello, I'm down to talk about giraffes")

dicts = messages_to_dict(history.messages)
print(dicts)

new_messages = messages_from_dict(dicts)

llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.1)
history = ChatMessageHistory(messages=new_messages)
buffer = ConversationBufferMemory(chat_memory=history)

conversation = ConversationChain(llm=llm, memory=buffer, verbose=True)

print(conversation.predict(input="What are they?"))

