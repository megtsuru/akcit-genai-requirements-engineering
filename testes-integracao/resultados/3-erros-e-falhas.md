# Casos de teste de falha de integração: `POST /eventos/{evento_id}/inscricoes`

**Dados fictícios usados nos casos:**
- Eventos: `EVT-001` existe, das 14h às 16h. `EVT-002` existe, das 15h às 17h, e o horário se sobrepõe ao de `EVT-001`. `EVT-003` existe, das 18h às 19h, sem sobreposição. `EVT-999` não existe.
- Participantes: `PART-ana-01` e `PART-bruno-02`.
- O repositório e o notificador são dublês controláveis (stub/spy), para poder contar gravações e envios e injetar falhas.

**Legenda da coluna "O que verificar":**
- **R0**: nenhuma inscrição nova no repositório, que fica igual ao estado anterior.
- **N0**: nenhuma chamada ao notificador.
- **R1**: exatamente uma inscrição nova, com o `evento_id` e o `participante_id` da requisição.
- **N1**: exatamente uma chamada ao notificador.

---

## 1. Entrada inválida (cliente → API)

| ID | Tipo | Cenário | Como provocar a falha | Status esperado | O que verificar no repositório e no notificador |
|----|------|---------|-----------------------|-----------------|---------------------------|
| EI-01 | Campo ausente | Corpo sem `participante_id` | `POST /eventos/EVT-001/inscricoes` com `{}` | `422` | R0, N0 |
| EI-02 | Valor no limite | `participante_id` vazio | `{"participante_id": ""}` | `422` | R0, N0 |
| EI-03 | Campo nulo | `participante_id` nulo | `{"participante_id": null}` | `422` | R0, N0 |
| EI-04 | Tipo | `participante_id` numérico | `{"participante_id": 123}` | `422` | R0, N0 |
| EI-05 | Tipo | `participante_id` booleano | `{"participante_id": true}` | `422` | R0, N0 |
| EI-06 | Tipo | `participante_id` como objeto ou lista | `{"participante_id": {"id": "PART-ana-01"}}` e `{"participante_id": ["PART-ana-01"]}` | `422` | R0, N0 |
| EI-07 | Formato | Corpo é uma lista JSON em vez de objeto | `[{"participante_id": "PART-ana-01"}]` | `422` | R0, N0 |
| EI-08 | Formato | JSON malformado | `{"participante_id": "PART-ana-01"` (sem fechar a chave) | `422` | R0, N0 |
| EI-09 | Corpo ausente | Requisição sem corpo | `POST` sem payload | `422` | R0, N0 |
| EI-10 | Campo com nome errado | Chave escrita de outra forma | `{"participanteId": "PART-ana-01"}` ou `{"Participante_id": "PART-ana-01"}` | `422`, porque o campo obrigatório está ausente | R0, N0 |
| EI-11 | Valor no limite | Menor valor válido: um caractere | `{"participante_id": "a"}` em `EVT-003`, sem inscrições prévias | `201` | R1, N1. Serve de controle: o limite inferior válido não pode ser rejeitado. |

## 2. Recurso inexistente ou estado inconsistente (API → repositório e API → regra de negócio)

