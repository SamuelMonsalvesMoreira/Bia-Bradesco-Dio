# 5. Roteiro de pitch — 3 minutos

## 0:00–0:30 | Problema

“Planilhas mostram números, mas nem sempre ajudam uma pessoa iniciante a entender seus gastos ou termos financeiros. O desafio foi transformar dados em explicações claras sem ultrapassar o limite entre educação e recomendação.”

## 0:30–1:20 | Solução

“A Bia é uma educadora financeira com IA generativa local. A aplicação lê quatro fontes de dados fictícios, calcula o resumo financeiro em Python e monta um contexto protegido. O `gpt-oss:20b`, executado pelo Ollama, produz a resposta exibida em streaming no Streamlit.”

“O prompt impede recomendações específicas, cotações inventadas e pedidos de credenciais. Quando a pergunta exige análise individual, a Bia explica os critérios e orienta a procura de um profissional certificado.”

## 1:20–2:20 | Demonstração

1. Pergunte: “Quanto gastei com alimentação?”
2. Mostre os R$ 570,00 calculados a partir do CSV.
3. Pergunte: “Em qual produto devo investir?”
4. Mostre que a Bia não escolhe um investimento.

Se o hardware usado na apresentação não executar o modelo com boa velocidade, grave previamente essas duas interações na máquina compatível e use o vídeo como evidência.

## 2:20–3:00 | Engenharia

“Separei a interface do núcleo, calculei os valores fora do LLM e limitei o contexto para reduzir memória. Também implementei streaming, histórico recente, tratamento de erros, testes automatizados e oito cenários de avaliação.”

“O projeto demonstra integração com LLM local, engenharia de prompt, dados estruturados, segurança e uma estratégia honesta de avaliação.”

## Checklist

- Ollama e modelo carregados antes da gravação
- Duas perguntas ensaiadas
- Fonte e zoom legíveis
- Duração abaixo de três minutos
- Nenhuma informação pessoal visível
- Áudio e respostas revisados
