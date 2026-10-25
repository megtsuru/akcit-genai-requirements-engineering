"""Testes de integração da API de inscrição (especificacao-api-inscricao.md).

Cada teste corresponde a um exemplo A1–A9 e cita a regra que verifica.
"""

from datetime import datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient

from eventus.api import criar_aplicacao
from eventus.inscricao import Evento, Inscricao, StatusInscricao
from eventus.notificacao import NotificadorFalso
from eventus.repositorio import RepositorioEmMemoria

# Base dos exemplos: W1, W2 e W3 de especificacao-tarefa.md (dados fictícios).
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


@pytest.fixture
def repositorio() -> RepositorioEmMemoria:
    repositorio = RepositorioEmMemoria()
    for evento in (W1, W2, W3):
        repositorio.cadastrar_evento(evento)
    return repositorio


@pytest.fixture
def notificador() -> NotificadorFalso:
    return NotificadorFalso()


@pytest.fixture
def cliente(
    repositorio: RepositorioEmMemoria, notificador: NotificadorFalso
) -> TestClient:
    return TestClient(criar_aplicacao(repositorio, notificador))


def _inscrever(cliente: TestClient, evento_id: str, corpo: Any) -> Any:
    return cliente.post(f"/eventos/{evento_id}/inscricoes", json=corpo)


# --- Inscrição aceita (201) -------------------------------------------------


def test_a1_inscricao_confirmada_grava_e_envia_comprovante(
    cliente: TestClient,
    repositorio: RepositorioEmMemoria,
    notificador: NotificadorFalso,
) -> None:
    """A1 — RF02, RN01, RF03: evento gratuito com vaga confirma e notifica."""
    resposta = _inscrever(cliente, "W1", {"participante_id": "p1"})

    assert resposta.status_code == 201
    assert resposta.json() == {
        "evento_id": "W1",
        "participante_id": "p1",
        "status": "confirmada",
        "comprovante_enviado": True,
    }
    inscricao_esperada = Inscricao("p1", W1, CONFIRMADA)
    assert repositorio.listar_inscricoes() == [inscricao_esperada]
    assert notificador.comprovantes_enviados == [inscricao_esperada]


def test_a2_evento_pago_fica_pendente_pagamento(cliente: TestClient) -> None:
    """A2 — RN03: evento pago resulta em pendente_pagamento."""
    resposta = _inscrever(cliente, "W2", {"participante_id": "p1"})

    assert resposta.status_code == 201
    assert resposta.json()["status"] == "pendente_pagamento"


def test_a3_evento_lotado_vai_para_lista_espera(
    cliente: TestClient, repositorio: RepositorioEmMemoria
) -> None:
    """A3 — RN05, RF09: evento sem vaga resulta em lista_espera."""
    for outro_participante in ("p2", "p3", "p4"):
        repositorio.gravar_inscricao(Inscricao(outro_participante, W1, CONFIRMADA))

    resposta = _inscrever(cliente, "W1", {"participante_id": "p1"})

    assert resposta.status_code == 201
    assert resposta.json()["status"] == "lista_espera"


def test_a9_falha_do_notificador_mantem_inscricao(
    repositorio: RepositorioEmMemoria,
) -> None:
    """A9 — RF03 + decisão de 2026-10-25: falha no envio não tira a vaga."""
    cliente = TestClient(
        criar_aplicacao(repositorio, NotificadorFalso(deve_falhar=True))
    )

    resposta = _inscrever(cliente, "W1", {"participante_id": "p1"})

    assert resposta.status_code == 201
    assert resposta.json()["status"] == "confirmada"
    assert resposta.json()["comprovante_enviado"] is False
    assert repositorio.listar_inscricoes() == [Inscricao("p1", W1, CONFIRMADA)]


# --- Inscrição recusada (404, 409, 422): nada gravado, nada enviado ----------


def test_a4_conflito_de_horario_responde_409(
    cliente: TestClient,
    repositorio: RepositorioEmMemoria,
    notificador: NotificadorFalso,
) -> None:
    """A4 — RN06, RF06: conflito com inscrição confirmada é recusado."""
    inscricao_existente = Inscricao("p1", W1, CONFIRMADA)
    repositorio.gravar_inscricao(inscricao_existente)

    resposta = _inscrever(cliente, "W3", {"participante_id": "p1"})

    assert resposta.status_code == 409
    assert "conflito de horário" in resposta.json()["detail"].lower()
    assert repositorio.listar_inscricoes() == [inscricao_existente]
    assert notificador.comprovantes_enviados == []


def test_a5_participante_ja_inscrito_responde_409(
    cliente: TestClient,
    repositorio: RepositorioEmMemoria,
    notificador: NotificadorFalso,
) -> None:
    """A5 — validação de avaliar_inscricao: participante já inscrito no evento."""
    inscricao_existente = Inscricao("p1", W1, CONFIRMADA)
    repositorio.gravar_inscricao(inscricao_existente)

    resposta = _inscrever(cliente, "W1", {"participante_id": "p1"})

    assert resposta.status_code == 409
    assert "já tem inscrição" in resposta.json()["detail"]
    assert repositorio.listar_inscricoes() == [inscricao_existente]
    assert notificador.comprovantes_enviados == []


def test_a6_evento_inexistente_responde_404(
    cliente: TestClient,
    repositorio: RepositorioEmMemoria,
    notificador: NotificadorFalso,
) -> None:
    """A6 — RF02: só é possível se inscrever em evento existente."""
    resposta = _inscrever(cliente, "XX", {"participante_id": "p1"})

    assert resposta.status_code == 404
    assert "XX" in resposta.json()["detail"]
    assert repositorio.listar_inscricoes() == []
    assert notificador.comprovantes_enviados == []


@pytest.mark.parametrize(
    "corpo",
    [{}, {"participante_id": ""}],
    ids=["A7-corpo-vazio", "A8-participante-id-vazio"],
)
def test_a7_a8_corpo_invalido_responde_422(
    cliente: TestClient,
    repositorio: RepositorioEmMemoria,
    notificador: NotificadorFalso,
    corpo: dict[str, str],
) -> None:
    """A7, A8 — contrato: participante_id é texto obrigatório e não vazio."""
    resposta = _inscrever(cliente, "W1", corpo)

    assert resposta.status_code == 422
    assert repositorio.listar_inscricoes() == []
    assert notificador.comprovantes_enviados == []
