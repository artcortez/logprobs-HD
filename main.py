import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from structured_logprobs.main import add_logprobs, add_logprobs_inline


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


schema_content = {
    "type": "json_schema",
    "json_schema": {
        "name": "historical_interpretation",
        "description": "Structured historical interpretation",
        "schema": {
            "type": "object",
            "properties": {
                "periodo": {
                    "type": "string"
                },
                "local": {
                    "type": "string"
                },
                "tema": {
                    "type": "string"
                },
                "tipo_memoria": {
                    "type": "string",
                    "enum": [
                        "memória individual",
                        "memória coletiva",
                        "memória familiar",
                        "memória social"
                    ]
                }
            },
            "required": [
                "periodo",
                "local",
                "tema",
                "tipo_memoria"
            ],
            "additionalProperties": False
        },
        "strict": True
    }
}


pergunta = input("Faça uma pergunta sobre o corpus histórico: ")


completion = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    messages=[
        {
            "role": "system",
            "content": """
Você é um sistema experimental de análise histórica.

Sua tarefa é interpretar a pergunta do usuário em relação a um
corpus histórico.

Não invente informações que não estejam disponíveis.

Extraia uma interpretação estruturada seguindo exatamente o esquema
fornecido.
"""
        },
        {
            "role": "user",
            "content": pergunta
        }
    ],
    logprobs=True,
    response_format=schema_content
)


resultado = add_logprobs(completion)

print("\n==============================")
print("INTERPRETAÇÃO")
print("==============================\n")

print(json.dumps(
    resultado.log_probs[0],
    indent=4,
    ensure_ascii=False
))


print("\n==============================")
print("RESPOSTA ORIGINAL")
print("==============================\n")

print(completion.choices[0].message.content)