import asyncio
import time
from RAG_Chain_new import RAG_Chain  # 确保你已经正确导入 RAG_Chain

async def main():
    # 创建 RAG_Chain 实例
    rag_chain = RAG_Chain(verbose=True, rfp_path="./data/rfp/project_5")
    
    # 开始计时
    start_time = time.time()
    
    # 调用异步方法并获取结果
    # answer = await rag_chain.simple_query_answering("How to perform cybersecurity?")
    answer = await rag_chain.detailed_query_answering("How to perform cybersecurity?")
    
    # 结束计时
    end_time = time.time()
    
    # 打印结果和耗时
    print(f"Answer: {answer}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

# 异步运行主函数
if __name__ == "__main__":
    asyncio.run(main())



# rag_chain = RAG_Chain(verbose=True)

# # 获取事件循环
# loop = asyncio.get_event_loop()

# # 调用异步方法并等待结果
# result = loop.run_until_complete(asyncio.gather(rag_chain.extract_company_team_members()))
# print(result[0])


# 运行主程序

# Chatbot Mode
# chatbot = ChatBot(rag_chain)
# chatbot.start_without_memory()

# # Question Extraction
# questions_with_question_mark = rag_chain.retrieve_question_with_question_mark_using_regex()
# questions_without_question_mark = rag_chain.retrieve_question_without_question_mark()



# # Query
# rag_chain = rag_chain.query_answering("How to perform cybersecurity")

# 文件名：remove_versions.py

# 读取带版本号的 requirements.txt
# with open("requirements.txt", "r") as infile:
#     lines = infile.readlines()

# # 去掉版本号并写入新的文件
# with open("requirements_no_version.txt", "w") as outfile:
#     for line in lines:
#         # 只取包名部分，忽略 '==' 后的版本号
#         package = line.split("==")[0]
#         outfile.write(package + "\n")

# print("已生成不带版本号的 requirements_no_version.txt 文件")


# scp -i /Users/stev/Desktop/RFP_LLM/rfp.pem -r /Users/stev/Desktop/RFP_LLM/vue_front/dist/* ubuntu@3.107.19.137:/var/www/html/