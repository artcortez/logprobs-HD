import os
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(
    provider="nscale",
    api_key=HF_TOKEN,
)

pergunta = input("\nFaça uma pergunta histórica: ")

resposta = client.chat.completions.create(
    model="Qwen/Qwen3-4B-Instruct-2507",
    messages=[
        {
            "role": "user",
            "content": pergunta
        }
    ],
    max_tokens=150,
    logprobs=True,
    top_logprobs=5,
)

escolha = resposta.choices[0]

conteudo = escolha.message.content
logprobs = escolha.logprobs

if logprobs is None:
    print("\n❌ O modelo não retornou logprobs.")
    exit()

tokens = []

for token in logprobs.content:

    alternativas = []

    for alternativa in token.top_logprobs:
        alternativas.append({
            "token": alternativa.token,
            "logprob": alternativa.logprob
        })

    tokens.append({
        "token": token.token,
        "logprob": token.logprob,
        "alternativas": alternativas
    })

resultado = {
    "pergunta": pergunta,
    "resposta": conteudo,
    "modelo": "Qwen/Qwen3-4B-Instruct-2507",
    "provider": "nscale",
    "tokens": tokens
}

with open(
    "resultado.json",
    "w",
    encoding="utf-8"
) as arquivo:

    json.dump(
        resultado,
        arquivo,
        ensure_ascii=False,
        indent=2
    )

print("\n" + "=" * 60)
print("RESPOSTA")
print("=" * 60)
print(conteudo)

print("\n" + "=" * 60)
print("DADOS")
print("=" * 60)
print(f"Tokens registrados: {len(tokens)}")
print("Arquivo criado: resultado.json")