import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

URL = "https://openrouter.ai/api/v1/chat/completions"

modelos = [
    "inclusionai/ling-3.0-flash-fin:free",
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

for modelo in modelos:

    print("\n" + "=" * 70)
    print("TESTANDO:", modelo)
    print("=" * 70)

    payload = {
        "model": modelo,
        "messages": [
            {
                "role": "user",
                "content": "Responda apenas: História"
            }
        ],
        "max_tokens": 10,
        "logprobs": True,
        "top_logprobs": 5,
        "stream": False,
    }

    response = requests.post(
        URL,
        headers=headers,
        json=payload,
        timeout=120,
    )

    print("Status:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        continue

    data = response.json()

    escolha = data["choices"][0]

    print("Resposta:")
    print(escolha["message"]["content"])

    print("\nLogprobs:")

    logprobs = escolha.get("logprobs")

    if logprobs is None:
        print("❌ NÃO RETORNOU LOGPROBS")
        continue

    tokens = logprobs.get("content")

    if not tokens:
        print("❌ Campo content vazio")
        continue

    print(f"✅ LOGPROBS RECEBIDOS — {len(tokens)} tokens")

    for token in tokens:

        print(
            f"\nToken: {token['token']!r}"
            f"\nLogprob: {token['logprob']:.4f}"
        )

        print("Alternativas:")

        for alternativa in token.get("top_logprobs", []):

            print(
                f"  {alternativa['token']!r}"
                f" | {alternativa['logprob']:.4f}"
            )