"""Casos de teste de integração gerados por LLM, convertidos em pytest.

Fontes:
- `testes-integracao/resultados/2-contrato-v2.md` (casos CT-01 a CT-54);
- `testes-integracao/resultados/3-erros-e-falhas-v2.md` (casos E, R, N, C).

Os itens das seções "Dúvidas" dos dois arquivos não foram implementados.

Rótulos de regra usados nos casos gerados e a regra correspondente:
- R0: participante já inscrito no evento (validação de `avaliar_inscricao`);
- R1: conflito de horário (RN06);
- R2: vagas e lista de espera (RN05);
- R3: tipo do evento, gratuito ou pago (RN01, RN03).

Contrato: `desenvolvimento/especificacao-api-inscricao.md`. Dados fictícios.
"""

from datetime import datetime
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from eventus.api import criar_aplicacao
from eventus.inscricao import Evento, Inscricao, StatusInscricao
from eventus.repositorio import RepositorioEmMemoria

CONFIRMADA = StatusInscricao.CONFIRMADA
PENDENTE = StatusInscricao.PENDENTE_PAGAMENTO
LISTA_ESPERA = StatusInscricao.LISTA_ESPERA


class FalhaSimulada(Exception):
    """Exceção padrão lançada pelo dublê quando o envio deve falhar."""


class NotificadorEspiao:
    """Dublê do notificador que registra cada chamada e pode falhar.

    O `NotificadorFalso` do pacote não registra as tentativas que falham, e
    os casos N01, CT-38 e CT-39 pedem para verificar se o notificador foi ou
    não acionado mesmo quando ele falha.

    Attributes:
        tentativas: Inscrições para as quais o envio foi pedido.
        comprovantes_enviados: Inscrições cujo envio deu certo.
        falha: Exceção lançada em cada envio; None para enviar normalmente.
    """

    def __init__(self, falha: Exception | None = None) -> None:
        self.tentativas: list[Inscricao] = []
        self.comprovantes_enviados: list[Inscricao] = []
        self.falha = falha

    def enviar_comprovante(self, inscricao: Inscricao) -> None:
        """Registra a tentativa e, se configurado, lança `falha`."""
        self.tentativas.append(inscricao)
        if self.falha is not None:
            raise self.falha
        self.comprovantes_enviados.append(inscricao)


def _evento(
    evento_id: str,
    inicio: str,
    fim: str,
    vagas: int = 2,
    pago: bool = False,
    dia_inicio: int = 10,
    dia_fim: int | None = None,
) -> Evento:
    """Monta um evento de novembro de 2026 a partir de horários "HH:MM"."""
    hora_inicio, minuto_inicio = (int(parte) for parte in inicio.split(":"))
    hora_fim, minuto_fim = (int(parte) for parte in fim.split(":"))
    return Evento(
        id=evento_id,
        inicio=datetime(2026, 11, dia_inicio, hora_inicio, minuto_inicio),
        fim=datetime(2026, 11, dia_fim or dia_inicio, hora_fim, minuto_fim),
        vagas=vagas,
        pago=pago,
    )


def _repositorio(
    eventos: list[Evento], inscricoes: list[Inscricao] | None = None
) -> RepositorioEmMemoria:
    repositorio = RepositorioEmMemoria()
    for evento in eventos:
        repositorio.cadastrar_evento(evento)
    for inscricao in inscricoes or []:
        repositorio.gravar_inscricao(inscricao)
    return repositorio


def _cliente(
    repositorio: RepositorioEmMemoria, notificador: NotificadorEspiao
) -> TestClient:
    return TestClient(criar_aplicacao(repositorio, notificador))


def _inscrever(cliente: TestClient, evento_id: str, corpo: Any) -> httpx.Response:
    return cliente.post(f"/eventos/{evento_id}/inscricoes", json=corpo)


def _corpo_201(
    evento_id: str, participante_id: str, status: str, comprovante_enviado: bool
) -> dict[str, Any]:
    return {
        "evento_id": evento_id,
        "participante_id": participante_id,
        "status": status,
        "comprovante_enviado": comprovante_enviado,
    }


def _verificar_409_sem_efeitos(
    resposta: httpx.Response,
    repositorio: RepositorioEmMemoria,
    inscricoes_iniciais: list[Inscricao],
    notificador: NotificadorEspiao,
) -> None:
    """Contrato: 409 com `detail`; nada gravado e notificador não acionado."""
    assert resposta.status_code == 409
    assert "detail" in resposta.json()
    assert repositorio.listar_inscricoes() == inscricoes_iniciais
    assert notificador.tentativas == []


# ===========================================================================
# 2-contrato-v2.md — A. Funcionamento normal e tipo do evento
# ===========================================================================


def test_ct01_c06_n07_gratuito_com_vaga_confirma_e_envia_um_comprovante() -> None:
    """CT-01 (2-contrato-v2) = C06, N07 (3-erros-e-falhas-v2) — R2, R3.

    Evento gratuito com vaga: 201 confirmada, 1 registro igual à resposta e
    exatamente 1 comprovante; `comprovante_enviado` reflete o envio real.
    """
    e1 = _evento("E1", "09:00", "10:00")
    repositorio = _repositorio([e1])
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E1", {"participante_id": "P1"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201("E1", "P1", "confirmada", True)
    assert repositorio.listar_inscricoes() == [Inscricao("P1", e1, CONFIRMADA)]
    assert notificador.comprovantes_enviados == [Inscricao("P1", e1, CONFIRMADA)]
    assert len(notificador.tentativas) == 1


def test_ct02_c08_pago_com_vaga_fica_pendente_e_envia_comprovante() -> None:
    """CT-02 (2-contrato-v2) = C08 (3-erros-e-falhas-v2) — R2, R3 (RN03)."""
    e2 = _evento("E2", "09:00", "10:00", pago=True)
    repositorio = _repositorio([e2])
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E2", {"participante_id": "P1"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201("E2", "P1", "pendente_pagamento", True)
    assert repositorio.listar_inscricoes() == [Inscricao("P1", e2, PENDENTE)]
    assert len(notificador.comprovantes_enviados) == 1


