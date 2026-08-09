# Escolha dos Artefatos de Especificação

> Análise comparativa dos artefatos apresentados no material da disciplina
> (casos de uso, histórias de usuário, critérios de aceitação e protótipos),
> aplicada ao cenário do Sistema de Gestão de Eventos (Eventus), com apoio
> de IA generativa e revisão crítica.

## Comparativo geral

| Artefato | Quando é mais indicado (segundo o material) | Aplicação ao caso Eventus |
|---|---|---|
| **Casos de uso** | Projetos mais tradicionais, funcionalidades com múltiplos fluxos alternativos/exceção, quando se quer detalhamento das interações ator↔sistema. Custo de elaboração maior. | Bom para fluxos com muitas variações e regras — ex.: **Inscrever-se em Evento** (grátis x pago, vaga livre x lista de espera, conflito de horário) e **Cancelar Inscrição** (permitido x não permitido, prazo, reembolso). |
| **Histórias de usuário** | Contextos ágeis, foco no valor entregue, funcionalidades mais simples ou que serão refinadas de forma incremental. Pouco detalhe isoladamente. | Boas para representar as necessidades relatadas literalmente pelos stakeholders (ex.: visualizar eventos, emitir certificado, consultar participantes). |
| **Critérios de aceitação** | Complementam histórias de usuário (ou casos de uso), tornando o comportamento esperado verificável objetivamente; base direta para testes. | Essenciais aqui, pois várias regras de negócio (RN01–RN07) só ficam claras quando descritas como condições verificáveis (dado–quando–então). |
| **Protótipos** | Quando a interface/navegação precisa ser validada antes da implementação; não substituem requisitos, complementam. | Úteis para telas com mais complexidade de interação, ex.: **catálogo de eventos** e **checkout de inscrição** (vaga, pagamento, lista de espera). Fora do escopo textual deste exercício (não há ferramenta de UI envolvida), então tratarei como *opcional/baixa prioridade*. |

## Recomendação (sugerida pela IA, avaliada criticamente)

Combinar três artefatos, seguindo exatamente o padrão que o material
descreve na Figura 4 (história de usuário → critérios de aceitação →
protótipo), mas usando **casos de uso** nos fluxos mais complexos e com
mais regras de negócio embutidas:

1. **Histórias de usuário** — para as funcionalidades voltadas a
   Participantes, Organizadores, Equipe Financeira e Palestrantes,
   cobrindo RF01, RF03, RF05, RF10, RF11, RF12, RF15, RF16. São
   funcionalidades relativamente diretas, bem descritas por "Como
   `<usuário>`, quero `<ação>`, para `<benefício>`".

2. **Casos de uso** — para os dois fluxos mais críticos, com múltiplas
   regras de negócio e caminhos alternativos:
   - **Inscrever-se em Evento** (RF02, RF06, RF08, RF09, RF14, RN01, RN03,
     RN05, RN06)
   - **Cancelar Inscrição** (RF04, RN02, RN04)

   Esses dois concentram a maior parte das regras de negócio e das
   dúvidas/lacunas levantadas — o detalhamento de fluxo principal/
   alternativo do caso de uso ajuda a tornar explícitas as decisões que
   ainda estavam ambíguas no documento de elicitação.

3. **Critérios de aceitação** — para **todas** as histórias de usuário e
   casos de uso do item 1 e 2, no formato Dado–Quando–Então, cobrindo
   inclusive os cenários alternativos (evento lotado, cancelamento não
   permitido, pagamento pendente etc.).

4. **Protótipos** — **não incluídos** nesta entrega. Justificativa: o
   exercício está centrado em análise/especificação textual de requisitos;
   sem uma ferramenta de design e sem validação real com stakeholders, um
   protótipo aqui seria apenas estético, sem o benefício real de validação
   precoce que o material atribui a esse artefato. Registrado como
   artefato considerado e descartado (a justificar no README.md).

### O que foi aceito / modificado da sugestão da IA

- **Aceito:** uso combinado de histórias de usuário + critérios de
  aceitação, seguindo o padrão do material (Figura 4).
- **Modificado:** a IA inicialmente sugeriu casos de uso para *todas* as
  funcionalidades; optei por restringir casos de uso apenas às duas
  funcionalidades com maior densidade de regras de negócio, e usar
  histórias de usuário (mais leves) para o restante — evita
  sobre-especificação de funcionalidades simples.
- **Descartado:** protótipos, pelo motivo explicado acima.

## Artefatos a produzir em `especificacao/`

```
especificacao/
├── historias-de-usuario.md
├── casos-de-uso.md
└── criterios-de-aceitacao.md
```
