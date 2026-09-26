import requests
import math

URL = "http://localhost:33831/v1/chat/completions"

pergunta = input("Faça uma pergunta: ")

payload = {
    "model": "/root/.cache/llama.cpp/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
    "messages": [
        {
            "role": "user",
            "content": pergunta
        }
    ],
    "max_tokens": 50,
    "logprobs": True,
    "top_logprobs": 5,
    "stream": False
}

response = requests.post(URL, json=payload)

if response.status_code != 200:
    print("Erro:", response.status_code)
    print(response.text)
    exit()

data = response.json()

print("\n--- RESPOSTA ---")
print(data["choices"][0]["message"]["content"])

print("\n--- DISTRIBUIÇÃO DOS TOKENS ---")

tokens = data["choices"][0]["logprobs"]["content"]

for token in tokens:

    print("\n" + "=" * 60)

    escolhido = token["token"]
    logprob_escolhido = token["logprob"]

    print(f"Token escolhido: {escolhido!r}")
    print(f"Logprob: {logprob_escolhido:.4f}")

    print("\nAlternativas:")

    for alternativa in token["top_logprobs"]:

        probabilidade = math.exp(alternativa["logprob"]) * 100

        print(
            f"  {alternativa['token']!r}"
            f" | logprob: {alternativa['logprob']:.4f}"
            f" | prob. relativa: {probabilidade:.2f}%"
        )