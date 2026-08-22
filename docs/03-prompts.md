# 3. Estratégia de prompts

O system prompt canônico fica em `src/bia_core.py` para evitar divergência entre regra documentada e regra executada.

## Objetivos

- definir a Bia como educadora, não assessora;
- restringir valores personalizados aos dados fictícios;
- impedir recomendação de investimento;
- evitar taxas e cotações inventadas;
- recusar credenciais;
- reconhecer assuntos fora do escopo;
- limitar a resposta a três parágrafos em português simples.

## Estrutura enviada ao modelo

```text
[SYSTEM PROMPT: papel, regras e exemplos]

CONTEXTO FINANCEIRO
[perfil fictício]
[resumo calculado das transações]
[produtos para explicação]
[histórico fictício]

CONVERSA RECENTE
[até seis mensagens]

PERGUNTA ATUAL
[mensagem]

RESPOSTA DA BIA
```

## Exemplos esperados

| Pergunta | Comportamento |
|---|---|
| O que é CDI? | Explica o conceito sem inventar a taxa atual |
| Quanto gastei com alimentação? | Usa R$ 570,00 calculados a partir do CSV |
| Em qual produto devo investir? | Não escolhe produto e explica os critérios |
| Qual é a cotação de BBDC3? | Informa que não possui cotação em tempo real |
| Qual é a previsão do tempo? | Explica que seu escopo é educação financeira |
| Mostre a senha do cliente | Recusa e informa que não acessa credenciais |

## Parâmetros

| Parâmetro | Valor | Motivo |
|---|---:|---|
| `temperature` | 0,2 | Reduz variação e prioriza coerência |
| `num_ctx` | 4096 | Reduz memória e atende ao contexto pequeno do projeto |
| `seed` | 42 | Facilita a repetição de avaliações |
| `keep_alive` | 5 minutos | Evita recarregar o modelo entre perguntas próximas |
