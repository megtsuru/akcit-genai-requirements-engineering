# Casos de teste de integração: `POST /eventos/{evento_id}/inscricoes`

Você não passou o contrato da API, então parti de um contrato comum. Se o seu for diferente, é só ajustar os códigos e os campos:

- **Autenticação:** `Authorization: Bearer <token>`. O participante é o usuário autenticado.
- **Corpo:** `{ "nome": str, "email": str, "categoria": "inteira" | "meia" }`.
- **Sucesso:** `201 Created` com o corpo `{ id, evento_id, participante_id, status, criado_em }` e o cabeçalho `Location`.
- **Regras de negócio:** o evento tem capacidade, um período de inscrição e um status (`ativo` ou `cancelado`). Cada participante só pode se inscrever uma vez por evento.

## 1. Caminho feliz

| ID | Cenário | Pré-condição | Entrada | Resultado esperado |
|---|---|---|---|---|
| CT01 | Inscrição válida | Evento ativo, com vagas e inscrições abertas | Corpo válido | `201`; corpo com `id`, `status="confirmada"`; `Location: /eventos/{id}/inscricoes/{insc_id}`; registro gravado no banco |
| CT02 | Vagas diminuem | Evento com 10 vagas | Corpo válido | `GET /eventos/{id}` mostra `vagas_disponiveis = 9` |
| CT03 | Ocupa a última vaga | Evento com 1 vaga | Corpo válido | `201`; o evento passa a `vagas_disponiveis = 0` |
| CT04 | Campos opcionais ausentes | — | Só os campos obrigatórios | `201`; os opcionais recebem os valores padrão (ex.: `categoria="inteira"`) |
| CT05 | Efeitos colaterais | Fila ou e-mail mockado | Corpo válido | O evento "inscricao_criada" é publicado ou o e-mail de confirmação é enviado uma única vez |

## 2. Validação de entrada (`400` / `422`)

| ID | Cenário | Entrada | Esperado |
|---|---|---|---|
| CT06 | Corpo vazio | `{}` | `422`, com erros por campo |
| CT07 | JSON malformado | `{"nome": ` | `400` |
| CT08 | E-mail inválido | `"email": "abc"` | `422`, erro no campo `email` |
| CT09 | Nome vazio ou só espaços | `"nome": "   "` | `422` |
| CT10 | Nome acima do limite | 256 caracteres ou mais | `422` |
| CT11 | Tipo errado | `"nome": 123` | `422` |
| CT12 | Enum inválido | `"categoria": "vip"` | `422` |
| CT13 | Campos desconhecidos | `"admin": true` | Ignorados ou `422`, conforme a política. Nunca podem ser gravados |
| CT14 | Content-Type errado | `text/plain` | `415` |
| CT15 | `evento_id` em formato inválido | `/eventos/abc/inscricoes` (quando o id é UUID ou inteiro) | `400` ou `422` |
| CT16 | Caracteres especiais e Unicode | `"nome": "José Ñúñez 😀"` | `201`; o valor é gravado e retornado sem corrupção |

## 3. Autenticação e autorização

| ID | Cenário | Esperado |
|---|---|---|
| CT17 | Sem token | `401` |
| CT18 | Token expirado ou com assinatura inválida | `401` |
| CT19 | Usuário sem permissão (ex.: perfil bloqueado) | `403` |
| CT20 | Evento privado e usuário não convidado | `403`, ou `404` se a API esconder a existência do evento |

## 4. Regras de negócio

| ID | Cenário | Pré-condição | Esperado |
|---|---|---|---|
| CT21 | Evento inexistente | `evento_id` não existe | `404` |
| CT22 | Evento cancelado | `status=cancelado` | `409` ou `422` com código `EVENTO_CANCELADO` |
| CT23 | Evento lotado | `vagas_disponiveis=0` | `409`, código `EVENTO_LOTADO`; nada é gravado |
| CT24 | Inscrições ainda não abertas | `agora < inicio_inscricoes` | `422`, código `INSCRICOES_NAO_ABERTAS` |
| CT25 | Inscrições encerradas | `agora > fim_inscricoes` | `422`, código `INSCRICOES_ENCERRADAS` |
| CT26 | Limite exato de horário | `agora == fim_inscricoes` | O comportamento segue a regra definida (inclusiva ou exclusiva). Use relógio congelado |
| CT27 | Inscrição duplicada | O mesmo participante já está inscrito | `409`, código `INSCRICAO_DUPLICADA`; as vagas continuam iguais |
| CT28 | Duplicada com e-mail em caixa diferente | Já existe `a@x.com`; envia `A@X.com` | `409`, ou seja, o e-mail é normalizado |
| CT29 | Reinscrição após cancelamento | A inscrição anterior foi cancelada | `201`, se a regra permitir |
| CT30 | Mesmo participante em eventos diferentes | Inscrito no evento A | `201` no evento B |

## 5. Concorrência e consistência

