import re
from langchain.schema import Document
from config import *
from src.prompt_and_chain import *
from src.utils import *
from src.model_initializer import llm_model, chat_gpt
from src.text_splitter import recursive_character_splitter
from src.vectorstore_retriever import chroma_vectorstore, top_k_retriever, \
    historical_messages_retriever, ensemble_retriever_1

class RAG_Chain:
    def __init__(self, model="gpt-4o-mini", verbose=False):
        self.model = llm_model(model)
        self.json_model = self.model.bind(response_format={"type": "json_object"})
        self.rfp_docs = load_data(rfp_path)
        self.company_docs = load_data(company_profile_path)
        self.rfp_general_context = None
        self.company_general_context = None
        self.verbose = verbose
        
    def get_answer_without_memory(self, query):
        answer = self.query_answering(query)
        return answer


    # Question Extraction
    def question_extraction(self):
        questions = []
        questions_with_qm = self.retrieve_question_with_question_mark()
        questions_without_qm = self.retrieve_question_without_question_mark()
        questions.extend(questions_with_qm)
        questions.extend(questions_without_qm)
        doc_questions = self.check_duplicate_questions(questions)

        return doc_questions


    def retrieve_question_with_question_mark(self):
        if self.verbose:
            print("\nExtracting question with question mark..")
        questions = []
        qe_chain_1 = create_chain(self.model, question_extraction_prompt_1)
        for doc in self.rfp_docs:
            response = qe_chain_1.invoke({"context": [doc]})
            doc_questions = extract_questions_from_response(response)
            questions.extend(doc_questions)
        return list(set(questions))


    def retrieve_question_with_question_mark_using_regex(self):
        if self.verbose:
            print("\nExtracting question with question mark..")
        questions = []
        for doc in self.rfp_docs:
            questions += match_questions(doc.page_content)
        return questions


    def retrieve_question_without_question_mark(self):
        if self.verbose:
            print("\nExtracting question without question mark..")
        questions = []
        qe_chain_2 = create_chain(self.model, question_extraction_prompt_2)
        for doc in self.rfp_docs:
            response = qe_chain_2.invoke({"context": [doc]})
            doc_questions = extract_questions_from_response(response)
            questions.extend(doc_questions)
        return list(set(questions))


    def check_duplicate_questions(self, questions_1, questions_2):
        if self.verbose:
            print("\nChecking duplicate questions..")
        questions = []
        questions_2 = split_list(questions_2)
        qe_chain_3 = create_chain(self.model, question_extraction_prompt_3)
        for questions in questions_2:
            check_questions = questions_1 + questions
            # Convert each question into a Document object
            all_questions = [Document(page_content=q) for q in check_questions]

            # Pass the list of Document objects to the chain
            response = qe_chain_3.invoke({"context": all_questions})

            # Process the response as needed
            extracted_questions = extract_questions_from_response(response)
            questions += extracted_questions

        return questions
    
    
    def extract_RFP_local_context(self, query):
        if self.verbose:
            print("\nExtracting RFP local context for query..")
        context = ""
        ce_chain = create_chain(self.model, local_context_extraction_prompt)
        for doc in self.rfp_docs:
            response = ce_chain.invoke({"context": [doc], "query": query})
            if "doesn't provide any relevant information" not in response:
                context = context + response + "\n"
                
        return context
    
    
    def extract_company_local_context(self, query):
        if self.verbose:
            print("\nExtracting local context of company profile for query..")
        context = ""
        ce_chain = create_chain(self.model, local_context_extraction_prompt)
        for doc in self.company_docs:
            response = ce_chain.invoke({"context": [doc], "query": query})
            if "doesn't provide any relevant information" not in response:
                context = context + response + "\n"
        return context
    
    
    def extract_RFP_background(self):
        if self.verbose:
            print("\nExtracting RFP background..")
        context = ""
        text = ""
        background_chain = create_chain(self.model, background_extraction_prompt)
        background_text_chain = create_chain(self.model, background_text_extraction_prompt)
        background_compression_chain = create_chain(self.model, background_compression_prompt)
        for doc in self.rfp_docs:
            response_1 = background_chain.invoke({"context": [doc]})
            # response_2 = background_text_chain.invoke({"context": [doc]})
            # print(response_1)
            # print("-----------")
            # print(response_2)
            # print("-----s-----")
            if "doesn't provide any relevant information" not in response_1:
                context = context + response_1 + "\n"
            # if "doesn't provide any relevant information" not in response_2:
            #     text = text + response_2 + "\n"
        
        context = background_compression_chain.invoke({"context": [Document(page_content=context)]})
        # text = background_compression_chain.invoke({"context": [Document(page_content=text)]})
        # text = context + "<background>" + text + "</background>" 
        
        # compressed_background = background_compression_chain.invoke({"context": [Document(page_content=text)]})
        compressed_background = background_compression_chain.invoke({"context": [Document(page_content=context)]})
        compressed_background = re.sub(r'</?background>', '', compressed_background)
        return compressed_background
    

    def extract_RFP_objectives(self):
        if self.verbose:
            print("\nExtracting RFP objectives..")
        context = ""
        text = ""
        objectives_chain = create_chain(self.model, objectives_extraction_prompt)
        objectives_text_chain = create_chain(self.model, objectives_text_extraction_prompt)
        objectives_compression_chain = create_chain(self.model, objectives_compression_prompt)
        for doc in self.rfp_docs:
            response_1 = objectives_chain.invoke({"context": [doc]})
            response_2 = objectives_text_chain.invoke({"context": [doc]})
            # print(response_1)
            # print("-----------")
            # print(response_2)
            # print("-----s-----")
            if "doesn't provide any relevant information" not in response_1:
                context = context + response_1 + "\n"
            if "doesn't provide any relevant information" not in response_2:
                text = text + response_2 + "\n"
        
        context = objectives_compression_chain.invoke({"context": [Document(page_content=context)]})
        text = objectives_compression_chain.invoke({"context": [Document(page_content=text)]})
        text = context + "<objectives>" + text + "</objectives>" 
        
        compressed_objectives = objectives_compression_chain.invoke({"context": [Document(page_content=text)]})
        compressed_objectives = re.sub(r'</?objectives>', '', compressed_objectives)
        return compressed_objectives
    
    def extract_RFP_scopes(self):
        if self.verbose:
            print("\nExtracting RFP scopes..")
        context = ""
        text = ""
        scopes_chain = create_chain(self.model, scopes_extraction_prompt)
        scopes_text_chain = create_chain(self.model, scopes_text_extraction_prompt)
        scopes_compression_chain = create_chain(self.model, scopes_compression_prompt)
        for doc in self.rfp_docs:
            response_1 = scopes_chain.invoke({"context": [doc]})
            response_2 = scopes_text_chain.invoke({"context": [doc]})
            # print(response_1)
            # print("-----------")
            # print(response_2)
            # print("-----s-----")
            if "doesn't provide any relevant information" not in response_1:
                context = context + response_1 + "\n"
            if "doesn't provide any relevant information" not in response_2:
                text = text + response_2 + "\n"
        
        context = scopes_compression_chain.invoke({"context": [Document(page_content=context)]})
        text = context + "<scopes>" + text + "</scopes>" 
        
        compressed_scopes = scopes_compression_chain.invoke({"context": [Document(page_content=text)]})
        compressed_scopes = re.sub(r'</?scopes>', '', compressed_scopes)
        
        return compressed_scopes
    
    
    def extract_RFP_general_context(self):
        rfp_background = self.extract_RFP_background()
        rfp_objectives = self.extract_RFP_objectives()
        rfp_scopes = self.extract_RFP_scopes()
        
        general_context = rfp_background + "\n\n" + rfp_objectives +"\n\n" + rfp_scopes
        self.rfp_general_context = general_context
        # rfp_summary_chain = csreate_chain(self.model, RFP_summary_prompt)
        # general_context = rfp_summary_chain.invoke({"context": [Document(page_content=general_context)]})
        return general_context
    
    
    def extract_company_background(self):
        if self.verbose:
            print("\nExtracting company background..")
        context = ""
        text = ""
        company_background_chain = create_chain(self.model, company_background_prompt)
        company_background_text_chain = create_chain(self.model, company_background_text_extraction_prompt)
        company_background_compression_chain = create_chain(self.model, company_background_compression_prompt)
        for doc in self.company_docs:
            response_1 = company_background_chain.invoke({"context": [doc]})
            response_2 = company_background_text_chain.invoke({"context": [doc]})
            if "doesn't provide any relevant information" not in response_1:
                context = context + response_1 + "\n"
            if "doesn't provide any relevant information" not in response_2:
                text = text + response_2 + "\n"
                
        context = company_background_compression_chain.invoke({"context": [Document(page_content=context)]})
        text = company_background_compression_chain.invoke({"context": [Document(page_content=text)]})
        text = context + "<background>" + text + "</background>" 
        
        compressed_company_background= company_background_compression_chain.invoke({"context": [Document(page_content=text)]})
        compressed_company_background = re.sub(r'</?background>', '', compressed_company_background)

        return compressed_company_background
    
    
    def extract_company_project_experience(self):
        if self.verbose:
            print("\nExtracting company project experience..")
        context = ""
        project_experience_chain = create_chain(self.model, project_experience_prompt)
        project_experience_compression_chain = create_chain(self.model, project_experience_compression_prompt)
        for doc in self.company_docs:
            response = project_experience_chain.invoke({"context": [doc]})
            if "doesn't provide any relevant information" not in response:
                context = context + response + "\n"
        compressed_project_experience = project_experience_compression_chain.invoke({"context": [Document(page_content=context)]})

        return compressed_project_experience
    
    
    def extract_company_product_services(self):
        if self.verbose:
            print("\nExtracting company product & services..")
        context = ""
        product_services_chain = create_chain(self.model, product_services_prompt)
        product_services_compression_chain = create_chain(self.model, product_services_compression_prompt)
        for doc in self.company_docs:
            response = product_services_chain.invoke({"context": [doc]})
            if "doesn't provide any relevant information" not in response:
                context = context + response + "\n"
        compressed_product_services = product_services_compression_chain.invoke({"context": [Document(page_content=context)]})

        return compressed_product_services
    
    
    def extract_company_team_members(self):
        if self.verbose:
            print("\nExtracting company team members..")
        context = ""
        team_members_chain = create_chain(self.model, team_members_prompt)
        team_members_compression_chain = create_chain(self.model, team_members_compression_prompt)
        for doc in self.company_docs:
            response = team_members_chain.invoke({"context": [doc]})
            if "doesn't provide any relevant information" not in response:
                context = context + response + "\n"
        compressed_team_members = team_members_compression_chain.invoke({"context": [Document(page_content=context)]})

        return compressed_team_members
    
    
    def extract_company_general_context(self):
        company_profile = self.extract_company_background()
        project_experience = self.extract_company_project_experience()
        product_services = self.extract_company_product_services()
        team_members = self.extract_company_team_members()
        general_context = company_profile + "\n\n" + project_experience +"\n\n" + product_services
        # company_profile_summary_chain = create_chain(self.model, company_profile_summary_prompt)
        # general_context = company_profile_summary_chain.invoke({"context":[Document(page_content=general_context)]})
        general_context = general_context + "\n\n" + team_members
        self.company_general_context = general_context 
        return general_context
    
    
    def get_context(self):
        if self.company_general_context == None:
            company_general_context = self.extract_company_general_context()
            self.company_general_context = company_general_context
        else:
            company_general_context = self.company_general_context
        if self.rfp_general_context == None:
            rfp_general_context = self.extract_RFP_general_context()
            self.rfp_general_context = rfp_general_context
        else:
            rfp_general_context = self.rfp_general_context
        return company_general_context, rfp_general_context
    
    
    def query_answering_with_context(self, query, company_general_context, company_local_context, rfp_general_context, rfp_local_context):
        query_answering_chain = create_chain(self.model, query_answering_prompt)
        answer = query_answering_chain.invoke(
            {"context":[Document(page_content=company_general_context)],
             "company_local_context":company_local_context,
             "rfp_general_context": rfp_general_context,
             "rfp_local_context": rfp_local_context,
             "query":query})
        return answer
    
    
    def simple_query_answering(self, query):
        company_general_context, rfp_general_context = self.get_context()
        company_local_context = self.extract_company_local_context(query)
        rfp_local_context = self.extract_RFP_local_context(query)
        answer = self.query_answering_with_context(query, company_general_context, company_local_context, rfp_general_context, rfp_local_context)
        return answer
    
    
    def convert_init_answer_to_json(self, init_answer):
        json_answer_chain = create_chain(self.json_model, answer_json_conversion_prompt)
        answer = json_answer_chain.invoke({"context":[Document(page_content=init_answer)]})
        return answer
    
    
    def making_detailed_answer(self, query, jsonized_answer):
        #JSON verification has to be done.
        heading_text = jsonized_answer["heading_text"]
        ending_text = jsonized_answer["ending_text"]
        strategies = jsonized_answer["strategies"]
        company_general_context, rfp_general_context = self.get_context()
        detailed_ansewr_chain = create_chain(self.model, detailed_answer_prompt)
        if len(strategies) == 0:
            answer = heading_text + "\n\n" + ending_text
        else:
            answer = heading_text + "\n\n"
            for count, strategy in enumerate(strategies):
                title = strategy["title"]
                description = strategy["description"]
                rfp_local_context = self.extract_RFP_local_context(query + "\n" + title + "\n" + description)
                company_local_context = self.extract_company_local_context(query + "\n" + title + "\n" + description)
                strategy_answer = detailed_ansewr_chain.invoke(
                {"context":[Document(page_content=company_general_context)],
                "company_local_context":company_local_context,
                "rfp_general_context": rfp_general_context,
                "rfp_local_context": rfp_local_context,
                "query":title + "\n" + description})
                strategy_answer = strategy_answer.replace("\n\n", "\n")
                answer += "{}. {}\n\n {} {}\n\n".format(count+1, title, description, strategy_answer)
            answer = answer + "\n" + ending_text
            
        answer = re.sub(r'(?<!\n)\n(?!\n)', '\n\n', answer)
        return answer
    
    
    def simple_to_detailed_answer(self, query, simple_answer):
        jsonized_answer = load_json(self.convert_init_answer_to_json(simple_answer))
        detailed_answer = self.making_detailed_answer(query, jsonized_answer)
        return detailed_answer
    
    
    def detailed_query_answering(self, query):
        simple_answer = self.simple_query_answering(query)
        jsonized_answer = load_json(self.convert_init_answer_to_json(simple_answer))
        detailed_answer = self.making_detailed_answer(query, jsonized_answer)
        return detailed_answer
    
    
    def regex_find_questions(self):
        questions = []
        all_questions = []
        for doc in self.rfp_docs:
            questions += re.findall(r'(?:[^.?!]*\?)(?=\s|$)', doc.page_content)
        for question in questions:
            all_questions.append(question.strip())
        return list(set(all_questions))

    
    def get_rfp_path(self):
        return rfp_path

    
    def company_profile_path(self):
        return self.company_profile_path

