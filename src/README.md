# Código da aplicação

- `app.py`: interface Streamlit, perguntas sugeridas, histórico e resposta em streaming.
- `bia_core.py`: carregamento dos dados, cálculos, prompt e integração com o Ollama.

A separação mantém a interface simples e permite testar o núcleo com respostas simuladas da API, sem baixar o modelo durante os testes automatizados.
