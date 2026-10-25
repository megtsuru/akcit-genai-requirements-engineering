# Especificação da tarefa — `avaliar_inscricao`

> Escrita **antes** da geração de código. Dados fictícios.
> Regras cobertas: RN01, RN03, RN05, RN06 (RF02, RF06, RF08, RF09, RF14).

## Objetivo

Dada uma tentativa de inscrição de um participante em um evento, decidir o
resultado: confirmar, deixar pendente de pagamento, colocar em lista de
espera ou recusar por conflito de horário. A função **não** grava nada: só
decide.

## Onde gravar

- Código: `desenvolvimento/src/eventus/`
- Testes: `desenvolvimento/tests/`

## Entradas

```python
class StatusInscricao(Enum):
    CONFIRMADA = "confirmada"
    PENDENTE_PAGAMENTO = "pendente_pagamento"
    LISTA_ESPERA = "lista_espera"

@dataclass(frozen=True)
class Evento:
    id: str
    inicio: datetime
    fim: datetime
    vagas: int
    pago: bool

@dataclass(frozen=True)
class Inscricao:
    participante_id: str
    evento: Evento
    status: StatusInscricao

def avaliar_inscricao(
    participante_id: str,
    evento: Evento,
    inscricoes: list[Inscricao],   # inscrições já existentes (qualquer participante, qualquer evento)
) -> ResultadoInscricao: ...
```

## Saída

```python
class ResultadoInscricao(Enum):
    CONFIRMADA = "confirmada"
    PENDENTE_PAGAMENTO = "pendente_pagamento"
    LISTA_ESPERA = "lista_espera"
    RECUSADA_CONFLITO_HORARIO = "recusada_conflito_horario"
```

## Regras, em ordem de avaliação

1. **Validação** — lança `ValueError` se:
   - `evento.fim <= evento.inicio`;
   - `evento.vagas < 1`;
   - o participante já tem inscrição (qualquer status) neste evento.
2. **Conflito de horário (RN06)** — se o participante tem inscrição
   `CONFIRMADA` em outro evento cujo horário se sobrepõe ao deste →
   `RECUSADA_CONFLITO_HORARIO` (bloqueia, conforme caso de uso
   "Inscrever-se em Evento", A2). Há sobreposição quando
   `a.inicio < b.fim and b.inicio < a.fim`; eventos que só se encostam
   (um termina às 10:00 e o outro começa às 10:00) **não** conflitam.
3. **Vagas (RN05)** — se o evento não tem vaga disponível →
   `LISTA_ESPERA`. Ocupam vaga as inscrições `CONFIRMADA` e
   `PENDENTE_PAGAMENTO` do evento; `LISTA_ESPERA` não ocupa.
   *Decisão de 2026-10-25 sobre a lacuna 6 de `duvidas-e-lacunas.md`
   (opção A): a inscrição pendente de pagamento reserva a vaga. O prazo de
   expiração dessa reserva continua em aberto e está fora desta tarefa.*
4. **Tipo do evento (RN01, RN03)** — gratuito → `CONFIRMADA`; pago →
   `PENDENTE_PAGAMENTO`.

## Exemplos

Base usada nos exemplos (datas em 2026-11-10):

- `W1`: workshop 09:00–10:00, 3 vagas, gratuito
- `W2`: workshop 10:00–11:00, 3 vagas, pago
- `W3`: workshop 09:30–10:30, 3 vagas, gratuito

### Funcionamento normal

| ID | Situação | Esperado |
|----|----------|----------|
| N1 | `p1` em `W1`, sem inscrições existentes | `CONFIRMADA` |
| N2 | `p1` em `W2`, sem inscrições existentes | `PENDENTE_PAGAMENTO` |
| N3 | `p1` em `W1`, que já tem 3 inscrições `CONFIRMADA` de outros participantes | `LISTA_ESPERA` |
| N4 | `p1` em `W3`, tendo inscrição `CONFIRMADA` em `W1` | `RECUSADA_CONFLITO_HORARIO` |

### Limite

| ID | Situação | Esperado |
|----|----------|----------|
| L1 | `p1` em `W1` com 2 `CONFIRMADA` de outros (última vaga) | `CONFIRMADA` |
| L2 | `p1` em `W2`, tendo `CONFIRMADA` em `W1` (W1 termina 10:00, W2 começa 10:00) | `PENDENTE_PAGAMENTO` (sem conflito) |
| L3 | `p1` em `W3` (lotado com 3 `CONFIRMADA`), tendo `CONFIRMADA` em `W1` | `RECUSADA_CONFLITO_HORARIO` (conflito avaliado antes das vagas) |
| L4 | `p1` em `W3`; **outro** participante `p2` tem `CONFIRMADA` em `W1` | `CONFIRMADA` (conflito é só do próprio participante) |
| L5 | `p1` em `W3`, tendo inscrição `LISTA_ESPERA` em `W1` | `CONFIRMADA` (só inscrição confirmada gera conflito) |
| L6 | `p1` em `W2`, que tem 2 `CONFIRMADA` e 1 `PENDENTE_PAGAMENTO` de outros | `LISTA_ESPERA` (pendente reserva vaga) |
| L7 | `p1` em `W1`, que tem 2 `CONFIRMADA` e 1 `LISTA_ESPERA` de outros | `CONFIRMADA` (lista de espera não ocupa vaga) |

### Erro

| ID | Situação | Esperado |
|----|----------|----------|
| E1 | evento com `fim == inicio` | `ValueError` |
| E2 | evento com `vagas = 0` | `ValueError` |
| E3 | `p1` em `W1`, já tendo inscrição `LISTA_ESPERA` em `W1` | `ValueError` |
