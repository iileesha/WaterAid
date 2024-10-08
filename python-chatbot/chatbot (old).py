## THIS STREAMLIT CHATBOT SCRIPT IS OLD AND ONLY FOR INTERNAL REFERENCE (NOT FOR ACTUAL IMPLEMENTATION). 
## THIS WAS USED TO TEST ALTERNATIVE METHODS, APPROACHES, AND IMPLEMENTATIONS. 

import streamlit as st
import time

from langchain.vectorstores.pgvector import PGVector
import pandas as pd
import numpy as np
from langchain.document_loaders import DataFrameLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores.pgvector import DistanceStrategy
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods
from ibm_watson_machine_learning.foundation_models.extensions.langchain import WatsonxLLM


# Set up Connections to database and Watsonx AI for LLM Models
CONNECTION_STRING = "postgresql://postgres:123456@localhost:5433/wateraid"
wxa_url = "https://eu-gb.ml.cloud.ibm.com"
# wxa_api_key = "ew9FSpkxGdAS91FvT_t4CjC30JYF-vRZayqRMDs7Afsb" # old because hit monthly token limit
wxa_api_key = "7AMq7kpxXp8tJTMo-_qj59FhEcC5ewkTS_pAPfOgAjFz" 
# wxa_project_id = "573a5af9-21d8-414c-90ea-ca983ffa683c" # old because hit monthly token limit
wxa_project_id = "f65d106f-b186-418b-8c00-f67cd14f95cf"

# Set up Watsonx Granite LLM Model

def LLM_set_up():
    parameters = {
        GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
        GenParams.MIN_NEW_TOKENS: 1,
        GenParams.MAX_NEW_TOKENS: 500
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

    return granite_llm_ibm

# Connect to DB and set up retriever and receive response for query
def DB_retrieve_and_query(query):
    embeddings = HuggingFaceEmbeddings()

    store = PGVector(
        connection_string=CONNECTION_STRING, 
        embedding_function=embeddings, 
        collection_name="listings_documents",
        distance_strategy=DistanceStrategy.COSINE
    )

    retriever = store.as_retriever(search_kwargs={"k": 6})

    prompt = PromptTemplate(template="""

        Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
        {context}

        ##Question:{question} \n\

        ##Top 3 recommnedations of activities:\n""",input_variables=["context","question"])

    chain_type_kwargs = {"prompt": prompt}

    qa = RetrievalQA.from_chain_type(llm=LLM_set_up(), chain_type="stuff",
                                        retriever=retriever,
                                        chain_type_kwargs=chain_type_kwargs,
                                        verbose=True)

    retrieved_docs = retriever.get_relevant_documents(query)

    links = ""
    for doc in retrieved_docs:
        doc_metadata = doc.metadata
        temp = doc_metadata['Listing URL'] + "\n"
        links += temp

    res = qa.run(query)

    d = {'response': res,
         'links': links}
    return d


st.title("I'm Walter from WaterAid!")

### HELPER FUNCTIONS #################


#######################################

# Initialise chat history
if "messages" not in st.session_state:
    # st.session_state.messages = []
    st.session_state.messages = [{"role": "Walter", "content": "What do you like to do in your free time? Separate by comma if you have more than 2 interests/hobbies. \n Hint: I like to _________________ in my free time. Fill in the blanks."}]
if "question_index" not in st.session_state:
    st.session_state.question_index = 1
if "query" not in st.session_state:
    st.session_state.query = ""

# Define the questions
questions = [
    "What do you like to do in your free time? Separate by comma if you have multiple interests/hobbies. \n Hint: I like to _________________ in my free time. Fill in the blanks.",
    "Whereabouts are you based in? Which location would you prefer? \n Hint: I am based in _______. Fill in the blanks."
    # "How old are you? Type a number!",
    # "What do you do for a living?"
    # "Do you have any past work experiences? Separate by comma if you have multiple experiences. Use 'NA' if you do not have any experience.",
    # "What skills (hard/soft) do you have? Separate by comma if you have multiple skills.",
    
]

st.markdown("Welcome, I’m Walter from WaterAid. Help me answer a few questions and I can help you find activities that you may enjoy while contributing to our cause!")
st.divider()

# Build Q&A dialogue conversation & Accept User input
def chat():
    prompt = st.chat_input("Type something...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Get correct question index - If user input asks to run recommendation again
        if st.session_state.messages[-2]["content"] != "Whereabouts are you based in? Which location would you prefer? \n Hint: I am based in _______. Fill in the blanks.":
            if prompt == "Again" or prompt == "again":
                st.session_state.question_index = 0
                st.session_state.query = ""

        if st.session_state.question_index < len(questions):
            if st.session_state.question_index == 1:
                temp = "I like to " + prompt + " in my free time. "
                st.session_state.query += temp

            Walter_res = questions[st.session_state.question_index]
            st.session_state.messages.append({"role": "Walter", "content": Walter_res})
            st.session_state.question_index += 1

        else:
            temp = "I am based in " + prompt + ". What activities are recommended for me based on the context provided - give the specific name of the activity? Give a reason why each activity is recommended for me."
            st.session_state.query += temp
            if st.session_state.messages[-2]["content"] != "Whereabouts are you based in? Which location would you prefer? \n Hint: I am based in _______. Fill in the blanks.":
                if prompt != "Again" or prompt != "again":
                    bye_msg = "Thank you for using our recommendation service! Type 'Again' anytime to restart the service"
                    st.session_state.messages.append({"role": "Walter", "content": bye_msg})

            else: # No more questions, provide recommendations
                print(st.session_state.query)

                summary = "Based on your responses, here are the top 3 activities recommended for you: \n" 
                st.session_state.messages.append({"role": "Walter", "content": summary})

                # with st.spinner('Please wait while results load'):
                #     time.sleep(5)

                retrieve = DB_retrieve_and_query(st.session_state.query)
                response = retrieve['response']
                urls = retrieve['links']
                print(response)
                print(urls)

                res = response + "\n \n" + urls
                st.session_state.messages.append({"role": "Walter", "content": res})
                
                feedback = "Are you satisfied with our recommendations? If not, type 'Again' to run the recommendation service again!"
                st.session_state.messages.append({"role": "Walter", "content": feedback})
            

chat()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message['content'] == "Are you satisfied with our recommendations? If not, type 'Again' to run the recommendation service again!":
        time.sleep(3)

    # if message['content'] == "Based on your responses, here are the top 3 activities recommended for you: \n":
    #     time.sleep(3)
    with st.chat_message(message["role"]):
        if message['content'] == "Based on your responses, here are the top 3 activities recommended for you: \n":
            with st.spinner('Loading... Please wait.'):
                    time.sleep(8)
        st.markdown(message["content"])

        # if message['content'] == "Based on your responses, here are the top 3 activities recommended for you: \n":
        #     with st.spinner('Loading... Please wait.'):
        #             time.sleep(8)
            
        #     retrieve = DB_retrieve_and_query(st.session_state.query)
        #     response = retrieve['response']
        #     urls = retrieve['links']
        #     print(response)
        #     print(urls)

        #     res = response + "\n \n" + urls
        #     # st.markdown(message["content"])
        #     st.session_state.messages.append({"role": "Walter", "content": res})
                
        #     feedback = "Are you satisfied with our recommendations? If not, type 'Again' to run the recommendation service again!"
        #     st.session_state.messages.append({"role": "Walter", "content": feedback})
        

