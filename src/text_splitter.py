from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import CharacterTextSplitter
# from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.schema import Document


def character_text_splitter(data, chunk_size=2000, chunk_overlap=300):
    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    all_splits = text_splitter.split_documents(data)
    return all_splits


def recursive_character_splitter(data, chunk_size=2000, chunk_overlap=300):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    all_splits = text_splitter.split_documents(data)
    return all_splits


# def semantic_splitter(data):
#     text_splitter = SemanticChunker(OpenAIEmbeddings())
#     all_splits = text_splitter.split_documents(data)
#     return all_splits


def split_document_by_newline(data):
    formatted_documents = []

    for doc in data:
        lines = doc.page_content.split('\n')

        for line in lines:
            new_doc = Document(metadata=doc.metadata, page_content=line)
            formatted_documents.append(new_doc)

    return formatted_documents
