from openai import OpenAI

from app.config import settings


client = OpenAI(api_key=settings.openai_api_key)


def generate_ai_response(prompt: str) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    return response.output_text