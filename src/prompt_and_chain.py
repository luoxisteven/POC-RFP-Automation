from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableParallel

answer_giving_template = """
        <web info>
        {context}
        </web info>
"""

answer_giving_template_with_memory = """
You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know.\
{context}
"""

contextualize_q_system_prompt_template = """
Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is.
"""

# question_extraction_prompt =PromptTemplate.from_template("""
# Help me to extract any question with question mark in the context.
# Just extract it and keep it as origin.
# If there is no question in the context, just say you don't know.
# You should follow examples of the following format:
# 1. How old are you?
# 2. What is Artificial Intelligence?
# 3. What is ..?
# .....
# {context}
#     """)

# question_extraction_prompt = PromptTemplate.from_template("""
# Help me to extract any question with question mark in the context.
# Just extract it and keep it as origin.
# Also extract any potential question in the context.
# You should follow examples of the following format:
# 1.
# 2.
# 3.
# {context}
#     """)

# 改成JSON Mode
question_extraction_prompt_1 = PromptTemplate.from_template("""
<context>                                                                                         
{context}
</context>         
Help me to extract any question ends with question mark in the context.
Just extract it and keep it as origin.
If there is no question in the context, just say you don't know.

You should follow examples of the following format:
1.
2.
3.                                
""")

question_extraction_prompt_2 = PromptTemplate.from_template("""
<context>                                                                                         
{context}
</context>  
This is a request for a proposal. 
Please help me extract any potential questions from the context that could serve as strong topics for a proposal.
If there is no question in the context, just say you don't know.

List the questions in the following format:
1. 
2.
3.
""")

question_extraction_prompt_3 = PromptTemplate.from_template("""
<context>                                                                                         
{context}
</context>  

The context contains multiple questions. Please help me identify any duplicate questions.

- If there are duplicate questions, keep only the first occurrence.
- If a question is unique, retain it as it is in the original context.

List the questions in the following format:
1. 
2.
3.
""")

# context_extraction_template = """
# Please extract any relevant information as much as possible that may answer the following question from the provided text.
# Extract the information related to this question.
# Extract only from the text and give response only with the extracted text.
# If there is no relevant information, respond with "This doesn't provide any relevant information."
# <Question>
# {question}
# </Question>
# <Text>
# {context}
# </Text>
# """


local_context_extraction_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

<query>
{query}
</query>

Extract all the information from the provided text that is related to the query.
Ensure that no relevant details are left out.
Only use the information directly from the text.
If there is no relevant information, respond with "This doesn't provide any relevant information.
""")


background_extraction_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

This is part of a Request for Proposal (RFP).
Please extract and summarize the **Background** section from the provided RFP document.
If the provided text does not contain a clear background section or relevant information, respond with "This doesn't provide any relevant information."
Focus on retaining any key details such as the context for the project, 
and any essential background information that explains why the RFP is being issued.
Keep as many key points as possible, ensuring that all critical background are retained.
""")


background_text_extraction_prompt = PromptTemplate.from_template("""
<text>
{context}
</text>

This is part of a Request for Proposal (RFP).

If "background" or "context" appear is a heading, make a summary of the above text.
Ensure "background" or "context" is a heading in the above text.
Ensure "background" or "context" is a heading in the above text.

If "background" or "context" does not appear as a heading above, respond with "This doesn't provide any relevant information."
Include any essential background information that explains why the RFP is being issued.
Keep as many key points as possible, ensuring that all critical background are retained.
""")


background_compression_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

Help to summarize the **Background** of a Request for Proposal (RFP).
Keep as many key points as possible.
If <background>...</background> is found in the context, summarize the content within those tags first.
""")


objectives_extraction_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

This is part of a Request for Proposal (RFP).
Please extract and summarize the **Objectives** from the provided RFP document.
If the provided text does not contain clear objectives, respond with "This doesn't provide any relevant information."
Include any specific goals, objectives, intended outcomes, Budget, Pricing, Timeline or other abstract objectives that the RFP aims to achieve.
Keep as many key points as possible, ensuring that all critical objectives are retained.
""")


