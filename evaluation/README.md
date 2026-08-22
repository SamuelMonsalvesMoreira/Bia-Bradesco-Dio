# Avaliação da Bia

`scenarios.json` reúne as perguntas usadas para avaliar assertividade, segurança e coerência.

Com Ollama e `gpt-oss:20b` em execução:

```powershell
python evaluation/run_evaluation.py
```

O resultado é salvo localmente em `latest-results.json` para revisão humana. O arquivo é ignorado pelo Git para evitar a publicação de saídas não revisadas.
