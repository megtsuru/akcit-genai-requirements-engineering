# Casos de teste de falha de integração: `POST /eventos/{evento_id}/inscricoes`

## Dados fictícios usados nos casos

Datas em 10/11/2026. Os IDs abaixo são inventados.

| Evento | Tipo | Vagas | Horário | Observação |
|---|---|---|---|---|
| `EVT-100` | gratuito | 2 | 09:00–11:00 | base |
| `EVT-200` | pago | 2 | 10:00–12:00 | sobrepõe parcialmente o `EVT-100` |
| `EVT-210` | gratuito | 5 | 09:30–10:30 | fica dentro do `EVT-100` |
| `EVT-220` | gratuito | 5 | 09:00–11:00 | mesmo horário do `EVT-100` |
| `EVT-300` | gratuito | 5 | 11:00–13:00 | encosta no fim do `EVT-100` |
| `EVT-400` | gratuito | 1 | 14:00–15:00 | sem sobreposição |
| `EVT-500` | pago | 1 | 16:00–17:00 | sem sobreposição |
| `EVT-999` | não existe | – | – | – |

Participantes: `part-001`, `part-002`, `part-003`.

**Abreviações:**
- **Repo inalterado**: o repositório tem a mesma quantidade de inscrições e o mesmo conteúdo de antes da requisição.
- **Notif = N**: o dublê do notificador registrou N chamadas nesta requisição.

Salvo quando o caso diz outra coisa, o notificador funciona e o repositório começa sem inscrições.

---

## 1. Entrada inválida (cliente → API)

Requisição para `POST /eventos/EVT-100/inscricoes`. O `EVT-100` existe, então a entrada é o único motivo de falha.

| ID | Tipo | Cenário | Como provocar a falha | Status esperado | O que verificar no repositório e no notificador |
|---|---|---|---|---|---|
| E01 | Entrada inválida | Campo obrigatório ausente | Corpo `{}` | `422` | Repo inalterado; Notif = 0 |
| E02 | Entrada inválida | Nome do campo errado (equivale a campo ausente) | `{"participanteId": "part-001"}` | `422` | Repo inalterado; Notif = 0 |
| E03 | Entrada inválida | Valor vazio | `{"participante_id": ""}` | `422` | Repo inalterado, sem inscrição com id vazio; Notif = 0 |
| E04 | Entrada inválida | Valor nulo | `{"participante_id": null}` | `422` | Repo inalterado; Notif = 0 |
| E05 | Entrada inválida | Tipo numérico em vez de texto | `{"participante_id": 123}` | `422` | Repo inalterado, sem inscrição `"123"`; Notif = 0 |
| E06 | Entrada inválida | Tipo booleano | `{"participante_id": true}` | `422` | Repo inalterado; Notif = 0 |
| E07 | Entrada inválida | Tipo objeto | `{"participante_id": {"id": "part-001"}}` | `422` | Repo inalterado; Notif = 0 |
| E08 | Entrada inválida | Tipo lista | `{"participante_id": ["part-001"]}` | `422` | Repo inalterado; Notif = 0 |
| E09 | Entrada inválida | Requisição sem corpo | POST sem body | `422` | Repo inalterado; Notif = 0 |
| E10 | Entrada inválida | JSON malformado | `{"participante_id": "part-001"` (falta o `}`) | `422` | Repo inalterado; Notif = 0 |
| E11 | Entrada inválida | Corpo é lista, não objeto | `[{"participante_id": "part-001"}]` | `422` | Repo inalterado; Notif = 0 |
| E12 | Entrada inválida | Corpo é string JSON | `"part-001"` | `422` | Repo inalterado; Notif = 0 |
| E13 | Entrada no limite (válida) | Menor valor não vazio | `{"participante_id": "a"}` | `201`, `status: "confirmada"`, `comprovante_enviado: true` | Exatamente 1 inscrição (`EVT-100`, `"a"`, `confirmada`); Notif = 1. Garante que a validação não recusa um valor válido |

Os casos E05 a E08 esperam `422` porque o contrato define `participante_id` como texto.

## 2. Recurso inexistente ou estado inconsistente (API → repositório / regra de negócio)

