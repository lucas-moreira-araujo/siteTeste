// Consulta a API e mostra o resultado na página (confirma que front e back conversam).
fetch("/api/health")
    .then((response) => response.json())
    .then((data) => {
        document.getElementById("status").textContent = data.status;
    })
    .catch(() => {
        document.getElementById("status").textContent = "erro";
    });
