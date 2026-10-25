# Prompt 3 — Focado em erros e falhas de integração

> Tipo: papel + contexto do contrato + foco em falhas entre componentes
> (*o que pode dar errado na comunicação*), com classificação por tipo de
> falha.

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

Efeitos:

- `201`: a inscrição é gravada no repositório e **um** comprovante é
  enviado.
- `404`, `409` e `422`: nada é gravado e nenhum comprovante é enviado.
- Se o envio do comprovante falhar, a inscrição continua gravada e a API
  responde `201` com `"comprovante_enviado": false`.

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
