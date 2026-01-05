# Base de Conhecimento

Este documento descreve a estrutura e organização da base de conhecimento utilizada pela Bia, nossa consultora financeira educativa.

## Dados Utilizados

| Arquivo | Formato | Para que serve na Bia? |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores e identificar quando o cliente já foi orientado sobre produtos específicos, evitando repetições e garantindo continuidade educativa. |
| `perfil_investidor.json` | JSON | Personalizar as explicações educativas e identificar quando o perfil do cliente requer orientação de assessor profissional para decisões de investimento. |
| `produtos_financeiros.json` | JSON | Explicar didaticamente os tipos de produtos financeiros disponíveis, suas características e quando cada um é mais adequado, sem fazer recomendações específicas. |
| `transacoes.csv` | CSV | Analisar padrão de gastos do cliente para contextualizar explicações sobre organização financeira e usar exemplos práticos baseados no comportamento real. |
| `taxas_referencia.json` | JSON | Fornecer informações atualizadas sobre Selic e CDI para explicar rentabilidades de forma precisa e contextualizada com dados reais do mercado. |

---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

A Bia utiliza essas informações para identificar situações que requerem encaminhamento profissional. Por exemplo, se o perfil mostra objetivos complexos ou valores altos para investimento, ela reconhece a necessidade de assessoria especializada.

> Adição de Taxas de Referência.

Foi incluído o arquivo taxas_referencia.json com dados atuais da Selic (15,0%) e CDI (14,95%), permitindo que a Bia forneça informações precisas sobre rentabilidades e faça cálculos educativos mais realistas.

---

## Estratégia de Integração

### Como os dados são carregados?
> Descreva como seu agente acessa a base de conhecimento.

Existem duas possibilidades: injetar os dados diretamente no prompt (Ctrl + C, Ctrl + V) ou carregar os arquivos via código, como no exemplo abaixo:

```python
import pandas as pd
import json

# Carregamento dos arquivos
perfil = json.load(open('./data/perfil_investidor.json'))
transacoes = pd.read_csv('./data/transacoes.csv')
historico = pd.read_csv('./data/historico_atendimento.csv')
produtos = json.load(open('./data/produtos_financeiros.json'))
taxas = json.load(open('./data/taxas_referencia.json'))
```

### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?

Para simplificar, os dados são "injetados" diretamente no prompt, garantindo que a Bia tenha o melhor contexto possível para educar e identificar quando encaminhar para assessoria profissional.
> 💡 Nota: Em soluções mais robustas, o ideal é que essas informações sejam carregadas dinamicamente para ganhar flexibilidade.

