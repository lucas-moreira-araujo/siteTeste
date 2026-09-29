import math

import pytest

import pid
from app import app

PARAMETROS_VALIDOS = {"kp": 2, "ki": 0.5, "kd": 0.1, "setpoint": 50, "tempo_total": 60}


# --- Simulação ---------------------------------------------------------------

def test_controle_so_proporcional_tem_erro_em_regime_previsto_pela_teoria():
    # Com só P, o nível estabiliza em K*Kp / (1 + K*Kp) * setpoint.
    kp, setpoint = 1.0, 50.0
    resultado = pid.simular(kp=kp, ki=0, kd=0, setpoint=setpoint, tempo_total=60)

    esperado = pid.GANHO_PLANTA * kp / (1 + pid.GANHO_PLANTA * kp) * setpoint
    assert resultado["saida"][-1] == pytest.approx(esperado, abs=0.01)
    assert resultado["metricas"]["overshoot_pct"] == 0


def test_termo_integral_elimina_erro_em_regime():
    resultado = pid.simular(kp=2, ki=0.5, kd=0, setpoint=50, tempo_total=60)

    assert resultado["saida"][-1] == pytest.approx(50, rel=0.01)
    assert resultado["metricas"]["tempo_acomodacao"] is not None


def test_series_tem_mesmo_tamanho_e_passo_constante():
    resultado = pid.simular(**{**PARAMETROS_VALIDOS, "tempo_total": 10})

    passos = round(10 / pid.DT) + 1
    assert len(resultado["tempo"]) == len(resultado["saida"]) == len(resultado["controle"]) == passos
    assert resultado["tempo"][0] == 0 and resultado["tempo"][-1] == 10


def test_ganhos_extremos_nao_divergem():
    resultado = pid.simular(kp=100, ki=100, kd=50, setpoint=100, tempo_total=120)

    assert all(math.isfinite(y) for y in resultado["saida"])
    assert all(0 <= y <= pid.GANHO_PLANTA * pid.U_MAX for y in resultado["saida"])
    assert all(pid.U_MIN <= u <= pid.U_MAX for u in resultado["controle"])


# --- Métricas ----------------------------------------------------------------

def test_metricas_em_curva_conhecida():
    tempo = [0, 1, 2, 3, 4, 5]
    saida = [0, 5, 9, 11, 10.1, 10]

    metricas = pid.calcular_metricas(tempo, saida, setpoint=10)

    assert metricas["overshoot_pct"] == 10       # pico 11 sobre setpoint 10
    assert metricas["tempo_subida"] == 1         # 10% em t=1, 90% em t=2
    assert metricas["tempo_acomodacao"] == 4     # último ponto fora da faixa em t=3


def test_metricas_none_quando_criterio_nao_e_atingido():
    metricas = pid.calcular_metricas([0, 1, 2], [0, 3, 5], setpoint=10)

    assert metricas["tempo_subida"] is None
    assert metricas["tempo_acomodacao"] is None


# --- Validação ---------------------------------------------------------------

@pytest.mark.parametrize("alteracao", [
    {"kp": -1},
    {"ki": 101},
    {"setpoint": 0},
    {"tempo_total": 500},
    {"kd": "abc"},
    {"kp": True},
    {"kp": float("nan")},
])
def test_validacao_rejeita_valores_invalidos(alteracao):
    with pytest.raises(ValueError):
        pid.validar_parametros({**PARAMETROS_VALIDOS, **alteracao})


def test_validacao_rejeita_parametro_ausente():
    dados = {k: v for k, v in PARAMETROS_VALIDOS.items() if k != "kp"}
    with pytest.raises(ValueError, match="kp"):
        pid.validar_parametros(dados)


# --- Rota /api/simular -------------------------------------------------------

@pytest.fixture
def cliente():
    return app.test_client()


def test_rota_simular_retorna_series_e_metricas(cliente):
    resposta = cliente.post("/api/simular", json=PARAMETROS_VALIDOS)

    assert resposta.status_code == 200
    corpo = resposta.get_json()
    assert {"tempo", "saida", "controle", "metricas"} <= corpo.keys()


def test_rota_simular_retorna_400_com_mensagem(cliente):
    resposta = cliente.post("/api/simular", json={**PARAMETROS_VALIDOS, "kp": -5})

    assert resposta.status_code == 400
    assert "kp" in resposta.get_json()["erro"]


def test_rota_simular_retorna_400_sem_json(cliente):
    resposta = cliente.post("/api/simular", data="isto não é json")

    assert resposta.status_code == 400
