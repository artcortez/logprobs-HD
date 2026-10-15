import os
import json
import math

from dotenv import load_dotenv
from huggingface_hub import InferenceClient


# ============================================================
# CONFIGURAÇÃO
# ============================================================

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN não encontrado no arquivo .env")

MODEL = "Qwen/Qwen3-32B"

client = InferenceClient(
    provider="nscale",
    api_key=HF_TOKEN
)


# ============================================================
# FONTE HISTÓRICA
# ============================================================

fonte = """
RANKE, Leopold von. History of the Reformation in Germany.
Trad. Sarah Austin. New York: P. F. Collier & Son, 1905.
v. 1. p. 2-3.

Uma das épocas mais importantes da história mundial foi o início
do século VIII, quando, por um lado, o islamismo ameaçava se
espalhar pela Itália e pela Gália e, por outro, a antiga idolatria
da Saxônia e da Frísia forçava novamente sua passagem para além
do Reno.

Nesse perigo para as instituições cristãs, um jovem príncipe de
origem germânica, Carlos Martell, surgiu como seu defensor,
defendendo-as com toda a energia que a necessidade de autodefesa
exige e, finalmente, expandindo-as para novas regiões.
"""


# ============================================================
# PERGUNTA
# ============================================================

pergunta = """
Como o documento descreve a vitória de Carlos Martel sobre as
tropas islâmicas?
"""


# ============================================================
# PROMPT
# ============================================================

prompt = f"""
Você está analisando uma fonte histórica.

Utilize exclusivamente as informações presentes na fonte fornecida.

Não acrescente informações externas à fonte.

Não invente informações.

Se a pergunta não puder ser respondida com base na fonte,
diga claramente que essa informação não está presente no documento.

FONTE HISTÓRICA
==================================================

{fonte}

==================================================

PERGUNTA

{pergunta}
"""


# ============================================================
# REQUISIÇÃO
# ============================================================

print("\nEnviando pergunta ao Qwen3-32B...\n")

resposta = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "system",
            "content": (
                "Você é um assistente especializado em análise "
                "de fontes históricas. "
                "Responda em português. "
                "Responda de forma clara e objetiva."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    max_tokens=1000,
    logprobs=True,
    top_logprobs=5,
    extra_body={
        "enable_thinking": False
    }
)


# ============================================================
# OBJETOS
# ============================================================

escolha = resposta.choices[0]

message = escolha.message

texto_resposta = message.content or ""

logprobs = escolha.logprobs


# ============================================================
# EXTRAIR TODOS OS TOKENS
# ============================================================

tokens = []

if (
    logprobs is not None
    and getattr(logprobs, "content", None) is not None
):

    for item in logprobs.content:

        token_texto = getattr(
            item,
            "token",
            ""
        )

        logprob = getattr(
            item,
            "logprob",
            None
        )

        alternativas = []

        top_logprobs = getattr(
            item,
            "top_logprobs",
            None
        )

        if top_logprobs:

            for alternativa in top_logprobs:

                alternativas.append({
                    "token": getattr(
                        alternativa,
                        "token",
                        ""
                    ),
                    "logprob": getattr(
                        alternativa,
                        "logprob",
                        None
                    )
                })

        tokens.append({
            "token": token_texto,
            "logprob": logprob,
            "alternativas": alternativas
        })


# ============================================================
# RECONSTRUIR TEXTO DOS TOKENS
# ============================================================

texto_tokens = "".join(
    token["token"]
    for token in tokens
)


# ============================================================
# LOCALIZAR RESPOSTA PÚBLICA
# ============================================================

posicao = texto_tokens.find(
    texto_resposta
)


if posicao == -1:

    raise RuntimeError(
        "Não foi possível localizar "
        "message.content dentro dos tokens."
    )


# ============================================================
# SEPARAR TOKENS DA RESPOSTA PÚBLICA
# ============================================================

tokens_resposta = []

inicio_resposta = posicao

fim_resposta = (
    posicao +
    len(texto_resposta)
)

posicao_atual = 0

começou = False


for token in tokens:

    token_texto = token["token"]

    inicio_token = posicao_atual

    fim_token = (
        posicao_atual +
        len(token_texto)
    )

    posicao_atual = fim_token


    # Ainda não chegamos à resposta
    if fim_token <= inicio_resposta:
        continue


    # Começamos a resposta
    if not começou:
        começou = True


    tokens_resposta.append(token)


    # Já ultrapassamos o final
    if fim_token >= fim_resposta:
        break


# ============================================================
# CONVERTER LOGPROB EM PROBABILIDADE
# ============================================================

def logprob_para_probabilidade(logprob):

    if logprob is None:
        return None

    return math.exp(logprob)


# ============================================================
# PREPARAR DADOS PARA O FRONTEND
# ============================================================

dados_visualizacao = []


for token in tokens_resposta:

    logprob = token["logprob"]

    probabilidade = logprob_para_probabilidade(
        logprob
    )


    alternativas = []

    for alternativa in token["alternativas"]:

        alt_logprob = alternativa["logprob"]

        alt_probabilidade = (
            logprob_para_probabilidade(
                alt_logprob
            )
        )

        alternativas.append({
            "token": alternativa["token"],
            "logprob": alt_logprob,
            "probabilidade": alt_probabilidade
        })


    dados_visualizacao.append({

        "token": token["token"],

        "logprob": logprob,

        "probabilidade": probabilidade,

        "alternativas": alternativas

    })


# ============================================================
# RESULTADOS
# ============================================================

print("==========================================")
print("RESPOSTA PÚBLICA")
print("==========================================")

print(texto_resposta)


print("\n==========================================")
print("TOKENS DA RESPOSTA")
print("==========================================")

print(
    "Quantidade:",
    len(dados_visualizacao)
)


# ============================================================
# PRIMEIROS TOKENS
# ============================================================

print("\n==========================================")
print("PRIMEIROS 10 TOKENS")
print("==========================================")

for item in dados_visualizacao[:10]:

    print(
        repr(item["token"]),
        "| logprob:",
        item["logprob"],
        "| probabilidade:",
        item["probabilidade"]
    )


# ============================================================
# EXEMPLO DE ALTERNATIVAS
# ============================================================

print("\n==========================================")
print("ALTERNATIVAS DO PRIMEIRO TOKEN")
print("==========================================")

if dados_visualizacao:

    primeiro = dados_visualizacao[0]

    for alternativa in primeiro["alternativas"]:

        print(
            repr(alternativa["token"]),
            "| logprob:",
            alternativa["logprob"],
            "| probabilidade:",
            alternativa["probabilidade"]
        )


# ============================================================
# VERIFICAÇÃO
# ============================================================

texto_reconstruido = "".join(
    item["token"]
    for item in dados_visualizacao
)


print("\n==========================================")
print("VERIFICAÇÃO")
print("==========================================")

print(
    "Texto reconstruído:",
    texto_reconstruido
)

print()

print(
    "Igual à resposta original:",
    texto_reconstruido == texto_resposta
)


# ============================================================
# SALVAR JSON
# ============================================================

resultado_json = {

    "modelo": MODEL,

    "resposta": texto_resposta,

    "tokens": dados_visualizacao

}


with open(
    "resultado_qwen32b.json",
    "w",
    encoding="utf-8"
) as arquivo:

    json.dump(
        resultado_json,
        arquivo,
        ensure_ascii=False,
        indent=2
    )


print("\n==========================================")
print("JSON SALVO")
print("==========================================")

print(
    "resultado_qwen32b.json"
)

print()