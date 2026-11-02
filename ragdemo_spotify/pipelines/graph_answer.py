
from pipelines.graph_rag import load_knowledge_graph
from pipelines.graph_retriever import retrieve_graph_relationships


def generate_graph_answer(question):
    """
    Produce a relationship answer directly from
    the source-verified Knowledge Graph.
    """

    graph = load_knowledge_graph()

    relationships = retrieve_graph_relationships(
        question=question,
        graph=graph,
        max_results=10
    )

    if not relationships:
        return None

    lines = [
        "The document describes the following "
        "relationships between architecture components:"
    ]

    pages = set()

    for index, item in enumerate(
        relationships,
        start=1
    ):
        subject = item["subject"]
        relationship = item["relationship"]
        obj = item["object"]
        page = item.get("page")

        lines.append(
            f"{index}. **{subject}** "
            f"{relationship} **{obj}** "
            f"(PDF page {page})."
        )

        if isinstance(page, int):
            pages.add(page)

    return {
        "answer": "\n\n".join(lines),
        "supported": True,
        "pages": sorted(pages)
    }
