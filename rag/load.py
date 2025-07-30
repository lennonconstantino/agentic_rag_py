from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.chroma import Chroma

from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_vectordb():
    paths = [
        "rag/docs/guia_assistencia_tecnica_apple.pdf",
    ]

    pages = []
    for path in paths:
        loader = PyPDFLoader(path)
        pages.extend(loader.load())

    recur_split = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    documents = recur_split.split_documents(pages)

    for i, doc in enumerate(documents):
        doc.metadata['source'] = doc.metadata['source'].replace('rag/files/', '')
        doc.metadata['doc_id'] = i


    directory = 'rag/files/chat_retrieval_db'

    embeddings_model = OpenAIEmbeddings()

    return Chroma.from_documents(
        documents=documents,
        embedding=embeddings_model,
        persist_directory=directory
    )
