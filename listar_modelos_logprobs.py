import requests

URL = "https://openrouter.ai/api/v1/models"

response = requests.get(URL)

print("Status:", response.status_code)

if response.status_code != 200:
    print(response.text)
    exit()

data = response.json()

print("\nMODELOS GRATUITOS COM LOGPROBS\n")
print("=" * 80)

encontrados = []

for modelo in data["data"]:

    pricing = modelo.get("pricing", {})
    prompt = pricing.get("prompt")
    completion = pricing.get("completion")

    parametros = modelo.get("supported_parameters", [])

    if (
        prompt == "0"
        and completion == "0"
        and "logprobs" in parametros
    ):
        encontrados.append(modelo)

for modelo in encontrados:

    print(f"\nNome: {modelo.get('name')}")
    print(f"ID:   {modelo.get('id')}")
    print(
        f"Contexto: {modelo.get('context_length')}"
    )

    parametros = modelo.get("supported_parameters", [])

    print(
        "Top logprobs:",
        "SIM" if "top_logprobs" in parametros else "NÃO"
    )

print("\n" + "=" * 80)
print(f"Total encontrado: {len(encontrados)}")