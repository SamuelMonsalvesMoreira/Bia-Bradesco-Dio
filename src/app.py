"""Interface Streamlit da Bia com IA generativa local."""

import streamlit as st

from bia_core import (
    DEFAULT_MODEL,
    BiaServiceError,
    load_knowledge_base,
    stream_ollama,
)


st.set_page_config(
    page_title="Bia | Educação financeira com IA",
    page_icon="🤖",
    layout="centered",
)


@st.cache_data
def get_knowledge_base():
    """Carrega os dados mockados uma única vez por sessão."""
    return load_knowledge_base()


def render_message(role, content):
    """Exibe valores monetários sem interpretá-los como fórmulas Markdown."""
    if role == "assistant":
        st.markdown(content.replace("$", r"\$"))
    else:
        st.write(content)


knowledge_base = get_knowledge_base()

with st.sidebar:
    st.header("Bia do Futuro")
    st.info(f"Modelo local: {DEFAULT_MODEL}")
    st.write(
        "A aplicação usa o Ollama para executar o modelo localmente. "
        "Na primeira resposta, o carregamento do modelo pode levar mais tempo."
    )
    st.divider()
    st.write(
        "Projeto educacional com dados fictícios. A Bia não recomenda investimentos "
        "nem substitui orientação profissional."
    )

st.title("🤖 Bia")
st.subheader("Educação financeira com IA generativa")
st.caption(
    "Projeto desenvolvido para o desafio BIA do Futuro da DIO. "
    "Não é um canal oficial do Bradesco ou da DIO."
)

example_questions = (
    "O que é CDI?",
    "Onde estou gastando mais?",
    "Quanto gastei com alimentação?",
    "Como está a reserva de emergência?",
    "O que é Tesouro Selic?",
    "Em qual produto devo investir?",
)

selected_question = None
with st.expander("Perguntas para experimentar", expanded=True):
    columns = st.columns(2)
    for index, example in enumerate(example_questions):
        if columns[index % 2].button(
            example,
            key=f"example-{index}",
            use_container_width=True,
        ):
            selected_question = example

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Olá! Sou a Bia. Posso explicar conceitos financeiros usando os dados "
                "fictícios deste projeto. O que você gostaria de aprender?"
            ),
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        render_message(message["role"], message["content"])

typed_question = st.chat_input("Digite uma dúvida sobre finanças pessoais...")
question = typed_question or selected_question

if question:
    previous_messages = st.session_state.messages[-6:]
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        try:
            def escaped_stream():
                for chunk in stream_ollama(
                    question,
                    knowledge_base,
                    conversation=previous_messages,
                ):
                    yield chunk.replace("$", r"\$")

            rendered_answer = st.write_stream(escaped_stream())
            answer = str(rendered_answer).replace(r"\$", "$")
        except BiaServiceError as error:
            answer = str(error)
            st.error(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