objectives_text_extraction_prompt = PromptTemplate.from_template("""
<text>
{context}
</text>

This is part of a Request for Proposal (RFP).

If "objectives" or "purposes" appear is a title, make a summary of the above text.
Ensure "objectives" or "purposes" is a title in the above text.
Ensure "objectives" or "purposes" is a title in the above text.

If "objectives" or "purposes" does not appear as a heading, respond with "This doesn't provide any relevant information."
Include any specific goals, objectives, intended outcomes, Budget, Pricing, Timeline or other abstract objectives that the RFP aims to achieve.
Keep as many key points as possible, ensuring that all critical objectives are retained.
""")


objectives_compression_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

Help to summarize the **Objectives** of a Request for Proposal (RFP).
Keep as many key points as possible.

If <objectives>...</objectives> is found in the context, summarize the content within those tags first.
""")


scopes_extraction_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

This is part of a Request for Proposal (RFP).

Please extract and summarize the **Scopes** from the provided RFP document.
If the provided text does not contain clear scopes, respond with "This doesn't provide any relevant information."
Focus on identifying the scope of work, key deliverables, and any other specific tasks or services expected from the respondent. 
Keep as many key points as possible, ensuring that all scopes are retained.
""")


scopes_text_extraction_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

This is part of a Request for Proposal (RFP).

If "scopes" or "deliverables" appear is a heading, make a summary of the following text.
Ensure "scopes" or "deliverables" is a heading in the context.
Ensure "scopes" or "deliverables" is a heading in the context.

If "scopes" or "deliverables" does not appear as a heading, respond with "This doesn't provide any relevant information."
Focus on identifying the scope of work, key deliverables, and any other specific tasks or services expected from the respondent. 
Keep as many key points as possible, ensuring that all scopes are retained.
""")


scopes_compression_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

Help to summarize the **Scopes** of a Request for Proposal (RFP).
Keep as many key points as possible.
If <scopes>...</scopes> is found in the context, summarize the content within those tags first.
""")

RFP_summary_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

This is a summary of a Request for Proposal (RFP) including the following sections: **Background**, **Objectives**, and **Scopes**.
There may be overlaps between these sections—please merge any redundant information into a single, cohesive summary.
Compress the content while retaining as many key points as possible.
""")


company_background_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

This is part of a company profile.
Please extract and summarize the **Company Background** from the provided company profile document.
Ensure that the answer is precise, concise.
Include details such as the company's history, technology, core business areas, major achievements, awards, and any relevant background information. Retain all key points to ensure a comprehensive summary of the company's background.
If the provided text does not contain clear information about the company background, respond with "This doesn't provide any relevant information.".
""")


company_background_text_extraction_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

This is part of a Request for Proposal (RFP).

If word "background" appear is a heading, make a summary of the following text.
Ensure the word "background" is a heading in the context.
Ensure the word "background" is a heading in the context.

If the word "background" does not appear as a heading, respond with "This doesn't provide any relevant information."
Include details such as the company's history, technology, core business areas, major achievements, awards, and any relevant background information. Retain all key points to ensure a comprehensive summary of the company's background.
If the provided text does not contain clear information about the company background, respond with "This doesn't provide any relevant information.".
""")


company_background_compression_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

Help to summarize the **Company Background** of a company profile.
Keep as many key points as possible.

If <background>...</background> is found in the context, summarize the content within those tags first.
""")


project_experience_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

This is part of a company profile.
Please extract and summarize the **Project Experience** from the provided company profile document. 
Ensure that the answer is precise, concise.
Focus on identifying the projects undertaken by the company, objectives, technologies used, and outcomes, and any relevant project experience information.
If the provided text does not contain clear information about project experience, respond with "This doesn't provide any relevant information."
""")


project_experience_compression_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

Help to summarize the **Project Experience** of a company profile.
Keep as many key points as possible.
""")