```text
DADOS DO CLIENTE E PERFIL (data/perfil_investidor.json):
{
  {
  "nome": "João Silva",
  "idade": 32,
  "profissao": "Analista de Sistemas",
  "renda_mensal": 5000.00,
  "perfil_investidor": "moderado",
  "objetivo_principal": "Construir reserva de emergência",
  "patrimonio_total": 15000.00,
  "reserva_emergencia_atual": 10000.00,
  "aceita_risco": false,
 }
  "metas": [
    {
      "meta": "Completar reserva de emergência",
      "valor_necessario": 15000.00,
      "prazo": "2026-06"
    },
    {
      "meta": "Entrada do apartamento",
      "valor_necessario": 50000.00,
      "prazo": "2027-12"
    }
  ]
}


Taxas de Referência ('./data/taxas_referencia.json'):

{
  "selic": {
    "valor": 15.0,
    "data_referencia": "2025-12-30",
    "fonte": "Banco Central do Brasil"
  },
  "cdi": {
    "valor": 14.95,
    "data_referencia": "2025-12-30",
    "fonte": "CETIP / B3"
  }
}

TRANSACOES DO CLIENTE (data/transacoes.csv):
data,descricao,categoria,valor,tipo
2025-10-01,Salário,receita,5000.00,entrada
2025-10-02,Aluguel,moradia,1200.00,saida
2025-10-03,Supermercado,alimentacao,450.00,saida
2025-10-05,Netflix,lazer,55.90,saida
2025-10-07,Farmácia,saude,89.00,saida
2025-10-10,Restaurante,alimentacao,120.00,saida
2025-10-12,Uber,transporte,45.00,saida
2025-10-15,Conta de Luz,moradia,180.00,saida
2025-10-20,Academia,saude,99.00,saida
2025-10-25,Combustível,transporte,250.00,saida

HISTORICO DE ATENDIMENTO DO CLIENTE (data/historico_atendimento.csv):
data,canal,tema,resumo,resolvido
2025-09-15,chat,CDB,Cliente perguntou sobre rentabilidade e prazos,sim
2025-09-22,telefone,Problema no app,Erro ao visualizar extrato foi corrigido,sim
2025-10-01,chat,Tesouro Selic,Cliente pediu explicação sobre o funcionamento do Tesouro Direto,sim
2025-10-12,chat,Metas financeiras,Cliente acompanhou o progresso da reserva de emergência,sim
2025-10-25,email,Atualização cadastral,Cliente atualizou e-mail e telefone,sim

PRODUTOS DISPONIVEIS PARA ENSINO (data/produtos_financeiros.json):
[
  {
    "nome": "Tesouro Selic",
    "categoria": "renda_fixa",
    "risco": "baixo",
    "rentabilidade": "100% da Selic",
    "aporte_minimo": 30.00,
    "indicado_para": "Reserva de emergência e iniciantes"
  },
  {
    "nome": "CDB Liquidez Diária",
    "categoria": "renda_fixa",
    "risco": "baixo",
    "rentabilidade": "102% do CDI",
    "aporte_minimo": 100.00,
    "indicado_para": "Quem busca segurança com rendimento diário"
  },
  {
    "nome": "LCI/LCA",
    "categoria": "renda_fixa",
    "risco": "baixo",
    "rentabilidade": "95% do CDI",
    "aporte_minimo": 1000.00,
    "indicado_para": "Quem pode esperar 90 dias (isento de IR)"
  },
  {
    "nome": "Fundo Imobiliário (FII)",
    "categoria": "fundo",
    "risco": "medio",
    "rentabilidade": "Dividend Yield (DY) costuma ficar entre 6% a 12% ao ano",
    "aporte_minimo": 100.00,
    "indicado_para": "Perfil moderado que busca diversificação e renda recorrente mensal"
  },
  {
    "nome": "Fundo de Ações",
    "categoria": "fundo",
    "risco": "alto",
    "rentabilidade": "Variável",
    "aporte_minimo": 100.00,
    "indicado_para": "Perfil arrojado com foco no longo prazo"
  },
  {
    "nome": "Tesouro Selic",
    "categoria": "renda_fixa",
    "risco": "baixo",
    "rentabilidade": "100% da Selic",
    "aporte_minimo": 30.00,
    "indicado_para": "Reserva de emergência e iniciantes"
  }
]
```

---

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

O exemplo de contexto montado abaixo se baseia nos dados originais da base de conhecimento, mas os sintetiza deixando apenas as informações mais relevantes para a Bia cumprir seu papel educativo e de triagem para assessoria profissional, otimizando assim o consumo de tokens.

```
DADOS DO CLIENTE:
- Nome: João Silva
- Perfil: Moderado
- Objetivo: Construir reserva de emergência
- Reserva atual: R\$ 10.000 (meta: R\$ 15.000)
- Meta futura: Entrada apartamento R\$ 50.000 (2027)

RESUMO DE GASTOS:
- Moradia: R\$ 1.380
- Alimentação: R\$ 570
- Transporte: R\$ 295
- Saúde: R\$ 188
- Lazer: R\$ 55,90
- Total de saídas: R\$ 2.488,90

TAXAS DE REFERÊNCIA ATUAIS (30/12/2025):
- Selic: 15,0% ao ano
- CDI: 14,95% ao ano

PRODUTOS DISPONÍVEIS PARA EXPLICAR:
- Tesouro Selic (100% da Selic = ~15% a.a.) - para reserva de emergência
- CDB Liquidez Diária (102% do CDI = ~15,25% a.a.) - segurança com liquidez
- LCI/LCA (95% do CDI = ~14,20% a.a.) - isento de IR, prazo 90 dias
- Fundo Imobiliário - FII (DY 6-12% a.a.) - renda mensal
- Fundo de Ações (variável) - longo prazo

CRITÉRIOS PARA ENCAMINHAMENTO:
- Solicitação de recomendação específica de onde investir
- Valores altos para investimento (>R\$ 10.000)
- Objetivos complexos de longo prazo
- Dúvidas sobre montagem de carteira
- Planejamento tributário avançado

🚀 Próximos Passos
 Implementar carregamento dinâmico dos dados
 Adicionar validação de integridade dos arquivos
 Criar sistema de cache para otimizar performance
 Implementar versionamento da base de conhecimento


📝 Nota: Esta base de conhecimento é projetada para fins educativos e de demonstração. Em ambiente de produção, considere implementar sistemas mais robustos de gerenciamento de dados.

```