| ID | Tipo | Cenário | Como provocar a falha | Status esperado | O que verificar no repositório e no notificador |
|----|------|---------|-----------------------|-----------------|---------------------------|
| RI-01 | Recurso inexistente | Evento não existe | `POST /eventos/EVT-999/inscricoes` com `{"participante_id": "PART-ana-01"}` | `404` com `{"detail"}` | R0. Nenhuma inscrição para `EVT-999` foi criada. N0. |
| RI-02 | Recurso inexistente | Repositório vazio, sem nenhum evento | Configurar o repositório sem eventos e chamar `POST /eventos/EVT-001/inscricoes` | `404` com `{"detail"}` | R0, N0 |
| RI-03 | Recurso inexistente | Evento removido entre duas chamadas | Inscrever `PART-ana-01` em `EVT-001` (`201`), remover `EVT-001` do repositório e inscrever `PART-bruno-02` | 2ª chamada: `404` | Na 2ª chamada, nenhuma inscrição nova (R0) e nenhum envio além do da 1ª chamada |
| RI-04 | Duplicidade | Participante já inscrito no mesmo evento | Pré-gravar a inscrição `PART-ana-01` em `EVT-001` e repetir a mesma requisição | `409` com `{"detail"}` | Continua existindo uma única inscrição `PART-ana-01`/`EVT-001`, sem duplicata. N0. |
| RI-05 | Conflito de regra | Conflito de horário com outro evento | Pré-gravar `PART-ana-01` em `EVT-001` e inscrevê-lo em `EVT-002` | `409` com `{"detail"}` | Nenhuma inscrição `PART-ana-01`/`EVT-002` e a de `EVT-001` fica intacta. N0. |
| RI-06 | Controle de conflito | Outro participante no mesmo horário | Pré-gravar `PART-ana-01` em `EVT-001` e inscrever `PART-bruno-02` em `EVT-002` | `201` | R1 só para `PART-bruno-02`, N1. Garante que o conflito é avaliado por participante e não de forma global. |
| RI-07 | Duplicidade + conflito | A mesma requisição viola as duas regras de `409` | Pré-gravar `PART-ana-01` em `EVT-001` e em `EVT-002` (estado inconsistente plantado direto no repositório) e repetir a inscrição em `EVT-002` | `409` | R0. As duas inscrições pré-existentes continuam sem alteração. N0. Ver dúvida D-08 sobre o conteúdo de `detail`. |
| RI-08 | Concorrência | Duas requisições idênticas e simultâneas | Disparar em paralelo 2× `{"participante_id": "PART-ana-01"}` para `EVT-003` | Uma resposta `201` e uma `409` | Exatamente uma inscrição `PART-ana-01`/`EVT-003`. Exatamente um envio. |
| RI-09 | Concorrência | Duas inscrições simultâneas em eventos com horário sobreposto | Disparar em paralelo `PART-ana-01` em `EVT-001` e em `EVT-002`, sem inscrições prévias | Uma resposta `201` e uma `409` | Só uma das duas inscrições existe no repositório. Exatamente um envio. |

## 3. Falha de componente dependente (API → notificador)

| ID | Tipo | Cenário | Como provocar a falha | Status esperado | O que verificar no repositório e no notificador |
|----|------|---------|-----------------------|-----------------|---------------------------|
| FD-01 | Notificador indisponível | O notificador lança erro, como recusa de conexão | Stub do notificador lança exceção. Chamar `POST /eventos/EVT-003/inscricoes` com `PART-ana-01`. | `201` com `"comprovante_enviado": false` | R1: a inscrição continua gravada, sem rollback. Corpo com `evento_id: "EVT-003"` e `participante_id: "PART-ana-01"`. |
| FD-02 | Notificador retorna falha | O notificador retorna erro em vez de lançar exceção | Stub devolve um resultado de falha | `201` com `"comprovante_enviado": false` | R1 |
| FD-03 | Caminho feliz de controle | O notificador funciona | Stub devolve sucesso | `201` com `"comprovante_enviado": true` | R1, N1. Garante que o `false` dos casos anteriores vem da falha e não está fixo no código. |
| FD-04 | Recuperação | Repetir a requisição depois de uma falha do notificador | Executar FD-01 e, com o notificador já funcionando, repetir a mesma requisição | 2ª chamada: `409` (participante já inscrito) | Continua existindo uma única inscrição. A 2ª chamada não faz nenhum envio. Ou seja, repetir não é uma forma de reenviar o comprovante, e isso também é efeito colateral. |
| FD-05 | Isolamento da falha | Uma falha do notificador não contamina a próxima inscrição | Notificador falha na 1ª chamada (`PART-ana-01` em `EVT-003`) e funciona na 2ª (`PART-bruno-02` em `EVT-003`) | 1ª: `201`/`false`. 2ª: `201`/`true`. | Duas inscrições, uma por participante. Na 2ª chamada, um envio. |
| FD-06 | Notificador × erros de entrada | O notificador está quebrado e a entrada é inválida ou o evento não existe | Stub que lança exceção combinado com EI-01, RI-01 e RI-04 | `422`, `404` e `409`, respectivamente, nunca `201` | R0 e N0: nenhuma tentativa de envio em nenhum dos casos |

