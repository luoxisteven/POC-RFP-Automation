import os
from key import *
from langchain.globals import set_verbose, set_debug

os.environ["OPENAI_API_KEY"] = openai.api_key
os.environ["GOOGLE_API_KEY"] = gemini_key
CONFIG_RFP_PATH = "./data/rfp/project_6"
CONFIG_COMPANY_PROFILE_PATH = "./data/company_profile"

# Debug config
# set_debug(True)
# set_verbose(True)