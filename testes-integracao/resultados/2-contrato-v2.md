# Casos de teste de integração: `POST /eventos/{evento_id}/inscricoes`

## Convenções

- **Datas:** todos os horários são de **10/11/2026**, salvo indicação.
- **Eventos:** `E1 (grat, 2v, 09:00–10:00)` significa evento gratuito, 2 vagas, das 09:00 às 10:00. `pago` indica evento pago.
- **Inscrições:** `P2@E1=confirmada` significa que o participante P2 tem inscrição `confirmada` no evento E1.
- **Notificador:** `N: ok` envia normalmente. `N: falha` gera erro ao enviar.
- **Requisição:** `E1 · "P1"` significa `POST /eventos/E1/inscricoes` com corpo `{"participante_id": "P1"}`. Outros corpos aparecem por extenso.
- **Corpo 201:** `{E1, P1, confirmada, true}` significa `{"evento_id": "E1", "participante_id": "P1", "status": "confirmada", "comprovante_enviado": true}`.
- **Corpo de erro:** `{"detail": …}` significa objeto com o campo `detail`. O texto da mensagem não é definido pelo contrato e não deve ser verificado.
- **"Nada gravado":** o repositório fica idêntico ao estado inicial e o notificador não é acionado (0 comprovantes).

## A. Funcionamento normal e tipo do evento

| ID | Cenário | Estado inicial | Requisição | Status | Corpo esperado | Efeitos esperados | Regra |
|---|---|---|---|---|---|---|---|
| CT-01 | Evento gratuito com vaga | E1 (grat, 2v, 09:00–10:00); sem inscrições; N: ok | E1 · "P1" | 201 | `{E1, P1, confirmada, true}` | Grava P1@E1=confirmada; 1 comprovante | R2, R3 |
| CT-02 | Evento pago com vaga | E2 (pago, 2v, 09:00–10:00); sem inscrições; N: ok | E2 · "P1" | 201 | `{E2, P1, pendente_pagamento, true}` | Grava P1@E2=pendente_pagamento; 1 comprovante | R2, R3 |
| CT-03 | `participante_id` com 1 caractere (limite mínimo válido) | E1 (grat, 2v, 09:00–10:00); sem inscrições; N: ok | E1 · `{"participante_id": "x"}` | 201 | `{E1, x, confirmada, true}` | Grava x@E1=confirmada; 1 comprovante | Validação do corpo |
| CT-04 | `participante_id` com espaços, acentos e símbolos | E1 (grat, 2v, 09:00–10:00); sem inscrições; N: ok | E1 · `{"participante_id": "Ana Ñ-01"}` | 201 | `{E1, Ana Ñ-01, confirmada, true}` | Grava a inscrição com o texto exato; 1 comprovante | Premissa: qualquer texto não vazio |

## B. Vagas (R2)

| ID | Cenário | Estado inicial | Requisição | Status | Corpo esperado | Efeitos esperados | Regra |
|---|---|---|---|---|---|---|---|
| CT-05 | Última vaga, evento gratuito | E1 (grat, 2v, 09:00–10:00); P2@E1=confirmada; N: ok | E1 · "P1" | 201 | `{E1, P1, confirmada, true}` | Grava P1@E1=confirmada (E1 fica com 2 ocupadas); 1 comprovante | R2 (limite) |
| CT-06 | Última vaga, evento pago, com pendente ocupando vaga | E2 (pago, 2v, 09:00–10:00); P2@E2=pendente_pagamento; N: ok | E2 · "P1" | 201 | `{E2, P1, pendente_pagamento, true}` | Grava P1@E2=pendente_pagamento; 1 comprovante | R2 (limite), R3 |
| CT-07 | Gratuito lotado por confirmadas | E1 (grat, 2v, 09:00–10:00); P2@E1=confirmada, P3@E1=confirmada; N: ok | E1 · "P1" | 201 | `{E1, P1, lista_espera, true}` | Grava P1@E1=lista_espera; 1 comprovante | R2 |
| CT-08 | Pago lotado: lista de espera tem precedência sobre o tipo | E2 (pago, 1v, 09:00–10:00); P2@E2=pendente_pagamento; N: ok | E2 · "P1" | 201 | `{E2, P1, lista_espera, true}` | Grava P1@E2=lista_espera; 1 comprovante | R2 antes de R3 |
| CT-09 | Lotado por confirmada + pendente | E2 (pago, 2v, 09:00–10:00); P2@E2=confirmada, P3@E2=pendente_pagamento; N: ok | E2 · "P1" | 201 | `{E2, P1, lista_espera, true}` | Grava P1@E2=lista_espera; 1 comprovante | R2 (pendente ocupa vaga) |
| CT-10 | `lista_espera` não ocupa vaga | E1 (grat, 2v, 09:00–10:00); P2@E1=confirmada, P3@E1=lista_espera, P4@E1=lista_espera; N: ok | E1 · "P1" | 201 | `{E1, P1, confirmada, true}` | Grava P1@E1=confirmada; 1 comprovante | R2 |
| CT-11 | Lotado com fila já existente | E1 (grat, 1v, 09:00–10:00); P2@E1=confirmada, P3@E1=lista_espera; N: ok | E1 · "P1" | 201 | `{E1, P1, lista_espera, true}` | Grava P1@E1=lista_espera (P3 inalterado); 1 comprovante | R2 |
| CT-12 | Vagas contam só inscrições do próprio evento | E1 (grat, 1v, 09:00–10:00), sem inscrições; E3 (grat, 1v, 14:00–15:00); P2@E3=confirmada; N: ok | E1 · "P1" | 201 | `{E1, P1, confirmada, true}` | Grava P1@E1=confirmada; 1 comprovante | R2 |

