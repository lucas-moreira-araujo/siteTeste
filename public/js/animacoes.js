// Animações discretas, só onde ajudam a leitura:
//  - a abertura da página entra suavemente;
//  - os quatro passos de "Como eu trabalho" aparecem em sequência, reforçando a ordem;
//  - os cartões de projeto surgem conforme a página rola.
// Sem JavaScript, ou com "reduzir movimento" ativado, tudo aparece normalmente.

(function () {
    const reduzir = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduzir || !("IntersectionObserver" in window)) return;

    const alvos = document.querySelectorAll(".passos .projeto, .pares .projeto");
    document.documentElement.classList.add("com-animacao");

    const observador = new IntersectionObserver(
        (entradas) => {
            entradas.forEach((entrada) => {
                if (!entrada.isIntersecting) return;
                entrada.target.classList.add("visivel");
                observador.unobserve(entrada.target);
            });
        },
        { threshold: 0.15 }
    );

    alvos.forEach((alvo) => {
        // Atraso em cascata dentro de cada grupo (0, 1, 2, 3...).
        const posicao = Array.prototype.indexOf.call(alvo.parentElement.children, alvo);
        alvo.style.setProperty("--atraso", `${posicao * 90}ms`);
        observador.observe(alvo);
    });
})();
