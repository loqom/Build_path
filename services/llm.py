from langchain_mistralai import ChatMistralAI
from config.settings import settings

llm = ChatMistralAI(
    api_key=settings.MISTRAL_API_KEY,
    model="mistral-small-2506",
    temperature=0.4
)
