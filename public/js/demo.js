// Interface do simulador PID: lê os controles, chama /api/simular e desenha o resultado.

const ESPERA_DEBOUNCE_MS = 250;

const formulario = document.getElementById("controles");
const areaGrafico = document.getElementById("grafico-area");
const avisoCarregando = document.getElementById("carregando");
const caixaErro = document.getElementById("erro");
const botoesPreset = document.querySelectorAll(".presets button");

let grafico = null;
let ultimoDesenho = null; // guardado para redesenhar quando o tema muda
let temporizador = null;
let requisicaoAtual = null;

// --- Controles ---------------------------------------------------------------

// Lê os parâmetros dos campos numéricos. Campo vazio vira null, e o back-end
// responde com uma mensagem de erro clara.
function lerParametros() {
    const parametros = {};
    formulario.querySelectorAll('input[type="number"]').forEach((campo) => {
        const valor = campo.valueAsNumber;
        parametros[campo.dataset.param] = Number.isNaN(valor) ? null : valor;
    });
    return parametros;
}

// Mantém slider e campo numérico do mesmo parâmetro com o mesmo valor.
function sincronizar(origem) {
    formulario.querySelectorAll(`[data-param="${origem.dataset.param}"]`).forEach((campo) => {
        if (campo !== origem) campo.value = origem.value;
    });
}

formulario.addEventListener("input", (evento) => {
    sincronizar(evento.target);
    marcarPreset(null);
    agendarSimulacao();
});

// Enter no campo numérico não deve recarregar a página.
formulario.addEventListener("submit", (evento) => evento.preventDefault());

// --- Presets -----------------------------------------------------------------

function marcarPreset(botaoAtivo) {
    botoesPreset.forEach((botao) => botao.setAttribute("aria-pressed", botao === botaoAtivo));
}

botoesPreset.forEach((botao) => {
    botao.addEventListener("click", () => {
        for (const param of ["kp", "ki", "kd"]) {
            const campo = document.getElementById(param);
            campo.value = botao.dataset[param];
            sincronizar(campo);
        }
        marcarPreset(botao);
        simular();
    });
});

// --- Simulação ---------------------------------------------------------------

// Debounce: espera o usuário parar de mexer antes de chamar a API.
function agendarSimulacao() {
    clearTimeout(temporizador);
    temporizador = setTimeout(simular, ESPERA_DEBOUNCE_MS);
}

async function simular() {
    clearTimeout(temporizador);

    // Cancela a requisição anterior: só a resposta mais recente deve aparecer.
    if (requisicaoAtual) requisicaoAtual.abort();
    requisicaoAtual = new AbortController();

    const parametros = lerParametros();
    mostrarCarregando(true);
    try {
        const resposta = await fetch("/api/simular", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(parametros),
            signal: requisicaoAtual.signal,
        });
        const dados = await resposta.json();
        if (!resposta.ok) throw new Error(dados.erro || "Erro ao simular.");

        desenharGrafico(dados, parametros.setpoint, parametros.tempo_total);
        mostrarMetricas(dados.metricas);
        mostrarErro(null);
    } catch (erro) {
        if (erro.name === "AbortError") return; // substituída por uma mais nova
        mostrarErro(erro instanceof SyntaxError ? "Resposta inválida do servidor." : erro.message);
        mostrarMetricas(null);
    }
    mostrarCarregando(false);
}

// --- Exibição ----------------------------------------------------------------

function mostrarCarregando(ativo) {
    avisoCarregando.hidden = !ativo;
    areaGrafico.classList.toggle("ocupado", ativo);
    areaGrafico.setAttribute("aria-busy", ativo);
}

function mostrarErro(mensagem) {
    caixaErro.hidden = !mensagem;
    caixaErro.textContent = mensagem || "";
}

function formatar(valor, unidade) {
    if (valor === null || valor === undefined) return "não atingiu";
    return `${valor.toLocaleString("pt-BR", { maximumFractionDigits: 2 })} ${unidade}`;
}

function mostrarMetricas(metricas) {
    document.getElementById("overshoot").textContent = metricas ? formatar(metricas.overshoot_pct, "%") : "—";
    document.getElementById("subida").textContent = metricas ? formatar(metricas.tempo_subida, "s") : "—";
    document.getElementById("acomodacao").textContent = metricas ? formatar(metricas.tempo_acomodacao, "s") : "—";
}

// As cores do gráfico vêm das variáveis CSS, para seguir o tema atual.
function coresDoTema() {
    const estilo = getComputedStyle(document.documentElement);
    const cor = (variavel) => estilo.getPropertyValue(variavel).trim();
    return {
        setpoint: cor("--grafico-setpoint"),
        saida: cor("--destaque"),
        controle: cor("--grafico-controle"),
        texto: cor("--texto-suave"),
        grade: cor("--borda"),
    };
}

function desenharGrafico(dados, setpoint, tempoTotal) {
    ultimoDesenho = [dados, setpoint, tempoTotal];
    const pontos = (serie) => dados.tempo.map((t, i) => ({ x: t, y: serie[i] }));
    const series = [
        [{ x: 0, y: setpoint }, { x: tempoTotal, y: setpoint }],
        pontos(dados.saida),
        pontos(dados.controle),
    ];

    if (grafico) {
        series.forEach((serie, i) => (grafico.data.datasets[i].data = serie));
        grafico.update("none"); // sem animação, para acompanhar o slider
        return;
    }

    const cores = coresDoTema();
    Chart.defaults.color = cores.texto;
    Chart.defaults.borderColor = cores.grade;
    Chart.defaults.font.family = "Inter, system-ui, sans-serif";

    grafico = new Chart(document.getElementById("grafico"), {
        type: "line",
        data: {
            datasets: [
                { label: "Setpoint", data: series[0], borderColor: cores.setpoint, borderDash: [6, 4], yAxisID: "nivel" },
                { label: "Nível do tanque (%)", data: series[1], borderColor: cores.saida, yAxisID: "nivel" },
                { label: "Abertura da válvula (%)", data: series[2], borderColor: cores.controle, yAxisID: "valvula" },
            ],
        },
        options: {
            maintainAspectRatio: false,
            animation: false,
            elements: { point: { radius: 0 }, line: { borderWidth: 2 } },
            interaction: { mode: "index", intersect: false },
            scales: {
                x: { type: "linear", title: { display: true, text: "Tempo (s)" } },
                nivel: { position: "left", beginAtZero: true, title: { display: true, text: "Nível (%)" } },
                valvula: {
                    position: "right",
                    min: 0,
                    max: 100,
                    title: { display: true, text: "Válvula (%)" },
                    grid: { drawOnChartArea: false },
                },
            },
        },
    });
}

// Ao trocar o tema, recria o gráfico com as novas cores (sem nova simulação).
document.addEventListener("temamudou", () => {
    if (!grafico) return;
    grafico.destroy();
    grafico = null;
    desenharGrafico(...ultimoDesenho);
});

// --- Início ------------------------------------------------------------------

if (typeof Chart === "undefined") {
    mostrarErro("Não foi possível carregar a biblioteca de gráficos. Verifique sua conexão.");
} else {
    marcarPreset(botoesPreset[1]); // os valores iniciais do formulário são os do preset crítico
    simular();
}
