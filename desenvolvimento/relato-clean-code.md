# Relato — Clean Code com o agente `desenvolvedor`

**Problema:** `avaliar_inscricao` do Eventus, reaproveitado da atividade
anterior (`especificacao-tarefa.md`: entradas, saídas, regras e exemplos
normais, de limite e de erro).

## 1. Orientação da geração

Critérios de Clean Code acrescentados às instruções (commit `b2ef3b7`):

- **Agente** (`.claude/agents/desenvolvedor.md`, seção "Clean Code"):
  nomes que revelam a intenção e usam o vocabulário do domínio; uma função,
  um propósito, com a função principal lendo como a sequência de regras;
  comentários que explicam o porquê; validar no início e falhar cedo com
  mensagem clara; sem duplicação de regra; "menos linhas ou mais funções
  não são, por si só, melhoria". Também um modo de **revisão**, com
  apontamentos `[bloqueia]`/`[melhora]`/`[estilo]`, localização e
  justificativa.
- **Guia da stack** (`guias/stack-python.md`): cláusulas de guarda,
  `any()`/`sum()` com condição curta (senão, extrair função com nome),
  constantes nomeadas para conjuntos de valores.
- **`AGENTS.md`:** usar o vocabulário dos documentos de análise, sem
  sinônimos.

## 2. Geração sem × com os critérios

O código da atividade 03 (commit `c179c75`) foi apagado e o agente gerou
tudo de novo, numa sessão nova (commit `436c05f`).

Antes (03) — uma função longa, blocos comentados com o *quê*, nomes curtos:

```python
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
```

Depois (04) — a função principal lê como as regras da especificação:

```python
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
```

## 3. Revisão crítica

**Leitura própria:** código claro, responsabilidades bem separadas, sem
segredos; função executada à mão no interpretador, além dos testes. Notei
ainda que o nome `_validar_inscricao_inexistente` não dizia a intenção.

**Revisão do agente** (sessão nova, sem alterar arquivos): nenhum
`[bloqueia]`, 4 `[melhora]`, 4 `[estilo]` e 2 dúvidas.

| Apontamento | Decisão | Por quê |
|---|---|---|
| [melhora] condições de várias linhas em `any()`/`sum()` → funções com nome | Aceito | Dá nome às regras (`_ocupa_vaga_no_evento`); é o que o guia pede |
| [melhora] conflito de horário não excluía o próprio evento (dependia da ordem das validações) | Aceito | A função fica correta sozinha; custa uma linha |
| [melhora] `pytest.raises` sem `match=` | Aceito | Sem isso, o teste passa com qualquer `ValueError` |
| [melhora] faltavam casos de `fim < inicio` e de duplicidade com outros status | Adaptado | O agente não inventou exemplos; eu acrescentei E4–E6 à especificação e ele criou os testes |
| [estilo] usar `parametrize` nos pares de testes | Rejeitado | Um teste por exemplo, com nome descritivo, lê melhor; é preferência |
| [estilo] apelido `PENDENTE` → `PENDENTE_PAGAMENTO` | Aceito | Vocabulário do domínio (`AGENTS.md`) |
| [estilo] docstring em `Evento` e `Inscricao` | Aceito | Custo mínimo |
| [estilo] padronizar `is`/`in` nas comparações de status | Resolvido junto com o primeiro item | — |
| Meu: renomear `_validar_inscricao_inexistente` | Aceito | Novo nome: `_validar_participante_ainda_nao_inscrito` |
| Dúvidas: fuso horário; `Evento` identificado só pelo `id` | Fora do escopo | Registradas aqui como lacunas |

Exemplo de ajuste aceito — antes:

```python
    return any(
        _horarios_se_sobrepoem(inscricao.evento, evento)
        for inscricao in inscricoes
        if inscricao.participante_id == participante_id
        and inscricao.status is StatusInscricao.CONFIRMADA
    )
```

Depois:

```python
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
```

## 4. Verificações (depois dos ajustes, refeitas fora do agente)

- `uv run pytest`: 17/17 (14 exemplos originais + E4–E6);
- `uv run ruff check src tests` e `uv run mypy src` (strict): sem erros;
- diff revisado: só os itens escolhidos, nenhuma regra de negócio mudou;
- sem segredos nem dados reais; código de produção só com a biblioteca
  padrão.
