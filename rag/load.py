from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.chroma import Chroma

from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_openai.chat_models import ChatOpenAI
from langchain.chains.retrieval_qa.base import RetrievalQA

from dotenv import load_dotenv

load_dotenv()


def load_vectordb():
    paths = [
        "rag/docs/apple_technical_support_guide_en.pdf",
        "rag/docs/guia_de_assistencia_tecnica_apple_pt.pdf"
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

def get_query(query: str):
    vectordb = load_vectordb()

    if 1==0:
        chat = ChatOpenAI(model="gpt-4o-mini")

        chat_chain = RetrievalQA.from_chain_type(
            llm=chat,
            retriever=vectordb.as_retriever(search_type='mmr'),
        )

        response = chat_chain.invoke({"query": query})
        return response["result"]

    if 1==0:
        docs = vectordb.similarity_search(query, k=3)
        for doc in docs:
            print(doc.page_content)
            print(f"========{doc.metadata}\n")
            return docs

    if 1==1: 
        docs = vectordb.max_marginal_relevance_search(query, k=3, fetch_k=10)
        for doc in docs:
            print(doc.page_content)
            print(f"========{doc.metadata}\n")
            return docs
