
import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise RuntimeError("OPENROUTER_API_KEY não encontrada no .env")

url = "https://openrouter.ai/api/v1/chat/completions"

payload = {
    "model": "liquid/lfm-2.5-2.6b:free",
    "messages": [
        {
            "role": "user",
            "content": "Quem foi Napoleão Bonaparte? Responda em um parágrafo."
        }
    ],
    "max_tokens": 150,
    "logprobs": True,
    "top_logprobs": 5
}

response = requests.post(
    url,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json=payload,
    timeout=120
)

print("Status HTTP:", response.status_code)

data = response.json()

if not response.ok:
    print(data)
else:
    choice = data["choices"][0]
    print("\nRESPOSTA:")
    print(choice["message"]["content"])

    logprobs = choice.get("logprobs")
    print("\nLOGPROBS retornados:", logprobs is not None)

    if logprobs and logprobs.get("content"):
        print("Quantidade de tokens:", len(logprobs["content"]))
        print("\nPrimeiros tokens:")
        for token in logprobs["content"][:5]:
            print(token)
    else:
        print("O provedor não retornou dados de logprobs.")