| ID | Tipo | Cenário | Como provocar a falha | Status esperado | O que verificar no repositório e no notificador |
|---|---|---|---|---|---|
| R01 | Recurso inexistente | Evento não cadastrado | POST em `EVT-999` com `part-001` | `404`, com `detail` | Nenhuma inscrição para `EVT-999`; Repo inalterado; Notif = 0 |
| R02 | Estado conflitante | Já inscrito com `confirmada` | Repo: `part-001` em `EVT-100` (`confirmada`). POST `EVT-100` / `part-001` | `409`, com `detail` | Continua 1 inscrição, ainda `confirmada`; Notif = 0 |
| R03 | Estado conflitante | Já inscrito com `pendente_pagamento` | Repo: `part-001` em `EVT-200` (`pendente_pagamento`). POST `EVT-200` / `part-001` | `409` | Continua 1 inscrição, ainda `pendente_pagamento`; Notif = 0 |
| R04 | Estado conflitante | Já inscrito com `lista_espera` | Repo: `EVT-400` com `part-002` `confirmada` e `part-001` `lista_espera`. POST `EVT-400` / `part-001` | `409` | Inscrição de `part-001` continua `lista_espera`; Notif = 0 |
| R05 | Estado conflitante | Já inscrito em `lista_espera` e agora há vaga (a duplicidade vem antes da vaga) | Repo: `part-001` em `EVT-400` com `lista_espera`, sem nenhuma `confirmada`/`pendente`. POST `EVT-400` / `part-001` | `409` | `part-001` não é promovido nem regravado; Notif = 0 |
| R06 | Conflito de horário | Sobreposição parcial | Repo: `part-001` `confirmada` em `EVT-100`. POST `EVT-200` / `part-001` | `409` | Nenhuma inscrição de `part-001` em `EVT-200`; a do `EVT-100` fica intacta; Notif = 0 |
| R07 | Conflito de horário | Um evento contido no outro | Repo: `part-001` `confirmada` em `EVT-100`. POST `EVT-210` / `part-001` | `409` | Nada gravado em `EVT-210`; Notif = 0 |
| R08 | Conflito de horário | Horários idênticos | Repo: `part-001` `confirmada` em `EVT-100`. POST `EVT-220` / `part-001` | `409` | Nada gravado em `EVT-220`; Notif = 0 |
| R09 | Conflito de horário | Sobreposição no sentido inverso | Repo: `part-001` `confirmada` em `EVT-200`. POST `EVT-100` / `part-001` | `409` | Nada gravado em `EVT-100`; Notif = 0 |
| R10 | Estado conflitante | Duplicidade e conflito ao mesmo tempo | Repo: `part-001` `confirmada` em `EVT-100` e em `EVT-210` (estado inconsistente de propósito). POST `EVT-100` / `part-001` | `409` | Repo inalterado; Notif = 0. Só o status é verificado (ver Dúvida D11) |
| R11 | Estado inconsistente | Inscrição duplicada já gravada | Repo: 2 registros de `part-001` em `EVT-100`. POST `EVT-100` / `part-001` | `409` | Continuam exatamente 2 registros, sem um terceiro; Notif = 0 |
| R12 | Estado inconsistente | Mais vagas ocupadas do que o total | Repo: `EVT-100` (2 vagas) com 3 `confirmada` de outros participantes. POST `EVT-100` / `part-003` | `201`, `lista_espera` | Nova inscrição `lista_espera`; as 3 existentes intactas; Notif = 1 |
| R13 | Limite da regra | Eventos que só se encostam não conflitam | Repo: `part-001` `confirmada` em `EVT-100` (até 11:00). POST `EVT-300` (de 11:00) / `part-001` | `201`, `confirmada` | 1 nova inscrição em `EVT-300`; Notif = 1 |
| R14 | Limite da regra | Sobreposição com `pendente_pagamento` não conflita | Repo: `part-001` `pendente_pagamento` em `EVT-200`. POST `EVT-100` / `part-001` | `201`, `confirmada` | 1 nova inscrição em `EVT-100`; a do `EVT-200` intacta; Notif = 1 |
| R15 | Limite da regra | Sobreposição com `lista_espera` não conflita | Repo: `EVT-210` com vagas ocupadas e `part-001` em `lista_espera`. POST `EVT-100` / `part-001` | `201`, `confirmada` | 1 nova inscrição; Notif = 1 |
| R16 | Limite da regra | A consulta de conflito filtra pelo participante | Repo: `part-002` `confirmada` em `EVT-100`. POST `EVT-200` / `part-001` | `201`, `pendente_pagamento` | 1 nova inscrição de `part-001`; Notif = 1 |
| R17 | Limite de vagas | Última vaga ocupada por `confirmada` | Repo: `part-002` `confirmada` em `EVT-400` (1 vaga). POST `EVT-400` / `part-001` | `201`, `lista_espera` | Nova inscrição `lista_espera`; Notif = 1 |
| R18 | Limite de vagas | Última vaga ocupada por `pendente_pagamento` | Repo: `part-002` `pendente_pagamento` em `EVT-500` (1 vaga). POST `EVT-500` / `part-001` | `201`, `lista_espera` | Nova inscrição `lista_espera` (não `pendente_pagamento`); Notif = 1 |
| R19 | Limite de vagas | `lista_espera` não ocupa vaga | Repo: `part-002` `lista_espera` em `EVT-400`, sem nenhuma `confirmada`/`pendente`. POST `EVT-400` / `part-001` | `201`, `confirmada` | Nova inscrição `confirmada`; Notif = 1 |
| R20 | Limite de vagas | Evento pago e lotado (a falta de vaga vem antes do pagamento) | Repo: `part-002` `confirmada` em `EVT-500`. POST `EVT-500` / `part-001` | `201`, `lista_espera` | Nova inscrição `lista_espera`; Notif = 1 |
| R21 | Limite de vagas | Evento pago com exatamente 1 vaga restante | Repo: `part-002` `pendente_pagamento` em `EVT-200` (2 vagas). POST `EVT-200` / `part-001` | `201`, `pendente_pagamento` | Nova inscrição `pendente_pagamento`; Notif = 1 |

