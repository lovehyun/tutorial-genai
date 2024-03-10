# https://python.langchain.com/docs/integrations/llms/huggingface_endpoint

# pip install huggingface_hub

from dotenv import load_dotenv

from langchain_community.llms import HuggingFaceEndpoint


load_dotenv(dotenv_path='../.env')

repo_id = "mistralai/Mistral-7B-Instruct-v0.2"

llm = HuggingFaceEndpoint(
    repo_id=repo_id, max_length=128, temperature=0.5
)

prompt = "What are good fitness tips?"

print(llm(prompt))
