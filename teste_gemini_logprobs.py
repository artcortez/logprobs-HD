import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY não encontrada no arquivo .env")

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-3.8-flash"

resposta = client.models.generate_content(
    model=MODEL,
    contents="Quem foi Carlos Martel?",
    config=types.GenerateContentConfig(
        max_output_tokens=150,
        response_logprobs=True,
        logprobs=5,
    ),
)

print("\n==========================================")
print("MODELO:")
print(MODEL)

print("\nRESPOSTA:")
print(resposta.text)

print("\nLOGPROBS:")
print(resposta.to_json())

print("==========================================\n")