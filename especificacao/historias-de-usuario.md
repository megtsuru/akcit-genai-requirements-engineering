# Histórias de Usuário

> Formato: Como `<tipo de usuário>`, quero `<funcionalidade>`, para
> `<benefício esperado>`. Cobrem as funcionalidades mais diretas
> identificadas na análise (`analise/requisitos-funcionais.md`).

| ID | História de Usuário | Requisito relacionado |
|----|----------------------|-------------------------|
| HU01 | Como **participante**, quero visualizar todos os eventos disponíveis em um único lugar, para escolher em quais desejo me inscrever sem precisar consultar múltiplas fontes. | RF01 |
| HU02 | Como **participante**, quero receber um comprovante logo após minha inscrição, para ter a confirmação de que ela foi realizada com sucesso. | RF03 |
| HU03 | Como **participante**, quero emitir meu certificado após a realização do evento, para comprovar minha participação. | RF05 |
| HU04 | Como **organizador**, quero acompanhar as inscrições e gerenciar os participantes de um evento, para ter controle sobre quem está inscrito e tomar decisões operacionais. | RF10 |
| HU05 | Como **organizador**, quero visualizar a quantidade de inscritos em tempo real, para monitorar a procura pelo evento e agir rapidamente se necessário. | RF11 |
| HU06 | Como **membro da equipe financeira**, quero confirmar os pagamentos das inscrições pagas, para liberar a participação do inscrito no evento. | RF12 |
| HU07 | Como **palestrante**, quero consultar a programação das minhas atividades, para me organizar previamente. | RF15 |
| HU08 | Como **palestrante**, quero consultar a lista de participantes inscritos nas minhas atividades, para conhecer previamente meu público. | RF16 |

> As funcionalidades **Inscrever-se em Evento** (RF02, RF06, RF08, RF09,
> RF14) e **Cancelar Inscrição** (RF04) não foram representadas como
> histórias de usuário porque concentram várias regras de negócio e fluxos
> alternativos — foram detalhadas como **casos de uso** em
> `casos-de-uso.md`, conforme justificado em
> `../analise/escolha-artefatos.md`.

Os critérios de aceitação correspondentes a cada história estão em
`criterios-de-aceitacao.md`.
