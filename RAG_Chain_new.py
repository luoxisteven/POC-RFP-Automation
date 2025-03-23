import re
import time
import asyncio
from langchain.schema import Document
from config import *
from src.prompt_and_chain import *
from src.utils import *
from src.model_initializer import llm_model, chat_gpt
from src.text_splitter import recursive_character_splitter
# from src.vectorstore_retriever import chroma_vectorstore, top_k_retriever, \
#     historical_messages_retriever, ensemble_retriever_1

class RAG_Chain:
    def __init__(self, model="gpt-4o-mini", rfp_path=None, verbose=False):
        self.model = llm_model(model)
        self.json_model = self.model.bind(response_format={"type": "json_object"})
        if rfp_path == None:
            rfp_path = CONFIG_RFP_PATH
        self.rfp_docs = load_data(rfp_path)
        self.company_docs = load_data(CONFIG_COMPANY_PROFILE_PATH)
        self.rfp_general_context = None
        self.company_general_context = None
        self.verbose = verbose
        
    def get_answer_without_memory(self, query):
        answer = self.simple_query_answering(query)
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
        qe_chain_1 = create_parallel_chain(len(self.rfp_docs), qe_chain_1)
        responses = qe_chain_1.invoke({"context":self.rfp_docs})
        for result in responses:
            doc_questions = extract_questions_from_response(result)
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
        qe_chain_2 = create_parallel_chain(len(self.rfp_docs), qe_chain_2)
        responses = qe_chain_2.invoke({"context":self.rfp_docs})
        for response in responses.values():
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
    

    # def extract_RFP_local_context(self, query):
    #     if self.verbose:
    #         print("\nExtracting RFP local context for query..")
    #     context = ""
    #     ce_chain = create_chain(self.model, local_context_extraction_prompt)
    #     ce_chain = create_parallel_chain(self.rfp_docs, ce_chain)
    #     inputs = copy.deepcopy(self.rfp_parallel_inputs)
    #     inputs["query"] = [query] * len(self.rfp_docs)
    #     responses = ce_chain.invoke(inputs)
    #     for response in responses.values():
    #         if "doesn't provide any relevant information" not in response:
    #             context = context + response + "\n"
    #     return context
    
    async def extract_RFP_local_context(self, query):
        if self.verbose:
            print("\nExtracting RFP local context for query..")
        context = ""
        ce_chain = create_chain(self.model, local_context_extraction_prompt)
        ce_chain = create_parallel_chain(len(self.rfp_docs), ce_chain)
        inputs = {"context": self.rfp_docs, "query": [query] * len(self.rfp_docs)}
        responses = await ce_chain.ainvoke(inputs)
        for response in responses.values():
            if "doesn't provide any relevant information" not in response:
                context = context + response + "\n"
        return context
    
    
    async def extract_company_local_context(self, query):
        if self.verbose:
            print("\nExtracting local context of company profile for query..")
        context = ""
        ce_chain = create_chain(self.model, local_context_extraction_prompt)
        ce_chain = create_parallel_chain(len(self.company_docs), ce_chain)
        inputs = {"context": self.company_docs, "query": [query] * len(self.company_docs)}
        responses = ce_chain.invoke(inputs)
        for response in responses.values():
            if "doesn't provide any relevant information" not in response:
                context = context + response + "\n"
        return context
    
    async def extract_RFP_background(self):
        # 记录开始时间
        start_time = time.time()
        
        if self.verbose:
            print("\nExtracting RFP background..")
        context = ""
        background_chain = create_chain(self.model, background_extraction_prompt)
        background_chain = create_parallel_chain(len(self.rfp_docs), background_chain)
        inputs = {"context": self.rfp_docs}
        responses = await background_chain.ainvoke(inputs)
        
        for response in responses.values():
            if "doesn't provide any relevant information" not in response:
                context = context + response + "\n"
        background_compression_chain = create_chain(self.model, background_compression_prompt)
        context = background_compression_chain.invoke({"context": [Document(page_content=context)]})
        compressed_background = background_compression_chain.invoke({"context": [Document(page_content=context)]})
        compressed_background = re.sub(r'</?background>', '', compressed_background)
        
        # 记录结束时间并计算耗时
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"RFP Background: {elapsed_time:.2f} seconds")
        
        return compressed_background
    
    # 1 thread: 16.86s  without thread: 13.16s 2 thread: 19.86s without parallel: 25.85s
    # def extract_RFP_objectives(self):
    #     # 记录开始时间
    #     start_time = time.time()
        
    #     if self.verbose:
    #         print("\nExtracting RFP objectives..")
    #     context = ""
    #     text = ""
    #     objectives_chain = create_chain(self.model, objectives_extraction_prompt)
    #     objectives_chain = create_parallel_chain(len(self.rfp_docs), objectives_chain)
        
    #     objectives_text_chain = create_chain(self.model, objectives_text_extraction_prompt)
    #     objectives_text_chain = create_parallel_chain(len(self.rfp_docs), objectives_text_chain)
        
    #     inputs = {"context": self.rfp_docs}
        
    #     # 使用线程池并行执行两个 invoke
    #     with ThreadPoolExecutor() as executor:
    #         future_1 = executor.submit(objectives_chain.invoke, inputs)
    #         future_2 = executor.submit(objectives_text_chain.invoke, inputs)
            
    #         # 等待两个线程完成并获取结果
    #         responses_1 = future_1.result()
    #         responses_2 = future_2.result()
        
    #     # responses_1 = objectives_chain.invoke(inputs)
    #     # responses_2 = objectives_text_chain.invoke(inputs)
        
    #     # 将 dict_values 转换为列表，以便通过索引访问
    #     responses_1_list = list(responses_1.values())
    #     responses_2_list = list(responses_2.values())

    #     # 处理 responses_1 和 responses_2
    #     for i in range(len(inputs["context"])):
    #         if "doesn't provide any relevant information" not in responses_1_list[i]:
    #             context = context + responses_1_list[i] + "\n"
    #         if "doesn't provide any relevant information" not in responses_2_list[i]:
    #             text = text + responses_2_list[i] + "\n"
        
    #     objectives_compression_chain = create_chain(self.model, objectives_compression_prompt)
    #     context = objectives_compression_chain.invoke({"context": [Document(page_content=context)]})
    #     text = objectives_compression_chain.invoke({"context": [Document(page_content=text)]})
    #     text = context + "<objectives>" + text + "</objectives>"
        
    #     compressed_objectives = objectives_compression_chain.invoke({"context": [Document(page_content=text)]})
    #     compressed_objectives = re.sub(r'</?objectives>', '', compressed_objectives)
        
    #     # 记录结束时间并计算耗时
    #     end_time = time.time()
    #     elapsed_time = end_time - start_time
    #     print(f"Total time taken: {elapsed_time:.2f} seconds")
        
    #     return compressed_objectives
    
    # def extract_RFP_objectives(self):
    #     # 记录开始时间
    #     start_time = time.time()
        
    #     if self.verbose:
    #         print("\nExtracting RFP objectives..")
    #     context = ""
    #     text = ""
    #     objectives_chain = create_chain(self.model, objectives_extraction_prompt)
    #     objectives_chain = create_parallel_chain(len(self.rfp_docs), objectives_chain)
        
    #     objectives_text_chain = create_chain(self.model, objectives_text_extraction_prompt)
    #     objectives_text_chain = create_parallel_chain(len(self.rfp_docs), objectives_text_chain)
        
    #     inputs = {"context": self.rfp_docs}
        
    #     # 使用线程池并行执行两个 invoke
    #     # with ThreadPoolExecutor() as executor:
    #     #     future_1 = executor.submit(objectives_chain.invoke, inputs)
    #     #     future_2 = executor.submit(objectives_text_chain.invoke, inputs)
            
    #     #     # 等待两个线程完成并获取结果
    #     #     responses_1 = future_1.result()
    #     #     responses_2 = future_2.result()
            
    #     responses_1 = objectives_chain.invoke(inputs)
    #     responses_2 = objectives_text_chain.invoke(inputs)
        
    #     # 将 dict_values 转换为列表，以便通过索引访问
    #     responses_1_list = list(responses_1.values())
    #     responses_2_list = list(responses_2.values())

    #     # 处理 responses_1 和 responses_2
    #     for i in range(len(inputs["context"])):
    #         if "doesn't provide any relevant information" not in responses_1_list[i]:
    #             context = context + responses_1_list[i] + "\n"
    #         if "doesn't provide any relevant information" not in responses_2_list[i]:
    #             text = text + responses_2_list[i] + "\n"
        
    #     objectives_compression_chain = create_chain(self.model, objectives_compression_prompt)
        
    #     # 使用线程池并行执行 context 和 text 的压缩
    #     # with ThreadPoolExecutor() as executor:
    #     #     future_context = executor.submit(objectives_compression_chain.invoke, {"context": [Document(page_content=context)]})
    #     #     future_text = executor.submit(objectives_compression_chain.invoke, {"context": [Document(page_content=text)]})
            
    #     #     # 等待两个线程完成并获取结果
    #     #     compressed_context = future_context.result()
    #     #     compressed_text = future_text.result()
        
    #     compressed_context = objectives_compression_chain.invoke({"context": [Document(page_content=context)]})
    #     compressed_text = objectives_compression_chain.invoke({"context": [Document(page_content=text)]})

    #     text = compressed_context + "<objectives>" + compressed_text + "</objectives>"
        
    #     # 最终压缩处理
    #     compressed_objectives = objectives_compression_chain.invoke({"context": [Document(page_content=text)]})
    #     compressed_objectives = re.sub(r'</?objectives>', '', compressed_objectives)
        
    #     # 记录结束时间并计算耗时
    #     end_time = time.time()
    #     elapsed_time = end_time - start_time
    #     print(f"Total time taken: {elapsed_time:.2f} seconds")
        
    #     return compressed_objectives
    
    
    async def extract_RFP_objectives(self):
        # 记录开始时间
        start_time = time.time()
        
        if self.verbose:
            print("\nExtracting RFP objectives..")
        context = ""
        text = ""
        
        objectives_chain = create_chain(self.model, objectives_extraction_prompt)
        objectives_chain = create_parallel_chain(len(self.rfp_docs), objectives_chain)
        
        objectives_text_chain = create_chain(self.model, objectives_text_extraction_prompt)
        objectives_text_chain = create_parallel_chain(len(self.rfp_docs), objectives_text_chain)
        
        inputs = {"context": self.rfp_docs}
        
        # 并行执行两个 ainvoke 调用
        responses_1, responses_2 = await asyncio.gather(
            objectives_chain.ainvoke(inputs),
            objectives_text_chain.ainvoke(inputs)
        )
        
        # 将 dict_values 转换为列表，以便通过索引访问
        responses_1_list = list(responses_1.values())
        responses_2_list = list(responses_2.values())

        # 处理 responses_1 和 responses_2
        for i in range(len(inputs["context"])):
            if "doesn't provide any relevant information" not in responses_1_list[i]:
                context += responses_1_list[i] + "\n"
            if "doesn't provide any relevant information" not in responses_2_list[i]:
                text += responses_2_list[i] + "\n"
        
        objectives_compression_chain = create_chain(self.model, objectives_compression_prompt)
        
        # 并行执行 context 和 text 的压缩
        compressed_context, compressed_text = await asyncio.gather(
            objectives_compression_chain.ainvoke({"context": [Document(page_content=context)]}),
            objectives_compression_chain.ainvoke({"context": [Document(page_content=text)]})
        )

        text = compressed_context + "<objectives>" + compressed_text + "</objectives>"
        
        # 最终压缩处理
        compressed_objectives = await objectives_compression_chain.ainvoke({"context": [Document(page_content=text)]})
        compressed_objectives = re.sub(r'</?objectives>', '', compressed_objectives)
        
        # 记录结束时间并计算耗时
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"RFP Objectives: {elapsed_time:.2f} seconds")
        
        return compressed_objectives
    
    
    async def extract_RFP_scopes(self):
        # 记录开始时间
        start_time = time.time()
        
        if self.verbose:
            print("\nExtracting RFP scopes..")
        context = ""
        text = ""
        scopes_chain = create_chain(self.model, scopes_extraction_prompt)
        scopes_chain = create_parallel_chain(len(self.rfp_docs), scopes_chain)
        
        scopes_text_chain = create_chain(self.model, scopes_text_extraction_prompt)
        scopes_text_chain = create_parallel_chain(len(self.rfp_docs), scopes_text_chain)
        
        inputs = {"context": self.rfp_docs}
        
        responses_1, responses_2 = await asyncio.gather(
            scopes_chain.ainvoke(inputs),
            scopes_text_chain.ainvoke(inputs)
        )
        
        # 将 dict_values 转换为列表，以便通过索引访问
        responses_1_list = list(responses_1.values())
        responses_2_list = list(responses_2.values())
        
        for i in range(len(inputs["context"])):
            if "doesn't provide any relevant information" not in responses_1_list[i]:
                context += responses_1_list[i] + "\n"
            if "doesn't provide any relevant information" not in responses_2_list[i]:
                text += responses_2_list[i] + "\n"

        scopes_compression_chain = create_chain(self.model, scopes_compression_prompt)
        context = scopes_compression_chain.invoke({"context": [Document(page_content=context)]})
        text = context + "<scopes>" + text + "</scopes>" 
        
        compressed_scopes = scopes_compression_chain.invoke({"context": [Document(page_content=text)]})
        compressed_scopes = re.sub(r'</?scopes>', '', compressed_scopes)
        
        # 记录结束时间并计算耗时
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"RFP Scopes: {elapsed_time:.2f} seconds")
        
        return compressed_scopes
    
    
    async def extract_RFP_general_context(self):
        rfp_background_task = self.extract_RFP_background()
        rfp_objectives_task = self.extract_RFP_objectives()
        rfp_scopes_task = self.extract_RFP_scopes()

        # 并行执行三个任务
        rfp_background, rfp_objectives, rfp_scopes = await asyncio.gather(
            rfp_background_task,
            rfp_objectives_task,
            rfp_scopes_task
        )
        
        general_context = rfp_background + "\n\n" + rfp_objectives + "\n\n" + rfp_scopes
        self.rfp_general_context = general_context
        return general_context
    

    async def extract_company_background(self):
        if self.verbose:
            print("\nExtracting company background..")
        
        context = ""
        text = ""
        
        company_background_chain = create_chain(self.model, company_background_prompt)
        company_background_chain = create_parallel_chain(len(self.company_docs), company_background_chain)
        
        company_background_text_chain = create_chain(self.model, company_background_text_extraction_prompt)
        company_background_text_chain = create_parallel_chain(len(self.company_docs), company_background_text_chain)
        
        inputs = {"context": self.company_docs}
        
        # 并行执行两个 ainvoke 调用
        responses_1, responses_2 = await asyncio.gather(
            company_background_chain.ainvoke(inputs),
            company_background_text_chain.ainvoke(inputs)
        )
        
        # 将 dict_values 转换为列表，以便通过索引访问
        responses_1_list = list(responses_1.values())
        responses_2_list = list(responses_2.values())

        # 处理 responses_1 和 responses_2
        for i in range(len(inputs["context"])):
            if "doesn't provide any relevant information" not in responses_1_list[i]:
                context += responses_1_list[i] + "\n"
            if "doesn't provide any relevant information" not in responses_2_list[i]:
                text += responses_2_list[i] + "\n"
        
        company_background_compression_chain = create_chain(self.model, company_background_compression_prompt)
        
        # 并行执行 context 和 text 的压缩
        compressed_context, compressed_text = await asyncio.gather(
            company_background_compression_chain.ainvoke({"context": [Document(page_content=context)]}),
            company_background_compression_chain.ainvoke({"context": [Document(page_content=text)]})
        )

        text = compressed_context + "<background>" + compressed_text + "</background>"
        
        # 最终压缩处理
        compressed_company_background = await company_background_compression_chain.ainvoke({"context": [Document(page_content=text)]})
        compressed_company_background = re.sub(r'</?background>', '', compressed_company_background)
        
        return compressed_company_background
    
    
    async def extract_company_project_experience(self):
        if self.verbose:
            print("\nExtracting company project experience..")
        context = ""
        project_experience_chain = create_chain(self.model, project_experience_prompt)
        project_experience_chain = create_parallel_chain(len(self.company_docs), project_experience_chain)
        inputs = {"context": self.company_docs}
        responses = await project_experience_chain.ainvoke(inputs)
        for response in responses.values():
            if "doesn't provide any relevant information" not in response:
                context = context + response + "\n"

        project_experience_compression_chain = create_chain(self.model, project_experience_compression_prompt)
        compressed_project_experience = await project_experience_compression_chain.ainvoke({"context": [Document(page_content=context)]})

        return compressed_project_experience
    
    
    async def extract_company_product_services(self):
        if self.verbose:
            print("\nExtracting company product & services..")
        
        context = ""
        product_services_chain = create_chain(self.model, product_services_prompt)
        product_services_chain = create_parallel_chain(len(self.company_docs), product_services_chain)
        
        inputs = {"context": self.company_docs}
        responses = await product_services_chain.ainvoke(inputs)
        
        for response in responses.values():
            if "doesn't provide any relevant information" not in response:
                context += response + "\n"
        
        product_services_compression_chain = create_chain(self.model, product_services_compression_prompt)
        compressed_product_services = await product_services_compression_chain.ainvoke({"context": [Document(page_content=context)]})

        return compressed_product_services


    async def extract_company_team_members(self):
        if self.verbose:
            print("\nExtracting company team members..")
        
        context = ""
        team_members_chain = create_chain(self.model, team_members_prompt)
        team_members_chain = create_parallel_chain(len(self.company_docs), team_members_chain)
        
        inputs = {"context": self.company_docs}
        responses = await team_members_chain.ainvoke(inputs)
        
        for response in responses.values():
            if "doesn't provide any relevant information" not in response:
                context += response + "\n"
        
        team_members_compression_chain = create_chain(self.model, team_members_compression_prompt)
        compressed_team_members = await team_members_compression_chain.ainvoke({"context": [Document(page_content=context)]})

        return compressed_team_members

    
    async def extract_company_general_context(self):
    # 使用 asyncio.gather 并行执行四个提取任务
        company_profile_task = self.extract_company_background()
        project_experience_task = self.extract_company_project_experience()
        product_services_task = self.extract_company_product_services()
        team_members_task = self.extract_company_team_members()
        
        # 并行运行四个任务并收集结果
        company_profile, project_experience, product_services, team_members = await asyncio.gather(
            company_profile_task,
            project_experience_task,
            product_services_task,
            team_members_task
        )
        
        # 合并结果
        general_context = (
            company_profile + "\n\n" + 
            project_experience + "\n\n" + 
            product_services + "\n\n" + 
            team_members
        )
        self.company_general_context = general_context 
        return general_context

    
    async def get_context(self):
        # 如果两个上下文都为空，则并行提取它们
        if self.company_general_context is None and self.rfp_general_context is None:
            company_general_context_task = self.extract_company_general_context()
            rfp_general_context_task = self.extract_RFP_general_context()
            
            # 并行执行两个提取任务
            company_general_context, rfp_general_context = await asyncio.gather(
                company_general_context_task,
                rfp_general_context_task
            )
            
            # 更新类属性
            self.company_general_context = company_general_context
            self.rfp_general_context = rfp_general_context

        # 如果只有 company_general_context 为 None
        elif self.company_general_context is None:
            company_general_context = await self.extract_company_general_context()
            self.company_general_context = company_general_context
            rfp_general_context = self.rfp_general_context

        # 如果只有 rfp_general_context 为 None
        elif self.rfp_general_context is None:
            rfp_general_context = await self.extract_RFP_general_context()
            self.rfp_general_context = rfp_general_context
            company_general_context = self.company_general_context

        # 如果都不为 None，直接使用已有的上下文
        else:
            company_general_context = self.company_general_context
            rfp_general_context = self.rfp_general_context

        return company_general_context, rfp_general_context


    async def query_answering_with_context(self, query, company_general_context, company_local_context, rfp_general_context, rfp_local_context):
        query_answering_chain = create_chain(self.model, query_answering_prompt)
        answer = await query_answering_chain.ainvoke(
            {"context": [Document(page_content=company_general_context)],
            "company_local_context": company_local_context,
            "rfp_general_context": rfp_general_context,
            "rfp_local_context": rfp_local_context,
            "query": query})
        return answer


    async def simple_query_answering(self, query):
        # 创建全局上下文任务
        global_context_task = self.get_context()
        
        # 创建局部上下文任务
        company_local_context_task = self.extract_company_local_context(query)
        rfp_local_context_task = self.extract_RFP_local_context(query)
        
        # 并行运行所有任务
        (company_general_context, rfp_general_context), company_local_context, rfp_local_context = await asyncio.gather(
            global_context_task, 
            company_local_context_task, 
            rfp_local_context_task
        )

        # 根据上下文获取答案
        answer = await self.query_answering_with_context(
            query, 
            company_general_context, 
            company_local_context, 
            rfp_general_context, 
            rfp_local_context
        )
        return answer


    async def convert_init_answer_to_json(self, init_answer):
        json_answer_chain = create_chain(self.json_model, answer_json_conversion_prompt)
        answer = await json_answer_chain.ainvoke({"context": [Document(page_content=init_answer)]})
        return answer


    # Making detailed answer
    async def making_detailed_answer(self, query, jsonized_answer):
        heading_text = jsonized_answer["heading_text"]
        ending_text = jsonized_answer["ending_text"]
        strategies = jsonized_answer["strategies"]
        company_general_context, rfp_general_context = await self.get_context()
        detailed_answer_chain = create_chain(self.model, detailed_answer_prompt)

        if not strategies:
            answer = heading_text + "\n\n" + ending_text
        else:
            answer = heading_text + "\n\n"
            tasks = []

            for count, strategy in enumerate(strategies):
                title = strategy["title"]
                description = strategy["description"]
                rfp_local_context_task = self.extract_RFP_local_context(query + "\n" + title + "\n" + description)
                company_local_context_task = self.extract_company_local_context(query + "\n" + title + "\n" + description)

                # 将局部上下文任务添加到任务列表中
                tasks.append((count, title, description, rfp_local_context_task, company_local_context_task))

            # 并行执行所有局部上下文任务
            for count, title, description, rfp_local_context_task, company_local_context_task in tasks:
                rfp_local_context, company_local_context = await asyncio.gather(rfp_local_context_task, company_local_context_task)
                strategy_answer = await detailed_answer_chain.ainvoke(
                    {"context": [Document(page_content=company_general_context)],
                    "company_local_context": company_local_context,
                    "rfp_general_context": rfp_general_context,
                    "rfp_local_context": rfp_local_context,
                    "query": title + "\n" + description})
                strategy_answer = strategy_answer.replace("\n\n", "\n")
                answer += "{}. {}\n\n {} {}\n\n".format(count + 1, title, description, strategy_answer)

            answer += "\n" + ending_text

        answer = re.sub(r'(?<!\n)\n(?!\n)', '\n\n', answer)
        return answer
    
    
    async def making_detailed_answer_fast(self, query, jsonized_answer):
        heading_text = jsonized_answer["heading_text"]
        ending_text = jsonized_answer["ending_text"]
        strategies = jsonized_answer["strategies"]
        company_general_context, rfp_general_context = await self.get_context()
        detailed_answer_chain = create_chain(self.model, detailed_answer_prompt)

        if not strategies:
            answer = heading_text + "\n\n" + ending_text
        else:
            answer = heading_text + "\n\n"
            tasks = []

            # 创建所有局部上下文任务并保存到任务列表中
            for count, strategy in enumerate(strategies):
                title = strategy["title"]
                description = strategy["description"]
                rfp_local_context_task = self.extract_RFP_local_context(query + "\n" + title + "\n" + description)
                company_local_context_task = self.extract_company_local_context(query + "\n" + title + "\n" + description)
                tasks.append((count, title, description, rfp_local_context_task, company_local_context_task))

            # 并行执行所有局部上下文任务
            async def process_task(count, title, description, rfp_local_context_task, company_local_context_task):
                # 获取上下文并生成答案
                rfp_local_context, company_local_context = await asyncio.gather(rfp_local_context_task, company_local_context_task)
                strategy_answer = await detailed_answer_chain.ainvoke(
                    {
                        "context": [Document(page_content=company_general_context)],
                        "company_local_context": company_local_context,
                        "rfp_general_context": rfp_general_context,
                        "rfp_local_context": rfp_local_context,
                        "query": title + "\n" + description,
                    }
                )
                strategy_answer = strategy_answer.replace("\n\n", "\n")
                return "{}. {}\n\n {} {}\n\n".format(count + 1, title, description, strategy_answer)

            # 将所有任务放入 asyncio.gather 并行执行
            results = await asyncio.gather(
                *[process_task(count, title, description, rfp_task, company_task) for count, title, description, rfp_task, company_task in tasks]
            )

            # 合并结果
            answer += "".join(results) + "\n" + ending_text

        # 格式化结果
        answer = re.sub(r'(?<!\n)\n(?!\n)', '\n\n', answer)
        return answer



    async def simple_to_detailed_answer(self, query, simple_answer):
        jsonized_answer = load_json(await self.convert_init_answer_to_json(simple_answer))
        detailed_answer = await self.making_detailed_answer(query, jsonized_answer)
        return detailed_answer


    async def detailed_query_answering(self, query):
        simple_answer = await self.simple_query_answering(query)
        jsonized_answer = load_json(await self.convert_init_answer_to_json(simple_answer))
        detailed_answer = await self.making_detailed_answer(query, jsonized_answer)
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
        return self.rfp_path

    
    def company_profile_path(self):
        return self.company_profile_path

