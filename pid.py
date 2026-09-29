"""Simulação de um controle PID discreto sobre o nível de um tanque.

Planta (primeira ordem): TAU * dy/dt = -y + GANHO_PLANTA * u
  y: nível do tanque (%)
  u: abertura da válvula de entrada (%), limitada entre U_MIN e U_MAX
"""

import math

DT = 0.05            # passo de simulação (s)
TAU = 5.0            # constante de tempo da planta (s)
GANHO_PLANTA = 2.0   # nível em regime por % de abertura da válvula
U_MIN, U_MAX = 0.0, 100.0
FAIXA_ACOMODACAO = 0.02  # critério de 2%

# (mínimo, máximo) aceitos para cada parâmetro de entrada
LIMITES = {
    "kp": (0.0, 100.0),
    "ki": (0.0, 100.0),
    "kd": (0.0, 50.0),
    "setpoint": (1.0, 100.0),
    "tempo_total": (1.0, 120.0),
}


def validar_parametros(dados):
    """Confere tipos e limites. Retorna os parâmetros como float ou lança ValueError."""
    if not isinstance(dados, dict):
        raise ValueError("O corpo da requisição deve ser um objeto JSON.")

    parametros = {}
    for nome, (minimo, maximo) in LIMITES.items():
        if nome not in dados:
            raise ValueError(f"Parâmetro obrigatório ausente: '{nome}'.")
        valor = dados[nome]
        # bool é subclasse de int em Python, então é excluído explicitamente
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValueError(f"'{nome}' deve ser um número.")
        if not math.isfinite(valor) or not minimo <= valor <= maximo:
            raise ValueError(f"'{nome}' deve estar entre {minimo:g} e {maximo:g}.")
        parametros[nome] = float(valor)
    return parametros


def simular(kp, ki, kd, setpoint, tempo_total):
    """Simula a resposta ao degrau (nível parte de 0) e devolve séries e métricas."""
    passos = round(tempo_total / DT)
    y = 0.0
    y_anterior = y
    integral = 0.0
    tempo, saida, controle = [], [], []

    for k in range(passos + 1):
        erro = setpoint - y

        # Derivada sobre a medição (e não sobre o erro): evita um pico no
        # sinal de controle quando o setpoint muda de uma vez.
        derivada = -(y - y_anterior) / DT

        integral_candidata = integral + erro * DT
        u = kp * erro + ki * integral_candidata + kd * derivada

        # Saturação: a válvula não abre além de 0-100%.
        u_saturado = min(max(u, U_MIN), U_MAX)

        # Anti-windup: só acumula a integral quando a válvula não está saturada.
        if u == u_saturado:
            integral = integral_candidata

        tempo.append(round(k * DT, 4))
        saida.append(round(y, 4))
        controle.append(round(u_saturado, 4))

        # Método de Euler: avança a planta um passo DT.
        y_anterior = y
        y = y + DT * (-y + GANHO_PLANTA * u_saturado) / TAU

    return {
        "tempo": tempo,
        "saida": saida,
        "controle": controle,
        "metricas": calcular_metricas(tempo, saida, setpoint),
    }


def calcular_metricas(tempo, saida, setpoint):
    """Overshoot (%), tempo de subida (10%-90%) e tempo de acomodação (2%).

    Os tempos valem None quando o critério não é atingido dentro da simulação.
    """
    overshoot = max(0.0, (max(saida) - setpoint) / setpoint * 100)

    t10 = _primeiro_tempo_acima(tempo, saida, 0.1 * setpoint)
    t90 = _primeiro_tempo_acima(tempo, saida, 0.9 * setpoint)
    tempo_subida = t90 - t10 if t10 is not None and t90 is not None else None

    # Acomodação: instante a partir do qual a saída não sai mais da faixa de 2%.
    faixa = FAIXA_ACOMODACAO * setpoint
    fora_da_faixa = [i for i, y in enumerate(saida) if abs(y - setpoint) > faixa]
    if not fora_da_faixa:
        tempo_acomodacao = 0.0
    elif fora_da_faixa[-1] == len(saida) - 1:
        tempo_acomodacao = None  # ainda fora da faixa no fim da simulação
    else:
        tempo_acomodacao = tempo[fora_da_faixa[-1] + 1]

    return {
        "overshoot_pct": round(overshoot, 2),
        "tempo_subida": _arredondar(tempo_subida),
        "tempo_acomodacao": _arredondar(tempo_acomodacao),
    }


def _primeiro_tempo_acima(tempo, saida, limiar):
    for t, y in zip(tempo, saida):
        if y >= limiar:
            return t
    return None


def _arredondar(valor):
    return None if valor is None else round(valor, 2)
