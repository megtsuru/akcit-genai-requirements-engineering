"""Testes de avaliar_inscricao, um por exemplo de especificacao-tarefa.md."""

from datetime import datetime

import pytest

from eventus.inscricao import (
    Evento,
    Inscricao,
    ResultadoInscricao,
    StatusInscricao,
    avaliar_inscricao,
)

# Base dos exemplos (datas em 2026-11-10, dados fictícios).
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

CONFIRMADA = StatusInscricao.CONFIRMADA
PENDENTE_PAGAMENTO = StatusInscricao.PENDENTE_PAGAMENTO
LISTA_ESPERA = StatusInscricao.LISTA_ESPERA


def _inscricao(
    participante_id: str, evento: Evento, status: StatusInscricao
) -> Inscricao:
    return Inscricao(participante_id=participante_id, evento=evento, status=status)


# --- Funcionamento normal ---------------------------------------------------


def test_n1_evento_gratuito_com_vaga_confirma() -> None:
    """N1 — RN01: evento gratuito com vaga resulta em CONFIRMADA."""
    assert avaliar_inscricao("p1", W1, []) == ResultadoInscricao.CONFIRMADA


def test_n2_evento_pago_com_vaga_fica_pendente_pagamento() -> None:
    """N2 — RN03: evento pago com vaga resulta em PENDENTE_PAGAMENTO."""
    assert avaliar_inscricao("p1", W2, []) == ResultadoInscricao.PENDENTE_PAGAMENTO


def test_n3_evento_lotado_vai_para_lista_espera() -> None:
    """N3 — RN05: sem vaga disponível resulta em LISTA_ESPERA."""
    inscricoes = [
        _inscricao("p2", W1, CONFIRMADA),
        _inscricao("p3", W1, CONFIRMADA),
        _inscricao("p4", W1, CONFIRMADA),
    ]
    assert avaliar_inscricao("p1", W1, inscricoes) == ResultadoInscricao.LISTA_ESPERA


def test_n4_conflito_com_inscricao_confirmada_recusa() -> None:
    """N4 — RN06: sobreposição com evento confirmado recusa a inscrição."""
    inscricoes = [_inscricao("p1", W1, CONFIRMADA)]
    assert (
        avaliar_inscricao("p1", W3, inscricoes)
        == ResultadoInscricao.RECUSADA_CONFLITO_HORARIO
    )


# --- Limite -----------------------------------------------------------------


def test_l1_ultima_vaga_confirma() -> None:
    """L1 — RN05: a última vaga ainda está disponível."""
    inscricoes = [
        _inscricao("p2", W1, CONFIRMADA),
        _inscricao("p3", W1, CONFIRMADA),
    ]
    assert avaliar_inscricao("p1", W1, inscricoes) == ResultadoInscricao.CONFIRMADA


def test_l2_eventos_que_se_encostam_nao_conflitam() -> None:
    """L2 — RN06: W1 termina 10:00 e W2 começa 10:00, sem conflito."""
    inscricoes = [_inscricao("p1", W1, CONFIRMADA)]
    assert (
        avaliar_inscricao("p1", W2, inscricoes) == ResultadoInscricao.PENDENTE_PAGAMENTO
    )


def test_l3_conflito_avaliado_antes_das_vagas() -> None:
    """L3 — RN06 antes de RN05: evento lotado com conflito é recusado."""
    inscricoes = [
        _inscricao("p1", W1, CONFIRMADA),
        _inscricao("p2", W3, CONFIRMADA),
        _inscricao("p3", W3, CONFIRMADA),
        _inscricao("p4", W3, CONFIRMADA),
    ]
    assert (
        avaliar_inscricao("p1", W3, inscricoes)
        == ResultadoInscricao.RECUSADA_CONFLITO_HORARIO
    )


def test_l4_conflito_de_outro_participante_nao_afeta() -> None:
    """L4 — RN06: o conflito é só do próprio participante."""
    inscricoes = [_inscricao("p2", W1, CONFIRMADA)]
    assert avaliar_inscricao("p1", W3, inscricoes) == ResultadoInscricao.CONFIRMADA