def test_ct03_e13_participante_id_com_um_caractere_e_aceito() -> None:
    """CT-03 (2-contrato-v2) = E13 (3-erros-e-falhas-v2) — validação do corpo.

    Limite mínimo válido de `participante_id`: 1 caractere.
    """
    e1 = _evento("E1", "09:00", "10:00")
    repositorio = _repositorio([e1])
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E1", {"participante_id": "x"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201("E1", "x", "confirmada", True)
    assert repositorio.listar_inscricoes() == [Inscricao("x", e1, CONFIRMADA)]
    assert len(notificador.comprovantes_enviados) == 1


def test_ct04_participante_id_com_espacos_acentos_e_simbolos() -> None:
    """CT-04 — premissa do prompt: qualquer texto não vazio é aceito."""
    e1 = _evento("E1", "09:00", "10:00")
    repositorio = _repositorio([e1])
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E1", {"participante_id": "Ana Ñ-01"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201("E1", "Ana Ñ-01", "confirmada", True)
    assert repositorio.listar_inscricoes() == [Inscricao("Ana Ñ-01", e1, CONFIRMADA)]
    assert len(notificador.comprovantes_enviados) == 1


# ===========================================================================
# 2-contrato-v2.md — B. Vagas (R2)
# ===========================================================================


def test_ct05_ultima_vaga_evento_gratuito() -> None:
    """CT-05 — R2 (RN05, limite): a última vaga ainda confirma."""
    e1 = _evento("E1", "09:00", "10:00")
    existentes = [Inscricao("P2", e1, CONFIRMADA)]
    repositorio = _repositorio([e1], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E1", {"participante_id": "P1"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201("E1", "P1", "confirmada", True)
    assert repositorio.listar_inscricoes() == [
        *existentes,
        Inscricao("P1", e1, CONFIRMADA),
    ]
    assert len(notificador.comprovantes_enviados) == 1


def test_ct06_ultima_vaga_evento_pago_com_pendente_ocupando_vaga() -> None:
    """CT-06 — R2 (RN05, limite), R3 (RN03)."""
    e2 = _evento("E2", "09:00", "10:00", pago=True)
    existentes = [Inscricao("P2", e2, PENDENTE)]
    repositorio = _repositorio([e2], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E2", {"participante_id": "P1"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201("E2", "P1", "pendente_pagamento", True)
    assert repositorio.listar_inscricoes() == [
        *existentes,
        Inscricao("P1", e2, PENDENTE),
    ]
    assert len(notificador.comprovantes_enviados) == 1


def test_ct07_gratuito_lotado_por_confirmadas_vai_para_lista_espera() -> None:
    """CT-07 — R2 (RN05)."""
    e1 = _evento("E1", "09:00", "10:00")
    existentes = [Inscricao("P2", e1, CONFIRMADA), Inscricao("P3", e1, CONFIRMADA)]
    repositorio = _repositorio([e1], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E1", {"participante_id": "P1"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201("E1", "P1", "lista_espera", True)
    assert repositorio.listar_inscricoes() == [
        *existentes,
        Inscricao("P1", e1, LISTA_ESPERA),
    ]
    assert len(notificador.comprovantes_enviados) == 1


def test_ct08_r18_pago_lotado_por_pendente_vai_para_lista_espera() -> None:
    """CT-08 (2-contrato-v2) = R18 (3-erros-e-falhas-v2) — R2 antes de R3.

    Evento pago de 1 vaga ocupada por `pendente_pagamento`: a nova inscrição
    vai para `lista_espera`, não `pendente_pagamento`.
    """
    e2 = _evento("E2", "09:00", "10:00", vagas=1, pago=True)
    existentes = [Inscricao("P2", e2, PENDENTE)]
    repositorio = _repositorio([e2], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E2", {"participante_id": "P1"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201("E2", "P1", "lista_espera", True)
    assert repositorio.listar_inscricoes() == [
        *existentes,
        Inscricao("P1", e2, LISTA_ESPERA),
    ]
    assert len(notificador.comprovantes_enviados) == 1


def test_ct09_lotado_por_confirmada_mais_pendente() -> None:
    """CT-09 — R2 (RN05 + decisão de 2026-10-25: pendente ocupa vaga)."""
    e2 = _evento("E2", "09:00", "10:00", pago=True)
    existentes = [Inscricao("P2", e2, CONFIRMADA), Inscricao("P3", e2, PENDENTE)]
    repositorio = _repositorio([e2], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E2", {"participante_id": "P1"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201("E2", "P1", "lista_espera", True)
    assert repositorio.listar_inscricoes() == [
        *existentes,
        Inscricao("P1", e2, LISTA_ESPERA),
    ]
    assert len(notificador.comprovantes_enviados) == 1


def test_ct10_lista_espera_nao_ocupa_vaga() -> None:
    """CT-10 — R2 (RN05): `lista_espera` não ocupa vaga."""
    e1 = _evento("E1", "09:00", "10:00")
    existentes = [
        Inscricao("P2", e1, CONFIRMADA),
        Inscricao("P3", e1, LISTA_ESPERA),
        Inscricao("P4", e1, LISTA_ESPERA),
    ]
    repositorio = _repositorio([e1], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E1", {"participante_id": "P1"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201("E1", "P1", "confirmada", True)
    assert repositorio.listar_inscricoes() == [
        *existentes,
        Inscricao("P1", e1, CONFIRMADA),
    ]
    assert len(notificador.comprovantes_enviados) == 1


def test_ct11_lotado_com_fila_ja_existente() -> None:
    """CT-11 — R2 (RN05): entra na fila e a inscrição de P3 fica inalterada."""
    e1 = _evento("E1", "09:00", "10:00", vagas=1)
    existentes = [Inscricao("P2", e1, CONFIRMADA), Inscricao("P3", e1, LISTA_ESPERA)]
    repositorio = _repositorio([e1], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E1", {"participante_id": "P1"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201("E1", "P1", "lista_espera", True)
    assert repositorio.listar_inscricoes() == [
        *existentes,
        Inscricao("P1", e1, LISTA_ESPERA),
    ]
    assert len(notificador.comprovantes_enviados) == 1


def test_ct12_vagas_contam_so_inscricoes_do_proprio_evento() -> None:
    """CT-12 — R2 (RN05): inscrição em outro evento não ocupa vaga."""
    e1 = _evento("E1", "09:00", "10:00", vagas=1)
    e3 = _evento("E3", "14:00", "15:00", vagas=1)
    existentes = [Inscricao("P2", e3, CONFIRMADA)]
    repositorio = _repositorio([e1, e3], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E1", {"participante_id": "P1"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201("E1", "P1", "confirmada", True)
    assert repositorio.listar_inscricoes() == [
        *existentes,
        Inscricao("P1", e1, CONFIRMADA),
    ]
    assert len(notificador.comprovantes_enviados) == 1


# ===========================================================================
# 2-contrato-v2.md — C. Já inscrito (R0)
# ===========================================================================


def test_ct13_r02_ja_inscrito_como_confirmada_responde_409() -> None:
    """CT-13 (2-contrato-v2) = R02 (3-erros-e-falhas-v2) — R0 (já inscrito)."""
    e1 = _evento("E1", "09:00", "10:00")
    existentes = [Inscricao("P1", e1, CONFIRMADA)]
    repositorio = _repositorio([e1], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E1", {"participante_id": "P1"}
    )

    _verificar_409_sem_efeitos(resposta, repositorio, existentes, notificador)


def test_ct14_r03_c03_ja_inscrito_como_pendente_responde_409() -> None:
    """CT-14 (2-contrato-v2) = R03, C03 (3-erros-e-falhas-v2) — R0.

    O 409 não altera nem sobrescreve o registro `pendente_pagamento`.
    """
    e2 = _evento("E2", "09:00", "10:00", pago=True)
    existentes = [Inscricao("P1", e2, PENDENTE)]
    repositorio = _repositorio([e2], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E2", {"participante_id": "P1"}
    )

    _verificar_409_sem_efeitos(resposta, repositorio, existentes, notificador)


def test_ct15_r05_ja_na_lista_espera_com_vaga_responde_409() -> None:
    """CT-15 (2-contrato-v2) = R05 (3-erros-e-falhas-v2) — R0 antes de R2.

    Já está em `lista_espera` e o evento tem vaga: não é promovido nem
    regravado.
    """
    e1 = _evento("E1", "09:00", "10:00")
    existentes = [Inscricao("P1", e1, LISTA_ESPERA)]
    repositorio = _repositorio([e1], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E1", {"participante_id": "P1"}
    )

    _verificar_409_sem_efeitos(resposta, repositorio, existentes, notificador)


def test_ct16_r04_ja_na_lista_espera_e_evento_lotado_responde_409() -> None:
    """CT-16 (2-contrato-v2) = R04 (3-erros-e-falhas-v2) — R0 antes de R2.

    Resultado esperado: 409, e não 201 `lista_espera`.
    """
    e1 = _evento("E1", "09:00", "10:00", vagas=1)
    existentes = [Inscricao("P2", e1, CONFIRMADA), Inscricao("P1", e1, LISTA_ESPERA)]
    repositorio = _repositorio([e1], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E1", {"participante_id": "P1"}
    )

    _verificar_409_sem_efeitos(resposta, repositorio, existentes, notificador)


def test_ct17_ja_inscrito_e_com_conflito_de_horario_responde_409() -> None:
    """CT-17 — R0 (precedência sobre R1; só o status é verificado, Dúvida 8)."""
    e2 = _evento("E2", "09:00", "10:00", pago=True)
    ea = _evento("EA", "09:30", "10:30")
    existentes = [Inscricao("P1", e2, PENDENTE), Inscricao("P1", ea, CONFIRMADA)]
    repositorio = _repositorio([e2, ea], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E2", {"participante_id": "P1"}
    )

    _verificar_409_sem_efeitos(resposta, repositorio, existentes, notificador)


def test_ct18_outro_participante_inscrito_nao_bloqueia() -> None:
    """CT-18 — R0 (a verificação é por participante)."""
    e1 = _evento("E1", "09:00", "10:00")
    existentes = [Inscricao("P2", e1, CONFIRMADA)]
    repositorio = _repositorio([e1], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E1", {"participante_id": "P1"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201("E1", "P1", "confirmada", True)
    assert repositorio.listar_inscricoes() == [
        *existentes,
        Inscricao("P1", e1, CONFIRMADA),
    ]
    assert len(notificador.comprovantes_enviados) == 1


# ===========================================================================
# 2-contrato-v2.md — D. Conflito de horário (R1)
# EA não tem tipo nem vagas nos casos; usamos gratuito com 2 vagas, que não
# influenciam o resultado. EB é gratuito com 2 vagas, salvo indicação.
# ===========================================================================


def _verificar_conflito_de_horario(evento_a: Evento, evento_b: Evento) -> None:
    """R1 (RN06): P1 confirmada em `evento_a`; pedido em `evento_b` → 409."""
    existentes = [Inscricao("P1", evento_a, CONFIRMADA)]
    repositorio = _repositorio([evento_a, evento_b], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), evento_b.id, {"participante_id": "P1"}
    )

    _verificar_409_sem_efeitos(resposta, repositorio, existentes, notificador)


def _verificar_sem_conflito_de_horario(
    existentes: list[Inscricao], eventos: list[Evento], evento_b: Evento
) -> None:
    """R1 (RN06): pedido de P1 em `evento_b` → 201 confirmada, 1 comprovante."""
    repositorio = _repositorio([*eventos, evento_b], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), evento_b.id, {"participante_id": "P1"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201(evento_b.id, "P1", "confirmada", True)
    assert repositorio.listar_inscricoes() == [
        *existentes,
        Inscricao("P1", evento_b, CONFIRMADA),
    ]
    assert len(notificador.comprovantes_enviados) == 1


def test_ct19_sobreposicao_parcial_alvo_comeca_durante_o_outro() -> None:
    """CT-19 — R1 (RN06)."""
    _verificar_conflito_de_horario(
        _evento("EA", "09:00", "11:00"), _evento("EB", "10:00", "12:00")
    )


def test_ct20_sobreposicao_parcial_alvo_termina_durante_o_outro() -> None:
    """CT-20 — R1 (RN06)."""
    _verificar_conflito_de_horario(
        _evento("EA", "10:00", "12:00"), _evento("EB", "09:00", "11:00")
    )


def test_ct21_alvo_contido_no_outro_evento() -> None:
    """CT-21 — R1 (RN06)."""
    _verificar_conflito_de_horario(
        _evento("EA", "09:00", "12:00"), _evento("EB", "10:00", "11:00")
    )


def test_ct22_alvo_contem_o_outro_evento() -> None:
    """CT-22 — R1 (RN06)."""
    _verificar_conflito_de_horario(
        _evento("EA", "10:00", "11:00"), _evento("EB", "09:00", "12:00")
    )


def test_ct23_horarios_identicos() -> None:
    """CT-23 — R1 (RN06)."""
    _verificar_conflito_de_horario(
        _evento("EA", "09:00", "10:00"), _evento("EB", "09:00", "10:00")
    )


def test_ct24_sobreposicao_minima_de_um_minuto() -> None:
    """CT-24 — R1 (RN06, limite)."""
    _verificar_conflito_de_horario(
        _evento("EA", "09:00", "10:01"), _evento("EB", "10:00", "11:00")
    )


def test_ct25_eventos_que_se_encostam_outro_termina_quando_alvo_comeca() -> None:
    """CT-25 — R1 (RN06, limite): eventos que só se encostam não conflitam."""
    ea = _evento("EA", "09:00", "10:00")
    _verificar_sem_conflito_de_horario(
        [Inscricao("P1", ea, CONFIRMADA)], [ea], _evento("EB", "10:00", "11:00")
    )


def test_ct26_eventos_que_se_encostam_alvo_termina_quando_outro_comeca() -> None:
    """CT-26 — R1 (RN06, limite): eventos que só se encostam não conflitam."""
    ea = _evento("EA", "09:00", "10:00")
    _verificar_sem_conflito_de_horario(
        [Inscricao("P1", ea, CONFIRMADA)], [ea], _evento("EB", "08:00", "09:00")
    )


def test_ct27_mesmo_horario_em_dias_diferentes() -> None:
    """CT-27 — R1 (RN06)."""
    ea = _evento("EA", "09:00", "10:00", dia_inicio=10)
    _verificar_sem_conflito_de_horario(
        [Inscricao("P1", ea, CONFIRMADA)],
        [ea],
        _evento("EB", "09:00", "10:00", dia_inicio=11),
    )


def test_ct28_sobreposicao_atravessando_a_meia_noite() -> None:
    """CT-28 — R1 (RN06)."""
    _verificar_conflito_de_horario(
        _evento("EA", "23:00", "01:00", dia_inicio=10, dia_fim=11),
        _evento("EB", "00:00", "02:00", dia_inicio=11),
    )


def test_ct29_pendente_em_evento_sobreposto_nao_conflita() -> None:
    """CT-29 — R1 (RN06): só inscrição confirmada gera conflito."""
    ea = _evento("EA", "09:00", "11:00", pago=True)
    _verificar_sem_conflito_de_horario(
        [Inscricao("P1", ea, PENDENTE)], [ea], _evento("EB", "10:00", "12:00")
    )


def test_ct30_lista_espera_em_evento_sobreposto_nao_conflita() -> None:
    """CT-30 — R1 (RN06): só inscrição confirmada gera conflito."""
    ea = _evento("EA", "09:00", "11:00")
    _verificar_sem_conflito_de_horario(
        [Inscricao("P1", ea, LISTA_ESPERA)], [ea], _evento("EB", "10:00", "12:00")
    )


def test_ct31_confirmada_de_outro_participante_nao_afeta_p1() -> None:
    """CT-31 — R1 (RN06, por participante)."""
    ea = _evento("EA", "09:00", "11:00")
    _verificar_sem_conflito_de_horario(
        [Inscricao("P2", ea, CONFIRMADA)], [ea], _evento("EB", "10:00", "12:00")
    )


def test_ct32_varias_inscricoes_nenhuma_conflitante() -> None:
    """CT-32 — R1 (RN06)."""
    ea = _evento("EA", "09:00", "11:00", pago=True)
    ec = _evento("EC", "14:00", "15:00")
    _verificar_sem_conflito_de_horario(
        [Inscricao("P1", ea, PENDENTE), Inscricao("P1", ec, CONFIRMADA)],
        [ea, ec],
        _evento("EB", "10:00", "12:00"),
    )


def test_ct33_conflito_antes_de_vaga_alvo_lotado_e_com_conflito() -> None:
    """CT-33 — R1 antes de R2: 409, e não 201 `lista_espera`."""
    ea = _evento("EA", "09:00", "11:00")
    eb = _evento("EB", "10:00", "12:00", vagas=1)
    existentes = [Inscricao("P2", eb, CONFIRMADA), Inscricao("P1", ea, CONFIRMADA)]
    repositorio = _repositorio([ea, eb], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "EB", {"participante_id": "P1"}
    )

    _verificar_409_sem_efeitos(resposta, repositorio, existentes, notificador)


def test_ct34_conflito_com_evento_alvo_pago() -> None:
    """CT-34 — R1 antes de R3."""
    _verificar_conflito_de_horario(
        _evento("EA", "09:00", "11:00"), _evento("EB", "10:00", "12:00", pago=True)
    )


# ===========================================================================
# 2-contrato-v2.md — E. Notificador
# ===========================================================================


def test_ct35_n01_c11_falha_no_envio_evento_gratuito() -> None:
    """CT-35 (2-contrato-v2) = N01, C11 (3-erros-e-falhas-v2).

    Efeito "falha do notificador" (decisão de 2026-10-25): 201 confirmada
    com `comprovante_enviado: false`; exatamente 1 registro, sem rollback e
    sem duplicata; o notificador foi acionado para essa inscrição; nenhum
    comprovante entregue; a exceção não vira 5xx.
    """
    e1 = _evento("E1", "09:00", "10:00")
    repositorio = _repositorio([e1])
    notificador = NotificadorEspiao(falha=FalhaSimulada("indisponível"))

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E1", {"participante_id": "P1"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201("E1", "P1", "confirmada", False)
    assert repositorio.listar_inscricoes() == [Inscricao("P1", e1, CONFIRMADA)]
    assert notificador.tentativas == [Inscricao("P1", e1, CONFIRMADA)]
    assert notificador.comprovantes_enviados == []


def test_ct36_n02_falha_no_envio_evento_pago() -> None:
    """CT-36 (2-contrato-v2) = N02 (3-erros-e-falhas-v2) — falha do notificador."""
    e2 = _evento("E2", "09:00", "10:00", pago=True)
    repositorio = _repositorio([e2])
    notificador = NotificadorEspiao(falha=FalhaSimulada("indisponível"))

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E2", {"participante_id": "P1"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201("E2", "P1", "pendente_pagamento", False)
    assert repositorio.listar_inscricoes() == [Inscricao("P1", e2, PENDENTE)]
    assert notificador.comprovantes_enviados == []


def test_ct37_n03_falha_no_envio_inscricao_em_lista_espera() -> None:
    """CT-37 (2-contrato-v2) = N03 (3-erros-e-falhas-v2) — falha + R2 (RN05)."""
    e1 = _evento("E1", "09:00", "10:00", vagas=1)
    existentes = [Inscricao("P2", e1, CONFIRMADA)]
    repositorio = _repositorio([e1], existentes)
    notificador = NotificadorEspiao(falha=FalhaSimulada("indisponível"))

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E1", {"participante_id": "P1"}
    )

    assert resposta.status_code == 201
    assert resposta.json() == _corpo_201("E1", "P1", "lista_espera", False)
    assert repositorio.listar_inscricoes() == [
        *existentes,
        Inscricao("P1", e1, LISTA_ESPERA),
    ]
    assert notificador.comprovantes_enviados == []


def test_ct38_notificador_com_falha_nao_altera_erro_409() -> None:
    """CT-38 — R0 + efeitos de erro: notificador não acionado."""
    e1 = _evento("E1", "09:00", "10:00")
    existentes = [Inscricao("P1", e1, CONFIRMADA)]
    repositorio = _repositorio([e1], existentes)
    notificador = NotificadorEspiao(falha=FalhaSimulada("indisponível"))

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E1", {"participante_id": "P1"}
    )

    _verificar_409_sem_efeitos(resposta, repositorio, existentes, notificador)


def test_ct39_notificador_com_falha_nao_altera_erro_404() -> None:
    """CT-39 — evento inexistente: 404 e notificador não acionado."""
    repositorio = _repositorio([])
    notificador = NotificadorEspiao(falha=FalhaSimulada("indisponível"))

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E9", {"participante_id": "P1"}
    )

    assert resposta.status_code == 404
    assert "detail" in resposta.json()
    assert repositorio.listar_inscricoes() == []
    assert notificador.tentativas == []


# ===========================================================================
# 2-contrato-v2.md — F. Evento inexistente
# ===========================================================================


def test_ct40_r01_c01_evento_inexistente_com_outros_eventos_cadastrados() -> None:
    """CT-40 (2-contrato-v2) = R01, C01 (3-erros-e-falhas-v2) — contrato 404.

    Com o repositório já populado: nada gravado, nenhum evento criado como
    efeito e notificador não acionado.
    """
    e1 = _evento("E1", "09:00", "10:00")
    existentes = [Inscricao("P2", e1, CONFIRMADA)]
    repositorio = _repositorio([e1], existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E9", {"participante_id": "P1"}
    )

    assert resposta.status_code == 404
    assert "detail" in resposta.json()
    assert repositorio.listar_inscricoes() == existentes
    assert repositorio.buscar_evento("E9") is None
    assert notificador.tentativas == []


def test_ct41_repositorio_sem_nenhum_evento() -> None:
    """CT-41 — contrato 404."""
    repositorio = _repositorio([])
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "E1", {"participante_id": "P1"}
    )

    assert resposta.status_code == 404
    assert "detail" in resposta.json()
    assert repositorio.listar_inscricoes() == []
    assert repositorio.buscar_evento("E1") is None
    assert notificador.tentativas == []


# ===========================================================================
# Corpo inválido (422): 2-contrato-v2.md seção G e 3-erros-e-falhas-v2.md
# seção 1. Estado: um evento gratuito com 2 vagas e sem inscrições.
# ===========================================================================


def _verificar_422_sem_efeitos(**argumentos_do_post: Any) -> None:
    """Contrato: 422; nada gravado e notificador não acionado."""
    e1 = _evento("E1", "09:00", "10:00")
    repositorio = _repositorio([e1])
    notificador = NotificadorEspiao()

    resposta = _cliente(repositorio, notificador).post(
        "/eventos/E1/inscricoes", **argumentos_do_post
    )

    assert resposta.status_code == 422
    assert repositorio.listar_inscricoes() == []
    assert notificador.tentativas == []


def test_ct42_e01_campo_ausente() -> None:
    """CT-42 (2-contrato-v2) = E01 (3-erros-e-falhas-v2) — campo obrigatório."""
    _verificar_422_sem_efeitos(json={})


def test_ct43_e03_c02_campo_vazio() -> None:
    """CT-43 (2-contrato-v2) = E03, C02 (3-erros-e-falhas-v2) — não vazio."""
    _verificar_422_sem_efeitos(json={"participante_id": ""})


def test_ct44_e04_campo_nulo() -> None:
    """CT-44 (2-contrato-v2) = E04 (3-erros-e-falhas-v2) — campo de texto."""
    _verificar_422_sem_efeitos(json={"participante_id": None})


def test_ct45_e09_requisicao_sem_corpo() -> None:
    """CT-45 (2-contrato-v2) = E09 (3-erros-e-falhas-v2) — corpo inválido."""
    _verificar_422_sem_efeitos()


def test_ct46_e10_json_malformado() -> None:
    """CT-46 (2-contrato-v2) = E10 (3-erros-e-falhas-v2) — corpo inválido."""
    _verificar_422_sem_efeitos(
        content='{"participante_id": "P1"',
        headers={"Content-Type": "application/json"},
    )


def test_ct47_corpo_que_nao_e_objeto() -> None:
    """CT-47 — corpo inválido: lista com texto."""
    _verificar_422_sem_efeitos(json=["P1"])


def test_ct48_nome_do_campo_errado() -> None:
    """CT-48 — campo obrigatório: `participante` no lugar de `participante_id`."""
    _verificar_422_sem_efeitos(json={"participante": "P1"})


def test_e02_nome_do_campo_em_camel_case() -> None:
    """E02 — campo obrigatório: `participanteId` equivale a campo ausente."""
    _verificar_422_sem_efeitos(json={"participanteId": "part-001"})


def test_e05_tipo_numerico_em_vez_de_texto() -> None:
    """E05 — contrato: `participante_id` é texto; não grava `"123"`."""
    _verificar_422_sem_efeitos(json={"participante_id": 123})


def test_e06_tipo_booleano() -> None:
    """E06 — contrato: `participante_id` é texto."""
    _verificar_422_sem_efeitos(json={"participante_id": True})


def test_e07_tipo_objeto() -> None:
    """E07 — contrato: `participante_id` é texto."""
    _verificar_422_sem_efeitos(json={"participante_id": {"id": "part-001"}})


def test_e08_tipo_lista() -> None:
    """E08 — contrato: `participante_id` é texto."""
    _verificar_422_sem_efeitos(json={"participante_id": ["part-001"]})


def test_e11_corpo_e_lista_de_objetos() -> None:
    """E11 — corpo inválido: lista, não objeto."""
    _verificar_422_sem_efeitos(json=[{"participante_id": "part-001"}])


def test_e12_corpo_e_string_json() -> None:
    """E12 — corpo inválido: string JSON."""
    _verificar_422_sem_efeitos(json="part-001")


# ===========================================================================
# 2-contrato-v2.md — H. Sequências (estado produzido pela própria API)
# ===========================================================================


def test_ct49_c10_mesma_inscricao_repetida() -> None:
    """CT-49 (2-contrato-v2) = C10 (3-erros-e-falhas-v2) — R0 + gravação.

    1º 201 confirmada; 2º 409. Final: 1 registro e 1 comprovante no total.
    """
    e1 = _evento("E1", "09:00", "10:00")
    repositorio = _repositorio([e1])
    notificador = NotificadorEspiao()
    cliente = _cliente(repositorio, notificador)

    primeira = _inscrever(cliente, "E1", {"participante_id": "P1"})
    segunda = _inscrever(cliente, "E1", {"participante_id": "P1"})

    assert primeira.status_code == 201
    assert primeira.json() == _corpo_201("E1", "P1", "confirmada", True)
    assert segunda.status_code == 409
    assert "detail" in segunda.json()
    assert repositorio.listar_inscricoes() == [Inscricao("P1", e1, CONFIRMADA)]
    assert len(notificador.comprovantes_enviados) == 1
    assert len(notificador.tentativas) == 1


def test_ct50_preenchimento_de_vagas() -> None:
    """CT-50 — R2 (RN05) + gravação: a vaga ocupada pela API conta depois."""
    e1 = _evento("E1", "09:00", "10:00", vagas=1)
    repositorio = _repositorio([e1])
    notificador = NotificadorEspiao()
    cliente = _cliente(repositorio, notificador)

    respostas = [
        _inscrever(cliente, "E1", {"participante_id": participante})
        for participante in ("P1", "P2", "P3")
    ]

    assert [resposta.status_code for resposta in respostas] == [201, 201, 201]
    assert [resposta.json()["status"] for resposta in respostas] == [
        "confirmada",
        "lista_espera",
        "lista_espera",
    ]
    assert all(resposta.json()["comprovante_enviado"] is True for resposta in respostas)
    assert repositorio.listar_inscricoes() == [
        Inscricao("P1", e1, CONFIRMADA),
        Inscricao("P2", e1, LISTA_ESPERA),
        Inscricao("P3", e1, LISTA_ESPERA),
    ]
    assert len(notificador.comprovantes_enviados) == 3


def test_ct51_confirmada_criada_pela_api_gera_conflito_depois() -> None:
    """CT-51 — R1 (RN06) + gravação."""
    ea = _evento("EA", "09:00", "11:00")
    eb = _evento("EB", "10:00", "12:00")
    repositorio = _repositorio([ea, eb])
    notificador = NotificadorEspiao()
    cliente = _cliente(repositorio, notificador)

    primeira = _inscrever(cliente, "EA", {"participante_id": "P1"})
    segunda = _inscrever(cliente, "EB", {"participante_id": "P1"})

    assert primeira.status_code == 201
    assert primeira.json() == _corpo_201("EA", "P1", "confirmada", True)
    assert segunda.status_code == 409
    assert "detail" in segunda.json()
    assert repositorio.listar_inscricoes() == [Inscricao("P1", ea, CONFIRMADA)]
    assert len(notificador.comprovantes_enviados) == 1


def test_ct52_pendente_criada_pela_api_nao_gera_conflito() -> None:
    """CT-52 — R1 (RN06), R3 (RN03)."""
    ea = _evento("EA", "09:00", "11:00", pago=True)
    eb = _evento("EB", "10:00", "12:00")
    repositorio = _repositorio([ea, eb])
    notificador = NotificadorEspiao()
    cliente = _cliente(repositorio, notificador)

    primeira = _inscrever(cliente, "EA", {"participante_id": "P1"})
    segunda = _inscrever(cliente, "EB", {"participante_id": "P1"})

    assert (primeira.status_code, segunda.status_code) == (201, 201)
    assert primeira.json() == _corpo_201("EA", "P1", "pendente_pagamento", True)
    assert segunda.json() == _corpo_201("EB", "P1", "confirmada", True)
    assert len(repositorio.listar_inscricoes()) == 2
    assert len(notificador.comprovantes_enviados) == 2


def test_ct53_lista_espera_criada_pela_api_nao_gera_conflito() -> None:
    """CT-53 — R1 (RN06), R2 (RN05)."""
    ea = _evento("EA", "09:00", "11:00", vagas=1)
    eb = _evento("EB", "10:00", "12:00")
    existentes = [Inscricao("P2", ea, CONFIRMADA)]
    repositorio = _repositorio([ea, eb], existentes)
    notificador = NotificadorEspiao()
    cliente = _cliente(repositorio, notificador)

    primeira = _inscrever(cliente, "EA", {"participante_id": "P1"})
    segunda = _inscrever(cliente, "EB", {"participante_id": "P1"})

    assert (primeira.status_code, segunda.status_code) == (201, 201)
    assert primeira.json() == _corpo_201("EA", "P1", "lista_espera", True)
    assert segunda.json() == _corpo_201("EB", "P1", "confirmada", True)
    assert repositorio.listar_inscricoes() == [
        *existentes,
        Inscricao("P1", ea, LISTA_ESPERA),
        Inscricao("P1", eb, CONFIRMADA),
    ]
    assert len(notificador.comprovantes_enviados) == 2


def test_ct54_n06_nova_tentativa_apos_falha_no_envio_bate_na_duplicidade() -> None:
    """CT-54 (2-contrato-v2) = N06 (3-erros-e-falhas-v2) — falha + R0.

    1º pedido com o notificador falhando: 201 `comprovante_enviado: false`.
    2º pedido com o notificador normal: 409, notificador não acionado nesta
    requisição. Final: 1 inscrição e 0 comprovantes entregues.
    """
    e1 = _evento("E1", "09:00", "10:00")
    repositorio = _repositorio([e1])
    notificador = NotificadorEspiao(falha=FalhaSimulada("indisponível"))
    cliente = _cliente(repositorio, notificador)

    primeira = _inscrever(cliente, "E1", {"participante_id": "P1"})
    notificador.falha = None
    tentativas_antes_da_segunda = len(notificador.tentativas)
    segunda = _inscrever(cliente, "E1", {"participante_id": "P1"})

    assert primeira.status_code == 201
    assert primeira.json() == _corpo_201("E1", "P1", "confirmada", False)
    assert segunda.status_code == 409
    assert "detail" in segunda.json()
    assert len(notificador.tentativas) == tentativas_antes_da_segunda
    assert repositorio.listar_inscricoes() == [Inscricao("P1", e1, CONFIRMADA)]
    assert notificador.comprovantes_enviados == []


# ===========================================================================
# 3-erros-e-falhas-v2.md — dados fictícios da tabela de eventos
# ===========================================================================

EVT_100 = _evento("EVT-100", "09:00", "11:00", vagas=2)
EVT_200 = _evento("EVT-200", "10:00", "12:00", vagas=2, pago=True)
EVT_210 = _evento("EVT-210", "09:30", "10:30", vagas=5)
EVT_220 = _evento("EVT-220", "09:00", "11:00", vagas=5)
EVT_300 = _evento("EVT-300", "11:00", "13:00", vagas=5)
EVT_400 = _evento("EVT-400", "14:00", "15:00", vagas=1)
EVT_500 = _evento("EVT-500", "16:00", "17:00", vagas=1, pago=True)
EVENTOS_DO_ARQUIVO_3 = [EVT_100, EVT_200, EVT_210, EVT_220, EVT_300, EVT_400, EVT_500]


def _repositorio_arquivo_3(
    inscricoes: list[Inscricao] | None = None,
) -> RepositorioEmMemoria:
    return _repositorio(EVENTOS_DO_ARQUIVO_3, inscricoes)


def _verificar_201(
    existentes: list[Inscricao],
    evento: Evento,
    participante_id: str,
    status_esperado: StatusInscricao,
) -> None:
    """Contrato 201: grava 1 nova inscrição, mantém as existentes, Notif = 1."""
    repositorio = _repositorio_arquivo_3(existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador),
        evento.id,
        {"participante_id": participante_id},
    )

    assert resposta.status_code == 201
    assert resposta.json()["status"] == status_esperado.value
    assert repositorio.listar_inscricoes() == [
        *existentes,
        Inscricao(participante_id, evento, status_esperado),
    ]
    assert len(notificador.tentativas) == 1


def _verificar_409(existentes: list[Inscricao], evento: Evento) -> None:
    """Contrato 409: repo inalterado, Notif = 0."""
    repositorio = _repositorio_arquivo_3(existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), evento.id, {"participante_id": "part-001"}
    )

    _verificar_409_sem_efeitos(resposta, repositorio, existentes, notificador)


# ===========================================================================
# 3-erros-e-falhas-v2.md — 2. Recurso inexistente ou estado inconsistente
# (R01 = CT-40, R02 = CT-13, R03 = CT-14, R04 = CT-16, R05 = CT-15, R18 = CT-08)
# ===========================================================================


def test_r06_c04_conflito_sobreposicao_parcial() -> None:
    """R06, C04 — R1 (RN06): nada em EVT-200; EVT-100 intacto; Notif = 0."""
    _verificar_409([Inscricao("part-001", EVT_100, CONFIRMADA)], EVT_200)


def test_r07_conflito_evento_contido_no_outro() -> None:
    """R07 — R1 (RN06)."""
    _verificar_409([Inscricao("part-001", EVT_100, CONFIRMADA)], EVT_210)


def test_r08_conflito_horarios_identicos() -> None:
    """R08 — R1 (RN06)."""
    _verificar_409([Inscricao("part-001", EVT_100, CONFIRMADA)], EVT_220)


def test_r09_conflito_sobreposicao_no_sentido_inverso() -> None:
    """R09 — R1 (RN06)."""
    _verificar_409([Inscricao("part-001", EVT_200, CONFIRMADA)], EVT_100)


def test_r10_duplicidade_e_conflito_ao_mesmo_tempo() -> None:
    """R10 — R0 e R1 (estado inconsistente de propósito); só o status conta."""
    _verificar_409(
        [
            Inscricao("part-001", EVT_100, CONFIRMADA),
            Inscricao("part-001", EVT_210, CONFIRMADA),
        ],
        EVT_100,
    )


def test_r11_inscricao_duplicada_ja_gravada() -> None:
    """R11 — R0: continuam exatamente 2 registros, sem um terceiro."""
    _verificar_409(
        [
            Inscricao("part-001", EVT_100, CONFIRMADA),
            Inscricao("part-001", EVT_100, CONFIRMADA),
        ],
        EVT_100,
    )


def test_r12_mais_vagas_ocupadas_do_que_o_total() -> None:
    """R12 — R2 (RN05): EVT-100 (2 vagas) com 3 confirmadas → lista_espera.

    Os ids dos 3 outros participantes (part-002, part-004, part-005) são
    fictícios: o caso não os nomeia.
    """
    _verificar_201(
        [
            Inscricao("part-002", EVT_100, CONFIRMADA),
            Inscricao("part-004", EVT_100, CONFIRMADA),
            Inscricao("part-005", EVT_100, CONFIRMADA),
        ],
        EVT_100,
        "part-003",
        LISTA_ESPERA,
    )


def test_r13_eventos_que_so_se_encostam_nao_conflitam() -> None:
    """R13 — R1 (RN06, limite)."""
    _verificar_201(
        [Inscricao("part-001", EVT_100, CONFIRMADA)], EVT_300, "part-001", CONFIRMADA
    )


def test_r14_sobreposicao_com_pendente_nao_conflita() -> None:
    """R14 — R1 (RN06): só inscrição confirmada gera conflito."""
    _verificar_201(
        [Inscricao("part-001", EVT_200, PENDENTE)], EVT_100, "part-001", CONFIRMADA
    )


def test_r15_sobreposicao_com_lista_espera_nao_conflita() -> None:
    """R15 — R1 (RN06): só inscrição confirmada gera conflito.

    EVT-210 (5 vagas) lotado por 5 participantes fictícios (o caso não os
    nomeia) e part-001 em `lista_espera`.
    """
    ocupantes = [
        Inscricao(f"part-0{numero:02d}", EVT_210, CONFIRMADA) for numero in range(2, 7)
    ]
    _verificar_201(
        [*ocupantes, Inscricao("part-001", EVT_210, LISTA_ESPERA)],
        EVT_100,
        "part-001",
        CONFIRMADA,
    )


def test_r16_consulta_de_conflito_filtra_pelo_participante() -> None:
    """R16 — R1 (RN06, por participante), R3 (RN03)."""
    _verificar_201(
        [Inscricao("part-002", EVT_100, CONFIRMADA)], EVT_200, "part-001", PENDENTE
    )


def test_r17_c07_ultima_vaga_ocupada_por_confirmada() -> None:
    """R17, C07 — R2 (RN05): lista_espera também envia comprovante (Notif = 1)."""
    _verificar_201(
        [Inscricao("part-002", EVT_400, CONFIRMADA)], EVT_400, "part-001", LISTA_ESPERA
    )


def test_r19_lista_espera_nao_ocupa_vaga() -> None:
    """R19 — R2 (RN05)."""
    _verificar_201(
        [Inscricao("part-002", EVT_400, LISTA_ESPERA)], EVT_400, "part-001", CONFIRMADA
    )


def test_r20_evento_pago_e_lotado_vai_para_lista_espera() -> None:
    """R20 — R2 antes de R3."""
    _verificar_201(
        [Inscricao("part-002", EVT_500, CONFIRMADA)], EVT_500, "part-001", LISTA_ESPERA
    )


def test_r21_evento_pago_com_exatamente_uma_vaga_restante() -> None:
    """R21 — R2 (RN05, limite), R3 (RN03)."""
    _verificar_201(
        [Inscricao("part-002", EVT_200, PENDENTE)], EVT_200, "part-001", PENDENTE
    )


# ===========================================================================
# 3-erros-e-falhas-v2.md — 3. Falha do notificador
# (N01 = CT-35, N02 = CT-36, N03 = CT-37, N06 = CT-54, N07 = CT-01)
# ===========================================================================


@pytest.mark.parametrize(
    "excecao",
    [RuntimeError("erro genérico"), ValueError("erro genérico")],
    ids=["N04-RuntimeError", "N04-ValueError"],
)
def test_n04_qualquer_tipo_de_excecao_do_notificador_e_tratado(
    excecao: Exception,
) -> None:
    """N04 — falha do notificador: qualquer exceção resulta em `false`.

    Confirma que a API trata qualquer exceção do notificador, e não só um tipo.
    """
    repositorio = _repositorio_arquivo_3()
    notificador = NotificadorEspiao(falha=excecao)

    resposta = _inscrever(
        _cliente(repositorio, notificador), "EVT-100", {"participante_id": "part-001"}
    )

    assert resposta.status_code == 201
    assert resposta.json()["comprovante_enviado"] is False
    assert repositorio.listar_inscricoes() == [
        Inscricao("part-001", EVT_100, CONFIRMADA)
    ]


def test_n05_inscricao_gravada_apos_falha_ocupa_vaga() -> None:
    """N05 — falha do notificador + R2 (RN05).

    1º: 201 confirmada, false. 2º, com o notificador normal: 201
    lista_espera, true. 2 inscrições.
    """
    repositorio = _repositorio_arquivo_3()
    notificador = NotificadorEspiao(falha=FalhaSimulada("indisponível"))
    cliente = _cliente(repositorio, notificador)

    primeira = _inscrever(cliente, "EVT-400", {"participante_id": "part-001"})
    notificador.falha = None
    segunda = _inscrever(cliente, "EVT-400", {"participante_id": "part-002"})

    assert primeira.status_code == 201
    assert primeira.json()["status"] == "confirmada"
    assert primeira.json()["comprovante_enviado"] is False
    assert segunda.status_code == 201
    assert segunda.json()["status"] == "lista_espera"
    assert segunda.json()["comprovante_enviado"] is True
    assert repositorio.listar_inscricoes() == [
        Inscricao("part-001", EVT_400, CONFIRMADA),
        Inscricao("part-002", EVT_400, LISTA_ESPERA),
    ]


# ===========================================================================
# 3-erros-e-falhas-v2.md — 4. Efeitos colaterais indevidos
# (C01 = CT-40, C02 = CT-43, C03 = CT-14, C04 = R06, C06 = CT-01,
#  C07 = R17, C08 = CT-02, C10 = CT-49, C11 = CT-35)
# ===========================================================================


def test_c05_conflito_tem_precedencia_sobre_falta_de_vaga() -> None:
    """C05 — R1 antes de R2: nenhuma `lista_espera` de part-001 em EVT-200.

    O caso não diz o status de part-002 e part-003; usamos `confirmada`.
    """
    _verificar_409(
        [
            Inscricao("part-001", EVT_100, CONFIRMADA),
            Inscricao("part-002", EVT_200, CONFIRMADA),
            Inscricao("part-003", EVT_200, CONFIRMADA),
        ],
        EVT_200,
    )


def test_c09_201_nao_altera_outras_inscricoes() -> None:
    """C09 — contrato 201: registros de part-002 e part-003 ficam idênticos.

    O caso não diz o status de part-002 e part-003; usamos `confirmada`.
    """
    existentes = [
        Inscricao("part-002", EVT_100, CONFIRMADA),
        Inscricao("part-003", EVT_100, CONFIRMADA),
    ]
    repositorio = _repositorio_arquivo_3(existentes)
    notificador = NotificadorEspiao()

    resposta = _inscrever(
        _cliente(repositorio, notificador), "EVT-100", {"participante_id": "part-001"}
    )

    assert resposta.status_code == 201
    assert repositorio.listar_inscricoes()[:2] == existentes


def test_c12_sequencia_422_404_409_nao_acumula_envios() -> None:
    """C12 — E01, R01 e R02 em sequência no mesmo dublê: Notif total = 0.

    Só o estado preparado pelo R02 continua no repositório.
    """
    existentes = [Inscricao("part-001", EVT_100, CONFIRMADA)]
    repositorio = _repositorio_arquivo_3(existentes)
    notificador = NotificadorEspiao()
    cliente = _cliente(repositorio, notificador)

    resposta_e01 = _inscrever(cliente, "EVT-100", {})
    resposta_r01 = _inscrever(cliente, "EVT-999", {"participante_id": "part-001"})
    resposta_r02 = _inscrever(cliente, "EVT-100", {"participante_id": "part-001"})

    assert [
        resposta_e01.status_code,
        resposta_r01.status_code,
        resposta_r02.status_code,
    ] == [422, 404, 409]
    assert notificador.tentativas == []
    assert repositorio.listar_inscricoes() == existentes
