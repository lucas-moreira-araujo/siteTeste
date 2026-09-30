// Alterna entre tema escuro (padrão) e claro, e lembra a escolha no navegador.

const botaoTema = document.getElementById("botao-tema");

function aplicarTema(tema) {
    document.documentElement.dataset.tema = tema;
    const proximo = tema === "escuro" ? "claro" : "escuro";
    botaoTema.setAttribute("aria-label", `Mudar para tema ${proximo}`);
    // Avisa outras partes da página (o gráfico da demo precisa trocar de cores).
    document.dispatchEvent(new Event("temamudou"));
}

botaoTema.addEventListener("click", () => {
    const novoTema = document.documentElement.dataset.tema === "escuro" ? "claro" : "escuro";
    aplicarTema(novoTema);
    try {
        localStorage.setItem("tema", novoTema);
    } catch (erro) {
        // Armazenamento bloqueado (ex.: navegação privada): o tema vale só para esta visita.
    }
});

aplicarTema(document.documentElement.dataset.tema);