## 3. Falha de componente dependente (API → notificador)

O dublê do notificador é configurado para lançar uma exceção.

| ID | Tipo | Cenário | Como provocar a falha | Status esperado | O que verificar no repositório e no notificador |
|---|---|---|---|---|---|
| N01 | Notificador indisponível | Falha numa inscrição `confirmada` | Notificador lança exceção. POST `EVT-100` / `part-001` | `201`, `confirmada`, `comprovante_enviado: false` | Inscrição gravada como `confirmada`, sem rollback; o notificador foi acionado para essa inscrição; a exceção não vira `5xx` |
| N02 | Notificador indisponível | Falha numa inscrição `pendente_pagamento` | Exceção. POST `EVT-200` / `part-001` | `201`, `pendente_pagamento`, `false` | Inscrição gravada como `pendente_pagamento` |
| N03 | Notificador indisponível | Falha numa inscrição `lista_espera` | Repo: `part-002` `confirmada` em `EVT-400`. Exceção. POST `EVT-400` / `part-001` | `201`, `lista_espera`, `false` | Inscrição gravada como `lista_espera` |
| N04 | Notificador com erro | Exceção de tipo genérico, sem relação com rede | O dublê lança `RuntimeError` ou `ValueError` em vez de um erro de conexão | `201`, `comprovante_enviado: false` | Inscrição gravada. Confirma que a API trata qualquer exceção, e não só um tipo |
| N05 | Notificador com erro | A inscrição gravada após a falha ocupa vaga | Exceção em POST `EVT-400` / `part-001`. Depois, com o notificador normal, POST `EVT-400` / `part-002` | 1º: `201`, `confirmada`, `false`. 2º: `201`, `lista_espera`, `true` | 2 inscrições; a de `part-001` conta como vaga ocupada |
| N06 | Notificador com erro | Nova tentativa após a falha bate na duplicidade | Depois de N01, repetir POST `EVT-100` / `part-001` com o notificador normal | `409` | Continua 1 inscrição; Notif = 0 nesta requisição |
| N07 | Contraprova | `comprovante_enviado` reflete o resultado real | Notificador normal. POST `EVT-100` / `part-001` | `201`, `comprovante_enviado: true` | Garante que o campo não é sempre `false` ou sempre `true` |

## 4. Efeitos colaterais indevidos

