# Prompt 3 (v2) — Focado em erros e falhas de integração

> Tipo: papel + contexto do contrato + foco em falhas entre componentes
> (*o que pode dar errado na comunicação*), com classificação por tipo de
> falha.
>
> **Ajustes em relação à v1** (`3-erros-e-falhas.md`): incluídos os valores
> de `status`, as regras de negócio e como o notificador sinaliza falha
> (a v1 marcou esses pontos como dúvida); concorrência e timeouts fora do
> escopo (a v1 supôs comportamentos para eles).

---

Você é um analista de testes especializado em falhas de integração. Para a
API abaixo, gere apenas casos de teste de **erro e falha** que aconteçam na
comunicação entre os componentes: cliente → API, API → regra de negócio,
API → repositório (onde ficam eventos e inscrições) e API → notificador
(que envia o comprovante de inscrição).

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

Regras de negócio (nesta ordem): participante já inscrito no evento, em
qualquer status → `409`; inscrição **confirmada** do participante em
**outro** evento com horário sobreposto → `409` (eventos que só se encostam
não conflitam); sem vaga → `lista_espera` (ocupam vaga `confirmada` e
`pendente_pagamento`); evento pago → `pendente_pagamento`; gratuito →
`confirmada`.

Efeitos:

- `201`: a inscrição é gravada no repositório e **um** comprovante é
  enviado.
- `404`, `409` e `422`: nada é gravado e nenhum comprovante é enviado.
- Se o envio do comprovante falhar, a inscrição continua gravada e a API
  responde `201` com `"comprovante_enviado": false`.

## Premissas e fora do escopo

- O notificador sinaliza falha **lançando uma exceção**.
- Os eventos cadastrados no repositório são sempre válidos (`vagas >= 1`,
  fim depois do início).
- Concorrência, timeouts, autenticação e reenvio de comprovante estão fora
  do escopo: não gere casos para eles.

## O que entregar

Agrupe os casos por tipo de falha:

1. **Entrada inválida** (formato, tipos, campos ausentes ou extras,
   valores no limite).
2. **Recurso inexistente ou estado inconsistente** no repositório.
3. **Falha de um componente dependente** (ex.: notificador indisponível).
4. **Efeitos colaterais indevidos** (algo gravado ou enviado quando não
   deveria, ou enviado mais de uma vez).

Para cada caso: **ID | Tipo | Cenário | Como provocar a falha | Status
esperado | O que verificar no repositório e no notificador**.

- Use apenas dados fictícios.
- **Não invente comportamento.** Se o contrato não define o resultado de
  um caso, não escreva o esperado: liste-o numa seção "Dúvidas" ao final,
  explicando por que ele importa.
