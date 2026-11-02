
from langchain_chroma import Chroma

from pipelines.vector_rag import (
    get_embedding_model,
    VECTOR_DB_PATH,
    COLLECTION_NAME,
    search_vector_db
)

from pipelines.graph_rag import load_knowledge_graph

from pipelines.graph_retriever import (
    retrieve_graph_relationships
)


def retrieve_hybrid_context(question, k=3):
    """
    Retrieve Spotify architecture evidence from
    both Vector RAG and Knowledge Graph RAG.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    # 1. Open ChromaDB
    vector_db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        persist_directory=str(VECTOR_DB_PATH)
    )

    if vector_db._collection.count() == 0:
        raise ValueError("Vector database is empty.")

    # 2. Vector retrieval
    vector_documents = search_vector_db(
        vector_db,
        question,
        k=k
    )

    vector_results = [
        {
            "text": doc.page_content,
            "page": doc.metadata.get("page", 0) + 1
        }
        for doc in vector_documents
    ]

    # 3. Knowledge Graph retrieval
    graph = load_knowledge_graph()

    graph_results = retrieve_graph_relationships(
        question=question,
        graph=graph,
        max_results=10
    )

    # 4. Return combined evidence
    return {
        "question": question,
        "vector_results": vector_results,
        "graph_results": graph_results,
        "vector_count": len(vector_results),
        "graph_count": len(graph_results)
    }
