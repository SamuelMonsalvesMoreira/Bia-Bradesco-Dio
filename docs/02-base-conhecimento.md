# 2. Base de conhecimento

## Fontes

| Arquivo | Conteúdo | Uso |
|---|---|---|
| `perfil_investidor.json` | Perfil, objetivos e metas fictícias | Contextualizar explicações |
| `transacoes.csv` | Entradas e saídas fictícias | Calcular totais e categorias |
| `historico_atendimento.csv` | Interações anteriores simuladas | Informar o histórico educacional |
| `produtos_financeiros.json` | Características didáticas | Explicar conceitos, riscos e liquidez |

Todos os registros são mockados. A aplicação não acessa conta bancária, CPF, credenciais ou qualquer dado pessoal real.

## Integração

`src/bia_core.py` resolve os caminhos a partir da raiz do projeto, carrega os quatro arquivos e calcula:

- total de entradas;
- total de saídas;
- saldo do período;
- saídas agrupadas por categoria.

Essas contas são determinísticas e não ficam sob responsabilidade do modelo. O LLM recebe um resumo calculado, a lista educacional de produtos, o histórico fictício e as mensagens recentes.

## Dados indisponíveis

Não existem taxas Selic/CDI atuais, preços de ativos ou cotações em tempo real. O system prompt instrui a Bia a declarar essa limitação em vez de inventar valores.

## Evolução

Uma solução de produção poderia usar validação de esquema, controle de acesso, criptografia, busca semântica, versionamento e fontes oficiais atualizadas. Esses itens não são apresentados como funcionalidades concluídas.
