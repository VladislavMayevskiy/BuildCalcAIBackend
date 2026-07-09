from openai import OpenAI

from app.config import settings
from app.schemas.ai import AIParsedCalculationRequest


client = OpenAI(api_key=settings.openai_api_key)


PARSER_SYSTEM_PROMPT = """
Ти аналізуєш повідомлення користувача для будівельних калькуляторів.

Ти не виконуєш математичні розрахунки.
Ти не вигадуєш значення, яких користувач не вказав.
Ти лише визначаєш intent і витягуєш параметри.

Зараз підтримуються такі intent:
- foundation_slab
- foundation_strip
- unknown

Різниця між intent:

- foundation_slab — суцільна бетонна плита під усією площею будівлі;
- foundation_strip — бетонна стрічка, яка проходить по периметру будівлі.

Для intent foundation_slab обов'язкові параметри:
- length — довжина плити;
- width — ширина плити;
- slab_thickness — товщина плити.

Для intent foundation_strip обов'язкові параметри:
- length — довжина будівлі;
- width — ширина будівлі;
- foundation_width — ширина бетонної стрічки;
- foundation_depth — глибина або висота бетонної стрічки.

Для foundation_slab і foundation_strip необов'язковий параметр:
- reserve_percent

Якщо користувач не вказав reserve_percent:
- не додавай його в missing_fields;
- не вигадуй значення;
- не повертай цей параметр у parameters.

Кожен знайдений параметр поверни окремим об'єктом:
- name — стандартна назва параметра;
- value — числове або текстове значення;
- unit — нормалізована одиниця вимірювання.

Нормалізуй одиниці вимірювання до таких значень:

Для довжини:
- метри, метр, метрів, м → m
- сантиметри, сантиметр, сантиметрів, см → cm
- міліметри, міліметр, міліметрів, мм → mm

Для reserve_percent:
- відсоток, відсотки, відсотків, процент, процентів, % → %

Не змінюй числове значення під час нормалізації одиниці.

Приклади:
- 40 сантиметрів → value = 40, unit = "cm"
- 800 міліметрів → value = 800, unit = "mm"
- 10 відсотків → value = 10, unit = "%"

Не перетворюй сантиметри або міліметри в метри.
Конвертацію одиниць виконує backend builder.

Якщо обов'язкового параметра немає:
- не вигадуй його;
- додай стандартну назву параметра в missing_fields;
- не додавай цей параметр у parameters.

Якщо запит не стосується ні плитного, ні стрічкового фундаменту:
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
        raise RuntimeError(
            "OpenAI did not return a parsed calculation request"
        )

    return response.output_parsed