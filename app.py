import json
import math
import os
import socket
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file


# ============================================================
# CONFIGURAÇÃO
# ============================================================

load_dotenv()

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

MODEL = "@cf/qwen/qwen3.8-27b"
PROVIDER = "Cloudflare Workers AI"

TOP_LOGPROBS = 5
MAX_COMPLETION_TOKENS = 1000
TIMEOUT_SECONDS = 120

BASE_DIR = Path(__file__).resolve().parent
HTML_FILE = BASE_DIR / "resultado_logprobs.html"

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

API_URL = (
    "https://api.cloudflare.com/client/v4/accounts/"
    f"{CLOUDFLARE_ACCOUNT_ID}/ai/v1/chat/completions"
    if CLOUDFLARE_ACCOUNT_ID
    else None
)


# ============================================================
# UTILITÁRIOS
# ============================================================

def logprob_para_probabilidade(logprob):
    """Converte logprob natural em probabilidade."""
    if logprob is None:
        return None

    try:
        valor = math.exp(float(logprob))
        return valor if math.isfinite(valor) else None
    except (TypeError, ValueError, OverflowError):
        return None


def ler_fonte(arquivo):
    """Lê uma fonte textual sem descartar acentos."""
    if not arquivo or not arquivo.filename:
        return None, None

    nome = Path(arquivo.filename).name
    extensao = Path(nome).suffix.lower()

    extensoes_permitidas = {".txt", ".md", ".csv"}

    if extensao not in extensoes_permitidas:
        raise ValueError(
            "Formato não permitido. Envie um arquivo .txt, .md ou .csv."
        )

    dados = arquivo.read()

    if not dados:
        raise ValueError("O arquivo enviado está vazio.")

    # UTF-8 é a codificação preferencial.
    try:
        texto = dados.decode("utf-8-sig")
    except UnicodeDecodeError:
        # Alternativa para arquivos antigos do Windows.
        try:
            texto = dados.decode("cp1252")
        except UnicodeDecodeError:
            raise ValueError(
                "Não foi possível interpretar a codificação do arquivo."
            )

    texto = texto.strip()

    if not texto:
        raise ValueError("O arquivo não contém texto.")

    return texto, nome


def montar_prompts(pergunta, texto_fonte=None):
    """Prepara as instruções e a mensagem enviada ao modelo."""

    if texto_fonte:
        system_prompt = (
            "Você é um assistente especializado em análise de fontes "
            "históricas. Responda em português, com clareza e objetividade. "
            "Use texto simples, sem Markdown. Utilize exclusivamente as "
            "informações da fonte fornecida. Não invente informações nem "
            "acrescente exemplos externos. Se a fonte não permitir responder "
            "à pergunta, informe claramente essa limitação."
        )

        prompt = (
            "Analise a fonte histórica a seguir e responda à pergunta "
            "utilizando exclusivamente as informações presentes no documento.\n\n"
            "INÍCIO DA FONTE HISTÓRICA\n"
            f"{texto_fonte}\n"
            "FIM DA FONTE HISTÓRICA\n\n"
            f"PERGUNTA:\n{pergunta}"
        )
    else:
        system_prompt = (
            "Você é um assistente especializado em História. "
            "Responda em português, de forma clara e objetiva, usando "
            "texto simples, sem Markdown."
        )
        prompt = pergunta

    return system_prompt, prompt


