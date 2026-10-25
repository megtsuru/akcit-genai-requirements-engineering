# Casos de teste de integração: `POST /eventos/{evento_id}/inscricoes`

## Convenções

- **Participantes fictícios:** P1 = `"part-001"`, P2 = `"part-002"`, P3 = `"part-003"` e assim por diante.
- **Eventos fictícios:** todos são no dia 10/11/2026, salvo indicação. A notação é `Ex (tipo, vagas=N, início–fim)`. **E1 é sempre o evento da requisição.**
- **Inscrições:** a notação é `(evento, participante, status)`.
- **Notificador:** é "OK" (envia normalmente) salvo indicação. "Falha" quer dizer que o envio retorna erro.
- **Efeitos:**
  - "Inscrições" é o estado final do repositório. "Inalterado" quer dizer igual ao estado inicial.
  - "Comprovantes" é a quantidade enviada com sucesso.
  - Nos casos de falha, "tentativas" diz se o notificador foi acionado.
- **Corpo `{"detail"}`:** só verifico se o campo `detail` existe. O contrato não define o texto da mensagem.

## Tabela de casos

| ID | Cenário | Estado inicial (eventos e inscrições no repositório; comportamento do notificador) | Requisição | Status esperado | Corpo esperado | Efeitos esperados (inscrições gravadas, comprovantes enviados) | Regra coberta |
|---|---|---|---|---|---|---|---|
| CT01 | Evento gratuito com vaga | E1 (gratuito, vagas=3, 10:00–12:00); nenhuma inscrição; notificador OK | `POST /eventos/E1/inscricoes` `{"participante_id":"part-001"}` | 201 | `{"evento_id":"E1","participante_id":"part-001","status":"confirmada","comprovante_enviado":true}` | +1 inscrição (E1, P1, confirmada); 1 comprovante | R3 (gratuito), contrato 201 |
| CT02 | Evento pago com vaga | E1 (pago, vagas=3, 10:00–12:00); nenhuma inscrição; notificador OK | E1, `{"participante_id":"part-001"}` | 201 | `{..., "status":"pendente_pagamento","comprovante_enviado":true}` | +1 (E1, P1, pendente_pagamento); 1 comprovante | R3 (pago) |
| CT03 | Limite: última vaga em evento gratuito | E1 (gratuito, vagas=3); (E1,P2,confirmada), (E1,P3,confirmada); notificador OK | E1, P1 | 201 | `status:"confirmada"`, `comprovante_enviado:true` | +1 (E1, P1, confirmada); 1 comprovante | R2 (limite: 2 de 3 ocupadas) |
| CT04 | Limite: evento gratuito lotado | E1 (gratuito, vagas=3); (E1,P2,confirmada), (E1,P3,confirmada), (E1,P4,confirmada); notificador OK | E1, P1 | 201 | `status:"lista_espera"`, `comprovante_enviado:true` | +1 (E1, P1, lista_espera); 1 comprovante | R2 (sem vaga) |
| CT05 | Pendente de pagamento ocupa vaga | E1 (gratuito, vagas=3); (E1,P2,confirmada), (E1,P3,confirmada), (E1,P4,pendente_pagamento); notificador OK | E1, P1 | 201 | `status:"lista_espera"`, `comprovante_enviado:true` | +1 (E1, P1, lista_espera); 1 comprovante | R2 (pendente ocupa vaga) |
| CT06 | Lista de espera não ocupa vaga | E1 (gratuito, vagas=2); (E1,P2,confirmada), (E1,P3,lista_espera), (E1,P4,lista_espera); notificador OK | E1, P1 | 201 | `status:"confirmada"`, `comprovante_enviado:true` | +1 (E1, P1, confirmada); 1 comprovante | R2 (lista_espera não ocupa) |
| CT07 | Evento pago lotado: vaga é avaliada antes do tipo | E1 (pago, vagas=2); (E1,P2,pendente_pagamento), (E1,P3,confirmada); notificador OK | E1, P1 | 201 | `status:"lista_espera"`, `comprovante_enviado:true` | +1 (E1, P1, lista_espera); 1 comprovante | Ordem R2 → R3 |
| CT08 | Limite: última vaga em evento pago | E1 (pago, vagas=2); (E1,P2,pendente_pagamento); notificador OK | E1, P1 | 201 | `status:"pendente_pagamento"`, `comprovante_enviado:true` | +1 (E1, P1, pendente_pagamento); 1 comprovante | R2 + R3 |
| CT09 | Limite: evento com 0 vagas | E1 (gratuito, vagas=0); nenhuma inscrição; notificador OK | E1, P1 | 201 | `status:"lista_espera"`, `comprovante_enviado:true` | +1 (E1, P1, lista_espera); 1 comprovante | R2 (sem vaga) |
| CT10 | Sequência: a 1ª inscrição gravada ocupa a vaga da 2ª | E1 (gratuito, vagas=1); nenhuma inscrição; notificador OK | (a) E1, P1; depois (b) E1, P2 | (a) 201; (b) 201 | (a) `status:"confirmada"`; (b) `status:"lista_espera"` | 2 inscrições: (E1,P1,confirmada), (E1,P2,lista_espera); 2 comprovantes | R2 + persistência real |
| CT11 | Conflito: sobreposição parcial (o outro evento começa antes) | E1 (gratuito, vagas=3, 10:00–12:00); E2 (09:00–11:00); (E2,P1,confirmada); notificador OK | E1, P1 | 409 | `{"detail": ...}` | Inscrições inalteradas; 0 comprovantes (notificador não acionado) | R1 |
| CT12 | Conflito: sobreposição parcial (o outro evento começa depois) | E1 (10:00–12:00); E2 (11:00–13:00); (E2,P1,confirmada) | E1, P1 | 409 | `{"detail"}` | Inalterado; 0 comprovantes | R1 |
| CT13 | Conflito: E1 contido em E2 | E1 (10:00–11:00); E2 (09:00–13:00); (E2,P1,confirmada) | E1, P1 | 409 | `{"detail"}` | Inalterado; 0 comprovantes | R1 |
| CT14 | Conflito: E1 contém E2 | E1 (09:00–13:00); E2 (10:00–11:00); (E2,P1,confirmada) | E1, P1 | 409 | `{"detail"}` | Inalterado; 0 comprovantes | R1 |
| CT15 | Conflito: horários idênticos | E1 (10:00–12:00); E2 (10:00–12:00); (E2,P1,confirmada) | E1, P1 | 409 | `{"detail"}` | Inalterado; 0 comprovantes | R1 |
| CT16 | Limite: sobreposição mínima de 1 minuto | E1 (10:00–12:00); E2 (08:00–10:01); (E2,P1,confirmada) | E1, P1 | 409 | `{"detail"}` | Inalterado; 0 comprovantes | R1 (limite) |
| CT17 | Limite: eventos que se encostam (E2 termina quando E1 começa) | E1 (gratuito, vagas=3, 10:00–12:00); E2 (08:00–10:00); (E2,P1,confirmada); notificador OK | E1, P1 | 201 | `status:"confirmada"`, `comprovante_enviado:true` | +1 (E1, P1, confirmada); 1 comprovante | R1 (encostar não conflita) |
| CT18 | Limite: eventos que se encostam (E1 termina quando E2 começa) | E1 (gratuito, vagas=3, 10:00–12:00); E2 (12:00–14:00); (E2,P1,confirmada) | E1, P1 | 201 | `status:"confirmada"`, `comprovante_enviado:true` | +1 (E1, P1, confirmada); 1 comprovante | R1 (encostar não conflita) |
| CT19 | Inscrição pendente de pagamento sobreposta não gera conflito | E1 (gratuito, vagas=3, 10:00–12:00); E2 (pago, 10:00–12:00); (E2,P1,pendente_pagamento) | E1, P1 | 201 | `status:"confirmada"`, `comprovante_enviado:true` | +1 (E1, P1, confirmada); (E2,P1) inalterada; 1 comprovante | R1 (só confirmada conflita) |
| CT20 | Inscrição em lista de espera sobreposta não gera conflito | E1 (gratuito, vagas=3, 10:00–12:00); E2 (10:00–12:00); (E2,P1,lista_espera) | E1, P1 | 201 | `status:"confirmada"`, `comprovante_enviado:true` | +1 (E1, P1, confirmada); 1 comprovante | R1 (só confirmada conflita) |
| CT21 | Inscrição confirmada em evento sem sobreposição | E1 (gratuito, vagas=3, 10/11 10:00–12:00); E2 (11/11 10:00–12:00); (E2,P1,confirmada) | E1, P1 | 201 | `status:"confirmada"`, `comprovante_enviado:true` | +1 (E1, P1, confirmada); 1 comprovante | R1 (sem sobreposição) |
| CT22 | Conflito é por participante: outro participante confirmado no evento sobreposto | E1 (gratuito, vagas=3, 10:00–12:00); E2 (10:00–12:00); (E2,P2,confirmada) | E1, P1 | 201 | `status:"confirmada"`, `comprovante_enviado:true` | +1 (E1, P1, confirmada); 1 comprovante | R1 |
| CT23 | Várias inscrições do participante, só uma confirmada e sobreposta | E1 (10:00–12:00); E2 (11/11 10:00–12:00); E3 (10:00–12:00); E4 (11:00–12:00); (E2,P1,confirmada), (E3,P1,lista_espera), (E4,P1,confirmada) | E1, P1 | 409 | `{"detail"}` | Inalterado; 0 comprovantes | R1 |
| CT24 | Conflito tem precedência sobre falta de vaga | E1 (gratuito, vagas=1, 10:00–12:00); (E1,P2,confirmada); E2 (10:00–12:00); (E2,P1,confirmada) | E1, P1 | 409 (não 201 com `lista_espera`) | `{"detail"}` | Inalterado; 0 comprovantes | Ordem R1 → R2 |
| CT25 | Conflito tem precedência sobre o tipo do evento | E1 (pago, vagas=3, 10:00–12:00); E2 (10:00–12:00); (E2,P1,confirmada) | E1, P1 | 409 | `{"detail"}` | Inalterado; 0 comprovantes | Ordem R1 → R3 |
| CT26 | Participante já inscrito (confirmada) no mesmo evento | E1 (gratuito, vagas=3); (E1,P1,confirmada); notificador OK | E1, P1 | 409 | `{"detail"}` | Continua 1 inscrição (E1,P1); 0 comprovantes | Contrato: já inscrito |
| CT27 | Mesma requisição enviada duas vezes | E1 (gratuito, vagas=3); nenhuma inscrição; notificador OK | (a) E1, P1; depois (b) E1, P1 | (a) 201; (b) 409 | (a) `status:"confirmada"`, `comprovante_enviado:true`; (b) `{"detail"}` | Só 1 inscrição (E1,P1,confirmada); 1 comprovante no total | Já inscrito + persistência |
| CT28 | Evento não existe | Só existe E1; (E1,P2,confirmada) | `POST /eventos/E999/inscricoes` `{"participante_id":"part-001"}` | 404 | `{"detail"}` | Inalterado; 0 comprovantes | Contrato 404 |
| CT29 | Corpo sem `participante_id` | E1 (gratuito, vagas=3) | E1, `{}` | 422 | Erro de validação | Inalterado; 0 comprovantes | Contrato 422 (obrigatório) |
| CT30 | `participante_id` vazio | E1 (gratuito, vagas=3) | E1, `{"participante_id":""}` | 422 | Erro de validação | Inalterado; 0 comprovantes | Contrato 422 (não vazio) |
| CT31 | `participante_id` nulo | E1 (gratuito, vagas=3) | E1, `{"participante_id":null}` | 422 | Erro de validação | Inalterado; 0 comprovantes | Contrato 422 |
| CT32 | Corpo ausente ou JSON malformado | E1 (gratuito, vagas=3) | E1, corpo vazio; e também `{"participante_id":` (truncado) | 422 | Erro de validação | Inalterado; 0 comprovantes | Contrato 422 |
| CT33 | Notificador falha em inscrição confirmada | E1 (gratuito, vagas=3); nenhuma inscrição; **notificador falha** | E1, P1 | 201 | `status:"confirmada"`, `comprovante_enviado:false` | +1 (E1, P1, confirmada); 0 comprovantes enviados (houve tentativa) | Contrato: falha no envio |
| CT34 | Notificador falha em inscrição pendente de pagamento | E1 (pago, vagas=3); **notificador falha** | E1, P1 | 201 | `status:"pendente_pagamento"`, `comprovante_enviado:false` | +1 (E1, P1, pendente_pagamento); 0 enviados | Falha no envio + R3 |
| CT35 | Notificador falha em lista de espera | E1 (gratuito, vagas=1); (E1,P2,confirmada); **notificador falha** | E1, P1 | 201 | `status:"lista_espera"`, `comprovante_enviado:false` | +1 (E1, P1, lista_espera); 0 enviados | Falha no envio + R2 |
| CT36 | Inscrição gravada apesar da falha ocupa vaga | E1 (gratuito, vagas=1); nenhuma inscrição; notificador **falha** na 1ª chamada e OK na 2ª | (a) E1, P1; depois (b) E1, P2 | (a) 201; (b) 201 | (a) `confirmada`, `comprovante_enviado:false`; (b) `lista_espera`, `comprovante_enviado:true` | (E1,P1,confirmada), (E1,P2,lista_espera); 1 comprovante enviado | Falha no envio + R2 |
| CT37 | Inscrição gravada apesar da falha gera conflito | E1 (gratuito, vagas=3, 10:00–12:00); E2 (gratuito, vagas=3, 11:00–13:00); nenhuma inscrição; notificador **falha** na 1ª chamada | (a) E2, P1; depois (b) E1, P1 | (a) 201; (b) 409 | (a) `confirmada`, `comprovante_enviado:false`; (b) `{"detail"}` | Só (E2,P1,confirmada); 0 comprovantes enviados | Falha no envio + R1 |
| CT38 | Inscrição gravada apesar da falha impede duplicidade | E1 (gratuito, vagas=3); notificador **falha** na 1ª chamada e OK depois | (a) E1, P1; depois (b) E1, P1 | (a) 201; (b) 409 | (a) `comprovante_enviado:false`; (b) `{"detail"}` | Só 1 inscrição (E1,P1,confirmada); 0 enviados; a 2ª requisição não aciona o notificador | Falha no envio + já inscrito |
| CT39 | Notificador com falha não altera as respostas de erro | **Notificador falha**; repetir com os estados de CT11 (409 conflito), CT26 (409 duplicidade), CT28 (404) e CT29 (422) | Iguais às de CT11, CT26, CT28 e CT29 | 409 / 409 / 404 / 422 | `{"detail"}` / `{"detail"}` / `{"detail"}` / erro de validação | Inalterado; notificador **não acionado** em nenhum dos casos | Efeitos dos erros |

