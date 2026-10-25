# Prompt 2 (v2) — Baseado no contrato e nas regras de negócio

> Tipo: papel + contexto completo (contrato da API e regras) + formato de
> saída definido + instrução para não inventar regras.
>
> **Ajustes em relação à v1** (`2-contrato.md`), a partir das dúvidas e
> erros da primeira resposta: regra de "já inscrito" (qualquer status) e
> sua posição na ordem; eventos do repositório sempre válidos (a v1 gerou
> um caso com evento de 0 vagas); concorrência fora do escopo.

---

Você é um analista de testes. Gere casos de teste de **integração** para a
API abaixo. Um caso de teste de integração verifica a API funcionando junto
com os componentes reais por trás dela: a regra de negócio, o repositório
(onde ficam eventos e inscrições) e o notificador (que envia o comprovante
de inscrição).

## Contrato

`POST /eventos/{evento_id}/inscricoes`, corpo `{"participante_id": "<texto>"}`
(`participante_id` obrigatório e não vazio).

| Situação | Status HTTP | Corpo |
|----------|-------------|-------|
| Inscrição aceita | `201` | `{"evento_id", "participante_id", "status", "comprovante_enviado"}` |
| Evento não existe | `404` | `{"detail"}` |
| Conflito de horário | `409` | `{"detail"}` |
| Participante já inscrito no evento | `409` | `{"detail"}` |
| Corpo inválido | `422` | erro de validação |

`status` no `201`: `"confirmada"`, `"pendente_pagamento"` ou `"lista_espera"`.

Efeitos:

- `201`: a inscrição é gravada no repositório e **um** comprovante é
  enviado.
- `404`, `409` e `422`: nada é gravado e nenhum comprovante é enviado.
- Se o envio do comprovante falhar, a inscrição continua gravada e a API
  responde `201` com `"comprovante_enviado": false`.

## Regras de negócio (avaliadas nesta ordem)

0. Já inscrito: se o participante já tem inscrição **em qualquer status**
   (`confirmada`, `pendente_pagamento` ou `lista_espera`) neste evento →
   `409`. É verificada antes das demais regras.
1. Conflito de horário: se o participante tem inscrição **confirmada** em
   **outro** evento cujo horário se sobrepõe → `409`. Eventos que só se
   encostam (um termina às 10:00, o outro começa às 10:00) não conflitam.
   Inscrição em lista de espera ou pendente de pagamento não gera
   conflito.
2. Vagas: ocupam vaga as inscrições `confirmada` e `pendente_pagamento`
   do evento; `lista_espera` não ocupa. Sem vaga → `201` com
   `"lista_espera"`.
3. Tipo do evento: gratuito → `"confirmada"`; pago → `"pendente_pagamento"`.

## Premissas e fora do escopo

- Os eventos cadastrados no repositório são sempre válidos: `vagas >= 1` e
  fim depois do início. Não gere casos com eventos inválidos.
- Concorrência (requisições simultâneas), autenticação, cancelamento,
  pagamento e reenvio de comprovante estão fora do escopo.
- `participante_id` não precisa existir em nenhum cadastro: qualquer texto
  não vazio é aceito.

## O que entregar

Uma tabela com as colunas: **ID | Cenário | Estado inicial (eventos e
inscrições no repositório; comportamento do notificador) | Requisição |
Status esperado | Corpo esperado | Efeitos esperados (inscrições gravadas,
comprovantes enviados) | Regra coberta**.

- Cubra funcionamento normal, limites e erros.
- Use apenas dados fictícios.
- **Não invente regras.** Se um caso depender de algo que o contrato e as
  regras não definem, não escreva o resultado esperado: liste-o numa seção
  "Dúvidas" ao final.
