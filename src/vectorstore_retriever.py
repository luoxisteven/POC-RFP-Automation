# from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.storage import InMemoryStore
from langchain.chains import create_history_aware_retriever
from langchain.retrievers import ParentDocumentRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.document_transformers import LongContextReorder
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
# from langchain_community.embeddings import OllamaEmbeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.multi_vector import MultiVectorRetriever
from src.prompt_and_chain import contextualize_q_prompt

# https://python.langchain.com/v0.1/docs/get_started/introduction
# def chroma_vectorstore(documents):
#     vectorstore_db = Chroma.from_documents(documents=documents, embedding=OpenAIEmbeddings())
#     return vectorstore_db

def faiss_vectorstore(documents):
    vectorstore_db = FAISS.from_documents(documents=documents, embedding=OpenAIEmbeddings())
    return vectorstore_db

# Llama embeddings
# def chroma_vectorstore(documents):
#     vectorstore_db = Chroma.from_documents(documents=documents, embedding=OllamaEmbeddings())
#     return vectorstore_db
#
# def faiss_vectorstore(documents):
#     vectorstore_db = FAISS.from_documents(documents=documents, embedding=OllamaEmbeddings())
#     return vectorstore_db


# Top K retrieval
def top_k_retriever(vectorstore_db, k=5):
    retriever = vectorstore_db.as_retriever(k=k)
    return retriever

# Generate Multiple Queries based on the question, and to retrieve documents
def multiquery_retriever(vectorstore_db, llm_model):
    retriever = MultiQueryRetriever.from_llm(
        retriever=vectorstore_db.as_retriever(), llm=llm_model
    )
    return retriever

# Using LLM model to compress the documents first, and then to retrieve documents based on the compressed ones
def contextualcompression_retriever(retriever, llm_model):
    compressor = LLMChainExtractor.from_llm(llm_model)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=retriever
    )
    return compression_retriever

# BM25
# def bm25_retriever(docs, k=5):
#     bm25_retriever = BM25Retriever(docs=docs, k=k)
#     return bm25_retriever

# BM25 cannot receive an empty docs list, Be careful
def bm25_retriever(docs, k):
    docs.append(Document(page_content="."))
    bm25_retriever = BM25Retriever.from_documents(documents=docs, k=k)
    return bm25_retriever

# Ensemble Retriever 1 with bm25 and base retriever with contextual compression
# BM25 cannot receive an empty docs list, be careful
def ensemble_retriever_1(base_retriever, docs, llm_model, k=5):
    docs.append(Document(page_content="."))
    compressor = LLMChainExtractor.from_llm(llm_model)
    bm25_retriever = BM25Retriever.from_documents(documents=docs, k=k)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=base_retriever
    )
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, compression_retriever], weights=[0.5, 0.5]
    )
    return ensemble_retriever

# Ensemble Retriever 2 with bm25 and base retriever
# BM25 cannot receive an empty docs list, be careful
def ensemble_retriever_2(base_retriever, docs, k=5):
    docs.append(Document(page_content="."))
    bm25_retriever = BM25Retriever.from_documents(documents=docs, k=k)
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, base_retriever], weights=[0.5, 0.5]
    )
    return ensemble_retriever

# Reordering docs to avoid the negative effects of long context
def reordering_docs(docs):
    reordering = LongContextReorder()
    reordered_docs = reordering.transform_documents(docs)
    return reordered_docs

# MultiVector_retriever
def multiVector_retriever(vectorstore_db):
    retriever = MultiVectorRetriever(vectorstore=vectorstore_db)
    return retriever

# # ParentDocument_retriever
# def parentDocument_retriever(data):
#     parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
#     child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
#     vectorstore = Chroma(
#         collection_name="full_documents", embedding_function=OpenAIEmbeddings()
#     )
#     store = InMemoryStore()
#     retriever = ParentDocumentRetriever(
#         vectorstore=vectorstore,
#         docstore=store,
#         child_splitter=child_splitter,
#         parent_splitter=parent_splitter,
#     )
#     retriever.add_documents(data)
#     return retriever

def historical_messages_retriever(model, base_retriever):
    history_aware_retriever = create_history_aware_retriever(
        model, base_retriever, contextualize_q_prompt
    )
    return history_aware_retriever