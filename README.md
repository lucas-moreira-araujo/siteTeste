# Portfólio — Lucas Moreira Araujo

**Site no ar: https://site-teste-ruby.vercel.app**

Portfólio pessoal com uma demo interativa: um **simulador de controle PID** em que
o visitante ajusta os ganhos do controlador e vê, em tempo real, como o nível de
um tanque responde. A simulação roda em Python no servidor e o resultado é
desenhado no navegador.

Sou estudante do 8º semestre de Engenharia de Controle e Automação, com
interesse em dados e IA aplicados a processos. O projeto junta a teoria de
controle da minha formação com desenvolvimento de software.

---

## O que tem no site

- **Sobre mim, Tecnologias e Projetos:** apresentação, linguagens e projetos
  acadêmicos (chatbot com API REST, robô seguidor de linha, controle de
  luminosidade).
- **Demo PID:** o simulador, descrito abaixo.
- **Contato:** e-mail, LinkedIn e GitHub.
- Tema escuro e claro, layout responsivo (testado em 375px de largura) e
  cuidados de acessibilidade: HTML semântico, foco visível, contraste adequado
  e respeito à preferência de "reduzir movimento".

---

## A demo: simulador de controle PID

### O que é um PID

Um controlador PID é o "piloto automático" de muitas máquinas. Ele compara o
valor desejado (**setpoint**) com o valor medido e ajusta a ação de controle
somando três termos:

- **P (proporcional):** reage ao erro atual. Quanto mais longe do alvo, mais
  forte a ação.
- **I (integral):** reage ao erro acumulado no tempo. Elimina o erro que
  sobraria só com o P.
- **D (derivativo):** reage à tendência do erro. Freia a resposta quando a
  variável muda rápido demais.

### O processo simulado

Um **tanque**, cujo nível (%) o PID controla abrindo e fechando uma **válvula
de entrada** (0 a 100%). O tanque é modelado como um sistema de primeira ordem:

```
τ · dy/dt = −y + K · u        (τ = 5 s, K = 2)
```

Em palavras: com a válvula parada, o nível caminha gradualmente até um ponto
de equilíbrio, e a constante de tempo τ define o quão devagar.

### Como a simulação funciona

A cada passo de 0,05 s, o código em [`pid.py`](pid.py):

1. Calcula o erro: `setpoint − nível`.
2. Calcula os três termos do PID. O termo D é calculado sobre a **medição**, e
   não sobre o erro. Assim, uma mudança brusca no setpoint não gera um pico no
   sinal de controle.
3. **Satura** o sinal entre 0 e 100%, porque uma válvula real não abre além
   disso.
4. Aplica **anti-windup**: enquanto a válvula está saturada, a integral para
   de acumular. Sem isso, ela "incharia" e causaria um overshoot enorme depois.
5. Avança o tanque um passo pelo **método de Euler**.

A saturação também garante que a simulação **nunca diverge**: com a entrada
limitada, o nível fica sempre entre 0 e 200%, quaisquer que sejam os ganhos.

### Métricas calculadas

| Métrica | Definição |
|---|---|
| Overshoot | Quanto o nível passou do setpoint, em % |
| Tempo de subida | Tempo para ir de 10% a 90% do setpoint |
| Tempo de acomodação | Instante a partir do qual o nível fica dentro de ±2% do setpoint |

Quando um critério não é atingido dentro do tempo simulado, o tempo vale
`null` (no site, "não atingiu"). Isso acontece, por exemplo, com um controle
só proporcional, que estabiliza abaixo do alvo.

### Presets

Os três exemplos prontos foram calculados pela teoria e conferidos na
simulação. Com um controlador PI sobre essa planta, a malha fechada vira um
sistema de 2ª ordem, com `ωn² = K·Ki/τ` e `2ζωn = (1 + K·Kp)/τ`:

