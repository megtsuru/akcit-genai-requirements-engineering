"""Testes de avaliar_inscricao a partir de desenvolvimento/especificacao-tarefa.md.

Os resultados esperados sao os literais da especificacao (tabelas N, L e E).
"""

from datetime import datetime

import pytest

from eventus.inscricao import (
    Evento,
    Inscricao,
    ResultadoInscricao,
    StatusInscricao,
    avaliar_inscricao,
)

# Base dos exemplos (2026-11-10), dados ficticios.
W1 = Evento(
    id="W1",
    inicio=datetime(2026, 11, 10, 9, 0),
    fim=datetime(2026, 11, 10, 10, 0),
    vagas=3,
    pago=False,
)
W2 = Evento(
    id="W2",
    inicio=datetime(2026, 11, 10, 10, 0),
    fim=datetime(2026, 11, 10, 11, 0),
    vagas=3,
    pago=True,
)
W3 = Evento(
    id="W3",
    inicio=datetime(2026, 11, 10, 9, 30),
    fim=datetime(2026, 11, 10, 10, 30),
    vagas=3,
    pago=False,
)

CONF = StatusInscricao.CONFIRMADA
ESPERA = StatusInscricao.LISTA_ESPERA


def _confirmadas_de_outros(evento: Evento, quantidade: int) -> list[Inscricao]:
    return [Inscricao(f"outro{n}", evento, CONF) for n in range(quantidade)]


# RN01, RN03: tipo do evento (gratuito -> CONFIRMADA; pago -> PENDENTE_PAGAMENTO)
@pytest.mark.parametrize(
    ("evento", "inscricoes", "esperado"),
    [
        (W1, [], ResultadoInscricao.CONFIRMADA),
        (W2, [], ResultadoInscricao.PENDENTE_PAGAMENTO),
    ],
    ids=["N1", "N2"],
)
def test_tipo_do_evento_rn01_rn03(
    evento: Evento, inscricoes: list[Inscricao], esperado: ResultadoInscricao
) -> None:
    assert avaliar_inscricao("p1", evento, inscricoes) is esperado


# RN05: vagas
@pytest.mark.parametrize(
    ("inscricoes", "esperado"),
    [
        (_confirmadas_de_outros(W1, 3), ResultadoInscricao.LISTA_ESPERA),
        (_confirmadas_de_outros(W1, 2), ResultadoInscricao.CONFIRMADA),
    ],
    ids=["N3-lotado", "L1-ultima-vaga"],
)
def test_vagas_rn05(inscricoes: list[Inscricao], esperado: ResultadoInscricao) -> None:
    assert avaliar_inscricao("p1", W1, inscricoes) is esperado


# RN05 + decisao sobre lacuna 6 (opcao A): PENDENTE_PAGAMENTO ocupa vaga;
# LISTA_ESPERA nao ocupa.
@pytest.mark.parametrize(
    ("evento", "inscricoes", "esperado"),
    [
        (
            W2,
            [
                *_confirmadas_de_outros(W2, 2),
                Inscricao("p9", W2, StatusInscricao.PENDENTE_PAGAMENTO),
            ],
            ResultadoInscricao.LISTA_ESPERA,
        ),
        (
            W1,
            [*_confirmadas_de_outros(W1, 2), Inscricao("p9", W1, ESPERA)],
            ResultadoInscricao.CONFIRMADA,
        ),
    ],
    ids=["L6-pendente-reserva-vaga", "L7-lista-espera-nao-ocupa-vaga"],
)
def test_status_que_ocupam_vaga_rn05(
    evento: Evento, inscricoes: list[Inscricao], esperado: ResultadoInscricao
) -> None:
    assert avaliar_inscricao("p1", evento, inscricoes) is esperado


# RN06: conflito de horario (bloqueia; caso de uso A2)
@pytest.mark.parametrize(
    ("evento", "inscricoes", "esperado"),
    [
        (
            W3,
            [Inscricao("p1", W1, CONF)],
            ResultadoInscricao.RECUSADA_CONFLITO_HORARIO,
        ),
        (
            W2,
            [Inscricao("p1", W1, CONF)],
            ResultadoInscricao.PENDENTE_PAGAMENTO,
        ),
        (
            W3,
            [Inscricao("p1", W1, CONF), *_confirmadas_de_outros(W3, 3)],
            ResultadoInscricao.RECUSADA_CONFLITO_HORARIO,
        ),
        (
            W3,
            [Inscricao("p2", W1, CONF)],
            ResultadoInscricao.CONFIRMADA,
        ),
        (
            W3,
            [Inscricao("p1", W1, ESPERA)],
            ResultadoInscricao.CONFIRMADA,
        ),
    ],
    ids=[
        "N4-sobreposicao",
        "L2-eventos-que-se-encostam",
        "L3-conflito-antes-das-vagas",
        "L4-conflito-de-outro-participante",
        "L5-lista-espera-nao-conflita",
    ],
)
def test_conflito_de_horario_rn06(
    evento: Evento, inscricoes: list[Inscricao], esperado: ResultadoInscricao
) -> None:
    assert avaliar_inscricao("p1", evento, inscricoes) is esperado


# Validacao (regra 1 da especificacao)
@pytest.mark.parametrize(
    ("evento", "inscricoes"),
    [
        (
            Evento(
                id="E1",
                inicio=datetime(2026, 11, 10, 9, 0),
                fim=datetime(2026, 11, 10, 9, 0),
                vagas=3,
                pago=False,
            ),
            [],
        ),
        (
            Evento(
                id="E2",
                inicio=datetime(2026, 11, 10, 9, 0),
                fim=datetime(2026, 11, 10, 10, 0),
                vagas=0,
                pago=False,
            ),
            [],
        ),
        (W1, [Inscricao("p1", W1, ESPERA)]),
    ],
    ids=["E1-fim-igual-inicio", "E2-zero-vagas", "E3-ja-inscrito"],
)
def test_validacao(evento: Evento, inscricoes: list[Inscricao]) -> None:
    with pytest.raises(ValueError):
        avaliar_inscricao("p1", evento, inscricoes)
