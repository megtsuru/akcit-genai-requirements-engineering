"""Avaliação de uma tentativa de inscrição em evento (RN01, RN03, RN05, RN06)."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class StatusInscricao(Enum):
    """Status de uma inscrição já existente."""

    CONFIRMADA = "confirmada"
    PENDENTE_PAGAMENTO = "pendente_pagamento"
    LISTA_ESPERA = "lista_espera"


class ResultadoInscricao(Enum):
    """Resultado da avaliação de uma tentativa de inscrição."""

    CONFIRMADA = "confirmada"
    PENDENTE_PAGAMENTO = "pendente_pagamento"
    LISTA_ESPERA = "lista_espera"
    RECUSADA_CONFLITO_HORARIO = "recusada_conflito_horario"


@dataclass(frozen=True)
class Evento:
    """Evento com horário, número de vagas e indicação de ser pago."""

    id: str
    inicio: datetime
    fim: datetime
    vagas: int
    pago: bool


@dataclass(frozen=True)
class Inscricao:
    """Inscrição já existente de um participante em um evento."""

    participante_id: str
    evento: Evento
    status: StatusInscricao


# RN05 + decisão de 2026-10-25 (lacuna 6, opção A): a inscrição pendente de
# pagamento reserva a vaga; a lista de espera não ocupa vaga.
STATUS_QUE_OCUPAM_VAGA = frozenset(
    {StatusInscricao.CONFIRMADA, StatusInscricao.PENDENTE_PAGAMENTO}
)


def avaliar_inscricao(
    participante_id: str,
    evento: Evento,
    inscricoes: list[Inscricao],
) -> ResultadoInscricao:
    """Decide o resultado de uma tentativa de inscrição, sem gravar nada.

    As regras são avaliadas nesta ordem: validação, conflito de horário
    (RN06), vagas (RN05) e tipo do evento (RN01, RN03).

    Args:
        participante_id: Participante que tenta se inscrever.
        evento: Evento no qual o participante tenta se inscrever.
        inscricoes: Inscrições já existentes, de qualquer participante e
            de qualquer evento.

    Returns:
        O resultado da inscrição.

    Raises:
        ValueError: Se o evento termina antes ou no mesmo instante em que
            começa, se não tem ao menos uma vaga ou se o participante já
            tem inscrição neste evento.
    """
    _validar_evento(evento)
    _validar_participante_ainda_nao_inscrito(participante_id, evento, inscricoes)

    if _tem_conflito_de_horario(participante_id, evento, inscricoes):
        return ResultadoInscricao.RECUSADA_CONFLITO_HORARIO
    if not _tem_vaga_disponivel(evento, inscricoes):
        return ResultadoInscricao.LISTA_ESPERA
    # RN01, RN03: evento pago exige pagamento antes de confirmar.
    if evento.pago:
        return ResultadoInscricao.PENDENTE_PAGAMENTO
    return ResultadoInscricao.CONFIRMADA


def _validar_evento(evento: Evento) -> None:
    if evento.fim <= evento.inicio:
        raise ValueError(
            f"Evento {evento.id!r} deve terminar depois de começar: "
            f"inicio={evento.inicio.isoformat()}, fim={evento.fim.isoformat()}"
        )
    if evento.vagas < 1:
        raise ValueError(
            f"Evento {evento.id!r} deve ter ao menos 1 vaga: vagas={evento.vagas}"
        )


def _validar_participante_ainda_nao_inscrito(
    participante_id: str, evento: Evento, inscricoes: list[Inscricao]
) -> None:
    for inscricao in inscricoes:
        if (
            inscricao.participante_id == participante_id
            and inscricao.evento.id == evento.id
        ):
            raise ValueError(
                f"Participante {participante_id!r} já tem inscrição no evento "
                f"{evento.id!r} com status {inscricao.status.value!r}"
            )


def _tem_conflito_de_horario(
    participante_id: str, evento: Evento, inscricoes: list[Inscricao]
) -> bool:
    """RN06: compara o horário do evento com o das inscrições que podem conflitar."""
    return any(
        _horarios_se_sobrepoem(inscricao.evento, evento)
        for inscricao in inscricoes
        if _pode_gerar_conflito(inscricao, participante_id, evento)
    )


def _pode_gerar_conflito(
    inscricao: Inscricao, participante_id: str, evento: Evento
) -> bool:
    """RN06: só inscrição CONFIRMADA do próprio participante em outro evento."""
    return (
        inscricao.participante_id == participante_id
        and inscricao.status is StatusInscricao.CONFIRMADA
        and inscricao.evento.id != evento.id
    )


def _horarios_se_sobrepoem(evento_a: Evento, evento_b: Evento) -> bool:
    # Intervalos semiabertos: eventos que só se encostam não conflitam.
    return evento_a.inicio < evento_b.fim and evento_b.inicio < evento_a.fim


def _tem_vaga_disponivel(evento: Evento, inscricoes: list[Inscricao]) -> bool:
    """RN05: compara as vagas do evento com as inscrições que as ocupam."""
    vagas_ocupadas = sum(
        1 for inscricao in inscricoes if _ocupa_vaga_no_evento(inscricao, evento)
    )
    return vagas_ocupadas < evento.vagas


def _ocupa_vaga_no_evento(inscricao: Inscricao, evento: Evento) -> bool:
    """RN05: inscrição deste evento com status que ocupa vaga."""
    return (
        inscricao.evento.id == evento.id and inscricao.status in STATUS_QUE_OCUPAM_VAGA
    )
