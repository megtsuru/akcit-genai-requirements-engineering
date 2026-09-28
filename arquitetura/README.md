# Arquitetura — Discovery de Documentação

Discovery de documentação de arquitetura do sistema **Eventus**, praticando
a abordagem *diagrams as code*, com apoio de GenAI (Claude Code) e a partir
da análise de requisitos já produzida em `../analise/`.

## Artefatos produzidos

- [`descricao-sistema.md`](./descricao-sistema.md) — descrição em
  linguagem natural: escopo, nível de visão, limites e responsabilidades,
  integrações, restrições e lacunas.
- [`diagramas/containers.md`](./diagramas/containers.md) — diagrama
  estrutural (visão de containers, C4 nível 2).
- [`diagramas/sequencia-inscricao-evento.md`](./diagramas/sequencia-inscricao-evento.md)
  — diagrama comportamental (sequência da jornada *Inscrever-se em
  Evento*).

## O que o modelo inferiu corretamente

Partindo da análise de requisitos já pronta (`../analise/`), o mapeamento
para containers — aplicação do participante, painel administrativo, API e
banco de dados — e a identificação de pagamento e notificação como
integrações externas saíram consistentes com os RF/RN já levantados, sem
precisar corrigir conteúdo de negócio. O nível de visão (C2 — containers)
também não exigiu decisão adicional: é o próprio exemplo dado no
enunciado da atividade, e é o nível certo aqui — C1 mostraria só uma caixa
sem informação útil, e C3 exigiria decisões internas que a elicitação não
define.

## O que precisei ajustar

- **Nenhuma tecnologia inventada:** a descrição e os diagramas identificam
  responsabilidade de cada container (o que ele faz), mas nunca nomeiam
  tecnologia (banco de dados, framework, protocolo de mensageria) — a
  elicitação original não define stack, e um diagrama de arquitetura não
  deveria preencher essa lacuna por conta própria.
- **Painel único como simplificação assumida, não decisão de negócio:**
  Organizador, Equipe Financeira e Palestrante usam três conjuntos de
  funcionalidades bem diferentes (RF07/RF09/RF10/RF11, RF12/RF13,
  RF15/RF16). Consolidar isso em um único "Painel Administrativo"
  facilita o diagrama, mas é uma simplificação minha — a elicitação não
  diz se essas interfaces deveriam ser separadas, e isso está registrado
  como tal em `descricao-sistema.md`, não apresentado como fato.
- **Integrações externas marcadas como suposição:** o gateway de
  pagamento e o serviço de notificação aparecem no diagrama porque o
  fluxo de negócio exige que apareçam (RN01/RN03, RF03/RN05), mas a
  elicitação nunca confirma que sejam sistemas separados — podem ser
  processos manuais hoje. Mantê-los "invisíveis" esconderia uma parte real
  do fluxo; tratá-los como confirmados inventaria uma decisão. A saída foi
  documentá-los como suposição explícita nos dois lugares (descrição e
  diagrama).
- **Verificar o artefato gerado, não só o conteúdo:** pedi o diagrama
  estrutural na sintaxe `C4Container` nativa do Mermaid, mais "correta"
  formalmente que um flowchart genérico — e a IA produziu um código
  sintaticamente válido. Só ao renderizar localmente (fora do editor) é
  que apareceram linhas cruzadas e rótulos sobrepostos, causados por uma
  limitação real do layout automático do Mermaid para C4 com múltiplos
  atores usando o mesmo container. Troquei para um flowchart anotado
  (`[Pessoa]`, `[Container]`, `[Sistema Externo]`), que dá controle total
  do posicionamento. O ponto geral: como o comportamento de um modelo de
  GenAI não é determinístico, "sintaticamente correto" não é o mesmo que
  "utilizável" — diagrama se verifica renderizando, não só lendo o código.

## O que a documentação precisaria ter a mais para um agente implementar sem inventar decisões

- Definições de negócio ainda pendentes (prazo de cancelamento, critério
  de reembolso, regra da lista de espera, momento de reserva de vaga) —
  hoje documentadas como lacunas, mas sem resposta.
- Requisitos não funcionais formalmente levantados (segurança, LGPD/dados
  de pagamento, disponibilidade, desempenho sob concorrência).
- Confirmação real de quais integrações externas existem de fato (gateway
  de pagamento, canal de notificação) e seus contratos/APIs.
- Modelo de dados e contratos de API (schemas de eventos, inscrições,
  pagamentos) — esta documentação descreve responsabilidades, não
  interfaces.
- Regras de autorização por papel (quais dados cada perfil pode ver/editar
  no Painel Administrativo).