def consultar_cloudflare(system_prompt, prompt):
    """Consulta o endpoint compatível com a API de chat da OpenAI."""

    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        raise RuntimeError(
            "Configure CLOUDFLARE_ACCOUNT_ID e CLOUDFLARE_API_TOKEN "
            "nas variáveis de ambiente."
        )

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "logprobs": True,
        "top_logprobs": TOP_LOGPROBS,
        "max_completion_tokens": MAX_COMPLETION_TOKENS,
        "temperature": 0,
        "chat_template_kwargs": {
            "enable_thinking": False
        },
    }

    dados = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    requisicao = Request(
        API_URL,
        data=dados,
        headers={
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(requisicao, timeout=TIMEOUT_SECONDS) as resposta:
            corpo = resposta.read().decode("utf-8")
            resultado = json.loads(corpo)

    except HTTPError as erro:
        detalhe = erro.read().decode("utf-8", errors="replace")

        # Não devolver cabeçalhos ou credenciais ao navegador.
        print(f"Erro HTTP do Cloudflare: {erro.code} — {detalhe[:1500]}")

        if erro.code == 401:
            raise RuntimeError(
                "O Cloudflare recusou a autenticação. Verifique o token."
            )

        if erro.code == 429:
            raise RuntimeError(
                "Limite de utilização atingido ou muitas requisições. "
                "Tente novamente mais tarde."
            )

        raise RuntimeError(
            f"O Cloudflare retornou o erro HTTP {erro.code}."
        )

    except URLError as erro:
        print(f"Erro de conexão com Cloudflare: {erro}")
        raise RuntimeError(
            "Não foi possível conectar ao Cloudflare Workers AI."
        )

    except (TimeoutError, socket.timeout):
        raise RuntimeError(
            "A Cloudflare demorou demais para responder. "
            "Tente novamente com uma pergunta mais curta."
        )

    if resultado.get("error"):
        detalhe = resultado["error"]
        print(f"Erro informado pela API: {detalhe}")
        raise RuntimeError("A API do Cloudflare não conseguiu gerar a resposta.")

    escolhas = resultado.get("choices") or []

    if not escolhas:
        raise RuntimeError("A API não retornou nenhuma resposta.")

    return escolhas[0]


def extrair_tokens(escolha):
    """Converte os logprobs da API para o formato da interface."""

    mensagem = escolha.get("message") or {}
    texto_resposta = mensagem.get("content") or ""

    if not isinstance(texto_resposta, str):
        texto_resposta = str(texto_resposta)

    texto_resposta = (
        texto_resposta
        .replace("<|im_end|>", "")
        .replace("<|endoftext|>", "")
        .strip()
    )

    logprobs_obj = escolha.get("logprobs") or {}
    itens = logprobs_obj.get("content") or []

    tokens_completos = []

    for item in itens:
        token_texto = item.get("token") or ""

        # Tokens especiais de encerramento não devem aparecer
        # como parte da resposta visível.
        if token_texto in {"<|im_end|>", "<|endoftext|>"}:
            continue

        logprob = item.get("logprob")

        alternativas = []

        for alternativa in item.get("top_logprobs") or []:
            alt_token = alternativa.get("token") or ""
            alt_logprob = alternativa.get("logprob")

            if alt_token in {"<|im_end|>", "<|endoftext|>"}:
                continue

            alternativas.append({
                "token": alt_token,
                "logprob": alt_logprob,
                "probabilidade": logprob_para_probabilidade(
                    alt_logprob
                ),
            })

        tokens_completos.append({
            "token": token_texto,
            "logprob": logprob,
            "probabilidade": logprob_para_probabilidade(logprob),
            "alternativas": alternativas,
        })

    # A API pode retornar logprobs ausentes ou incompletos.
    # Só consideramos alinhados os tokens que reproduzem exatamente
    # o texto público da resposta.
    texto_tokens = "".join(
        token["token"] for token in tokens_completos
    )

    posicao = texto_tokens.find(texto_resposta)

    if posicao == -1:
        return texto_resposta, [], False

    fim_resposta = posicao + len(texto_resposta)
    tokens_resposta = []
    posicao_atual = 0

    for token in tokens_completos:
        token_texto = token["token"]
        inicio_token = posicao_atual
        fim_token = inicio_token + len(token_texto)
        posicao_atual = fim_token

        # Token completamente anterior ao texto público.
        if fim_token <= posicao:
            continue

        # Não inclua tokens que ultrapassem o fim da resposta.
        if inicio_token >= fim_resposta:
            break

        # Se o token cruza os limites da resposta, não é seguro
        # recortá-lo: isso alteraria a identidade do token.
        if inicio_token < posicao or fim_token > fim_resposta:
            return texto_resposta, [], False

        tokens_resposta.append(token)

    texto_reconstruido = "".join(
        token["token"] for token in tokens_resposta
    )

    alinhamento_correto = texto_reconstruido == texto_resposta

    if not alinhamento_correto:
        return texto_resposta, [], False

    return texto_resposta, tokens_resposta, True


# ============================================================
# PÁGINA
# ============================================================

@app.route("/")
def index():
    if not HTML_FILE.is_file():
        return (
            "Arquivo resultado_logprobs.html não encontrado.",
            500,
        )

    return send_file(HTML_FILE)


# ============================================================
# API
# ============================================================

@app.route("/api/perguntar", methods=["POST"])
def perguntar():
    # Aceita tanto FormData (pergunta + arquivo) quanto JSON.
    dados_json = request.get_json(silent=True)

    if isinstance(dados_json, dict):
        pergunta = str(dados_json.get("pergunta") or "").strip()
    else:
        pergunta = str(request.form.get("pergunta") or "").strip()

    if not pergunta:
        return jsonify({"erro": "Digite uma pergunta."}), 400

    try:
        arquivo = request.files.get("arquivo")
        texto_fonte, nome_arquivo = ler_fonte(arquivo)
        system_prompt, prompt = montar_prompts(pergunta, texto_fonte)

        escolha = consultar_cloudflare(system_prompt, prompt)

        texto_resposta, tokens, alinhamento = extrair_tokens(escolha)

        if not texto_resposta:
            motivo = escolha.get("finish_reason", "desconhecido")
            print(f"Resposta vazia; finish_reason={motivo}")
            return jsonify({
                "erro": (
                    "O modelo não retornou texto visível. "
                    "Tente reformular a pergunta."
                )
            }), 502

        resposta = {
            "pergunta": pergunta,
            "arquivo": nome_arquivo,
            "tem_fonte": bool(texto_fonte),
            "modelo": MODEL,
            "provedor": PROVIDER,
            "resposta": texto_resposta,
            "tokens": tokens,
            "quantidade_tokens": len(tokens),
            "alinhamento_correto": alinhamento,
        }

        print(
            f"Modelo: {MODEL} | "
            f"Tokens alinhados: {len(tokens)} | "
            f"Alinhamento correto: {alinhamento}"
        )

        return jsonify(resposta)

    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400

    except RuntimeError as erro:
        print(f"Erro na consulta: {erro}")
        return jsonify({"erro": str(erro)}), 502

    except Exception:
        # Registre detalhes no servidor, não exponha rastreamentos
        # internos ao navegador.
        app.logger.exception("Erro inesperado na rota /api/perguntar")
        return jsonify({
            "erro": "Ocorreu um erro interno ao processar a pergunta."
        }), 500


# ============================================================
# EXECUÇÃO LOCAL
# ============================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "5000")),
        debug=False,
    )