| Preset | Ganhos | ζ | Overshoot | Acomodação |
|---|---|---|---|---|
| Subamortecido | Kp = 0,5 · Ki = 1 | 0,32 | 37% | 17,1 s |
| Criticamente amortecido | Kp = 1 · Ki = 0,2 | ≈ 1 | 0% | 9,8 s |
| Lento | Kp = 0,3 · Ki = 0,05 | 1,13 | 0% | 43 s |

---

## Tecnologias e por que foram escolhidas

| Tecnologia | Uso | Por quê |
|---|---|---|
| **Python** | Simulação e back-end | Linguagem que domino e padrão em dados, IA e computação científica. A simulação usa só Python puro, sem NumPy, para manter o projeto leve e cada passo do cálculo explícito. |
| **Flask** | Servidor web e API | Micro-framework simples: com poucas linhas expõe a página e a rota `/api/simular`. Para um site de uma página com uma API, um framework maior seria excesso. |
| **HTML, CSS e JavaScript puros** | Interface | Sem framework e sem etapa de build: o código é pequeno, fácil de ler e roda direto no navegador. As cores dos temas ficam em variáveis CSS. |
| **Chart.js** (via CDN) | Gráfico da demo | Biblioteca leve e madura para gráficos de linha, com dois eixos (nível e válvula) e sem precisar instalar nada. |
| **pytest** | Testes automatizados | Padrão em Python e simples de escrever. Os testes conferem a simulação contra a teoria de controle, as métricas, a validação e a API. |
| **Vercel** | Hospedagem | Suporta Flask sem configuração extra, serve os arquivos estáticos por CDN e publica automaticamente a cada `git push`. |
| **Git e GitHub** | Versionamento | Histórico do projeto e integração direta com a Vercel. |

**Sem banco de dados:** a simulação é calculada a cada pedido e nada precisa
ser salvo. Isso também combina com a Vercel, onde o servidor não mantém
arquivos entre requisições.

---

## Estrutura do projeto

```
app.py                # Flask: rotas da página e da API
pid.py                # Simulação do PID e cálculo das métricas (Python puro)
tests/test_pid.py     # Testes automatizados
templates/index.html  # Página do portfólio
public/               # Arquivos estáticos, servidos na raiz do site
  css/style.css       # Estilos e temas escuro/claro
  js/tema.js          # Alternância de tema
  js/demo.js          # Interface do simulador: controles, chamada à API e gráfico
requirements.txt      # Dependências de produção (só Flask)
requirements-dev.txt  # Dependências de desenvolvimento (inclui pytest)
.python-version       # Versão do Python usada na Vercel (3.13)
```

A lógica da simulação (`pid.py`) fica separada da parte web (`app.py`). Assim,
ela pode ser testada sem subir um servidor.

---

## API

### `POST /api/simular`

Corpo (JSON):

| Campo | Faixa aceita | Descrição |
|---|---|---|
| `kp` | 0 a 100 | Ganho proporcional |
| `ki` | 0 a 100 | Ganho integral |
| `kd` | 0 a 50 | Ganho derivativo |
| `setpoint` | 1 a 100 | Nível desejado (%) |
| `tempo_total` | 1 a 120 | Duração da simulação (s) |

A resposta traz as listas `tempo`, `saida` (nível) e `controle` (abertura da
válvula), e o objeto `metricas` com `overshoot_pct`, `tempo_subida` e
`tempo_acomodacao`. Parâmetros inválidos retornam `400` com uma mensagem
clara, por exemplo `{"erro": "'kp' deve estar entre 0 e 100."}`.

### `GET /api/health`

Retorna `{"status": "ok"}`. Serve para verificar se o servidor está no ar.

---

## Como rodar localmente

Requer Python 3.13.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python app.py
```

Acesse http://127.0.0.1:5000.

Para rodar os testes:

```powershell
pytest
```

---

## Contato

- E-mail: araujolucas0602@gmail.com
- LinkedIn: [lucas-moreira-araújo](https://www.linkedin.com/in/lucas-moreira-ara%C3%BAjo)
- GitHub: [lucas-moreira-araujo](https://github.com/lucas-moreira-araujo)
