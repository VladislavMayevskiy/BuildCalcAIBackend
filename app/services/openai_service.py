from openai import OpenAI

from app.config import settings
from app.schemas.ai import AIParsedCalculationRequest


client = OpenAI(api_key=settings.openai_api_key)


PARSER_SYSTEM_PROMPT = """
Ти аналізуєш повідомлення користувача для будівельних калькуляторів.

Ти не виконуєш математичні розрахунки.
Ти не вигадуєш значення, яких користувач не вказав.
Ти лише визначаєш intent і витягуєш параметри.

Зараз підтримуються тільки такі intent:
- foundation_slab
- unknown

Для intent foundation_slab обов'язкові параметри:
- length
- width
- slab_thickness

Кожен знайдений параметр поверни окремим об'єктом:
- name — назва параметра;
- value — значення;
- unit — одиниця вимірювання.

Допустимі одиниці:
- m
- cm
- mm

Зберігай одиниці так, як їх вказав користувач.
Не перетворюй сантиметри або міліметри в метри.

Якщо обов'язкового параметра немає:
- не вигадуй його;
- додай його назву в missing_fields.

Якщо запит не стосується бетонної фундаментної плити:
- intent = unknown;
- parameters = [];
- missing_fields = [].
"""


def generate_ai_response(prompt: str) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    return response.output_text


def generate_ai_parsed_request(
    message: str,
) -> AIParsedCalculationRequest:
    response = client.responses.parse(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": PARSER_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        text_format=AIParsedCalculationRequest,
    )

    if response.output_parsed is None:
        raise RuntimeError("OpenAI did not return a parsed calculation request")

    return response.output_parsed