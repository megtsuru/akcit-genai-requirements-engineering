# Descrição do Sistema — Eventus (Gestão de Eventos)

> Descrição em linguagem natural, no nível de visão de containers (C4),
> escrita a partir da análise de requisitos já realizada em `../analise/`
> (atividade de Engenharia de Requisitos). Serve de base para os diagramas
> em `diagramas/`.

## Escopo

O Eventus é um sistema de gestão de eventos que cobre todo o ciclo de vida
de um evento sob a perspectiva de quatro papéis: **Participante**,
**Organizador**, **Equipe Financeira** e **Palestrante**. O sistema permite
divulgar eventos, controlar inscrições e vagas (incluindo lista de espera),
processar pagamentos e reembolsos de eventos pagos, e emitir certificados
de participação.

Está fora do escopo desta descrição qualquer funcionalidade não citada no
documento de elicitação original (ex.: criação de conteúdo do evento,
emissão de nota fiscal, integração com redes sociais) — a ausência dessas
funcionalidades é deliberada, não uma omissão.

## Nível de visão

Visão de **containers** (C4 model, nível 2): mostra as aplicações/serviços
que compõem o Eventus e como eles se comunicam entre si e com sistemas
externos, sem detalhar componentes internos ou tecnologias de
implementação (não há, na elicitação original, nenhuma decisão de stack
tecnológica).

## Limites e responsabilidades

- **Aplicação Web do Participante** — único ponto de contato do
  Participante com o sistema. Responsável por listar eventos (RF01),
  realizar inscrição (RF02), exibir comprovante (RF03), permitir
  cancelamento (RF04) e emissão de certificado (RF05), e impedir
  inscrição em atividades com conflito de horário (RF06).
- **Painel Administrativo** — usado por três papéis com necessidades
  distintas: Organizador (criação/configuração de eventos — RF07;
  acompanhamento de inscritos em tempo real — RF10, RF11; gestão da lista
  de espera — RF09), Equipe Financeira (confirmação de pagamentos — RF12;
  controle de reembolsos — RF13) e Palestrante (consulta à programação e
  aos participantes de suas atividades — RF15, RF16). Esses três usos
  foram mantidos em um único container porque a elicitação não indica UIs
  separadas nem por quê deveriam ser separadas — é uma simplificação
  assumida, não uma decisão de negócio confirmada.
- **API de Aplicação** — concentra as regras de negócio centrais: controle
  de vagas (RF08), regra de conflito de horário (RN06), liberação de
  inscrição condicionada à confirmação de pagamento (RN03/RF14), regra de
  cancelamento configurável por evento (RN02) e critério de reembolso
  condicional (RN04).
- **Banco de Dados** — armazenamento de eventos, inscrições, participantes
  e registros de pagamento/reembolso.

## Integrações

- **Gateway de Pagamento** (sistema externo) — processa os pagamentos dos
  eventos pagos (RN01, RN03). **Assumido**: a elicitação menciona que a
  Equipe Financeira "confirma pagamentos", mas não afirma que exista um
  gateway de pagamento como sistema separado; pode ser um processo manual
  ou uma ferramenta já usada pela empresa. Tratado aqui como integração
  externa para tornar o fluxo explícito, e marcado como suposição.
- **Serviço de Notificação** (sistema externo) — envio de comprovante de
  inscrição (RF03) e avisos de lista de espera (RN05). **Assumido**: o
  canal de comunicação (e-mail, app, SMS) não foi definido na elicitação
  (ver `../analise/duvidas-e-lacunas.md`, item 5); representado como
  sistema externo genérico até essa decisão ser tomada.

## Restrições e lacunas conhecidas

Herdadas da análise de requisitos (`../analise/duvidas-e-lacunas.md`) e
relevantes para quem for implementar a arquitetura:

- Prazo de cancelamento de inscrição não definido (item 1).
- Critérios objetivos de elegibilidade a reembolso não definidos (item 2).
- Funcionamento da lista de espera (ordenação, notificação, promoção de
  vaga) não definido (item 3).
- Momento de reserva da vaga durante o checkout de pagamento não definido
  (item 6) — afeta diretamente o desenho da API e do banco de dados
  (ex.: necessidade de reserva temporária com expiração).
- Nenhum requisito não funcional foi formalmente levantado com os
  stakeholders (segurança, desempenho, disponibilidade, acessibilidade,
  privacidade) — ver `../analise/requisitos-nao-funcionais.md`. Isso é uma
  lacuna real da elicitação, não apenas desta descrição de arquitetura.
- Não está definido o conjunto de dados de participantes visível aos
  Palestrantes (item 8), o que afeta o desenho de autorização no Painel
  Administrativo.

**Observação:** essas lacunas não foram preenchidas com suposições de
implementação nesta descrição — permanecem como pontos abertos, para que
um agente de desenvolvimento que use este repositório como contexto saiba
que precisa perguntar antes de decidir, em vez de inventar uma resposta.
