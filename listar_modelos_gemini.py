import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY não encontrada no arquivo .env")

client = genai.Client(api_key=GEMINI_API_KEY)

print("\n==========================================")
print("MODELOS DISPONÍVEIS PARA ESTA CHAVE")
print("==========================================\n")

for modelo in client.models.list():

    nome = getattr(modelo, "name", "")
    nome_base = getattr(modelo, "base_model_id", "")
    acoes = getattr(modelo, "supported_actions", None)

    if acoes is None:
        acoes = []

    if "generateContent" in acoes:
        print(f"MODELO: {nome}")
        print(f"BASE:   {nome_base}")
        print(f"AÇÕES:  {acoes}")
        print("-" * 50)

print("\nFim.")