product_services_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

This is part of a company profile.
Please extract and summarize the **Product & Services** from the provided company profile document. 
Ensure that the answer is precise, concise.
Focus on identifying the company's product features, services offered, unique selling propositions, customer base, pricing models, and other relevant details. 
If the provided text does not contain clear information about product & services, respond with "This doesn't provide any relevant information."
""")


product_services_compression_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

Help to summarize the **Product & Services** of a company profile.
Keep as many key points as possible.
""")


team_members_prompt = PromptTemplate.from_template("""
<context>         
{context}
</context>

This is part of a company profile.
Please extract and summarize the **Team Members** from the provided company profile document. 
Focus on identifying key team members, their roles, responsibilities, experience, familiar technology, skills, and notable achievements within the company. 
Ensure that the answer is precise, concise.
If the provided text does not contain clear information about team members, respond with "This doesn't provide any relevant information."
""")


team_members_compression_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

Help to summarzie the **Team Members** of a company profile.
Keep as many key points as possible.
""")


company_profile_summary_prompt = PromptTemplate.from_template("""
<context>
{context}
</context>

This is a summary of a company prifle including the following sections: **Company Background**, **Project Experience**, and **Product & Services**.
There may be overlaps between these sections—please merge any redundant information into a single, cohesive summary.
Compress the content while retaining as many key points as possible. Ensure that the answer is precise, concise.
""")


query_answering_prompt = PromptTemplate.from_template("""
<Company General Context>
{context}
</Company General Context>

<Company Local Context> (IMPORTANT)
{company_local_context}
</Company Local Context>

<RFP General Context>
{rfp_general_context}
</RFP General Context>

<RFP Local Context> (IMPORTANT)
{rfp_local_context}
</RFP Local Context>

Based on the combined context from both the Request for Proposal (RFP) and the company profile, **please pay special attention to the local contexts** for both the company and the RFP, as they are crucial to delivering an accurate and relevant response. **Particularly, the company's local context is critical** in shaping the answer to reflect the company's unique characteristics, capabilities, and approach.
Your answer should consider the relevant details from both the RFP and the company profile, and **must include specific elements and features that are unique to your company**, considering the company's background, project experience, product & serives, team members.
Additionally, if necessary, you may supplement the answer with relevant points not explicitly mentioned in the context, but ensure they are logically inferred or industry-standard insights related to the query.

<Query>
{query}
</Query>

Ensure that the answer is precise, concise, and integrates key points from both the RFP and the company profile, with particular emphasis on **the company's unique local context** and any additional information that enhances the response.
""")


answer_json_conversion_prompt = PromptTemplate.from_template("""
<text>
{context}
</text>
Please convert the above text into JSON format as follows:
1. If the text includes strategies (e.g., numbered or bulleted points), split them into separate objects with "title" and "description" fields under the "strategies" key.
2. If there are no clear strategies, place the entire text into the "heading_text" field and leave "strategies" as an empty array.
3. Use the final paragraph as the "ending_text". If no ending text is available, set "ending_text" to an empty string ("").

Here is the JSON format:

{{
    "heading_text": "{{heading_text}}",
    "strategies": [
        {{
            "title": "{{title1}}",
            "description": "{{description1}}"
        }},
        {{
            "title": "{{title2}}",
            "description": "{{description2}}"
        }},
        ....
    ],
    "ending_text": "{{ending_text}}"
}}
""")


detailed_answer_prompt = PromptTemplate.from_template("""
<Company General Context>
{context}
</Company General Context>

<Company Local Context> 
{company_local_context}
</Company Local Context>

<RFP General Context>
{rfp_general_context}
</RFP General Context>

<RFP Local Context>
{rfp_local_context}
</RFP Local Context>

You are writing a proposal for a Request for Proposal (RFP).
Please provide two well-structured and cohesive paragraphs, with each paragraph containing 150-200 words, 
explaining how to achieve the following query considering the context above. 
Ensure that the response flows naturally and avoid using bullet points or listing key points.

