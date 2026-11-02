from pipelines.evidence_relevance import check_passage_relevance
from langchain_core.prompts import ChatPromptTemplate
from pipelines.llm_decision import get_decision_llm


def check_passage_relevance(question, passage):
    """
    Decide whether a PDF passage contains
    information useful for answering a question.
    """

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You check relevance of document evidence.

Answer only YES or NO.

YES: The passage explicitly contains facts
that could help answer the question.

NO: The passage does not contain useful facts
for answering the question.

Do not use outside knowledge.
Do not assume facts missing from the passage."""
        ),
        (
            "human",
            "Question:\n{question}\n\n"
            "Passage:\n{passage}\n\n"
            "Is this passage relevant?"
        )
    ])

    chain = prompt | get_decision_llm()

    response = chain.invoke({
        "question": question,
        "passage": passage[:1200]
     })

    answer = str(response.content).strip().upper()

    # Accept only an unambiguous YES response.
    return answer in {"YES", "YES."}

from langchain_chroma import Chroma

from pipelines.vector_rag import (
    get_embedding_model,
    VECTOR_DB_PATH,
    COLLECTION_NAME
)

from pipelines.graph_rag import load_knowledge_graph
from pipelines.graph_retriever import retrieve_graph_relationships


# Experimental distance threshold.
# Must be calibrated against real PDF questions.
MAX_VECTOR_DISTANCE = 0.45


def validate_evidence(question, decision, k=4):
    """
    Retrieve and screen evidence from the Spotify
    architecture Vector DB and Knowledge Graph.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if decision.get("scope") == "unrelated":
        return {
            "supported": False,
            "reason": "Question classified as unrelated.",
            "vector_evidence": [],
            "graph_evidence": [],
            "best_distance": None
        }

    # 1. Load existing ChromaDB
    vector_db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        persist_directory=str(VECTOR_DB_PATH)
    )

    if vector_db._collection.count() == 0:
        raise ValueError("Vector database is empty.")

    # 2. Retrieve passages with distance scores
    scored_results = vector_db.similarity_search_with_score(
        question,
        k=k
    )

    vector_evidence = []

   
    for document, distance in scored_results:

        passage = document.page_content

        # Let the LLM inspect the retrieved passage.
        is_relevant = check_passage_relevance(
            question=question,
            passage=passage
        )

        if is_relevant:
            vector_evidence.append({
                "text": passage,
                "page": document.metadata.get("page", 0) + 1,
                "distance": float(distance)
            })


    # 3. Retrieve graph relationships
    graph = load_knowledge_graph()

    graph_results = retrieve_graph_relationships(
        question=question,
        graph=graph,
        max_results=10
    )

    
    # Graph edges were rebuilt with PDF source verification.
    # Preserve their recorded evidence and page numbers.
    graph_evidence = []

    for item in graph_results:
        subject = str(item.get("subject", "")).strip()
        obj = str(item.get("object", "")).strip()
        relationship = str(
            item.get("relationship", "")
        ).strip()
        source_text = str(
            item.get("source_text", "")
        ).strip()

        # Reject self-references and incomplete edges.
        if not all([
            subject,
            obj,
            relationship,
            source_text
        ]):
            continue

        if subject.lower() == obj.lower():
            continue

        graph_evidence.append(item)

    # 4. Check whether usable vector evidence exists
    supported = bool(vector_evidence)

    return {
        "supported": supported,
        "reason": (
            "Relevant PDF passages retrieved."
            if supported
            else "Insufficient relevant PDF evidence."
        ),
        "vector_evidence": vector_evidence,
        "graph_evidence": graph_evidence,
        "best_distance": (
            min(
                item["distance"]
                for item in vector_evidence
            )
            if vector_evidence else None
        )
    }
