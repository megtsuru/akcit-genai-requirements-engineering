# Engenharia de Requisitos com GenAI — Sistema de Gestão de Eventos (Eventus)

Atividade prática da Unidade III (Análise e Especificação de Requisitos com
Inteligência Artificial Generativa). Cenário: sistema de gestão de eventos
para a empresa fictícia Eventus, a partir de um documento de elicitação
fornecido no material da disciplina.

## Estrutura do repositório

- `analise/` — requisitos funcionais, não funcionais, regras de negócio e
  dúvidas/lacunas identificados a partir do documento de elicitação.
- `especificacao/` — artefatos de especificação escolhidos para representar
  os requisitos do sistema.

## Reflexão sobre o uso da Inteligência Artificial

**Ferramenta de GenAI utilizada:** Claude (Anthropic).

**Como a IA apoiou as diferentes etapas da atividade:**

- Extraiu do documento de elicitação uma primeira versão dos requisitos
  funcionais, regras de negócio e ambiguidades/lacunas (`analise/`), sempre
  indicando a fala do stakeholder que originou cada item.
- Como o documento original não trazia requisitos não funcionais, propôs
  candidatos "a validar" em vez de apresentá-los como definitivos.
- Comparou os artefatos de especificação possíveis (casos de uso, histórias
  de usuário, critérios de aceitação, protótipos) e recomendou uma
  combinação para o cenário Eventus (`analise/escolha-artefatos.md`).
- Redigiu as histórias de usuário, os casos de uso e os critérios de
  aceitação (`especificacao/`), referenciando de volta os requisitos e
  regras de negócio da análise.

**Sugestões aceitas:**

- Combinar histórias de usuário + critérios de aceitação para as
  funcionalidades mais diretas, seguindo o padrão do material (Figura 4).
- Usar casos de uso só nos dois fluxos mais complexos: **Inscrever-se em
  Evento** e **Cancelar Inscrição**.

**Sugestões descartadas ou modificadas:**

- **Modificado:** a IA sugeriu casos de uso para todas as funcionalidades;
  restringi a esses dois fluxos e usei histórias de usuário para o resto,
  evitando documentação excessiva para funcionalidades simples.
- **Descartado:** protótipos de interface — sem ferramenta de design nem
  stakeholders reais para validar, seriam apenas estéticos, sem cumprir a
  função de validação precoce que o material atribui a esse artefato.

**Por que os artefatos escolhidos foram os mais adequados:** o cenário
mistura funcionalidades simples com dois fluxos que concentram quase todas
as regras de negócio e ambiguidades (inscrição e cancelamento). Casos de uso
detalham bem essas variações (grátis x pago, vaga x lista de espera,
conflito de horário, cancelamento condicional); histórias de usuário mantêm
o resto enxuto; e critérios de aceitação tornam as regras verificáveis
objetivamente, servindo de ponte para testes.