## Dúvidas (o resultado esperado não foi definido)

1. **404 ou 422:** se o evento não existe e o corpo também é inválido (por exemplo, `POST /eventos/E999/inscricoes` com `{}`), qual status vence?
2. **`evento_id` mal formatado:** se o ID tem formato inválido (por exemplo, texto onde se espera número, se for o caso), a resposta é 404 ou 422? O formato do ID não foi definido.
3. **Quem conta como "já inscrito":** um participante que já tem `pendente_pagamento` ou `lista_espera` no mesmo evento recebe 409? Ou pode se inscrever de novo, por exemplo para sair da lista de espera?
4. **Duplicidade em evento lotado:** a duplicidade não está na lista ordenada de regras. Se P1 já está inscrito e o evento está lotado, o resultado deveria ser 409 (como assumi em CT26) ou 201 com `lista_espera`? Isso precisa ser confirmado.
5. **Duplicidade e conflito ao mesmo tempo:** o status é 409 nos dois casos, mas qual mensagem vem no `detail`? O texto de `detail` não foi definido em nenhum 404/409, por isso os casos não verificam o conteúdo.
6. **`participante_id` só com espaços** (`"   "`): conta como vazio (422) ou é aceito?
7. **`participante_id` que não é texto** (`123`, `true`, `["x"]`): a resposta é 422 ou o valor é convertido para texto?
8. **Campos extras no corpo** (por exemplo, `{"participante_id":"part-001","x":1}`): são ignorados ou geram 422?
9. **Tamanho e caracteres de `participante_id`:** existe limite de tamanho ou de caracteres aceitos?
10. **Existência do participante:** o repositório guarda só eventos e inscrições. Um `participante_id` qualquer é sempre aceito?
11. **Concorrência:** duas requisições simultâneas disputando a última vaga podem gerar duas `confirmada`? E duas requisições simultâneas do mesmo participante podem gerar duplicidade?
12. **Detalhes do notificador:**
    - Há novas tentativas após uma falha? Quantas?
    - Um timeout conta como falha?
    - Qual o conteúdo e o destinatário do comprovante?
    - O comprovante muda conforme o `status`?
13. **Horários dos eventos:**
    - Qual o fuso horário e o formato?
    - O que acontece com eventos de duração zero (início = fim) ou com fim antes do início?
    - Um evento de duração zero às 10:00, dentro de outro das 09:00 às 11:00, "sobrepõe"?
14. **Capacidade:** existe evento sem limite de vagas (nulo ou ilimitado)? Como tratar capacidade negativa?
15. **Corpo do 201:** o corpo deve ter exatamente os quatro campos ou pode ter outros? Qual o tipo de `evento_id` na resposta (texto ou número)?
16. **Conflito com evento passado:** uma inscrição confirmada em evento que já aconteceu continua sendo avaliada? Pela regra literal, sim, mas convém confirmar que não há corte por data.
