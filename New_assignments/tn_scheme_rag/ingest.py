import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_URL = "https://www.tn.gov.in/scheme_list.php?dep_id=Mg=="

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "tn_agriculture_schemes"

embedding_model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def scrape_page(url):
    print(f"Reading: {url}")

    response = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove scripts/styles
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    text = clean_text(
        soup.get_text(" ", strip=True)
    )

    links = []

    for a in soup.find_all("a", href=True):
        link = urljoin(url, a["href"])

        if "tn.gov.in" in link:
            links.append(link)

    return text, list(set(links))


def store_chunks(text, source):
    chunks = splitter.split_text(text)

    if not chunks:
        return

    embeddings = embedding_model.encode(
        chunks
    ).tolist()

    ids = [
        f"{abs(hash(source))}_{i}"
        for i in range(len(chunks))
    ]

    metadatas = [
        {
            "source": source
        }
        for _ in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(
        f"Stored {len(chunks)} chunks from {source}"
    )


def main():
    main_text, links = scrape_page(BASE_URL)

    store_chunks(
        main_text,
        BASE_URL
    )

    print(
        f"Found {len(links)} internal links"
    )

    for link in links:
        try:
            text, _ = scrape_page(link)

            if len(text) > 200:
                store_chunks(
                    text,
                    link
                )

        except Exception as e:
            print(
                f"Skipped {link}: {e}"
            )

    print("Ingestion completed.")


if __name__ == "__main__":
    main()