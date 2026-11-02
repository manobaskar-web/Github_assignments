
from pathlib import Path
import networkx as nx

from pipelines.graph_rag import save_knowledge_graph
from langchain_community.document_loaders import PyPDFLoader


BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR / "data" / "spotify_web_app_architecture.pdf"


def extract_source_line(page_text, phrases):
    """Find a line containing one of the supplied phrases."""
    for line in page_text.splitlines():
        clean_line = line.strip()

        if any(
            phrase.lower() in clean_line.lower()
            for phrase in phrases
        ):
            return clean_line

    return None


pages = PyPDFLoader(str(PDF_PATH)).load()

graph = nx.MultiDiGraph()


# Relationships identified from the user's PDF inspection.
# Each record includes a supporting source phrase.
relationships = [
    {
        "subject": "API Gateway / BFF",
        "relationship": "aggregates data from",
        "object": "Underlying Microservices",
        "page": 1,
        "phrases": [
            "Aggregates data from underlying microservices"
        ]
    },
    {
        "subject": "Subscription & Billing Service",
        "relationship": "integrates with",
        "object": "Payment Gateways",
        "page": 2,
        "phrases": [
            "Integrates with payment gateways"
        ]
    },
    {
        "subject": "Media Processor Service",
        "relationship": "notifies",
        "object": "Catalog Service",
        "page": 2,
        "phrases": [
            "notifies Catalog/Streaming services"
        ]
    },
    {
        "subject": "Media Processor Service",
        "relationship": "notifies",
        "object": "Streaming Service",
        "page": 2,
        "phrases": [
            "notifies Catalog/Streaming services"
        ]
    },
    {
        "subject": "Analytics & Events Service",
        "relationship": "feeds listening data to",
        "object": "Recommendation Service",
        "page": 3,
        "phrases": [
            "Feeds Recommendation Service with listening data"
        ]
    }
]


for relation in relationships:

    page_number = relation["page"]

    source_line = extract_source_line(
        pages[page_number - 1].page_content,
        relation["phrases"]
    )

    # Never create an edge without matching PDF evidence.
    if source_line is None:
        print(
            "SKIPPED:",
            relation["subject"],
            "->",
            relation["object"],
            "| Source evidence not found"
        )
        continue

    graph.add_edge(
        relation["subject"],
        relation["object"],
        relationship=relation["relationship"],
        page=page_number,
        chunk_id="source_verified",
        source_text=source_line
    )

    print(
        "ADDED:",
        relation["subject"],
        "--",
        relation["relationship"],
        "-->",
        relation["object"]
    )


if graph.number_of_edges() == 0:
    raise RuntimeError(
        "No source-verified relationships found. "
        "Existing graph will not be replaced."
    )


print("\nGRAPH NODES:", graph.number_of_nodes())
print("GRAPH EDGES:", graph.number_of_edges())

# Only save after checking the constructed graph.
save_knowledge_graph(graph)

print("\nKnowledge Graph saved successfully.")