## 4. Efeitos colaterais indevidos

| ID | Tipo | Cenário | Como provocar a falha | Status esperado | O que verificar no repositório e no notificador |
|----|------|---------|-----------------------|-----------------|---------------------------|
| EC-01 | Gravação indevida | Erro de validação não grava nada | Rodar todos os casos EI-01 a EI-10 comparando um snapshot do repositório antes e depois | `422` | Repositório idêntico ao snapshot. Spy do notificador com 0 chamadas. |
| EC-02 | Gravação indevida | Um `404` não cria inscrição "órfã" | RI-01 | `404` | Nenhum registro com `evento_id = EVT-999`. 0 envios. |
| EC-03 | Gravação indevida | Um `409` não sobrescreve nem altera a inscrição existente | RI-04 e RI-05 comparando o registro pré-existente antes e depois | `409` | O registro pré-existente fica idêntico e a contagem de inscrições não muda. 0 envios. |
| EC-04 | Envio indevido | Um `409` por duplicidade não reenvia comprovante | RI-04 | `409` | Spy do notificador com 0 chamadas na requisição duplicada |
| EC-05 | Envio duplicado | Um `201` envia exatamente um comprovante | Inscrição válida com o notificador funcionando | `201`/`true` | O spy registra exatamente 1 chamada, nem 0 nem 2 |
| EC-06 | Envio duplicado | Um `201` com falha no envio gera no máximo uma tentativa visível | FD-01 com spy contando as chamadas | `201`/`false` | O contrato fala em **um** comprovante para o `201`. Registrar o número de chamadas e ver a dúvida D-05 antes de dar o caso como aprovado. |
| EC-07 | Gravação duplicada | Um `201` grava exatamente uma inscrição | Inscrição válida | `201` | Exatamente 1 registro novo (R1), sem duplicata |
| EC-08 | Rollback indevido | Uma falha do notificador não apaga a inscrição | FD-01 seguido de uma consulta direta ao repositório | `201`/`false` | A inscrição está presente depois da resposta |
| EC-09 | Sequência | Sequência mista sem vazamento de efeitos | Em sequência: EI-02 (`422`), RI-01 (`404`), inscrição válida (`201`), RI-04 (`409`), RI-05 (`409`) | `422`, `404`, `201`, `409`, `409` | Ao final: exatamente 1 inscrição nova e exatamente 1 envio, os dois vindos da chamada `201` |

---

## Dúvidas (o contrato não define o resultado)