def load_data(path):
    docs = []
    
    for pdf_path in get_all_pdfs(path):
        docs.extend(load_pdf(pdf_path))
    
    for file_path in get_all_file_paths(path):
        if not file_path.startswith('~$'):
            if file_path.endswith('.doc') or file_path.endswith('.docx'):
                docs.extend(load_word_document(file_path))
            elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                docs.extend(load_excel(file_path))
            elif file_path.endswith('.txt'):
                docs.extend(load_text(file_path))
            elif file_path.endswith('.csv'):
                docs.extend(load_csv(file_path))
                
    all_splits = recursive_character_splitter(docs)
    
    return all_splits


# def vector_store(data):
#     vectorstore = chroma_vectorstore(data)
#     return vectorstore


# def create_retriever_without_history(data, vectorstore, llm_model):
#     # retriever = bm25_retriever(all_splits, 100)
#     retriever = top_k_retriever(vectorstore, 20)
#     retriever = ensemble_retriever_1(retriever, data, llm_model, 20)
#     return retriever


# def create_retriever_with_history(data, model, vectorstore):
#     # retriever = bm25_retriever(all_splits, 100)
#     retriever = top_k_retriever(vectorstore, 20)
#     retriever = ensemble_retriever_1(retriever, data, model, 20)
#     retriever = historical_messages_retriever(model, retriever)
#     return retriever


def create_rag_chain_with_memory(model):
    # rag_chain = create_document_chain_answer_giving(model)
    rag_chain = create_chain(model, answer_giving_prompt_with_memory)
    return rag_chain


def create_rag_chain_without_memory(model):
    rag_chain = create_chain(model, answer_giving_prompt)
    return rag_chain
