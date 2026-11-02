
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader

from pipelines.pdf_processor import split_documents

from pipelines.graph_rag import (
    build_knowledge_graph,
    save_knowledge_graph,
    load_knowledge_graph
)


# 1. Define project and PDF directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# 2. Find the Spotify PDF
pdf_files = sorted(DATA_DIR.glob("*.pdf"))

if not pdf_files:
    raise FileNotFoundError(
        "No PDF found in data folder. "
        "Copy your Spotify architecture PDF into data/."
    )

if len(pdf_files) > 1:
    raise ValueError(
        "Multiple PDFs found in data/. "
        "Keep only the Spotify architecture PDF for this test."
    )

pdf_path = pdf_files[0]

print(f"Loading PDF: {pdf_path.name}", flush=True)

# 3. Load PDF pages
loader = PyPDFLoader(str(pdf_path))
documents = loader.load()

print(f"PDF pages loaded: {len(documents)}", flush=True)

# 4. Split pages into chunks
chunks = split_documents(documents)

print(f"Total chunks: {len(chunks)}", flush=True)

if not chunks:
    raise ValueError("No text chunks were created.")

# 5. Build NetworkX graph using Ollama
print("Starting Knowledge Graph extraction...", flush=True)

graph = build_knowledge_graph(chunks)

print(f"Nodes extracted: {graph.number_of_nodes()}")
print(f"Relationships extracted: {graph.number_of_edges()}")

# 6. Save graph
saved_path = save_knowledge_graph(graph)

print(f"Graph saved: {saved_path}")

# 7. Reload to verify persistence
loaded_graph = load_knowledge_graph()

print(f"Verified nodes: {loaded_graph.number_of_nodes()}")
print(f"Verified relationships: {loaded_graph.number_of_edges()}")

failed_chunks = graph.graph.get("failed_chunks", [])
print(f"Failed chunks: {failed_chunks}")

if loaded_graph.number_of_edges() > 0:
    print("Knowledge Graph saved and loaded successfully!")
else:
    print("WARNING: No relationships extracted. Review the results.")