| ID | Tipo | Cenário | Como provocar a falha | Status esperado | O que verificar no repositório e no notificador |
|---|---|---|---|---|---|
| C01 | Gravação indevida | Nada é gravado no `404` | POST `EVT-999` / `part-001` com o repo já populado | `404` | Repo inalterado, inclusive sem evento ou inscrição criados como efeito; Notif = 0 |
| C02 | Gravação indevida | Nada é gravado no `422` mesmo com evento válido | Corpo `{"participante_id": ""}` em `EVT-100` | `422` | Repo inalterado; Notif = 0 |
| C03 | Sobrescrita indevida | `409` de duplicidade não altera o registro existente | Repo: `part-001` `pendente_pagamento` em `EVT-200`. POST igual | `409` | Status e demais dados do registro iguais aos de antes; Notif = 0 |
| C04 | Gravação indevida | `409` de conflito não grava no evento-alvo nem altera o outro evento | Cenário do R06 | `409` | `EVT-200` sem inscrição de `part-001`; `EVT-100` intacto; Notif = 0 |
| C05 | Gravação indevida | O conflito tem precedência sobre a falta de vaga | Repo: `part-001` `confirmada` em `EVT-100`; `EVT-200` lotado por `part-002` e `part-003`. POST `EVT-200` / `part-001` | `409` | Nenhuma inscrição `lista_espera` de `part-001` em `EVT-200`; Notif = 0 |
| C06 | Envio duplicado | `201` grava 1 registro e envia 1 comprovante | POST `EVT-100` / `part-001` | `201`, `confirmada`, `true` | Exatamente 1 registro novo, com `evento_id`, `participante_id` e `status` iguais aos da resposta; Notif = 1 (nem 0, nem 2) |
| C07 | Envio ausente | `lista_espera` também envia comprovante | Cenário do R17 | `201`, `lista_espera` | Notif = 1 |
| C08 | Envio ausente | `pendente_pagamento` também envia comprovante | POST `EVT-200` / `part-001` | `201`, `pendente_pagamento` | Notif = 1 |
| C09 | Alteração indevida | `201` não altera outras inscrições | Repo com inscrições de `part-002` e `part-003` em `EVT-100`. POST `EVT-100` / `part-001` | `201` | Registros de `part-002` e `part-003` idênticos aos de antes |
| C10 | Envio duplicado | Duas requisições sequenciais iguais | POST `EVT-100` / `part-001` duas vezes, uma depois da outra | 1º `201`, 2º `409` | Total de 1 registro; Notif total = 1 |
| C11 | Gravação duplicada | A falha do notificador não gera registro duplicado | Cenário do N01 | `201`, `false` | Exatamente 1 registro, sem duplicata e sem rollback |
| C12 | Envio indevido | A sequência `422` → `404` → `409` não acumula envios | Executar E01, R01 e R02 em sequência no mesmo dublê | `422`, `404`, `409` | Notif total = 0; só o estado preparado pelo R02 continua no repo |

---

## Dúvidas (o contrato não define o resultado)

| # | Caso | Por que importa |
|---|---|---|
| D01 | `participante_id` só com espaços (`"   "`) | O contrato diz "não vazio" mas não diz se espaços contam como vazio. Se a API aceitar, grava um participante "em branco" e envia comprovante para ele |
| D02 | Campos extras no corpo (`{"participante_id": "part-001", "status": "confirmada"}`) | Ignorar, recusar com `422` ou usar o campo são três resultados diferentes. Se a API usar um `status` vindo do cliente, a regra de negócio pode ser burlada |
| D03 | Tamanho máximo e caracteres de `participante_id` (10 mil caracteres, Unicode, caracteres de controle) | Não há limite definido. Valores enormes ou estranhos podem falhar no repositório ou no notificador, num ponto em que o comportamento também não está definido (ver D07) |
| D04 | `Content-Type` ausente ou diferente de `application/json` | Pode resultar em `415`, `422` ou aceite. O contrato só cobre "corpo inválido" |
| D05 | `evento_id` em formato inesperado (vazio, caracteres especiais, diferença de maiúsculas/minúsculas como `evt-100` e `EVT-100`) | O formato do id não está definido. Não dá para saber se o resultado é `404`, `422` ou se o id seria considerado o mesmo evento |
| D06 | Corpo inválido em evento inexistente (`EVT-999` + `{}`) | A precedência entre `422` e `404` não está definida. Os dois resultados respeitam "nada é gravado", mas o status muda |
| D07 | Repositório falha (exceção na leitura do evento, na consulta de inscrições ou na gravação) | O contrato só define a falha do notificador. Ficam em aberto o status, se pode haver gravação parcial e se o comprovante é enviado quando a gravação falha |
| D08 | Regra de negócio lança exceção inesperada | Mesmo motivo do D07. Também não se sabe se algo é gravado ou enviado antes do erro |
| D09 | Notificador retorna sem lançar exceção, mas com valor de falha (ex.: `False`) | A premissa diz que a falha é sinalizada por exceção, mas não diz se um retorno "negativo" conta como sucesso. Isso decide o valor de `comprovante_enviado` |
| D10 | Inscrição `confirmada` que aponta para um evento que não existe mais no repositório | A API não tem os horários desse evento para checar conflito. Pode ignorar a inscrição, devolver `409` ou falhar. É um estado inconsistente sem regra |
| D11 | Texto do `detail` nos dois tipos de `409` | O contrato não define as mensagens. Sem isso não dá para verificar qual regra disparou (no R10, por exemplo), só o status |
| D12 | Conteúdo e destinatário do comprovante | Só dá para verificar que o notificador foi chamado e quantas vezes. Não dá para verificar que o comprovante tem os dados certos da inscrição |
| D13 | Inscrição em evento já encerrado ou em andamento | Nenhuma regra trata isso. Não se sabe se a ausência de regra é intencional (resultado `201`) ou se falta uma regra |
| D14 | Existência do participante | O repositório guarda só eventos e inscrições. Não se sabe se qualquer texto não vazio é um participante válido ou se deveria haver um `404` para participante desconhecido |