def test_l5_lista_espera_nao_gera_conflito() -> None:
    """L5 — RN06: só inscrição CONFIRMADA gera conflito."""
    inscricoes = [_inscricao("p1", W1, LISTA_ESPERA)]
    assert avaliar_inscricao("p1", W3, inscricoes) == ResultadoInscricao.CONFIRMADA


def test_l6_pendente_pagamento_reserva_vaga() -> None:
    """L6 — RN05 + decisão da lacuna 6 (opção A): pendente ocupa vaga."""
    inscricoes = [
        _inscricao("p2", W2, CONFIRMADA),
        _inscricao("p3", W2, CONFIRMADA),
        _inscricao("p4", W2, PENDENTE_PAGAMENTO),
    ]
    assert avaliar_inscricao("p1", W2, inscricoes) == ResultadoInscricao.LISTA_ESPERA


def test_l7_lista_espera_nao_ocupa_vaga() -> None:
    """L7 — RN05: inscrição em lista de espera não ocupa vaga."""
    inscricoes = [
        _inscricao("p2", W1, CONFIRMADA),
        _inscricao("p3", W1, CONFIRMADA),
        _inscricao("p4", W1, LISTA_ESPERA),
    ]
    assert avaliar_inscricao("p1", W1, inscricoes) == ResultadoInscricao.CONFIRMADA


# --- Erro -------------------------------------------------------------------


def test_e1_evento_com_fim_igual_inicio_e_invalido() -> None:
    """E1 — Validação: evento precisa terminar depois de começar."""
    evento = Evento(
        id="E1",
        inicio=datetime(2026, 11, 10, 9, 0),
        fim=datetime(2026, 11, 10, 9, 0),
        vagas=3,
        pago=False,
    )
    with pytest.raises(ValueError, match="deve terminar depois de começar"):
        avaliar_inscricao("p1", evento, [])


def test_e2_evento_sem_vagas_e_invalido() -> None:
    """E2 — Validação: evento precisa ter ao menos 1 vaga."""
    evento = Evento(
        id="E2",
        inicio=datetime(2026, 11, 10, 9, 0),
        fim=datetime(2026, 11, 10, 10, 0),
        vagas=0,
        pago=False,
    )
    with pytest.raises(ValueError, match="deve ter ao menos 1 vaga"):
        avaliar_inscricao("p1", evento, [])


def test_e3_participante_ja_inscrito_no_evento_e_invalido() -> None:
    """E3 — Validação: participante já inscrito (qualquer status) no evento."""
    inscricoes = [_inscricao("p1", W1, LISTA_ESPERA)]
    with pytest.raises(ValueError, match="já tem inscrição no evento"):
        avaliar_inscricao("p1", W1, inscricoes)


def test_e4_evento_com_fim_antes_do_inicio_e_invalido() -> None:
    """E4 — Validação: evento precisa terminar depois de começar."""
    evento = Evento(
        id="E4",
        inicio=datetime(2026, 11, 10, 10, 0),
        fim=datetime(2026, 11, 10, 9, 0),
        vagas=3,
        pago=False,
    )
    with pytest.raises(ValueError, match="deve terminar depois de começar"):
        avaliar_inscricao("p1", evento, [])


def test_e5_participante_ja_confirmado_no_evento_e_invalido() -> None:
    """E5 — Validação: participante já inscrito (qualquer status) no evento."""
    inscricoes = [_inscricao("p1", W1, CONFIRMADA)]
    with pytest.raises(ValueError, match="já tem inscrição no evento"):
        avaliar_inscricao("p1", W1, inscricoes)


def test_e6_participante_ja_pendente_pagamento_no_evento_e_invalido() -> None:
    """E6 — Validação: participante já inscrito (qualquer status) no evento."""
    inscricoes = [_inscricao("p1", W2, PENDENTE_PAGAMENTO)]
    with pytest.raises(ValueError, match="já tem inscrição no evento"):
        avaliar_inscricao("p1", W2, inscricoes)
