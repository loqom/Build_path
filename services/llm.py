import ssl
import os
import certifi
import httpx

from langchain_mistralai import ChatMistralAI
from config.settings import settings


ssl_context = ssl.create_default_context(cafile=certifi.where())

azure_ca_path = "/etc/ssl/certs/adc-egress-proxy-ca.crt"

if os.path.exists(azure_ca_path):
    ssl_context.load_verify_locations(cafile=azure_ca_path)


headers = {
    "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


http_client = httpx.Client(
    verify=ssl_context,
    base_url="https://api.mistral.ai/v1",
    headers=headers,
    timeout=120.0,
)

async_http_client = httpx.AsyncClient(
    verify=ssl_context,
    base_url="https://api.mistral.ai/v1",
    headers=headers,
    timeout=120.0,
)


llm = ChatMistralAI(
    api_key=settings.MISTRAL_API_KEY,
    model="open-mistral-nemo",
    temperature=0.4,
    client=http_client,
    async_client=async_http_client,
)