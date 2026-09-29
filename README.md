# Portfólio — Lucas Moreira Araujo

Site de portfólio com demo interativa. Back-end em Python (Flask) e front-end em
HTML, CSS e JavaScript puros, hospedado na Vercel.

## Estrutura

```
app.py              # Aplicação Flask (rotas da página e da API)
requirements.txt    # Dependências Python
.python-version     # Versão do Python usada na Vercel
templates/          # HTML renderizado pelo Flask
public/             # Arquivos estáticos (CSS, JS, imagens), servidos na raiz do site
```

## Rodando localmente

Requer Python 3.13.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Acesse http://127.0.0.1:5000

## Rotas

| Rota          | Descrição                        |
|---------------|----------------------------------|
| `/`           | Página inicial                   |
| `/api/health` | Verificação de saúde, retorna `{"status": "ok"}` |

## Deploy

A Vercel detecta o Flask automaticamente pelo `app.py` (objeto `app`) e pelo
`requirements.txt`, sem necessidade de `vercel.json`. Cada push na branch `main`
gera um novo deploy.
