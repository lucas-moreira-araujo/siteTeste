# Portfólio — Lucas Moreira Araujo

Site de portfólio com demo interativa. Back-end em Python (Flask) e front-end em
HTML, CSS e JavaScript puros, hospedado na Vercel.

## Estrutura

```
app.py              # Aplicação Flask (rotas da página e da API)
pid.py              # Simulação do controle PID (Python puro)
tests/              # Testes automatizados (pytest)
requirements.txt    # Dependências de produção (vão para a Vercel)
requirements-dev.txt # Dependências de desenvolvimento (pytest)
.python-version     # Versão do Python usada na Vercel
templates/          # HTML renderizado pelo Flask
public/             # Arquivos estáticos, servidos na raiz do site
  css/style.css     # Estilos; cores dos temas escuro/claro em variáveis CSS
  js/tema.js        # Alternância de tema (lembrada no navegador)
  js/demo.js        # Interface do simulador: controles, chamada à API e gráfico
```

A página tem as seções Início, Sobre mim, Tecnologias, Projetos, Demo (simulador
PID) e Contato.

## Rodando localmente

Requer Python 3.13.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python app.py
```

Acesse http://127.0.0.1:5000

Para rodar os testes:

```powershell
pytest
```

## Rotas

| Rota                 | Descrição                        |
|----------------------|----------------------------------|
| `GET /`              | Página inicial                   |
| `GET /api/health`    | Verificação de saúde, retorna `{"status": "ok"}` |
| `POST /api/simular`  | Simula o controle PID do nível de um tanque |

### `POST /api/simular`

Corpo (JSON):

| Campo         | Faixa aceita | Descrição                    |
|---------------|--------------|------------------------------|
| `kp`          | 0 a 100      | Ganho proporcional           |
| `ki`          | 0 a 100      | Ganho integral               |
| `kd`          | 0 a 50       | Ganho derivativo             |
| `setpoint`    | 1 a 100      | Nível desejado (%)           |
| `tempo_total` | 1 a 120      | Duração da simulação (s)     |

Resposta: listas `tempo`, `saida` (nível) e `controle` (abertura da válvula),
mais `metricas` com `overshoot_pct`, `tempo_subida` (10%–90% do setpoint) e
`tempo_acomodacao` (faixa de 2%). Os tempos valem `null` quando o critério não
é atingido dentro da simulação. Parâmetros inválidos retornam `400` com
`{"erro": "mensagem"}`.

Exemplo:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:5000/api/simular `
  -ContentType "application/json" `
  -Body '{"kp": 2, "ki": 0.5, "kd": 0, "setpoint": 50, "tempo_total": 60}'
```

## Deploy

A Vercel detecta o Flask automaticamente pelo `app.py` (objeto `app`) e pelo
`requirements.txt`, sem necessidade de `vercel.json`. Cada push na branch `main`
gera um novo deploy.
