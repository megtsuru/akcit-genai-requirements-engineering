# Requisitos Não Funcionais

> O documento de elicitação registra explicitamente, na seção de
> Observações, que **"não foram levantados requisitos relacionados à
> segurança, desempenho, disponibilidade, acessibilidade e privacidade dos
> dados"**. Ou seja, não há RNFs formalmente coletados junto aos
> stakeholders — essa é uma lacuna real do processo de elicitação (ver
> `duvidas-e-lacunas.md`).
>
> Os itens abaixo são **candidatos** de RNF, inferidos indiretamente a
> partir de necessidades funcionais relatadas nas entrevistas. Eles não
> substituem uma elicitação de RNF propriamente dita e devem ser
> validados com os stakeholders antes de serem tratados como requisitos
> confirmados.

| ID | Requisito (candidato) | Justificativa / origem indireta |
|----|------------------------|----------------------------------|
| RNF01 (a validar) | A contagem de inscritos exibida aos organizadores deve ser atualizada em tempo real ou quase real (ex.: poucos segundos de defasagem). | "Gostaríamos de acompanhar a quantidade de inscritos em tempo real." |
| RNF02 (a validar) | O sistema deve tratar corretamente inscrições concorrentes no mesmo evento, sem permitir ultrapassar o número de vagas configurado (consistência sob concorrência). | Controle automático de vagas + lista de espera |
| RNF03 (a validar) | O sistema deve suportar o funcionamento simultâneo de múltiplos workshops no mesmo horário, sem impacto perceptível de desempenho entre eles. | "Os workshops que acontecem no mesmo horário devem ocorrer simultaneamente." |
| RNF04 (a validar) | Dados de pagamento e reembolso devem ser tratados com controles de segurança e privacidade adequados (o sistema lida com dados financeiros e pessoais). | Fluxo de confirmação de pagamento/reembolso pela equipe financeira |
| RNF05 (a validar) | O acesso às informações de participantes por palestrantes deve respeitar princípios de privacidade (visibilidade restrita ao necessário). | Ver dúvida sobre quais dados os palestrantes podem visualizar |

**Próximo passo recomendado:** levantar RNFs de forma explícita com os
stakeholders (em especial Equipe de TI e Equipe Financeira), cobrindo pelo
menos segurança, desempenho, disponibilidade, acessibilidade e privacidade,
antes de considerar esta lista completa.
