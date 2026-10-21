import chromadb
import ollama

from sentence_transformers import SentenceTransformer

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "tn_agriculture_schemes"

embedding_model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(
    COLLECTION_NAME
)


def retrieve_context(question, top_k=5):
    question_embedding = embedding_model.encode(
        [question]
    )[0].tolist()

    results = collection.query(
        query_embeddings=[
            question_embedding
        ],
        n_results=top_k
    )

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    context = []

    sources = []

    for doc, meta in zip(
        documents,
        metadatas
    ):
        context.append(doc)
        sources.append(
            meta.get("source", "")
        )

    return "\n\n".join(context), list(set(sources))


def ask_rag(question):
    context, sources = retrieve_context(
        question
    )

    prompt = f"""
You are a Tamil Nadu agriculture scheme assistant.

Rules:
1. Answer ONLY using the provided context.
2. Do NOT use web search.
3. If the answer is not available in the context, say:
   "The information is not available in the loaded Tamil Nadu scheme data."
4. Respond in the same language as the user's question.
5. Be concise but useful to farmers.

Context:
{context}

Question:
{question}

Answer:
"""

    response = ollama.chat(
        model="qwen2.5:0.5b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "num_gpu": 0
        }
    )

    answer = response[
        "message"
    ]["content"]

    return answer, sources