from ollama import Client
from app.config import settings

client = Client(host=settings.ollama_base_url)


def generate_text(prompt: str) -> str:
    response = client.chat(
        model=settings.ollama_model,
        messages=[
            {"role": "system", "content": "You are a precise research assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return response["message"]["content"]