<Query>
{query}
</Query>
""")


company_overview_extraction_prompt = PromptTemplate.from_template("""
<Project Overview>
{project_overview}
</Project Overview>

<Company Profile>
{context}
</Company Profile>

Based on the provided project overview, extract and summarize any relevant company profile that directly relates to the project. 
If the provided text does not contain any relevant company profile, respond with "This doesn't provide any relevant information."
""")


company_overview_prompt = PromptTemplate.from_template("""
<Project Overview>
{project_overview}
</Project Overview>

<Existing Company Profile>
{company_profile}
</Existing Company Profile>

<Additional Company Information>
{context}
</Additional Company Information>

I am drafting a company overview for the bidding party of this project.  
Please enhance and expand the content of "Existing Company Profile" by incorporating relevant details from "Additional Company Information."  
Ensure that the final version:
- Maintains the structure and tone of "Existing Company Profile."  
- Highlights key aspects from "Project Overview." 
- Highlight key aspects and preserve as much key information as possible from "Additional Company Information."
- Integrates important and relevant details from "Additional Company Information" without losing coherence.  
- Preserves a professional and persuasive style suitable for a bidding document.  
""")


time_extraction_prompt = PromptTemplate.from_template("""
<Project>
{context}
</Project>

This text is part of a project document.  
Please extract any time-related information, such as deadlines, milestones, schedules, or any relevant dates mentioned in the document.
If the provided text does not contain any time-related information, respond with "This doesn't provide any relevant information."
""")


general_methodology_and_implementation_prompt = PromptTemplate.from_template("""
<general_rfp_context>
{context}
</general_rfp_context>

<project_timeline>
{time}
</project_timeline>

Based on the provided request for proposal (RFP) context and project timeline, draft a comprehensive **Methodology & Implementation Plan** for the bid proposal.

The plan should include the following sections:
1. **Methodology** - Clearly outline the approach, key principles, and best practices used to execute the project.
2. **Work Breakdown Structure (WBS)** - Provide a structured breakdown of the project phases, including key tasks and deliverables.
3. **Key Milestones & Timeline** - Present a timeline of critical milestones, with estimated completion dates.
4. **Risk Management & Contingency Plan** - Identify potential risks and propose mitigation strategies to ensure project success.

Ensure the response is **detailed, structured, and professional**, while maintaining clarity and conciseness.
""")

methodology_and_implementation_json_conversion_prompt = PromptTemplate.from_template("""
Convert the given methodology and implementation plan into a structured JSON format with the following keys:

{
    "Methodology": "...",
    "Work Breakdown Structure": "...",
    "Key Milestones & Timeline": "...",
    "Risk Management & Contingency Plan": "..."
}

Ensure the JSON is properly formatted and accurately reflects the content.
""")


answer_giving_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", answer_giving_template),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

answer_giving_prompt_with_memory = ChatPromptTemplate.from_messages(
    [
        ("system", answer_giving_template_with_memory),
        MessagesPlaceholder("chat_history"),
        MessagesPlaceholder(variable_name="messages"),
        # ("human", "{input}"),
    ]
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt_template),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

def create_chain(model, prompt):
    document_chain = create_stuff_documents_chain(model, prompt)
    return document_chain


def create_parallel_chain(len, chain):
    parallel_chain = RunnableParallel({
        f"response_{i}": chain for i in range(len)
    })
    return parallel_chain


def execute_chain_without_memory(document_chain, question, context):
    messages = [
        HumanMessage(content=question),
    ]
    response = document_chain.invoke({"messages": messages, "context": context})
    return response


def execute_chain_with_memory(document_chain, question, context, chat_history):
    messages = [
        HumanMessage(content=question),
    ]
    response = document_chain.invoke({"messages": messages, "context": context, "chat_history": chat_history})
    return response


def create_history(question, answer):
    history = [HumanMessage(content=question), HumanMessage(content=answer)]
    return history
