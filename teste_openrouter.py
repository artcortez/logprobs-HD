import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

URL = "https://openrouter.ai/api/v1/chat/completions"

payload = {
    "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
    "messages": [
        {
            "role": "user",
            "content": "Quem foi Napoleão Bonaparte?"
        }
    ],
    "max_tokens": 100,
    "logprobs": True,
    "top_logprobs": 5,
    "stream": False
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(
    URL,
    headers=headers,
    json=payload
)

print("Status:", response.status_code)

if response.status_code != 200:
    print(response.text)
    exit()

data = response.json()

print("\n--- RESPOSTA ---")

print(
    data["choices"][0]["message"]["content"]
)

print("\n--- LOGPROBS ---")
print(data["choices"][0]["logprobs"])