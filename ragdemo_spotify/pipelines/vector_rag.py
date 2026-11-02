
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_DB_PATH = BASE_DIR / "vector_db"

COLLECTION_NAME = "spotify_architecture"


def get_embedding_model():
    """Create the local embedding model."""

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )


def create_vector_db(chunks):
    """Create the ChromaDB vector database."""

    if not chunks:
        raise ValueError("No document chunks found.")

    VECTOR_DB_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    embeddings = get_embedding_model()

    vector_db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(VECTOR_DB_PATH)
    )

    # Remove previously indexed chunks
    # before rebuilding this single-document demo.
    existing_ids = vector_db.get(include=[])["ids"]

    if existing_ids:
        vector_db.delete(ids=existing_ids)

    # Store PDF chunks and their embeddings
    vector_db.add_documents(chunks)

    return vector_db


def search_vector_db(vector_db, question, k=3):
    """Retrieve the most relevant PDF chunks."""

    return vector_db.similarity_search(
        question,
        k=k
    )
