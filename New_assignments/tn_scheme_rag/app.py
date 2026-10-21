import streamlit as st
from Github_assignments.New_assignments.tn_scheme_rag.rag import ask_rag

st.set_page_config(
    page_title="Tamil Nadu Agriculture Scheme Assistant",
    page_icon="🌾",
    layout="wide"
)

st.title(
    "🌾 Tamil Nadu Agriculture Scheme RAG Assistant"
)

st.caption(
    "Answers are generated only from the loaded Tamil Nadu Government scheme data."
)

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(
        message["role"]
    ):
        st.markdown(
            message["content"]
        )


question = st.chat_input(
    "Ask about Tamil Nadu agriculture schemes..."
)


if question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner(
            "Searching scheme knowledge base..."
        ):

            answer, sources = ask_rag(
                question
            )

            st.markdown(answer)

            if sources:
                st.markdown(
                    "### Sources"
                )

                for source in sources:
                    st.write(source)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )