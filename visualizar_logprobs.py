from pathlib import Path


HTML = r'''<!DOCTYPE html>

<html lang="pt-BR">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>História IA</title>


<style>

/* =========================================================
   BASE
   ========================================================= */

* {
    box-sizing: border-box;
}

html,
body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
}

body {

    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    background: #ffffff;

    color: #202123;

    overflow: hidden;
}


/* =========================================================
   APLICAÇÃO
   ========================================================= */

#app {

    width: 100%;
    height: 100vh;

    display: flex;
    flex-direction: column;
}


/* =========================================================
   CABEÇALHO
   ========================================================= */

#topbar {

    height: 64px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding: 0 28px;

    border-bottom: 1px solid #ececec;

    background: rgba(255,255,255,0.97);

    flex-shrink: 0;

    z-index: 20;
}


.brand {

    display: flex;

    align-items: center;

    gap: 10px;
}


.brand-icon {

    width: 30px;
    height: 30px;

    border-radius: 9px;

    display: flex;

    align-items: center;
    justify-content: center;

    background: #111827;

    color: white;

    font-size: 15px;

    font-weight: 700;
}


.brand-name {

    font-size: 16px;

    font-weight: 650;

    letter-spacing: -0.2px;
}


.model-info {

    font-size: 12px;

    color: #777;

    display: flex;

    align-items: center;

    gap: 7px;
}


.model-dot {

    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: #22c55e;

    flex-shrink: 0;
}


/* =========================================================
   ÁREA DA CONVERSA
   ========================================================= */

#chat {

    flex: 1;

    overflow-y: auto;

    scroll-behavior: smooth;
}


#chat-inner {

    width: min(850px, calc(100% - 40px));

    margin: 0 auto;

    padding: 60px 0 180px;
}


/* =========================================================
   TELA INICIAL
   ========================================================= */

#welcome {

    min-height: calc(100vh - 64px);

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    padding-bottom: 100px;
}


.welcome-icon {

    width: 54px;
    height: 54px;

    border-radius: 16px;

    background: #111827;

    color: white;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 25px;

    margin-bottom: 22px;
}


#welcome h1 {

    margin: 0 0 10px;

    font-size: 30px;

    font-weight: 650;

    letter-spacing: -1px;
}


#welcome p {

    margin: 0;

    color: #777;

    font-size: 15px;

    text-align: center;
}


/* =========================================================
   MENSAGEM DO USUÁRIO
   ========================================================= */

.user-message {

    display: flex;

    justify-content: flex-end;

    margin-bottom: 34px;
}


.user-bubble {

    max-width: 75%;

    background: #f1f1f1;

    border-radius: 18px;

    padding: 13px 17px;

    font-size: 15px;

    line-height: 1.55;

    color: #222;
}


/* =========================================================
   RESPOSTA DA IA
   ========================================================= */

.assistant-message {

    margin-bottom: 55px;
}


.assistant-header {

    display: flex;

    align-items: center;

    gap: 9px;

    margin-bottom: 14px;
}


.assistant-avatar {

    width: 27px;
    height: 27px;

    border-radius: 8px;

    background: #111827;

    color: white;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 13px;

    font-weight: 700;
}


.assistant-name {

    font-size: 14px;

    font-weight: 600;
}


.answer {

    font-size: 16px;

    line-height: 1.8;

    color: #242424;

    word-break: normal;

    overflow-wrap: break-word;
}


/* =========================================================
   TOKENS
   ========================================================= */

.token {

    cursor: default;

    border-radius: 3px;

    position: relative;

    transition:
        background 0.08s ease;
}


.token:hover,
.token.token-active {

    background: #e8eefc;

    box-shadow:
        0 0 0 2px #e8eefc;
}


/* =========================================================
   TOOLTIP
   ========================================================= */

#token-tooltip {

    position: fixed;

    z-index: 99999;

    width: 290px;

    /*
     * O tamanho deve ser determinado
     * exclusivamente pelo conteúdo.
     */
    height: auto;

    min-height: 0;

    max-height: none;

    overflow: visible;

    background: #111827;

    color: white;

    border-radius: 10px;

    /*
     * Espaçamento interno reduzido.
     */
    padding: 9px 11px;

    box-shadow:
        0 10px 28px rgba(0,0,0,0.20);

    display: none;

    font-size: 10px;

    line-height: 1.15;

    pointer-events: none;

    user-select: none;

    /*
     * Importante:
     * nenhuma transição de posição.
     */
    transition: none;
}


/* =========================================================
   TOKEN PRINCIPAL
   ========================================================= */

.tooltip-token {

    font-size: 14px;

    line-height: 1.15;

    font-weight: 650;

    margin: 0;

    padding: 0 0 6px 0;

    border-bottom:
        1px solid
        rgba(255,255,255,0.10);

    word-break: break-word;

    white-space: pre-wrap;
}


/* =========================================================
   INFORMAÇÕES PRINCIPAIS
   ========================================================= */

.tooltip-stat {

    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 10px;

    height: 18px;

    margin: 0;

    padding: 0;

    border-bottom:
        1px solid
        rgba(255,255,255,0.055);
}


.tooltip-stat span:first-child {

    color: #9ca3af;

    line-height: 1;
}


.tooltip-stat strong {

    color: #f3f4f6;

    font-weight: 600;

    line-height: 1;
}


/* =========================================================
   TÍTULO DAS ALTERNATIVAS
   ========================================================= */

.tooltip-title {

    margin: 6px 0 2px 0;

    padding: 0;

    color: #9ca3af;

    font-size: 8px;

    line-height: 1;

    text-transform: uppercase;

    letter-spacing: 0.07em;

    font-weight: 600;
}


/* =========================================================
   ALTERNATIVAS
   ========================================================= */

.alternative {

    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 10px;

    /*
     * AQUI está a principal redução
     * do espaçamento.
     */
    height: 16px;

    min-height: 16px;

    margin: 0;

    padding: 0;
}


.alt-token {

    font-family:
        ui-monospace,
        SFMono-Regular,
        Menlo,
        Monaco,
        Consolas,
        monospace;

    color: #f3f4f6;

    white-space: pre-wrap;

    overflow-wrap: anywhere;

    min-width: 0;

    flex: 1;

    line-height: 1;
}


.alt-prob {

    color: #9ca3af;

    white-space: nowrap;

    flex-shrink: 0;

    text-align: right;

    line-height: 1;
}


/* =========================================================
   ÁREA DE INPUT
   ========================================================= */

#input-area {

    position: fixed;

    left: 0;
    right: 0;
    bottom: 0;

    padding: 18px 20px 22px;

    background:
        linear-gradient(
            to top,
            #ffffff 72%,
            rgba(255,255,255,0)
        );

    z-index: 50;
}


#input-container {

    width: min(850px, 100%);

    margin: 0 auto;

    background: #ffffff;

    border: 1px solid #d9d9d9;

    border-radius: 18px;

    box-shadow:
        0 5px 25px rgba(0,0,0,0.08);

    display: flex;

    align-items: flex-end;

    padding: 10px;
}


#pergunta {

    flex: 1;

    border: none;

    outline: none;

    resize: none;

    font-family: inherit;

    font-size: 15px;

    line-height: 1.5;

    padding: 9px 11px;

    max-height: 150px;

    background: transparent;

    color: #222;
}


#pergunta::placeholder {

    color: #999;
}


#botao-perguntar {

    width: 38px;
    height: 38px;

    border: none;

    border-radius: 11px;

    background: #111827;

    color: white;

    cursor: pointer;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 17px;

    transition:
        transform 0.15s ease,
        opacity 0.15s ease;
}


#botao-perguntar:hover {

    transform: translateY(-1px);

    opacity: 0.9;
}


#botao-perguntar:disabled {

    opacity: 0.45;

    cursor: wait;

    transform: none;
}


#status {

    width: min(850px, 100%);

    margin: 8px auto 0;

    font-size: 11px;

    color: #999;

    text-align: center;
}


#erro {

    width: min(850px, 100%);

    margin: 8px auto;

    color: #b42318;

    font-size: 13px;

    text-align: center;

    display: none;
}


/* =========================================================
   RESPONSIVO
   ========================================================= */

@media (max-width: 700px) {

    #topbar {

        padding: 0 16px;
    }

    .model-info {

        display: none;
    }

    #chat-inner {

        width: calc(100% - 28px);

        padding-top: 35px;
    }

    .user-bubble {

        max-width: 88%;
    }

    #token-tooltip {

        width: 290px;

        max-width:
            calc(100vw - 20px);
    }

    #welcome h1 {

        font-size: 26px;
    }
}

</style>

</head>


<body>


<div id="app">


    <!-- =====================================================
         CABEÇALHO
         ===================================================== -->

    <header id="topbar">

        <div class="brand">

            <div class="brand-icon">
                ✦
            </div>

            <div class="brand-name">
                História IA
            </div>

        </div>


        <div class="model-info">

            <span class="model-dot"></span>

            <span id="model-name">
                Qwen3-4B-Instruct-2507 · Hugging Face / Nscale
            </span>

        </div>

    </header>



    <!-- =====================================================
         CHAT
         ===================================================== -->

    <main id="chat">

        <div id="chat-inner">


            <!-- TELA INICIAL -->

            <section id="welcome">

                <div class="welcome-icon">
                    ✦
                </div>

                <h1>
                    História IA
                </h1>

                <p>
                    Faça uma pergunta e explore como a resposta é gerada.
                </p>

            </section>


            <!-- MENSAGENS -->

            <div id="messages"></div>


        </div>

    </main>



    <!-- =====================================================
         INPUT
         ===================================================== -->

    <div id="input-area">

        <div id="input-container">

            <textarea
                id="pergunta"
                rows="1"
                placeholder="Faça uma pergunta..."
            ></textarea>


            <button
                id="botao-perguntar"
                title="Perguntar"
            >
                ↑
            </button>

        </div>


        <div id="status"></div>

        <div id="erro"></div>

    </div>


</div>



<!-- =========================================================
     TOOLTIP
     ========================================================= -->

<div id="token-tooltip"></div>



<script>


/* =========================================================
   ELEMENTOS
   ========================================================= */

const perguntaInput =
    document.getElementById("pergunta");

const botao =
    document.getElementById("botao-perguntar");

const messages =
    document.getElementById("messages");

const welcome =
    document.getElementById("welcome");

const status =
    document.getElementById("status");

const erro =
    document.getElementById("erro");

const tooltip =
    document.getElementById("token-tooltip");


let tokenAtivo = null;

let tooltipTimer = null;


/* =========================================================
   PERGUNTAR
   ========================================================= */

async function perguntar() {

    const pergunta =
        perguntaInput.value.trim();


    if (!pergunta) {
        return;
    }


    erro.style.display =
        "none";


    botao.disabled =
        true;


    status.textContent =
        "A IA está gerando a resposta...";


    welcome.style.display =
        "none";


    /*
     * MENSAGEM DO USUÁRIO
     */

    const userMessage =
        document.createElement("div");


    userMessage.className =
        "user-message";


    userMessage.innerHTML = `

        <div class="user-bubble">

            ${escaparHTML(pergunta)}

        </div>

    `;


    messages.appendChild(
        userMessage
    );


    /*
     * RESPOSTA
     */

    const assistantMessage =
        document.createElement("div");


    assistantMessage.className =
        "assistant-message";


    assistantMessage.innerHTML = `

        <div class="assistant-header">

            <div class="assistant-avatar">
                ✦
            </div>

            <div class="assistant-name">
                História IA
            </div>

        </div>

        <div class="answer"></div>

    `;


    messages.appendChild(
        assistantMessage
    );


    const answer =
        assistantMessage.querySelector(
            ".answer"
        );


    perguntaInput.value =
        "";


    ajustarTextarea();


    scrollFinal();


    try {

        const response =
            await fetch(
                "/api/perguntar",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        pergunta:
                            pergunta
                    })

                }
            );


        const dados =
            await response.json();


        if (!response.ok) {

            throw new Error(
                dados.erro ||
                "Erro ao consultar a IA."
            );

        }


        /*
         * ATUALIZA O MODELO
         */

        if (dados.modelo) {

            const nomeModelo =
                dados.modelo.replace(
                    "Qwen/",
                    ""
                );


            document.getElementById(
                "model-name"
            ).textContent =

                nomeModelo
                + " · "
                + (
                    dados.provedor ||
                    "Hugging Face"
                );

        }


        /*
         * RENDERIZA
         */

        renderizarResposta(

            answer,

            dados.resposta,

            dados.tokens || []

        );


        status.textContent =
            "Passe o cursor sobre os tokens para explorar a geração.";


        scrollFinal();


    } catch (e) {

        erro.textContent =
            e.message;


        erro.style.display =
            "block";


        answer.textContent =
            "";

    }


    botao.disabled =
        false;

}



/* =========================================================
   RENDERIZAR RESPOSTA
   ========================================================= */

function renderizarResposta(
    elemento,
    texto,
    tokens
) {

    elemento.innerHTML =
        "";


    if (!tokens.length) {

        elemento.textContent =
            texto || "";

        return;

    }


    tokens.forEach(
        (dados) => {

            const span =
                document.createElement(
                    "span"
                );


            span.className =
                "token";


            span.textContent =
                dados.token;


            span.addEventListener(
                "mouseenter",
                () => {

                    mostrarTooltip(
                        span,
                        dados
                    );

                }
            );


            span.addEventListener(
                "mouseleave",
                () => {

                    esconderTooltip(
                        span
                    );

                }
            );


            elemento.appendChild(
                span
            );

        }
    );

}



/* =========================================================
   MOSTRAR TOOLTIP
   ========================================================= */

function mostrarTooltip(
    elemento,
    dados
) {

    clearTimeout(
        tooltipTimer
    );


    if (tokenAtivo) {

        tokenAtivo.classList.remove(
            "token-active"
        );

    }


    tokenAtivo =
        elemento;


    elemento.classList.add(
        "token-active"
    );


    const logprob =
        Number(
            dados.logprob
        );


    const probabilidade =
        Math.exp(
            logprob
        ) * 100;


    let html =
        "";


    /*
     * TOKEN
     */

    html += `

        <div class="tooltip-token">

            ${escaparHTML(
                dados.token || " "
            )}

        </div>

    `;


    /*
     * PROBABILIDADE
     */

    html += `

        <div class="tooltip-stat">

            <span>
                Probabilidade
            </span>

            <strong>
                ${formatarProbabilidade(
                    probabilidade
                )}
            </strong>

        </div>

    `;


    /*
     * LOGPROB
     */

    html += `

        <div class="tooltip-stat">

            <span>
                Logprob
            </span>

            <strong>
                ${logprob.toFixed(4)}
            </strong>

        </div>

    `;


    /*
     * ALTERNATIVAS
     */

    if (
        dados.alternativas &&
        dados.alternativas.length
    ) {

        html += `

            <div class="tooltip-title">

                Outras possibilidades

            </div>

        `;


        dados.alternativas.forEach(
            (alternativa) => {

                const prob =
                    Math.exp(
                        Number(
                            alternativa.logprob
                        )
                    ) * 100;


                html += `

                    <div class="alternative">

                        <span class="alt-token">

                            ${escaparHTML(
                                alternativa.token ||
                                " "
                            )}

                        </span>

                        <span class="alt-prob">

                            ${formatarProbabilidade(
                                prob
                            )}

                        </span>

                    </div>

                `;

            }
        );

    }


    tooltip.innerHTML =
        html;


    tooltip.style.display =
        "block";


    /*
     * Força o navegador a calcular
     * a altura real antes do posicionamento.
     */

    tooltip.offsetHeight;


    posicionarTooltip(
        elemento
    );

}



/* =========================================================
   ESCONDER TOOLTIP
   ========================================================= */

function esconderTooltip(
    elemento
) {

    tooltipTimer =
        setTimeout(
            () => {

                if (
                    tokenAtivo === elemento
                ) {

                    tooltip.style.display =
                        "none";


                    elemento.classList.remove(
                        "token-active"
                    );


                    tokenAtivo =
                        null;

                }

            },
            50
        );

}



/* =========================================================
   POSICIONAR TOOLTIP
   =========================================================

   REGRA:

   SEMPRE ACIMA DO TOKEN.

   Nunca abaixo.
   Nunca à direita.
   Nunca à esquerda.

   Se não couber horizontalmente,
   apenas deslocamos a janela para
   dentro da tela.

   ========================================================= */

function posicionarTooltip(
    elemento
) {

    const rect =
        elemento.getBoundingClientRect();


    const tooltipRect =
        tooltip.getBoundingClientRect();


    const margem =
        10;


    const distancia =
        8;


    /*
     * CENTRO HORIZONTAL DO TOKEN
     */

    let left =
        rect.left +
        (rect.width / 2) -
        (tooltipRect.width / 2);


    /*
     * GARANTE QUE NÃO SAIA
     * PELAS LATERAIS.
     */

    left =
        Math.max(
            margem,
            Math.min(
                left,
                window.innerWidth -
                tooltipRect.width -
                margem
            )
        );


    /*
     * SEMPRE ACIMA.
     */

    let top =
        rect.top -
        tooltipRect.height -
        distancia;


    /*
     * Se houver espaço acima:
     * usa exatamente essa posição.
     */

    if (
        top >= margem
    ) {

        tooltip.style.left =
            `${left}px`;

        tooltip.style.top =
            `${top}px`;

        return;

    }


    /*
     * =====================================================
     * CASO ESPECIAL:
     * TOKEN MUITO PRÓXIMO DO TOPO
     * =====================================================
     *
     * Não colocamos o tooltip abaixo.
     *
     * Ele fica preso ao topo da janela,
     * preservando a regra de que o tooltip
     * pertence à região superior.
     */

    tooltip.style.left =
        `${left}px`;


    tooltip.style.top =
        `${margem}px`;

}



/* =========================================================
   PROBABILIDADE
   ========================================================= */

function formatarProbabilidade(
    valor
) {

    if (
        !Number.isFinite(valor)
    ) {

        return "—";

    }


    if (
        valor >= 99.999999
    ) {

        return "≈ 100%";

    }


    if (
        valor >= 1
    ) {

        return valor.toFixed(2)
            + "%";

    }


    if (
        valor >= 0.01
    ) {

        return valor.toFixed(4)
            + "%";

    }


    return valor.toExponential(2)
        + "%";

}



/* =========================================================
   ESCAPAR HTML
   ========================================================= */

function escaparHTML(
    texto
) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        texto;


    return div.innerHTML;

}



/* =========================================================
   ENTER
   ========================================================= */

perguntaInput.addEventListener(
    "keydown",
    (evento) => {

        if (
            evento.key === "Enter" &&
            !evento.shiftKey
        ) {

            evento.preventDefault();

            perguntar();

        }

    }
);


/* =========================================================
   BOTÃO
   ========================================================= */

botao.addEventListener(
    "click",
    perguntar
);


/* =========================================================
   TEXTAREA
   ========================================================= */

perguntaInput.addEventListener(
    "input",
    ajustarTextarea
);


function ajustarTextarea() {

    perguntaInput.style.height =
        "auto";


    perguntaInput.style.height =
        Math.min(
            perguntaInput.scrollHeight,
            150
        ) + "px";

}



/* =========================================================
   SCROLL
   ========================================================= */

function scrollFinal() {

    const chat =
        document.getElementById(
            "chat"
        );


    setTimeout(
        () => {

            chat.scrollTo({

                top:
                    chat.scrollHeight,

                behavior:
                    "smooth"

            });

        },
        50
    );

}



/* =========================================================
   ESCONDER TOOLTIP AO ROLAR
   ========================================================= */

document
    .getElementById("chat")
    .addEventListener(
        "scroll",
        () => {

            tooltip.style.display =
                "none";


            if (tokenAtivo) {

                tokenAtivo.classList.remove(
                    "token-active"
                );

                tokenAtivo =
                    null;

            }

        }
    );



/* =========================================================
   ESCONDER AO REDIMENSIONAR
   ========================================================= */

window.addEventListener(
    "resize",
    () => {

        tooltip.style.display =
            "none";


        if (tokenAtivo) {

            tokenAtivo.classList.remove(
                "token-active"
            );

            tokenAtivo =
                null;

        }

    }
);


</script>


</body>

</html>
'''


arquivo = Path(
    "resultado_logprobs.html"
)


arquivo.write_text(
    HTML,
    encoding="utf-8"
)


print(
    f"HTML criado em: {arquivo.resolve()}"
)