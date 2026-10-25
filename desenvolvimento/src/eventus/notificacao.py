"""Envio do comprovante de inscrição (RF03).

O canal de envio não foi definido (lacuna 5 de `duvidas-e-lacunas.md`),
por isso o notificador é uma interface e só há uma implementação falsa.
"""

from typing import Protocol

from eventus.inscricao import Inscricao


class Notificador(Protocol):
    """Envia ao participante o comprovante de uma inscrição (RF03)."""

    def enviar_comprovante(self, inscricao: Inscricao) -> None:
        """Envia o comprovante; lança exceção se o envio falhar."""
        ...


class FalhaNoEnvioDeComprovante(Exception):
    """Falha simulada pelo `NotificadorFalso`."""


class NotificadorFalso:
    """Notificador que só registra os envios, sem canal real.

    Attributes:
        comprovantes_enviados: Inscrições cujo comprovante foi enviado.
        deve_falhar: Se True, todo envio lança `FalhaNoEnvioDeComprovante`.
    """

    def __init__(self, deve_falhar: bool = False) -> None:
        self.comprovantes_enviados: list[Inscricao] = []
        self.deve_falhar = deve_falhar

    def enviar_comprovante(self, inscricao: Inscricao) -> None:
        """Registra o envio ou, se `deve_falhar`, lança exceção.

        Raises:
            FalhaNoEnvioDeComprovante: Se o notificador foi configurado
                para falhar.
        """
        if self.deve_falhar:
            raise FalhaNoEnvioDeComprovante(
                f"Falha simulada ao enviar comprovante para "
                f"{inscricao.participante_id!r} no evento {inscricao.evento.id!r}"
            )
        self.comprovantes_enviados.append(inscricao)
