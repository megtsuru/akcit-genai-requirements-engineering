# Engenharia de Requisitos com GenAI — Sistema de Gestão de Eventos (Eventus)

Atividade prática de Análise e Especificação de Requisitos com Inteligência
Artificial Generativa. Cenário: sistema de gestão de eventos para a empresa
fictícia Eventus, a partir de um documento de elicitação de requisitos.

## Estrutura do repositório

- `analise/` — requisitos funcionais, não funcionais, regras de negócio e
  dúvidas/lacunas identificados a partir do documento de elicitação.
- `especificacao/` — artefatos de especificação escolhidos para representar
  os requisitos do sistema.

## Reflexão sobre o uso da Inteligência Artificial

**Artefatos de especificação produzidos:**

- Histórias de usuário
- Casos de uso
- Critérios de aceitação

**Por que esses artefatos:**

O projeto mistura funcionalidades simples com dois fluxos que concentram
quase todas as regras de negócio (inscrição no evento e cancelamento da
inscrição). Casos de uso detalham bem essas variações e histórias de
usuário mantêm o resto enxuto. Já os critérios de aceitação tornam
testáveis as regras já definidas; as que ainda dependem de parâmetros
indefinidos, como prazo de cancelamento e critério de reembolso, ficam
registradas como premissas a serem validadas.

**Ferramenta de GenAI utilizada:** Claude Code.

**Como a IA apoiou a atividade:**

Usei o Claude Code para extrair requisitos/regras/ambiguidades do
documento de elicitação, comparar e recomendar os artefatos de
especificação, e redigir os artefatos escolhidos com rastreabilidade com a
análise realizada.

**Sugestões aproveitadas, modificadas ou descartadas:**

- **Aproveitada:** uso combinado de histórias de usuário e critérios de
  aceitação para as funcionalidades mais diretas.
- **Modificada:** inicialmente a IA planejou a geração de casos de uso
  para todas as funcionalidades, mas a decisão final foi manter a
  descrição de casos de uso apenas para os dois fluxos mais complexos
  (**Inscrever-se em Evento** e **Cancelar Inscrição**), por terem
  múltiplas regras de negócio envolvidas e diversos caminhos alternativos;
  os demais fluxos foram descritos como histórias de usuário. Requisitos
  não funcionais inferidos pela IA foram mantidos como pendências a
  validar com os stakeholders.
- **Descartada:** geração de protótipos, por não fazer parte do escopo da
  atividade.