| ID | Caso | Por que importa |
|----|------|-----------------|
| D-01 | **`participante_id` só com espaços** (`"   "`) ou com espaços nas pontas (`" PART-ana-01 "`) | Não está definido se isso conta como "vazio" nem se a API normaliza os espaços. Sem normalização, `" PART-ana-01 "` e `"PART-ana-01"` podem virar duas inscrições do mesmo participante e escapar da regra de duplicidade e da de conflito. |
| D-02 | **Campos extras** no corpo (`{"participante_id": "PART-ana-01", "status": "confirmada"}`) | Não está definido se o resultado é `422` ou se o campo é ignorado. Se o campo for aceito e repassado ao repositório, o cliente pode injetar valores como `status`. |
| D-03 | **Tamanho máximo** de `participante_id` (ex.: 10.000 caracteres) e caracteres especiais ou Unicode | Não há limite superior no contrato. O repositório pode truncar ou falhar ao gravar, e o notificador pode rejeitar o envio. Não dá para afirmar `201` nem `422`. |
| D-04 | **Participante inexistente** | O contrato só valida o formato de `participante_id`, não se o participante existe. Não se sabe se o resultado é `201`, `404` ou outro. Isso afeta o notificador, que talvez não tenha para quem enviar. |
| D-05 | **Retentativas do notificador** | O contrato não diz se a API tenta enviar de novo quando falha. Se tentar, uma falha "falsa" (o comprovante saiu, mas a resposta foi erro ou timeout) gera comprovantes duplicados e contradiz o "**um** comprovante". |
| D-06 | **Timeout ou lentidão do notificador** | Não há tempo limite definido. Se o notificador demorar muito, não se sabe se a API espera indefinidamente, desiste e responde `false`, ou estoura timeout para o cliente. Também não se sabe o que `comprovante_enviado` deve dizer quando o envio acontece depois que a API já desistiu. |
| D-07 | **Repositório indisponível ou erro ao gravar** | Nenhum status está definido (500? 503?). Também não está definido se o comprovante pode ser enviado quando a gravação falhou, nem a ordem gravar → enviar. Um envio sem gravação deixaria o participante com o comprovante de uma inscrição que não existe. |
| D-08 | **Duplicidade e conflito ao mesmo tempo** (RI-07) | Os dois casos dão `409`, mas o contrato não define qual regra tem precedência nem o texto de `detail`. O cliente não consegue distinguir os dois casos sem saber isso. |
| D-09 | **Precedência entre `404` e `422`** (evento inexistente **e** corpo inválido) | O contrato não define qual erro sai primeiro. Isso decide se a API consulta o repositório antes de validar a entrada. |
| D-10 | **Formato de `evento_id`** (vazio, só espaços, caracteres especiais, maiúsculas e minúsculas) | Não há regra para o path. Não se sabe se o resultado é `404`, `422` ou `405`, nem se `evt-001` equivale a `EVT-001`. |
| D-11 | **Content-Type diferente de JSON** (ex.: `text/plain`) | O contrato só lista `422` para "corpo inválido". O resultado poderia ser `415`. |
| D-12 | **Valor do campo `status` no `201`** | O campo existe, mas os valores possíveis não estão definidos. Não dá para verificar se a inscrição foi gravada com o estado certo, nem se esse valor muda quando o envio falha. |
| D-13 | **Falha inesperada na regra de negócio** (exceção que não é conflito) | Não há status definido. Também não se sabe se algo pode ter sido gravado antes da exceção. |
| D-14 | **Conteúdo do comprovante** | O contrato só diz que **um** comprovante é enviado, sem definir destinatário nem dados. Não dá para afirmar que o envio leva o `evento_id` e o `participante_id` certos, só contar as chamadas. |
| D-15 | **Definição de "conflito de horário"** | Não está definido se eventos que só se encostam (um termina às 16h e o outro começa às 16h) estão em conflito. O caso de limite não pode ter um resultado esperado sem essa regra. |
| D-16 | **Repetição depois de `comprovante_enviado: false`** | FD-04 espera `409` porque o participante já está inscrito, o que segue o contrato. Mas o contrato não oferece nenhuma forma de reenviar o comprovante, então um participante sem comprovante fica sem saída. Vale confirmar se esse comportamento é o desejado. |

**Duas suposições** sustentam alguns resultados esperados e devem ser confirmadas:
- **Tipos não textuais (EI-04 a EI-06):** espero `422` porque o contrato diz que `participante_id` é `"<texto>"`. Alguns frameworks convertem números em texto automaticamente; se for o caso, esses casos passam para as Dúvidas.
- **Requisições simultâneas (RI-08 e RI-09):** o resultado vem de aplicar a regra de duplicidade e a de conflito também quando as requisições chegam juntas. O contrato não fala de concorrência explicitamente.
