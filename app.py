import os

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

MODEL = "Qwen/Qwen3-4B-Instruct-2507"

client = InferenceClient(
    provider="auto",
    api_key=HF_TOKEN
)

app = Flask(__name__)


# ============================================================
# PÁGINA
# ============================================================

@app.route("/")
def index():
    return send_file("resultado_logprobs.html")


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
    # DOCUMENTO — AGORA É OPCIONAL
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
            "presentes nessa fonte."
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
    # CONSULTAR QWEN
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

            max_tokens=300,

            logprobs=True,

            top_logprobs=5

        )


    except Exception as erro:

        print("\nERRO NA API:")
        print(erro)

        return jsonify({
            "erro": str(erro)
        }), 500


    # ========================================================
    # RESPOSTA
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
    # LOGPROBS
    # ========================================================

    tokens = []


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

                    alternativas.append({

                        "token":
                            getattr(
                                alternativa,
                                "token",
                                ""
                            ),

                        "logprob":
                            getattr(
                                alternativa,
                                "logprob",
                                None
                            )

                    })


            tokens.append({

                "token":
                    token_texto,

                "logprob":
                    logprob,

                "alternativas":
                    alternativas

            })


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


    print("\nRESPOSTA:")
    print(texto_resposta)


    print("\nQUANTIDADE DE TOKENS:")
    print(len(tokens))


    if tokens:

        print("\nPRIMEIROS TOKENS:")

        for token in tokens[:10]:

            print(
                repr(token["token"]),
                token["logprob"]
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
            tokens

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