## C. Já inscrito (R0)

| ID | Cenário | Estado inicial | Requisição | Status | Corpo esperado | Efeitos esperados | Regra |
|---|---|---|---|---|---|---|---|
| CT-13 | Já inscrito como `confirmada` | E1 (grat, 2v, 09:00–10:00); P1@E1=confirmada; N: ok | E1 · "P1" | 409 | `{"detail": …}` | Nada gravado (continua 1 inscrição de P1 em E1); 0 comprovantes | R0 |
| CT-14 | Já inscrito como `pendente_pagamento` | E2 (pago, 2v, 09:00–10:00); P1@E2=pendente_pagamento; N: ok | E2 · "P1" | 409 | `{"detail": …}` | Nada gravado; 0 comprovantes | R0 |
| CT-15 | Já inscrito como `lista_espera`, evento com vaga | E1 (grat, 2v, 09:00–10:00); P1@E1=lista_espera; N: ok | E1 · "P1" | 409 | `{"detail": …}` | Nada gravado; 0 comprovantes | R0 |
| CT-16 | R0 antes de R2: já está na fila e o evento está lotado | E1 (grat, 1v, 09:00–10:00); P2@E1=confirmada, P1@E1=lista_espera; N: ok | E1 · "P1" | 409 (não 201 lista_espera) | `{"detail": …}` | Nada gravado; 0 comprovantes | R0 antes de R2 |
| CT-17 | Já inscrito e também com conflito de horário | E2 (pago, 2v, 09:00–10:00); EA (grat, 2v, 09:30–10:30); P1@E2=pendente_pagamento, P1@EA=confirmada; N: ok | E2 · "P1" | 409 | `{"detail": …}` | Nada gravado; 0 comprovantes | R0 (precedência sobre R1; ver Dúvida 8) |
| CT-18 | Outro participante inscrito não bloqueia | E1 (grat, 2v, 09:00–10:00); P2@E1=confirmada; N: ok | E1 · "P1" | 201 | `{E1, P1, confirmada, true}` | Grava P1@E1=confirmada; 1 comprovante | R0 (por participante) |

## D. Conflito de horário (R1)

Em todos os casos desta seção, o evento-alvo (EB) é gratuito e tem vaga, salvo indicação.

