
import json
import os
import re
from pathlib import Path

import networkx as nx

from langchain_ollama import ChatOllama
from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)


# =====================================================
# 1. PROJECT CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

GRAPH_DB_PATH = BASE_DIR / "graph_db"

GRAPH_FILE = GRAPH_DB_PATH / "spotify_graph.json"

MODEL_NAME = "qwen2.5:0.5b"


# =====================================================
# 2. INITIALIZE OLLAMA MODEL
# =====================================================

def get_graph_llm():
    """
     Initialize Ollama for Knowledge Graph processing.

    Windows: http://localhost:11434
    Docker:  http://ollama:11434
    """

    return ChatOllama(
        model=MODEL_NAME,
        base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        num_ctx=512,
        num_predict=160,
        num_gpu=0,
        num_thread=2,
        timeout=120
    )


# =====================================================
# 3. EXTRACT ARCHITECTURE RELATIONSHIPS
# =====================================================

def extract_relationships(chunk):
    """
    Extract factual subject-relationship-object
    triples from one PDF document chunk.

    Returns a list of dictionaries.
    """

    llm = get_graph_llm()

    system_prompt = """
Extract relationships explicitly stated in the text.

Return ONLY a JSON array:

[
  {
    "subject": "entity",
    "relationship": "action or connection",
    "object": "entity"
  }
]

Rules:
- Use only supplied text.
- Do not invent entities or relationships.
- Return [] if none are explicitly stated.
- No explanations or Markdown.
"""

    # Limit input to reduce memory usage.
    text = chunk.page_content[:850]

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=text)
    ]

    response = llm.invoke(messages)

    raw_output = response.content

    if not isinstance(raw_output, str):
        return []

    raw_output = raw_output.strip()

    # Remove optional Markdown code fences.
    raw_output = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        raw_output
    ).strip()

    # Try to isolate a JSON array.
    start = raw_output.find("[")
    end = raw_output.rfind("]")

    if start == -1 or end == -1 or end < start:
        print(
            "WARNING: Model did not return a JSON array.",
            flush=True
        )
        return []

    raw_output = raw_output[start:end + 1]

    try:
        relationships = json.loads(raw_output)

    except json.JSONDecodeError:
        print(
            "WARNING: Invalid JSON from Ollama.",
            flush=True
        )
        return []

    if not isinstance(relationships, list):
        return []

    valid_relationships = []

    for item in relationships:

        if not isinstance(item, dict):
            continue

        subject = item.get("subject")
        relationship = item.get("relationship")
        obj = item.get("object")

        values = (subject, relationship, obj)

        if not all(
            isinstance(value, str) and value.strip()
            for value in values
        ):
            continue

        valid_relationships.append({
            "subject": subject.strip(),
            "relationship": relationship.strip(),
            "object": obj.strip()
        })

    return valid_relationships


# =====================================================
# 4. BUILD THE NETWORKX KNOWLEDGE GRAPH
# =====================================================

def build_knowledge_graph(chunks):
    """
    Process PDF chunks sequentially and construct
    a directed Knowledge Graph.

    Each edge retains its source page,
    chunk ID, and supporting source text.
    """

    graph = nx.MultiDiGraph()

    total_chunks = len(chunks)

    print(
        f"Starting Graph RAG extraction: {total_chunks} chunks",
        flush=True
    )

    for index, chunk in enumerate(chunks, start=1):

        page_number = (
            chunk.metadata.get("page", 0) + 1
        )

        print(
            f"Processing chunk {index}/{total_chunks} "
            f"- Page {page_number}",
            flush=True
        )

        try:
            relationships = extract_relationships(chunk)

        except Exception as error:

            print(
                f"ERROR in chunk {index}: {error}",
                flush=True
            )

            graph.graph.setdefault(
                "failed_chunks", []
            ).append(index)

            continue

        for item in relationships:

            subject = item["subject"]
            relationship = item["relationship"]
            obj = item["object"]

            # Add architecture components as nodes.
            graph.add_node(subject)
            graph.add_node(obj)

            # Add directional relationships.
            graph.add_edge(
                subject,
                obj,
                relationship=relationship,
                page=page_number,
                chunk_id=index,
                source_text=chunk.page_content[:850]
            )

        print(
            f"Relationships extracted: {len(relationships)}",
            flush=True
        )

    print(
        f"Graph completed: "
        f"{graph.number_of_nodes()} nodes, "
        f"{graph.number_of_edges()} relationships",
        flush=True
    )

    return graph


# =====================================================
# 5. SAVE KNOWLEDGE GRAPH
# =====================================================

def save_knowledge_graph(graph):
    """
    Save the NetworkX Knowledge Graph to JSON.
    """

    GRAPH_DB_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    graph_data = nx.node_link_data(
        graph,
        edges="links"
    )

    with open(
        GRAPH_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            graph_data,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Knowledge Graph saved to: {GRAPH_FILE}",
        flush=True
    )

    return GRAPH_FILE


# =====================================================
# 6. LOAD KNOWLEDGE GRAPH
# =====================================================

def load_knowledge_graph():
    """
    Load the previously saved Knowledge Graph.
    """

    if not GRAPH_FILE.exists():
        raise FileNotFoundError(
            "Knowledge Graph not found. "
            "Run build_graph.py first."
        )

    with open(
        GRAPH_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        graph_data = json.load(file)

    graph = nx.node_link_graph(
        graph_data,
        edges="links"
    )

    return graph
