import os
import getpass
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods
from ibm_watson_machine_learning.foundation_models.extensions.langchain import WatsonxLLM

from pymongo import MongoClient


# from ibm_watsonx_ai import Credentials
# from ibm_watsonx_ai.foundation_models import ModelInference
# from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
# from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes, DecodingMethods

# watsonx URL

try:
    wxa_url = os.environ["WXA_URL"] 
    # wxa_url = os.environ["https://eu-gb.ml.cloud.ibm.com"] 
    #https://api.eu-gb.dataplatform.cloud.ibm.com/wx NOT THIS
    # https://eu-gb.ml.cloud.ibm.com

except KeyError:
    wxa_url = getpass.getpass("Please enter your watsonx.ai URL domain (hit enter): ")


# watsonx API Key

try:
    # wxa_api_key = os.environ["ew9FSpkxGdAS91FvT_t4CjC30JYF-vRZayqRMDs7Afsb"]
    wxa_api_key = os.environ["WXA_API_KEY"]
    #ew9FSpkxGdAS91FvT_t4CjC30JYF-vRZayqRMDs7Afsb
except KeyError:
    wxa_api_key = getpass.getpass("Please enter your watsonx.ai API key (hit enter): ")


# watsonx Project ID

try:
    # wxa_project_id = os.environ["573a5af9-21d8-414c-90ea-ca983ffa683c"]
    wxa_project_id = os.environ["WXA_PROJECT_ID"]
    # 573a5af9-21d8-414c-90ea-ca983ffa683c
except KeyError:
    wxa_project_id = getpass.getpass("Please enter your watsonx.ai Project ID (hit enter): ")

# Init Mongo Client
try:
    MONGO_CONN = os.environ["MONGO_CONN"]
except KeyError:
    MONGO_CONN = getpass.getpass("Please enter your MongoDB connection String (hit enter): ")


# Language Model

parameters = {
    GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.MAX_NEW_TOKENS: 200
}


model = Model(
    # model_id=ModelTypes.GRANITE_13B_INSTRUCT_V2,
    model_id="ibm/granite-13b-instruct-v2",
    params=parameters,
    credentials={
        "url": wxa_url,
        "apikey": wxa_api_key
    },
    project_id=wxa_project_id
)

granite_llm_ibm = WatsonxLLM(model=model)

query = "I want to introduce my daughter to science and spark her enthusiasm. What kind of gifts should I get her?"

# Sample LLM query without RAG framework
result = granite_llm_ibm(query)
# print(result)
print(".\n".join(i.strip() for i in result.split(".")))
