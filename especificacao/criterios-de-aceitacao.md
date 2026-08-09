# Critérios de Aceitação

> Formato Dado – Quando – Então (Given – When – Then), conforme o material
> da disciplina. Cobrem as histórias de usuário e os casos de uso
> definidos em `historias-de-usuario.md` e `casos-de-uso.md`, incluindo os
> cenários alternativos.

## Referentes às Histórias de Usuário

### HU01 — Visualizar eventos disponíveis
| Dado | Quando | Então |
|---|---|---|
| O participante está autenticado. | Acessa a área de eventos. | O sistema apresenta a lista de todos os eventos disponíveis para inscrição. |

### HU02 — Comprovante de inscrição
| Dado | Quando | Então |
|---|---|---|
| A inscrição do participante foi confirmada. | O sistema conclui o processamento da inscrição. | O sistema envia um comprovante de inscrição ao participante. |

### HU03 — Emitir certificado
| Dado | Quando | Então |
|---|---|---|
| O evento já foi realizado e o participante esteve inscrito. | O participante solicita a emissão do certificado. | O sistema disponibiliza o certificado para download. |
| O evento ainda não foi realizado. | O participante tenta emitir o certificado. | O sistema informa que o certificado só estará disponível após a realização do evento. |

### HU04 — Acompanhar inscrições e gerenciar participantes
| Dado | Quando | Então |
|---|---|---|
| O organizador está autenticado e possui eventos criados. | Acessa o painel de um evento. | O sistema apresenta a lista de participantes inscritos e permite ações de gerenciamento (ex.: remover, contatar). |

### HU05 — Inscritos em tempo real
| Dado | Quando | Então |
|---|---|---|
| Existem inscrições registradas para um evento. | O organizador acessa o painel do evento. | O sistema exibe a quantidade atual de inscritos, refletindo inscrições/cancelamentos recentes. |

### HU06 — Confirmar pagamentos
| Dado | Quando | Então |
|---|---|---|
| Existe uma inscrição pendente de pagamento. | A equipe financeira confirma o recebimento do pagamento. | O sistema libera a inscrição do participante (RN03) e dispara o envio do comprovante (RF03). |

### HU07 — Consultar programação (palestrante)
| Dado | Quando | Então |
|---|---|---|
| O palestrante está autenticado e possui atividades vinculadas. | Acessa a área "Minha Programação". | O sistema exibe as atividades, horários e locais das atividades do palestrante. |

### HU08 — Consultar participantes (palestrante)
| Dado | Quando | Então |
|---|---|---|
| O palestrante está autenticado e possui atividades com inscritos. | Acessa a lista de participantes de uma atividade sua. | O sistema exibe os participantes inscritos, limitado às informações definidas como visíveis a palestrantes (ver `../analise/duvidas-e-lacunas.md`, item 8). |

## Referentes ao Caso de Uso — Inscrever-se em Evento

| Dado | Quando | Então |
|---|---|---|
| O evento é gratuito e possui vagas disponíveis. | O participante solicita inscrição. | O sistema confirma a inscrição imediatamente e envia o comprovante. |
| O evento é pago e possui vagas disponíveis. | O participante conclui o pagamento. | O sistema libera a inscrição somente após a confirmação do pagamento pela equipe financeira. |
| O evento está com todas as vagas preenchidas. | O participante solicita inscrição. | O sistema oferece a entrada na lista de espera em vez de recusar diretamente. |
| O participante já possui inscrição confirmada em outra atividade no mesmo horário. | O participante tenta se inscrever em uma nova atividade conflitante. | O sistema impede a inscrição e informa o conflito de horário. |

## Referentes ao Caso de Uso — Cancelar Inscrição

| Dado | Quando | Então |
|---|---|---|
| O evento permite cancelamento e o participante está dentro do prazo definido. | O participante solicita o cancelamento. | O sistema efetiva o cancelamento e libera a vaga. |
| O evento não permite cancelamento. | O participante solicita o cancelamento. | O sistema informa que o cancelamento não é permitido para este evento. |
| O cancelamento ocorre fora do prazo permitido. | O participante solicita o cancelamento. | O sistema informa que o prazo para cancelamento expirou. |
| O participante tem direito a reembolso conforme as regras do evento. | O cancelamento é efetivado. | O sistema notifica a equipe financeira para processar o reembolso. |
| Existe um participante na lista de espera do evento. | Uma vaga é liberada por cancelamento. | O sistema notifica o próximo participante da lista de espera. |
