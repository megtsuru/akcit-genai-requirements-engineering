# Casos de Uso

> Estrutura: nome, objetivo, ator(es), pré-condições, fluxo principal,
> fluxos alternativos, pós-condições. Escolhidos para as duas
> funcionalidades com maior densidade de regras de negócio e fluxos
> alternativos (ver `../analise/escolha-artefatos.md`).

## Caso de Uso 1 — Inscrever-se em Evento

| Campo | Descrição |
|---|---|
| **Nome** | Inscrever-se em Evento |
| **Objetivo** | Permitir que o participante se inscreva em um evento ou atividade (workshop) disponível. |
| **Ator principal** | Participante |
| **Ator secundário** | Equipe Financeira (confirmação de pagamento, quando aplicável) |
| **Pré-condições** | Participante autenticado no sistema; evento com inscrições abertas. |
| **Fluxo principal** | 1. O participante seleciona um evento na lista de eventos disponíveis.<br>2. O sistema verifica se há vagas disponíveis (RF08).<br>3. O sistema verifica se há conflito de horário com outra inscrição já confirmada do participante (RN06).<br>4. Se o evento for gratuito, o sistema confirma a inscrição imediatamente e envia o comprovante (RF03, RN01).<br>5. Se o evento for pago, o sistema encaminha o participante para pagamento; após a confirmação do pagamento pela Equipe Financeira, a inscrição é liberada e o comprovante é enviado (RF14, RN01, RN03). |
| **Fluxos alternativos** | **A1 — Evento sem vagas:** o sistema oferece entrada na lista de espera (RF09, RN05); o participante confirma ou desiste.<br>**A2 — Conflito de horário:** o sistema impede a inscrição e informa o conflito ao participante (RN06).<br>**A3 — Pagamento não confirmado:** a inscrição não é liberada; tratamento da reserva de vaga durante esse período depende de definição pendente (ver `duvidas-e-lacunas.md`, item 6). |
| **Pós-condição** | Inscrição registrada como confirmada ou em lista de espera; comprovante enviado quando aplicável. |

## Caso de Uso 2 — Cancelar Inscrição

| Campo | Descrição |
|---|---|
| **Nome** | Cancelar Inscrição |
| **Objetivo** | Permitir que o participante cancele uma inscrição já realizada, quando o evento permitir. |
| **Ator principal** | Participante |
| **Ator secundário** | Equipe Financeira (processamento de reembolso, quando aplicável) |
| **Pré-condições** | Participante autenticado, com inscrição ativa em um evento que permite cancelamento (RN02). |
| **Fluxo principal** | 1. O participante acessa "Minhas Inscrições" e seleciona a inscrição a cancelar.<br>2. O sistema verifica se o evento permite cancelamento (RN02).<br>3. O sistema verifica se o cancelamento está dentro do prazo permitido (ver `duvidas-e-lacunas.md`, item 1).<br>4. O sistema efetiva o cancelamento e libera a vaga.<br>5. Se o participante tiver direito a reembolso (RN04), o sistema notifica a Equipe Financeira para processá-lo.<br>6. O sistema notifica o próximo participante da lista de espera, se houver (RN05). |
| **Fluxos alternativos** | **A1 — Cancelamento não permitido:** o sistema informa que este evento não permite cancelamento de inscrição (RN02).<br>**A2 — Fora do prazo:** o sistema informa que o prazo para cancelamento já expirou.<br>**A3 — Sem direito a reembolso:** o sistema efetiva o cancelamento sem gerar solicitação de reembolso (RN04). |
| **Pós-condição** | Inscrição cancelada; vaga liberada; reembolso processado quando aplicável. |

Os critérios de aceitação correspondentes a cada caso de uso estão em
`criterios-de-aceitacao.md`.