def load_data(path):
    docs = []
    for pdf_path in get_all_pdfs(path):
        docs.extend(load_pdf(pdf_path))
    for path in get_all_file_paths(path):
        if ".doc" in path or ".docx" in path:
            docs.extend(load_word_document(path))
        elif ".txt" in path:
            docs.extend(load_text(path))
        elif ".xlsx" in path or ".xls" in path:
            docs.extend(load_excel(path))
        elif ".csv" in path:
            docs.extend(load_csv(path))
        # else:
        #     docs.extend(load_unstructure(path))

    all_splits = recursive_character_splitter(docs)
    return all_splits


def vector_store(data):
    vectorstore = chroma_vectorstore(data)
    return vectorstore


def create_retriever_without_history(data, vectorstore, llm_model):
    # retriever = bm25_retriever(all_splits, 100)
    retriever = top_k_retriever(vectorstore, 20)
    retriever = ensemble_retriever_1(retriever, data, llm_model, 20)
    return retriever


def create_retriever_with_history(data, model, vectorstore):
    # retriever = bm25_retriever(all_splits, 100)
    retriever = top_k_retriever(vectorstore, 20)
    retriever = ensemble_retriever_1(retriever, data, model, 20)
    retriever = historical_messages_retriever(model, retriever)
    return retriever


def create_rag_chain_with_memory(model):
    # rag_chain = create_document_chain_answer_giving(model)
    rag_chain = create_chain(model, answer_giving_prompt_with_memory)
    return rag_chain


def create_rag_chain_without_memory(model):
    rag_chain = create_chain(model, answer_giving_prompt)
    return rag_chain