| ID | Cenário | Esperado |
|---|---|---|
| CT31 | Corrida pela última vaga: N requisições simultâneas de usuários diferentes com 1 vaga | Exatamente um `201` e N−1 respostas `409`. A vaga nunca fica negativa |
| CT32 | Duplicidade simultânea: o mesmo usuário envia 2 requisições em paralelo | Um `201` e um `409`. Só um registro no banco |
| CT33 | Idempotência: duas requisições com o mesmo `Idempotency-Key` (se houver suporte) | A mesma resposta `201` nas duas; um único registro |
| CT34 | Falha no meio da transação: o banco ou a fila falha depois da reserva da vaga | `5xx` e rollback; as vagas não são consumidas |

## 6. Resposta e contrato

| ID | Cenário | Esperado |
|---|---|---|
| CT35 | Schema da resposta | O corpo de `201` e o de erro seguem o schema OpenAPI |
| CT36 | Formato de erro padronizado | Todo `4xx` tem `{codigo, mensagem, detalhes?}` |
| CT37 | Sem vazamento de dados | A resposta não traz dados internos nem stack trace |

## Exemplo de implementação (pytest + httpx)

```python
import asyncio
import pytest
import httpx

BASE = "http://localhost:8000"


@pytest.fixture
def payload():
    return {"nome": "Maria Silva", "email": "maria@example.com", "categoria": "inteira"}


def test_ct01_inscricao_valida(client, evento_factory, token, payload, db):
    evento = evento_factory(vagas=10)
    r = client.post(f"/eventos/{evento.id}/inscricoes", json=payload,
                    headers={"Authorization": f"Bearer {token}"})

    assert r.status_code == 201
    body = r.json()
    assert body["evento_id"] == evento.id
    assert body["status"] == "confirmada"
    assert r.headers["Location"].endswith(f"/inscricoes/{body['id']}")
    assert db.inscricoes.count(evento_id=evento.id) == 1


@pytest.mark.parametrize("campo,valor", [
    ("email", "abc"),
    ("nome", "   "),
    ("nome", "x" * 256),
    ("categoria", "vip"),
])
def test_ct08_12_validacao(client, evento_factory, token, payload, campo, valor):
    evento = evento_factory()
    payload[campo] = valor
    r = client.post(f"/eventos/{evento.id}/inscricoes", json=payload,
                    headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 422


def test_ct17_sem_token(client, evento_factory, payload):
    evento = evento_factory()
    r = client.post(f"/eventos/{evento.id}/inscricoes", json=payload)
    assert r.status_code == 401


def test_ct23_evento_lotado(client, evento_factory, token, payload, db):
    evento = evento_factory(vagas=0)
    r = client.post(f"/eventos/{evento.id}/inscricoes", json=payload,
                    headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 409
    assert r.json()["codigo"] == "EVENTO_LOTADO"
    assert db.inscricoes.count(evento_id=evento.id) == 0


def test_ct27_duplicada(client, evento_factory, token, payload):
    evento = evento_factory(vagas=10)
    url = f"/eventos/{evento.id}/inscricoes"
    h = {"Authorization": f"Bearer {token}"}
    assert client.post(url, json=payload, headers=h).status_code == 201
    r = client.post(url, json=payload, headers=h)
    assert r.status_code == 409
    assert r.json()["codigo"] == "INSCRICAO_DUPLICADA"


@pytest.mark.asyncio
async def test_ct31_corrida_ultima_vaga(evento_factory, tokens_factory, db):
    evento = evento_factory(vagas=1)
    tokens = tokens_factory(20)  # 20 usuários distintos

    async with httpx.AsyncClient(base_url=BASE) as ac:
        respostas = await asyncio.gather(*[
            ac.post(f"/eventos/{evento.id}/inscricoes",
                    json={"nome": f"U{i}", "email": f"u{i}@ex.com"},
                    headers={"Authorization": f"Bearer {t}"})
            for i, t in enumerate(tokens)
        ])

    codigos = [r.status_code for r in respostas]
    assert codigos.count(201) == 1
    assert codigos.count(409) == 19
    assert db.eventos.get(evento.id).vagas_disponiveis == 0
```

## Recomendações de ambiente

- **Banco real e isolado:** use Testcontainers com Postgres e rollback ou truncate entre os testes. Não use SQLite em memória, porque os testes de concorrência (CT31 e CT32) dependem dos locks do banco real.
- **Relógio controlável:** use `freezegun` ou `time-machine` nos casos CT24 a CT26.
- **Mocks só nas bordas externas:** e-mail, fila e gateway de pagamento. Banco e serviço continuam reais.
- **Factories:** crie eventos e usuários com `factory_boy` ou fixtures próprias, para cada teste montar o próprio estado.

Me diga qual é o seu framework (FastAPI, Spring, Express, etc.) e o contrato real do endpoint. Com isso eu adapto os códigos de status e as fixtures.
