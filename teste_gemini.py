import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY não encontrada no arquivo .env")

client = genai.Client(api_key=api_key)

pergunta = input("Faça uma pergunta: ")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=pergunta,
    config={
        "response_logprobs": True,
        "logprobs": 5,
    }
)

print("\n==============================")
print("RESPOSTA")
print("==============================\n")

print(response.text)

print("\n==============================")
print("LOGPROBS")
print("==============================\n")

print(response.candidates[0].logprobs_result)