| ID | Cenário | Estado inicial | Requisição | Status | Corpo esperado | Efeitos esperados | Regra |
|---|---|---|---|---|---|---|---|
| CT-19 | Sobreposição parcial (alvo começa durante o outro) | EA (09:00–11:00); EB (grat, 2v, 10:00–12:00); P1@EA=confirmada; N: ok | EB · "P1" | 409 | `{"detail": …}` | Nada gravado; 0 comprovantes | R1 |
| CT-20 | Sobreposição parcial (alvo termina durante o outro) | EA (10:00–12:00); EB (09:00–11:00); P1@EA=confirmada; N: ok | EB · "P1" | 409 | `{"detail": …}` | Nada gravado; 0 comprovantes | R1 |
| CT-21 | Alvo contido no outro evento | EA (09:00–12:00); EB (10:00–11:00); P1@EA=confirmada; N: ok | EB · "P1" | 409 | `{"detail": …}` | Nada gravado; 0 comprovantes | R1 |
| CT-22 | Alvo contém o outro evento | EA (10:00–11:00); EB (09:00–12:00); P1@EA=confirmada; N: ok | EB · "P1" | 409 | `{"detail": …}` | Nada gravado; 0 comprovantes | R1 |
| CT-23 | Horários idênticos | EA (09:00–10:00); EB (09:00–10:00); P1@EA=confirmada; N: ok | EB · "P1" | 409 | `{"detail": …}` | Nada gravado; 0 comprovantes | R1 |
| CT-24 | Sobreposição mínima (1 minuto) | EA (09:00–10:01); EB (10:00–11:00); P1@EA=confirmada; N: ok | EB · "P1" | 409 | `{"detail": …}` | Nada gravado; 0 comprovantes | R1 (limite) |
| CT-25 | Eventos que só se encostam (outro termina quando o alvo começa) | EA (09:00–10:00); EB (10:00–11:00); P1@EA=confirmada; N: ok | EB · "P1" | 201 | `{EB, P1, confirmada, true}` | Grava P1@EB=confirmada; 1 comprovante | R1 (limite) |
| CT-26 | Eventos que só se encostam (alvo termina quando o outro começa) | EA (09:00–10:00); EB (08:00–09:00); P1@EA=confirmada; N: ok | EB · "P1" | 201 | `{EB, P1, confirmada, true}` | Grava P1@EB=confirmada; 1 comprovante | R1 (limite) |
| CT-27 | Mesmo horário em dias diferentes | EA (10/11 09:00–10:00); EB (11/11 09:00–10:00); P1@EA=confirmada; N: ok | EB · "P1" | 201 | `{EB, P1, confirmada, true}` | Grava P1@EB=confirmada; 1 comprovante | R1 |
| CT-28 | Sobreposição atravessando a meia-noite | EA (10/11 23:00 – 11/11 01:00); EB (11/11 00:00–02:00); P1@EA=confirmada; N: ok | EB · "P1" | 409 | `{"detail": …}` | Nada gravado; 0 comprovantes | R1 |
| CT-29 | `pendente_pagamento` em evento sobreposto não conflita | EA (pago, 09:00–11:00); EB (10:00–12:00); P1@EA=pendente_pagamento; N: ok | EB · "P1" | 201 | `{EB, P1, confirmada, true}` | Grava P1@EB=confirmada; P1@EA inalterada; 1 comprovante | R1 |
| CT-30 | `lista_espera` em evento sobreposto não conflita | EA (09:00–11:00); EB (10:00–12:00); P1@EA=lista_espera; N: ok | EB · "P1" | 201 | `{EB, P1, confirmada, true}` | Grava P1@EB=confirmada; 1 comprovante | R1 |
| CT-31 | Confirmada de outro participante em evento sobreposto não afeta P1 | EA (09:00–11:00); EB (10:00–12:00); P2@EA=confirmada; N: ok | EB · "P1" | 201 | `{EB, P1, confirmada, true}` | Grava P1@EB=confirmada; 1 comprovante | R1 (por participante) |
| CT-32 | Várias inscrições, nenhuma conflitante | EA (pago, 09:00–11:00); EC (14:00–15:00); EB (10:00–12:00); P1@EA=pendente_pagamento, P1@EC=confirmada; N: ok | EB · "P1" | 201 | `{EB, P1, confirmada, true}` | Grava P1@EB=confirmada; 1 comprovante | R1 |
| CT-33 | R1 antes de R2: alvo lotado e com conflito | EA (09:00–11:00); EB (grat, 1v, 10:00–12:00); P2@EB=confirmada; P1@EA=confirmada; N: ok | EB · "P1" | 409 (não 201 lista_espera) | `{"detail": …}` | Nada gravado; 0 comprovantes | R1 antes de R2 |
| CT-34 | Conflito com evento-alvo pago | EA (09:00–11:00); EB (pago, 2v, 10:00–12:00); P1@EA=confirmada; N: ok | EB · "P1" | 409 | `{"detail": …}` | Nada gravado; 0 comprovantes | R1 antes de R3 |

## E. Notificador

