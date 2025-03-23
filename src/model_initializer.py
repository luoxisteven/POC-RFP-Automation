from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_google_vertexai import VertexAI
# from langchain_ollama.llms import OllamaLLM
from langchain_core.rate_limiters import InMemoryRateLimiter

# def chat_gpt(model_name="gpt-4o-mini", temperature=0):
#     model = ChatOpenAI(model=model_name, temperature=temperature, max_tokens=3000)
#     return model

def chat_gpt(model_name="gpt-4o-mini", temperature=0):
    model = ChatOpenAI(model=model_name, temperature=temperature)
    return model

def gemini(model_name="gemini-1.5-pro", temperature=0):
    model = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
    return model

# def llama(model_name="llama3.1"):
#     model = OllamaLLM(model=model_name)
#     return model

# Currently Conflict with ChatOpenAI
# def vertex(model_name, temperature=0):
#     model = VertexAI(model_name=model_name, temperature=temperature)
#     return model

def llm_model(model_name):
    if("gpt" in model_name):
        return chat_gpt(model_name)
    elif("gemini" in model_name):
        return gemini(model_name)
    # elif("llama" in model_name):
    #     return llama(model_name)
    
def rate_limiter():
    rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.1,  # <-- Super slow! We can only make a request once every 10 seconds!!
    check_every_n_seconds=0.1,  # Wake up every 100 ms to check whether allowed to make a request,
    max_bucket_size=10,  # Controls the maximum burst size.
)

