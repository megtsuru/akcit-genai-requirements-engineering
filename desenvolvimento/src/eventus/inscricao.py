"""Avaliacao de uma tentativa de inscricao (RN01, RN03, RN05, RN06)."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class StatusInscricao(Enum):
    """Status de uma inscricao ja existente."""

    CONFIRMADA = "confirmada"
    PENDENTE_PAGAMENTO = "pendente_pagamento"
    LISTA_ESPERA = "lista_espera"


class ResultadoInscricao(Enum):
    """Resultado da avaliacao de uma tentativa de inscricao."""

    CONFIRMADA = "confirmada"
    PENDENTE_PAGAMENTO = "pendente_pagamento"
    LISTA_ESPERA = "lista_espera"
    RECUSADA_CONFLITO_HORARIO = "recusada_conflito_horario"


@dataclass(frozen=True)
class Evento:
    """Evento (ou atividade) em que o participante pode se inscrever."""

    id: str
    inicio: datetime
    fim: datetime
    vagas: int
    pago: bool


@dataclass(frozen=True)
class Inscricao:
    """Inscricao ja existente de um participante em um evento."""

    participante_id: str
    evento: Evento
    status: StatusInscricao


# RN05: status que ocupam vaga no evento (pendente de pagamento reserva a vaga).
_STATUS_QUE_OCUPAM_VAGA = frozenset(
    {StatusInscricao.CONFIRMADA, StatusInscricao.PENDENTE_PAGAMENTO}
)


def _sobrepoe(a: Evento, b: Evento) -> bool:
    # RN06: eventos que so se encostam (fim de um == inicio do outro) nao conflitam.
    return a.inicio < b.fim and b.inicio < a.fim


def avaliar_inscricao(
    participante_id: str,
    evento: Evento,
    inscricoes: list[Inscricao],
) -> ResultadoInscricao:
    """Decide o resultado de uma tentativa de inscricao, sem gravar nada.

    Regras avaliadas nesta ordem: validacao, conflito de horario (RN06),
    vagas (RN05) e tipo do evento (RN01, RN03).

    Args:
        participante_id: Identificador do participante que quer se inscrever.
        evento: Evento em que o participante quer se inscrever.
        inscricoes: Inscricoes ja existentes, de qualquer participante e de
            qualquer evento.

    Returns:
        O resultado da inscricao.

    Raises:
        ValueError: Se o evento terminar antes ou no mesmo instante em que
            comeca, se tiver menos de 1 vaga ou se o participante ja tiver
            inscricao (qualquer status) neste evento.
    """
    # 1. Validacao
    if evento.fim <= evento.inicio:
        raise ValueError(
            f"Evento {evento.id!r}: fim ({evento.fim}) deve ser posterior "
            f"ao inicio ({evento.inicio})."
        )
    if evento.vagas < 1:
        raise ValueError(
            f"Evento {evento.id!r}: vagas deve ser pelo menos 1 "
            f"(recebido {evento.vagas})."
        )
    if any(
        i.participante_id == participante_id and i.evento.id == evento.id
        for i in inscricoes
    ):
        raise ValueError(
            f"Participante {participante_id!r} ja tem inscricao no evento "
            f"{evento.id!r}."
        )

    # 2. RN06: conflito de horario com inscricao CONFIRMADA do proprio
    # participante em outro evento bloqueia a inscricao (caso de uso A2).
    if any(
        i.participante_id == participante_id
        and i.status is StatusInscricao.CONFIRMADA
        and i.evento.id != evento.id
        and _sobrepoe(i.evento, evento)
        for i in inscricoes
    ):
        return ResultadoInscricao.RECUSADA_CONFLITO_HORARIO

    # 3. RN05: sem vaga disponivel -> lista de espera.
    # Ocupam vaga CONFIRMADA e PENDENTE_PAGAMENTO; LISTA_ESPERA nao ocupa
    # (decisao de 2026-10-25 sobre duvidas-e-lacunas.md item 6, opcao A).
    ocupadas = sum(
        1
        for i in inscricoes
        if i.evento.id == evento.id and i.status in _STATUS_QUE_OCUPAM_VAGA
    )
    if ocupadas >= evento.vagas:
        return ResultadoInscricao.LISTA_ESPERA

    # 4. RN01, RN03: gratuito confirma; pago fica pendente de pagamento.
    if evento.pago:
        return ResultadoInscricao.PENDENTE_PAGAMENTO
    return ResultadoInscricao.CONFIRMADA
