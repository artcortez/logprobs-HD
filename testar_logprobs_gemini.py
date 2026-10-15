import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY não encontrada no .env")

client = genai.Client(api_key=GEMINI_API_KEY)

modelos = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite",
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-pro-latest",
]

pergunta = "Quem foi Carlos Martel?"

print("\n==========================================")
print("TESTE DE LOGPROBS — GEMINI")
print("==========================================\n")

for modelo in modelos:

    print(f"TESTANDO: {modelo}")

    try:

        resposta = client.models.generate_content(
            model=modelo,
            contents=pergunta,
            config=types.GenerateContentConfig(
                max_output_tokens=50,
                response_logprobs=True,
                logprobs=5,
            ),
        )

        logprobs = getattr(resposta, "response_logprobs", None)

        if logprobs:
            print("RESULTADO: OK — LOGPROBS DISPONÍVEIS")
        else:
            print("RESULTADO: RESPONDEU, MAS LOGPROBS NÃO APARECERAM")

        print()

    except Exception as erro:

        mensagem = str(erro)

        if "Logprobs is not enabled" in mensagem:
            print("RESULTADO: SEM LOGPROBS")

        elif "NOT_FOUND" in mensagem or "not found" in mensagem.lower():
            print("RESULTADO: MODELO NÃO DISPONÍVEL")

        else:
            print("RESULTADO: ERRO")
            print(mensagem)

        print()

print("==========================================")
print("FIM DO TESTE")
print("==========================================")