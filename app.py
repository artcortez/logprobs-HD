import os
import math

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file
from huggingface_hub import InferenceClient


# ============================================================
# CONFIGURAÇÃO
# ============================================================

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise RuntimeError(
        "HF_TOKEN não encontrado no arquivo .env"
    )

MODEL = "Qwen/Qwen3-32B"

client = InferenceClient(
    provider="nscale",
    api_key=HF_TOKEN
)

app = Flask(__name__)


# ============================================================
# PÁGINA
# ============================================================

@app.route("/")
def index():

    return send_file(
        "resultado_logprobs.html"
    )


# ============================================================
# CONVERTER LOGPROB EM PROBABILIDADE
# ============================================================

def logprob_para_probabilidade(logprob):

    if logprob is None:
        return None

    return math.exp(logprob)


# ============================================================
# API
# ============================================================

@app.route("/api/perguntar", methods=["POST"])
def perguntar():

    pergunta = request.form.get(
        "pergunta",
        ""
    ).strip()


    if not pergunta:

        return jsonify({
            "erro": "Digite uma pergunta."
        }), 400


    # ========================================================
    # DOCUMENTO — OPCIONAL
    # ========================================================

    arquivo = request.files.get(
        "arquivo"
    )

    texto_fonte = None
    nome_arquivo = None


    if arquivo and arquivo.filename:

        nome_arquivo = arquivo.filename

        try:

            dados_arquivo = arquivo.read()

            try:

                texto_fonte = dados_arquivo.decode(
                    "utf-8"
                )

            except UnicodeDecodeError:

                texto_fonte = dados_arquivo.decode(
                    "latin-1"
                )

            texto_fonte = texto_fonte.strip()


        except Exception as erro:

            return jsonify({
                "erro":
                    f"Erro ao ler a fonte: {erro}"
            }), 400


    # ========================================================
    # DEFINIR PROMPT
    # ========================================================

    if texto_fonte:

        prompt = f"""
Você está analisando uma fonte histórica.

Utilize exclusivamente as informações presentes
na fonte fornecida abaixo.

Não acrescente informações externas à fonte.

Não invente informações.

Se a pergunta não puder ser respondida com base
na fonte, diga claramente que essa informação
não está presente no documento.

Não mencione exemplos históricos externos para
explicar aquilo que não está presente na fonte.

FONTE HISTÓRICA
==================================================

{texto_fonte}

==================================================

PERGUNTA

{pergunta}
"""


        system_prompt = (
            "Você é um assistente especializado "
            "em análise de fontes históricas. "
            "Responda em português. "
            "Responda em texto simples. "
            "Não utilize Markdown. "
            "Não utilize asteriscos. "
            "Não utilize hashtags. "
            "Não utilize listas com hífens. "
            "Quando houver uma fonte fornecida, "
            "utilize exclusivamente as informações "
            "presentes nessa fonte. "
            "Não acrescente exemplos históricos "
            "externos à fonte."
        )


    else:

        # ----------------------------------------------------
        # CONVERSA LIVRE
        # ----------------------------------------------------

        prompt = pergunta


        system_prompt = (
            "Você é um assistente especializado "
            "em História. "
            "Responda em português. "
            "Responda em texto simples. "
            "Não utilize Markdown. "
            "Não utilize asteriscos. "
            "Não utilize hashtags. "
            "Não utilize listas com hífens. "
            "Responda de forma clara e objetiva."
        )


    # ========================================================
    # CONSULTAR QWEN3-32B
    # ========================================================

    try:

        resposta = client.chat.completions.create(

            model=MODEL,

            messages=[

                {
                    "role": "system",
                    "content": system_prompt
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


    except Exception as erro:

        print("\nERRO NA API:")
        print(erro)

        return jsonify({
            "erro": str(erro)
        }), 500


    # ========================================================
    # RESPOSTA PÚBLICA
    # ========================================================

    escolha = resposta.choices[0]

    texto_resposta = (
        escolha.message.content
        or ""
    )


    # ========================================================
    # LIMPAR MARCADORES ESPECIAIS
    # ========================================================

    texto_resposta = (
        texto_resposta
        .replace(
            "<|im_end|>",
            ""
        )
        .replace(
            "<|endoftext|>",
            ""
        )
        .strip()
    )


    # ========================================================
    # EXTRAIR TODOS OS LOGPROBS
    # ========================================================

    tokens_completos = []

    logprobs = escolha.logprobs


    if (
        logprobs is not None
        and getattr(
            logprobs,
            "content",
            None
        ) is not None
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

                    alt_token = getattr(
                        alternativa,
                        "token",
                        ""
                    )

                    alt_logprob = getattr(
                        alternativa,
                        "logprob",
                        None
                    )


                    alternativas.append({

                        "token":
                            alt_token,

                        "logprob":
                            alt_logprob,

                        "probabilidade":
                            logprob_para_probabilidade(
                                alt_logprob
                            )

                    })


            tokens_completos.append({

                "token":
                    token_texto,

                "logprob":
                    logprob,

                "probabilidade":
                    logprob_para_probabilidade(
                        logprob
                    ),

                "alternativas":
                    alternativas

            })


    # ========================================================
    # RECONSTRUIR TEXTO DOS TOKENS
    # ========================================================

    texto_tokens = "".join(

        token["token"]

        for token in tokens_completos
    )


    # ========================================================
    # LOCALIZAR A RESPOSTA PÚBLICA
    # ========================================================

    posicao = texto_tokens.find(
        texto_resposta
    )


    # ========================================================
    # ALINHAMENTO DOS TOKENS
    # ========================================================

    tokens_resposta = []


    if posicao != -1:

        inicio_resposta = posicao

        fim_resposta = (
            posicao +
            len(texto_resposta)
        )


        posicao_atual = 0


        for token in tokens_completos:

            token_texto = token["token"]


            inicio_token = (
                posicao_atual
            )


            fim_token = (
                posicao_atual +
                len(token_texto)
            )


            posicao_atual = fim_token


            # ----------------------------------------------
            # Token ainda antes da resposta
            # ----------------------------------------------

            if fim_token <= inicio_resposta:

                continue


            # ----------------------------------------------
            # Token pertence à resposta
            # ----------------------------------------------

            tokens_resposta.append(
                token
            )


            # ----------------------------------------------
            # Chegamos ao final
            # ----------------------------------------------

            if fim_token >= fim_resposta:

                break


    else:

        print(
            "\nAVISO: não foi possível "
            "alinhar os tokens à resposta."
        )


    # ========================================================
    # VERIFICAÇÃO DO ALINHAMENTO
    # ========================================================

    texto_reconstruido = "".join(

        token["token"]

        for token in tokens_resposta
    )


    alinhamento_correto = (
        texto_reconstruido ==
        texto_resposta
    )


    # ========================================================
    # DEBUG
    # ========================================================

    print("\n==========================================")

    print("PERGUNTA:")
    print(pergunta)


    print("\nDOCUMENTO:")

    if nome_arquivo:

        print(nome_arquivo)

    else:

        print("Nenhum documento")


    print("\nMODELO:")
    print(MODEL)


    print("\nRESPOSTA:")
    print(texto_resposta)


    print("\nTOKENS COMPLETOS:")
    print(
        len(tokens_completos)
    )


    print("\nTOKENS DA RESPOSTA:")
    print(
        len(tokens_resposta)
    )


    print("\nALINHAMENTO:")
    print(
        alinhamento_correto
    )


    if tokens_resposta:

        print("\nPRIMEIROS TOKENS DA RESPOSTA:")

        for token in tokens_resposta[:10]:

            print(
                repr(
                    token["token"]
                ),
                "| logprob:",
                token["logprob"],
                "| probabilidade:",
                token["probabilidade"]
            )


    print("==========================================\n")


    # ========================================================
    # RETORNO
    # ========================================================

    return jsonify({

        "pergunta":
            pergunta,

        "arquivo":
            nome_arquivo,

        "tem_fonte":
            bool(texto_fonte),

        "modelo":
            MODEL,

        "provedor":
            "Hugging Face / Nscale",

        "resposta":
            texto_resposta,

        "tokens":
            tokens_resposta,

        "quantidade_tokens":
            len(tokens_resposta),

        "alinhamento_correto":
            alinhamento_correto

    })


# ============================================================
# EXECUTAR
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )