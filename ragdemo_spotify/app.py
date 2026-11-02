from pipelines.answer_generator import generate_grounded_answer
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
import tempfile
import os

# Import our RAG pipeline functions 

from pipelines.graph_rag import load_knowledge_graph
from pipelines.graph_visualizer import visualize_graph
from pipelines.pdf_processor import split_documents
from pipelines.vector_rag import (
    create_vector_db,
    search_vector_db,
    get_embedding_model,
    VECTOR_DB_PATH,
    COLLECTION_NAME
)

from langchain_chroma import Chroma

# 1. Configure Streamlit page
st.set_page_config(
    page_title="Spotify Architecture RAG Demo",
    page_icon="🎧",
    layout="wide"
)

# 2. Application heading
st.title("🎧 Spotify Architecture RAG Demo")
st.write(
    "Upload your Spotify web architecture PDF "
    "to begin document processing."
)

# 3. PDF upload
uploaded_file = st.file_uploader(
    "Choose your Spotify architecture PDF",
    type=["pdf"]
)

# 4. Process uploaded PDF
if uploaded_file is not None:

    if not uploaded_file.name.lower().endswith(".pdf"):
        st.error("Please upload a PDF file.")
        st.stop()

    st.success(f"Uploaded: {uploaded_file.name}")

    temp_path = None

    try:
        # 5. Save uploaded PDF temporarily
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = temp_file.name

        # 6. Extract PDF using LangChain
        with st.spinner("Extracting PDF text..."):
            loader = PyPDFLoader(temp_path)
            documents = loader.load()

        if not documents:
            st.warning("No pages found in this PDF.")
            st.stop()

        extracted_text = "\n\n".join(
            document.page_content
            for document in documents
        )

        if not extracted_text.strip():
            st.warning(
                "No selectable text found. "
                "The PDF may contain scanned images."
            )
            st.stop()

        # 7. Display extraction results
        st.subheader("PDF Processing Results")

        col1, col2 = st.columns(2)

        col1.metric("Pages extracted", len(documents))
        col2.metric(
            "Characters extracted",
            len(extracted_text)
        )

        st.success("PDF text extraction completed!")

        # 8. Split documents into chunks
        st.subheader("Document Chunking")

        with st.spinner("Splitting PDF into chunks..."):
            chunks = split_documents(documents)

        st.success("Document chunking completed!")

        col1, col2 = st.columns(2)

        col1.metric("Total chunks", len(chunks))
        col2.metric(
            "Chunk size configured",
            "1000 characters"
        )

        # 9. Preview document chunks
        with st.expander("View document chunks"):
            for index, chunk in enumerate(chunks):

                page_number = (
                    chunk.metadata.get("page", 0) + 1
                )

                st.markdown(
                    f"**Chunk {index + 1} | "
                    f"Page {page_number}**"
                )

                st.write(chunk.page_content)

        # 10. Preview extracted text
        st.subheader("Extracted Text Preview")

        st.text_area(
            "First 5,000 characters",
            value=extracted_text[:5000],
            height=300
        )

        # 11. Display individual pages
        with st.expander("View individual pages"):

            for index, document in enumerate(documents):

                page_number = (
                    document.metadata.get("page", index)
                    + 1
                )

                st.markdown(f"**Page {page_number}**")
                st.write(document.page_content[:1500])

        # 12. Build Vector Database
        st.divider()
        st.subheader("Step 5 - Vector RAG")

        st.write(
            "Generate embeddings for the Spotify "
            "architecture document and store "
            "them in ChromaDB."
        )

        if st.button(
            "Build Vector Database",
            type="primary"
        ):

            with st.spinner(
                "Generating embeddings and building ChromaDB..."
            ):

                vector_db = create_vector_db(chunks)

                vector_count = (
                    vector_db._collection.count()
                )

            st.success(
                "Vector Database created successfully!"
            )

            st.metric(
                "Total vectors stored",
                vector_count
            )

            st.info(
                "Vector database saved inside "
                "the vector_db folder."
            )

        # 13. Vector Similarity Search
        st.divider()
        st.subheader("Step 5.3 - Vector Similarity Search")

        st.write(
            "Ask a question to retrieve relevant "
            "information from the Spotify architecture PDF."
        )

        question = st.text_input(
            "Enter your architecture question",
            placeholder="How does Spotify web architecture work?"
        )

        if st.button("Search Vector Database"):

            if not question.strip():
                st.warning("Please enter a question.")

            else:
                with st.spinner("Searching ChromaDB..."):

                    # Reopen the existing stored database
                    vector_db = Chroma(
                        collection_name=COLLECTION_NAME,
                        embedding_function=get_embedding_model(),
                        persist_directory=str(VECTOR_DB_PATH)
                    )

                    if vector_db._collection.count() == 0:
                        st.error(
                            "Vector database is empty. "
                            "Build the database first."
                        )
                        st.stop()

                    results = search_vector_db(
                        vector_db,
                        question,
                        k=3
                    )

                st.success(
                    f"Retrieved {len(results)} document chunks."
                )

                for index, document in enumerate(results):

                    page_number = (
                        document.metadata.get("page", 0) + 1
                    )

                    with st.expander(
                        f"Result {index + 1} - Page {page_number}",
                        expanded=(index == 0)
                    ):
                        st.write(document.page_content)

    except Exception as error:
        st.error(f"PDF processing failed: {error}")

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

else:
    st.info("Upload a PDF to start processing.")

    
# ============================================
# STEP 8.5 - SPOTIFY HYBRID RAG CHATBOT
# ============================================

st.divider()
st.header("Spotify Architecture AI Assistant")

st.caption(
    "Ask questions about the uploaded Spotify "
    "Web Application Architecture document."
)

# Initialize conversation history
if "spotify_chat_history" not in st.session_state:
    st.session_state.spotify_chat_history = []


# Display previous messages
for message in st.session_state.spotify_chat_history:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("pages"):
            st.caption(
                "Retrieved PDF pages: "
                + ", ".join(
                    str(page)
                    for page in message["pages"]
                )
            )


# Chat input
user_question = st.chat_input(
    "Ask about Spotify architecture..."
)

if user_question:

    # Display and save user message
    st.session_state.spotify_chat_history.append({
        "role": "user",
        "content": user_question
    })

    with st.chat_message("user"):
        st.markdown(user_question)

    # Generate the response
    with st.chat_message("assistant"):

        with st.spinner(
            "Analyzing Spotify architecture..."
        ):

            try:
                result = generate_grounded_answer(
                    user_question
                )

                answer = result["answer"]
                pages = result.get("pages", [])

                st.markdown(answer)

                if pages:
                    st.caption(
                        "Retrieved PDF pages: "
                        + ", ".join(
                            str(page)
                            for page in pages
                        )
                    )

            except Exception as error:

                answer = (
                    "Unable to generate an answer. "
                    "Please check the application logs."
                )

                pages = []

                st.error(answer)
                st.exception(error)

    # Save assistant response
    st.session_state.spotify_chat_history.append({
        "role": "assistant",
        "content": answer,
        "pages": pages
    })