| ID | Cenário | Estado inicial | Requisição | Status | Corpo esperado | Efeitos esperados | Regra |
|---|---|---|---|---|---|---|---|
| CT-35 | Falha no envio, evento gratuito | E1 (grat, 2v, 09:00–10:00); sem inscrições; N: falha | E1 · "P1" | 201 | `{E1, P1, confirmada, false}` | Grava P1@E1=confirmada; nenhum comprovante entregue | Efeito: falha do comprovante |
| CT-36 | Falha no envio, evento pago | E2 (pago, 2v, 09:00–10:00); sem inscrições; N: falha | E2 · "P1" | 201 | `{E2, P1, pendente_pagamento, false}` | Grava P1@E2=pendente_pagamento; nenhum comprovante entregue | Efeito: falha do comprovante |
| CT-37 | Falha no envio, inscrição em lista de espera | E1 (grat, 1v, 09:00–10:00); P2@E1=confirmada; N: falha | E1 · "P1" | 201 | `{E1, P1, lista_espera, false}` | Grava P1@E1=lista_espera; nenhum comprovante entregue | Efeito: falha do comprovante, R2 |
| CT-38 | Notificador com falha não altera erro 409 | E1 (grat, 2v, 09:00–10:00); P1@E1=confirmada; N: falha | E1 · "P1" | 409 | `{"detail": …}` | Nada gravado; notificador não acionado | R0 + efeitos de erro |
| CT-39 | Notificador com falha não altera erro 404 | Sem evento E9; N: falha | E9 · "P1" | 404 | `{"detail": …}` | Nada gravado; notificador não acionado | Evento inexistente |

## F. Evento inexistente

| ID | Cenário | Estado inicial | Requisição | Status | Corpo esperado | Efeitos esperados | Regra |
|---|---|---|---|---|---|---|---|
| CT-40 | Evento inexistente com outros eventos cadastrados | E1 (grat, 2v, 09:00–10:00); sem E9; N: ok | E9 · "P1" | 404 | `{"detail": …}` | Nada gravado; 0 comprovantes | Contrato 404 |
| CT-41 | Repositório sem nenhum evento | Repositório vazio; N: ok | E1 · "P1" | 404 | `{"detail": …}` | Nada gravado; 0 comprovantes | Contrato 404 |

## G. Corpo inválido (422)

Em todos os casos desta seção, o estado inicial é E1 (grat, 2v, 09:00–10:00), sem inscrições, N: ok.

| ID | Cenário | Estado inicial | Requisição | Status | Corpo esperado | Efeitos esperados | Regra |
|---|---|---|---|---|---|---|---|
| CT-42 | Campo ausente | ver nota | E1 · `{}` | 422 | Erro de validação | Nada gravado; 0 comprovantes | Campo obrigatório |
| CT-43 | Campo vazio | ver nota | E1 · `{"participante_id": ""}` | 422 | Erro de validação | Nada gravado; 0 comprovantes | Campo não vazio |
| CT-44 | Campo nulo | ver nota | E1 · `{"participante_id": null}` | 422 | Erro de validação | Nada gravado; 0 comprovantes | Campo obrigatório (texto) |
| CT-45 | Requisição sem corpo | ver nota | `POST /eventos/E1/inscricoes` sem corpo | 422 | Erro de validação | Nada gravado; 0 comprovantes | Corpo inválido |
| CT-46 | JSON malformado | ver nota | E1 · `{"participante_id": "P1"` (sem fechar) | 422 | Erro de validação | Nada gravado; 0 comprovantes | Corpo inválido |
| CT-47 | Corpo que não é objeto | ver nota | E1 · `["P1"]` | 422 | Erro de validação | Nada gravado; 0 comprovantes | Corpo inválido |
| CT-48 | Nome do campo errado | ver nota | E1 · `{"participante": "P1"}` | 422 | Erro de validação | Nada gravado; 0 comprovantes | Campo obrigatório |

## H. Sequências (estado produzido pela própria API)

