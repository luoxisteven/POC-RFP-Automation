import os
import re
import json
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, UnstructuredExcelLoader, CSVLoader
from langchain_unstructured import UnstructuredLoader

def find_key_by_value_content(dictionary, search_str):
    for key, value in dictionary.items():
        if search_str in value:
            return key
    return None

def read_files(file_paths):
    content = ""
    for path in file_paths:
        with open(path, 'r', errors='ignore') as file:
            content += file.read() + "\n"
    return content

def load_word_document(file_path):
    loader = UnstructuredWordDocumentLoader(file_path)
    data = loader.load()
    return data

def load_text(file_path):
    loader = TextLoader(file_path)
    data = loader.load()
    return data

def load_pdf(file_path):
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    return docs

def load_excel(file_path):
    loader = UnstructuredExcelLoader(file_path)
    docs = loader.load()
    return docs

def load_csv(file_path):
    loader = CSVLoader(file_path)
    docs = loader.load()
    return docs

def load_unstructure(file_path):
    loader = UnstructuredLoader(file_path)
    docs = loader.load()
    return docs

def get_all_pdfs(directory):
    pdf_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.pdf'):
                pdf_paths.append(os.path.join(root, file))
    return pdf_paths

def get_all_file_paths(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

def load_content_dict(file_path):
    content_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            key, value = line.split(' ', 1)
            content_dict[key] = line
    return content_dict

def load_path_dict(path):
    path_dict = {}
    with open(path, 'r') as file:
        for line in file:
            line = line.strip()
            key, value = line.split(' ', 1)
            path_dict[key] = value
    return path_dict

def load_json(text):
    return json.loads(text)

def split_list(lst, chunk_size=50):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def match_questions(text):
    # This regex pattern matches questions, including those with line breaks (\n)
    pattern = r'([A-Z][^.!?]*?(?:\n[^.!?]*?)*\?)'
    
    # Find all matches in the text
    matches = re.findall(pattern, text, re.MULTILINE)
    
    return matches

def extract_questions_from_response(response):
    questions = []
    lines = response.split("\n")
    for line in lines:
        if line and line[0].isdigit():
            question = re.sub(r'^\d+\.\s*', '', line)
            questions.append(question)
    return questions