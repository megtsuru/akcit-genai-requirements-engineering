"""Repositório de eventos e inscrições usado pela API de inscrição."""

from typing import Protocol

from eventus.inscricao import Evento, Inscricao


class RepositorioInscricoes(Protocol):
    """Guarda eventos e inscrições; a persistência real está fora do escopo."""

    def buscar_evento(self, evento_id: str) -> Evento | None:
        """Devolve o evento com o id informado, ou None se ele não existe."""
        ...

    def listar_inscricoes(self) -> list[Inscricao]:
        """Devolve todas as inscrições, de qualquer participante e evento."""
        ...

    def gravar_inscricao(self, inscricao: Inscricao) -> None:
        """Grava uma nova inscrição."""
        ...


class RepositorioEmMemoria:
    """Implementação em memória de `RepositorioInscricoes`."""

    def __init__(self) -> None:
        self._eventos: dict[str, Evento] = {}
        self._inscricoes: list[Inscricao] = []

    def cadastrar_evento(self, evento: Evento) -> None:
        """Cadastra um evento, substituindo outro de mesmo id."""
        self._eventos[evento.id] = evento

    def buscar_evento(self, evento_id: str) -> Evento | None:
        """Devolve o evento com o id informado, ou None se ele não existe."""
        return self._eventos.get(evento_id)

    def listar_inscricoes(self) -> list[Inscricao]:
        """Devolve uma cópia da lista de inscrições gravadas."""
        return list(self._inscricoes)

    def gravar_inscricao(self, inscricao: Inscricao) -> None:
        """Grava uma nova inscrição."""
        self._inscricoes.append(inscricao)
