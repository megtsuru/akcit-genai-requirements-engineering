# Guia da stack — Python

> Guia de linguagem e ferramentas para o agente `desenvolvedor`. Vale para
> qualquer projeto Python que o indique no seu `AGENTS.md`. Todas as
> ferramentas são livres e de código aberto.

## Ferramentas

| Função | Ferramenta | Comando |
|--------|-----------|---------|
| Linguagem | Python 3.13 | — |
| Ambiente e dependências | [uv](https://docs.astral.sh/uv/) | `uv sync` |
| Testes | [pytest](https://docs.pytest.org/) | `uv run pytest` |
| Lint | [Ruff](https://docs.astral.sh/ruff/) | `uv run ruff check src tests` |
| Formatação | Ruff | `uv run ruff format src tests` |
| Tipos | [mypy](https://mypy.readthedocs.io/) | `uv run mypy src` |

- Rode os comandos a partir da pasta que contém o `pyproject.toml`.
- O código de produção usa **só a biblioteca padrão**. pytest, Ruff e mypy
  são dependências de desenvolvimento (`[dependency-groups] dev`) e já
  estão aprovadas. Qualquer outra dependência exige aprovação.
- Não use `pip install` direto nem ambientes globais: tudo passa pelo uv.

## Estrutura

```
<raiz-python>/
├── pyproject.toml
├── src/<pacote>/      # código de produção
└── tests/             # testes pytest (test_<modulo>.py)
```

## Convenções de código

- Siga a [PEP 8](https://peps.python.org/pep-0008/) (garantida pelo Ruff)
  e, para o que ela não cobre, o
  [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
- Type hints em todas as funções e métodos públicos; o mypy deve passar.
- Use `@dataclass(frozen=True)` para objetos de valor e `enum.Enum` para
  conjuntos fechados de valores (status, tipos).
- Use `datetime` para datas e horas. Não use strings para representá-las.
- Para entrada inválida, lance uma exceção da biblioteca padrão
  (normalmente `ValueError`) com mensagem que diga o que está errado.
  Não retorne `None` nem códigos especiais para indicar erro, e não
  silencie exceções.
- Não use `print` para lógica nem estado global mutável.
- Docstrings no estilo Google nas funções públicas: o que faz, argumentos,
  retorno e exceções.

## Testes

- Um arquivo de teste por módulo, em `tests/`.
- Use `pytest.raises(ValueError)` para os casos de erro.
- Use `pytest.mark.parametrize` quando vários exemplos da especificação
  testam a mesma regra, mantendo o ID do exemplo em `ids=`.
- Monte os dados de teste de forma explícita, perto do teste. Não use
  dados aleatórios nem o relógio do sistema.
