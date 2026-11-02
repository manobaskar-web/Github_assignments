
import re
from pipelines.graph_rag import load_knowledge_graph


GENERAL_RELATIONSHIP_TERMS = (
    "communicate",
    "communication",
    "connect",
    "connected",
    "relationship",
    "relationships",
    "interact",
    "interaction",
    "data flow",
    "how do",
    "architecture",
)


def retrieve_graph_relationships(
    question,
    graph=None,
    max_results=10
):
    """
    Retrieve relationships from the saved
    Spotify architecture Knowledge Graph.

    Supports:
    - Questions mentioning specific graph nodes
    - General architecture relationship questions
    """

    if graph is None:
        graph = load_knowledge_graph()

    if graph.number_of_edges() == 0:
        return []

    question_lower = question.lower().strip()

    matched_nodes = [
        node
        for node in graph.nodes()
        if str(node).lower() in question_lower
    ]

    is_general_question = (
        not matched_nodes
        and any(
            term in question_lower
            for term in GENERAL_RELATIONSHIP_TERMS
        )
    )

    # Do not return every relationship for an
    # arbitrary unrelated question.
    if not matched_nodes and not is_general_question:
        return []

    results = []
    seen = set()

    for source, target, edge_key, data in (
        graph.edges(keys=True, data=True)
    ):

        if matched_nodes and not (
            source in matched_nodes
            or target in matched_nodes
        ):
            continue

        # Ignore invalid self-referencing edges.
        if source == target:
            continue

        # Require source evidence for each edge.
        source_text = str(
            data.get("source_text", "")
        ).strip()

        if not source_text:
            continue

        relationship = str(
            data.get("relationship", "")
        ).strip()

        signature = (
            str(source),
            relationship,
            str(target),
            str(data.get("page", ""))
        )

        if signature in seen:
            continue

        seen.add(signature)

        results.append({
            "subject": str(source),
            "relationship": relationship,
            "object": str(target),
            "page": data.get("page", ""),
            "chunk_id": data.get("chunk_id", ""),
            "source_text": source_text
        })

        if len(results) >= max_results:
            break

    return results
