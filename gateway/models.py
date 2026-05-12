from openai import OpenAI
from .config import VLLM_API_KEY

def client_for(base_url: str) -> OpenAI:
    return OpenAI(base_url=base_url, api_key=VLLM_API_KEY)
