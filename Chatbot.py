from RAG_Chain import *
from src.timer import *

class ChatBot:
    def __init__(self,rag_chain=RAG_Chain()):
        self.rag_chain = rag_chain

    # def start_with_memory(self):
    #     print(start_msg())
    #     while True:
    #         question = input('Input: ')
    #         if question == "exit" or question == "e":
    #             answer = exit_msg()
    #             print(answer)
    #             break
    #         else:
    #             answer = self.rag_chain.get_answer_with_memory(question)
    #         print(answer)

    def start_without_memory(self):
        print(start_msg())
        while True:
            query = input('Input: ')
            timer = Timer()
            timer.start()
            if query == "exit" or query == "e":
                answer = exit_msg()
                print(answer)
                break
            else:
                answer = self.rag_chain.get_answer_without_memory(query)
            print("\n\nQuery: "+query+"\n")
            print(answer)
            timer.end()

    def start_one_time(self, query):
        answer = self.rag_chain.get_answer_without_memory(query)
        print(answer)




def start_msg():
    start_msg = """
    This is a chatbot for your Requests For Proposal (RFP) with company profile.
    Or you can input "exit" or "e" to exit the chatbot.
    Or you can input any query.\n
    """
    return start_msg


def exit_msg():
    exit_msg = """
    You are exiting the chatbot..
    """
    return exit_msg


if __name__ == "__main__":
    chatbot = ChatBot()
    chatbot.start_without_memory()
