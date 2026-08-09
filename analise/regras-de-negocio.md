# Regras de Negócio

> Condições e restrições que governam o comportamento do sistema,
> identificadas a partir das falas dos stakeholders e das observações do
> documento de elicitação.

| ID | Regra | Origem |
|----|-------|--------|
| RN01 | Um evento pode ser gratuito ou pago; o fluxo de inscrição depende desse tipo. | Equipe Financeira: "Alguns eventos são gratuitos e outros exigem pagamento." |
| RN02 | Nem todo evento permite cancelamento de inscrição — a permissão é configurável por evento (definida pelo organizador). | Organizador: "Nem todos os eventos permitem o cancelamento da inscrição." |
| RN03 | Em eventos pagos, a inscrição só é confirmada/liberada após a confirmação do pagamento pela equipe financeira. | Equipe Financeira: "Precisamos confirmar os pagamentos antes de liberar determinadas inscrições." |
| RN04 | O direito a reembolso é condicional — aplica-se apenas em determinadas situações, não em todas. | Equipe Financeira: "Em alguns casos o participante tem direito ao reembolso, em outros não." |
| RN05 | Quando um evento atinge o limite de vagas, novas inscrições passam a compor uma lista de espera em vez de serem recusadas diretamente. | Organizador: "Quando um evento lotar, seria interessante criar uma lista de espera." |
| RN06 | Um participante não pode se inscrever em duas atividades (workshops) que ocorram no mesmo horário, pois workshops simultâneos são, por definição, paralelos. | Organizador: "Os workshops que acontecem no mesmo horário devem ocorrer simultaneamente." |
| RN07 | A emissão de certificado está associada à realização do evento (o participante só pode emiti-lo depois do evento ocorrer). | Participante: "Quero conseguir emitir meu certificado depois do evento." |

**Observação:** algumas dessas regras têm condições ainda não totalmente
definidas (por exemplo, os critérios exatos de RN04 e o funcionamento
detalhado de RN05). Essas lacunas estão registradas em
`duvidas-e-lacunas.md` e precisam ser esclarecidas antes da especificação
final.
