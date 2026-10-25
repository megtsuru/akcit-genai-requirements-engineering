"""API REST de inscrição em evento (RF02, RF03).

A camada HTTP só traduz requisições e respostas: a decisão é de
`avaliar_inscricao` (RN01, RN03, RN05, RN06).
"""

import logging
from typing import Annotated

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from eventus.inscricao import (
    Inscricao,
    ResultadoInscricao,
    StatusInscricao,
    avaliar_inscricao,
)
from eventus.notificacao import Notificador
from eventus.repositorio import RepositorioInscricoes

logger = logging.getLogger(__name__)


class PedidoInscricao(BaseModel):
    """Corpo de `POST /eventos/{evento_id}/inscricoes`."""

    # strict=True: um número não é convertido em texto, gera 422.
    participante_id: Annotated[str, Field(min_length=1, strict=True)]


class InscricaoCriada(BaseModel):
    """Resposta 201 de `POST /eventos/{evento_id}/inscricoes`."""

    evento_id: str
    participante_id: str
    status: str
    comprovante_enviado: bool


def criar_aplicacao(
    repositorio: RepositorioInscricoes, notificador: Notificador
) -> FastAPI:
    """Cria a aplicação com o repositório e o notificador informados.

    Args:
        repositorio: Onde ficam os eventos e as inscrições.
        notificador: Quem envia o comprovante de inscrição (RF03).

    Returns:
        A aplicação FastAPI com a rota de inscrição.
    """
    aplicacao = FastAPI(title="Eventus — inscrição")

    @aplicacao.post(
        "/eventos/{evento_id}/inscricoes",
        status_code=status.HTTP_201_CREATED,
        response_model=InscricaoCriada,
    )
    def inscrever(evento_id: str, pedido: PedidoInscricao) -> InscricaoCriada:
        evento = repositorio.buscar_evento(evento_id)
        if evento is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=f"Evento {evento_id!r} não encontrado",
            )

        participante_id = pedido.participante_id
        try:
            resultado = avaliar_inscricao(
                participante_id, evento, repositorio.listar_inscricoes()
            )
        except ValueError as erro:
            # avaliar_inscricao sinaliza "participante já inscrito" com
            # ValueError; a mensagem dela já diz o motivo.
            raise HTTPException(status.HTTP_409_CONFLICT, detail=str(erro)) from erro

        if resultado is ResultadoInscricao.RECUSADA_CONFLITO_HORARIO:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=(
                    f"Conflito de horário: participante {participante_id!r} já "
                    f"tem inscrição confirmada em evento que se sobrepõe a "
                    f"{evento_id!r}"
                ),
            )

        inscricao = Inscricao(
            participante_id=participante_id,
            evento=evento,
            status=StatusInscricao(resultado.value),
        )
        repositorio.gravar_inscricao(inscricao)
        comprovante_enviado = _enviar_comprovante(notificador, inscricao)

        return InscricaoCriada(
            evento_id=evento.id,
            participante_id=participante_id,
            status=inscricao.status.value,
            comprovante_enviado=comprovante_enviado,
        )

    return aplicacao


def _enviar_comprovante(notificador: Notificador, inscricao: Inscricao) -> bool:
    """RF03: envia o comprovante e informa se o envio deu certo.

    Decisão de 2026-10-25: falha na notificação não tira a vaga de quem se
    inscreveu, então a falha é registrada no log e não desfaz a inscrição.
    """
    try:
        notificador.enviar_comprovante(inscricao)
    except Exception:
        logger.exception(
            "Falha ao enviar comprovante para %r no evento %r",
            inscricao.participante_id,
            inscricao.evento.id,
        )
        return False
    return True