| ID | Cenário | Estado inicial | Requisição | Status | Corpo esperado | Efeitos esperados | Regra |
|---|---|---|---|---|---|---|---|
| CT-49 | Mesma inscrição repetida | E1 (grat, 2v, 09:00–10:00); sem inscrições; N: ok | (1) E1 · "P1"; (2) E1 · "P1" | (1) 201; (2) 409 | (1) `{E1, P1, confirmada, true}`; (2) `{"detail": …}` | Final: 1 inscrição P1@E1=confirmada; total de 1 comprovante | R0 + gravação |
| CT-50 | Preenchimento de vagas | E1 (grat, 1v, 09:00–10:00); sem inscrições; N: ok | (1) "P1"; (2) "P2"; (3) "P3" em E1 | 201, 201, 201 | `confirmada`, `lista_espera`, `lista_espera` (todos `true`) | Final: P1=confirmada, P2=lista_espera, P3=lista_espera; 3 comprovantes | R2 + gravação |
| CT-51 | Confirmada criada pela API gera conflito depois | EA (grat, 2v, 09:00–11:00); EB (grat, 2v, 10:00–12:00); sem inscrições; N: ok | (1) EA · "P1"; (2) EB · "P1" | (1) 201; (2) 409 | (1) `{EA, P1, confirmada, true}`; (2) `{"detail": …}` | Final: só P1@EA=confirmada; 1 comprovante | R1 + gravação |
| CT-52 | Pendente criada pela API não gera conflito | EA (pago, 2v, 09:00–11:00); EB (grat, 2v, 10:00–12:00); sem inscrições; N: ok | (1) EA · "P1"; (2) EB · "P1" | 201, 201 | (1) `{EA, P1, pendente_pagamento, true}`; (2) `{EB, P1, confirmada, true}` | Final: 2 inscrições; 2 comprovantes | R1, R3 |
| CT-53 | Lista de espera criada pela API não gera conflito | EA (grat, 1v, 09:00–11:00); P2@EA=confirmada; EB (grat, 2v, 10:00–12:00); N: ok | (1) EA · "P1"; (2) EB · "P1" | 201, 201 | (1) `{EA, P1, lista_espera, true}`; (2) `{EB, P1, confirmada, true}` | Final: P1@EA=lista_espera, P1@EB=confirmada; 2 comprovantes | R1, R2 |
| CT-54 | Falha no envio e nova tentativa: confirma que a inscrição foi gravada | E1 (grat, 2v, 09:00–10:00); sem inscrições; N: falha na 1ª chamada, ok depois | (1) E1 · "P1"; (2) E1 · "P1" | (1) 201; (2) 409 | (1) `{E1, P1, confirmada, false}`; (2) `{"detail": …}` | Final: 1 inscrição; 0 comprovantes entregues | Efeito: falha do comprovante + R0 |

## Dúvidas

Estes casos não têm resultado esperado porque o contrato e as regras não os definem.

1. **Precedência entre 422 e 404/409.** Não está definido o resultado de um corpo inválido enviado para um evento inexistente (ex.: `E9 · {}`), nem de um corpo inválido de um participante já inscrito.
2. **`participante_id` só com espaços** (`"   "`). Não está definido se isso conta como "não vazio". Também não está definido se o texto sofre *trim* antes da gravação (`" P1 "` vs `"P1"`).
3. **Tipos não-texto em `participante_id`** (`123`, `true`, `{}`). O contrato diz `<texto>`, mas não está definido se há conversão automática ou se o resultado é 422.
4. **Campos extras no corpo** (ex.: `{"participante_id": "P1", "x": 1}`): ignorados ou 422?
5. **Maiúsculas/minúsculas.** Não está definido se `"P1"` e `"p1"` são o mesmo participante para R0 e R1. O mesmo vale para `evento_id` (`E1` vs `e1`).
6. **Tamanho máximo de `participante_id`.** Não há limite definido.
7. **Formato de `evento_id`.** Não está definido se um formato malformado ou de tipo inesperado resulta em 404 ou 422.
8. **Conteúdo de `detail`.** Não está definido se a mensagem diferencia "conflito de horário" de "já inscrito". Sem isso, a precedência R0 > R1 (CT-17) só pode ser verificada pelo status, que é 409 nos dois casos.
9. **Falha do notificador.** Não estão definidos:
   - quantas tentativas de envio são feitas (há *retry*?);
   - se timeout conta como falha;
   - se `comprovante_enviado: false` fica registrado no repositório.
10. **Conteúdo e destinatário do comprovante.** Não estão definidos, inclusive para inscrições em `lista_espera`. Os casos acima verificam apenas a quantidade enviada.
11. **Falha do repositório** (erro ao ler ou gravar). O status e os efeitos esperados não estão definidos.
12. **Eventos passados ou já iniciados.** Nenhuma regra proíbe a inscrição, mas não está confirmado que deva ser aceita. Também não está definido se uma confirmada em evento passado conta para conflito.
13. **Fuso horário e formato dos horários.** Não está definido como comparar eventos cadastrados com fusos diferentes, nem qual é a granularidade dos horários (minutos, segundos). Isso afeta CT-24.
14. **Content-Type.** Não está definido o comportamento quando o cabeçalho é ausente ou diferente de `application/json` com corpo válido.
