
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents):
    """
    Split PDF pages into smaller overlapping chunks.

    Args:
        documents: List of LangChain PDF documents.

    Returns:
        List of document chunks with page metadata.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    chunks = text_splitter.split_documents(documents)

    return chunks
