# Diagrama de Containers — Eventus

> Visão estrutural (nível C2 — Container, no C4 model), gerada com apoio de
> GenAI a partir de `../descricao-sistema.md`. Mostra as aplicações/serviços
> que compõem o Eventus, os quatro papéis que os utilizam e as integrações
> externas envolvidas.
>
> **Nota sobre a sintaxe:** o Mermaid tem um tipo de diagrama `C4Container`
> nativo, mas seu layout automático não separa bem relações N:1 (três
> papéis usando o mesmo Painel) nem integrações externas conectadas a um
> container interno — gerando linhas e rótulos sobrepostos. Por isso o
> diagrama abaixo usa `graph` (flowchart) com anotações de estilo C4
> (`[Pessoa]`, `[Container: ...]`, `[Sistema Externo]`), o que permite
> controlar o layout e manter o diagrama legível.

```mermaid
graph TB
    participante(("Participante<br/>[Pessoa]"))
    organizador(("Organizador<br/>[Pessoa]"))
    financeiro(("Equipe Financeira<br/>[Pessoa]"))
    palestrante(("Palestrante<br/>[Pessoa]"))

    subgraph eventus["Sistema Eventus"]
        webapp["Aplicação Web do Participante<br/>[Container: Web App]<br/>Catálogo de eventos, inscrição,<br/>cancelamento, certificado"]
        painel["Painel Administrativo<br/>[Container: Web App]<br/>Gestão de eventos, inscritos,<br/>pagamentos, programação"]
        api["API de Aplicação<br/>[Container: Backend]<br/>Vagas, lista de espera, conflito<br/>de horário, liberação de inscrição"]
        db[("Banco de Dados<br/>[Container: Database]<br/>Eventos, inscrições, participantes,<br/>pagamentos")]
    end

    gateway["Gateway de Pagamento<br/>[Sistema Externo]<br/>(integração assumida — não<br/>confirmada na elicitação)"]
    notificacao["Serviço de Notificação<br/>[Sistema Externo]<br/>Envio de comprovantes e avisos<br/>(canal não definido — lacuna)"]

    participante -->|"navega, inscreve-se, cancela,<br/>emite certificado"| webapp
    organizador -->|"cria/configura eventos,<br/>acompanha inscritos"| painel
    financeiro -->|"confirma pagamentos,<br/>processa reembolsos"| painel
    palestrante -->|"consulta programação<br/>e participantes"| painel

    webapp -->|"HTTPS/API"| api
    painel -->|"HTTPS/API"| api
    api -->|"lê e grava"| db
    api -->|"solicita/confirma pagamento"| gateway
    api -->|"envia comprovantes/avisos"| notificacao
```
