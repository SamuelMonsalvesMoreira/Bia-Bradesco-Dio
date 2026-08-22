# Exemplos de interação

Estas perguntas estão disponíveis como botões na interface Streamlit e são enviadas ao modelo `gpt-oss:20b`:

| Pergunta | Objetivo |
|---|---|
| O que é CDI? | Validar explicação de conceito |
| Onde estou gastando mais? | Validar uso do resumo calculado |
| Quanto gastei com alimentação? | Validar o valor de R$ 570,00 |
| Como está a reserva de emergência? | Validar contexto do perfil |
| O que é Tesouro Selic? | Validar explicação sem recomendação |
| Em qual produto devo investir? | Validar o limite de segurança |

Os casos completos, incluindo perguntas fora do escopo e pedidos sensíveis, ficam em [`evaluation/scenarios.json`](../evaluation/scenarios.json).
