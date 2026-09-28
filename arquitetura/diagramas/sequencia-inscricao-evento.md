# Diagrama de Sequência — Inscrever-se em Evento

> Visão comportamental de uma jornada crítica, gerada com apoio de GenAI a
> partir do Caso de Uso 1 (`../../especificacao/casos-de-uso.md`).
> Escolhida por concentrar a maior parte das regras de negócio do sistema:
> controle de vagas, lista de espera, conflito de horário e os dois fluxos
> de pagamento (gratuito e pago).

```mermaid
sequenceDiagram
    actor P as Participante
    participant WA as Aplicação Web
    participant API as API de Aplicação
    participant DB as Banco de Dados
    participant GW as Gateway de Pagamento
    actor F as Equipe Financeira

    P->>WA: Seleciona evento para inscrição
    WA->>API: Solicita inscrição (participante, evento)
    API->>DB: Verifica vagas disponíveis (RF08)
    API->>DB: Verifica conflito de horário (RN06)

    alt Conflito de horário
        API-->>WA: Erro: conflito de horário
        WA-->>P: Exibe mensagem de conflito
    else Sem vagas disponíveis
        API->>DB: Registra em lista de espera (RF09/RN05)
        API-->>WA: Inscrição em lista de espera
        WA-->>P: Informa posição na lista de espera
    else Vaga disponível
        alt Evento gratuito
            API->>DB: Confirma inscrição (RN01)
            API-->>WA: Inscrição confirmada
            WA-->>P: Exibe confirmação
            API->>P: Envia comprovante (RF03)
        else Evento pago
            API-->>WA: Redireciona para pagamento
            WA->>GW: Inicia pagamento
            GW-->>F: Notifica pagamento pendente
            F->>GW: Confirma pagamento
            GW->>API: Notifica confirmação de pagamento
            API->>DB: Libera inscrição (RF14/RN03)
            API->>P: Envia comprovante (RF03)
        end
    end
```
