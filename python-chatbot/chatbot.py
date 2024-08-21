import streamlit as st
import time
# from helper import *

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


### HELPER FUNCTIONS #################

# Set up Connections to database and Watsonx AI for LLM Models
CONNECTION_STRING = "postgresql://postgres:123456@localhost:5433/wateraid"
wxa_url = "https://eu-gb.ml.cloud.ibm.com"
# wxa_api_key = "ew9FSpkxGdAS91FvT_t4CjC30JYF-vRZayqRMDs7Afsb" # old because hit monthly token limit
# wxa_api_key = "7AMq7kpxXp8tJTMo-_qj59FhEcC5ewkTS_pAPfOgAjFz" # second account also hit monthly token limit
# wxa_api_key = "1BPdoGgE0gnc9HmADHed524_M9K2uLHdYCdIpDs6DSNp" #third account but will be focused to use for watson assistant chatbot (if current uncommented account hits limit, can use this instead)
wxa_api_key = "NG7zfeBgtz4YD4u91QXzOkgvdGlGSzYRxgtRmTebgitK" #focused to use for python chatbot

# wxa_project_id = "573a5af9-21d8-414c-90ea-ca983ffa683c" # old because hit monthly token limit
# wxa_project_id = "f65d106f-b186-418b-8c00-f67cd14f95cf" # second account also hit monthly token limit
# wxa_project_id = "a1acd8b8-07ce-461f-b512-e9854d00c075" #third account but will be focused to use for watson assistant chatbot (if current uncommented account hits limit, can use this instead)
wxa_project_id = "5ca8251a-a60f-4ef0-a9fe-bb65a3f72448" #focused to use for python chatbot

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
#######################################

st.title("I'm Walter from WaterAid!")

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
    "Do you have any present/past work/volunteering experiences? Separate by comma if you have more than two experiences. Use 'NA' if you do not have any experience. \n Hint: I have experiences as a ____________________. Fill in the blanks if you have any experiences.",
    "Whereabouts are you based in? Which location would you prefer? \n Hint: I am based in _______. Fill in the blanks."
    # "How old are you? Type a number!",
    # "What do you do for a living?"
    # "What skills (hard/soft) do you have? Separate by comma if you have multiple skills.",
    
]

st.markdown("Welcome, I’m Walter from WaterAid. Help me answer a few questions and I can help you find activities that you may enjoy while contributing to our cause!")
st.markdown("NOTE: I am a chatbot and not a real person, and will not be able to offer any services or answers outside of the designed chat!")
st.markdown("NOTE ALSO: If you find that results are not great, fill in 'NA' for the question on work/ volunteering experience.")
st.divider()

# Build Q&A dialogue conversation & Accept User input

prompt = st.chat_input("Type something...")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get correct question index - If user input asks to run recommendation again
    if st.session_state.messages[-2]["content"] != "Whereabouts are you based in? Which location would you prefer? \n Hint: I am based in _______. Fill in the blanks.":
        if prompt == "Again" or prompt == "again":
            st.session_state.question_index = 0
            st.session_state.query = ""

    if st.session_state.question_index < len(questions):
        if st.session_state.question_index == 1:
            temp = "I like to " + prompt + " in my free time. "
            st.session_state.query += temp

        elif st.session_state.question_index == 2:
            if prompt == "NA" or prompt == "na" or prompt == "no" or prompt == "No":
                temp = ""
            else:
                temp = "I have experiences as a " + prompt
            st.session_state.query += temp
        Walter_res = questions[st.session_state.question_index]
        st.session_state.messages.append({"role": "Walter", "content": Walter_res})
        st.session_state.question_index += 1
        with st.chat_message("Walter"):
            st.markdown(Walter_res)

    else:
        temp = "I am based in " + prompt + ". "
        temp2 = ". What activities are recommended for me based on the activities in the context provided - give the specific name of the activity? Give a reason why each activity is recommended for me."
        st.session_state.query = temp + st.session_state.query + temp2
        if st.session_state.messages[-2]["content"] != "Whereabouts are you based in? Which location would you prefer? \n Hint: I am based in _______. Fill in the blanks.":
            if prompt != "Again" or prompt != "again":
                bye_msg = "Thank you for using our recommendation service! Type 'Again' anytime to restart the service"
                st.session_state.messages.append({"role": "Walter", "content": bye_msg})
                with st.chat_message("Walter"):
                    st.markdown(bye_msg)

        else: # No more questions, provide recommendations
            print(st.session_state.query)

            summary = "Based on your responses, here are the top 3 activities recommended for you: \n" 
            st.session_state.messages.append({"role": "Walter", "content": summary})
            with st.chat_message("Walter"):
                st.markdown(summary)

                with st.spinner('Please wait while results load'):
                    time.sleep(5)

                    retrieve = DB_retrieve_and_query(st.session_state.query)
                    response = retrieve['response']
                    urls = retrieve['links']
                    print(response)
                    print(urls)

                res = response + "\n \n Links for above activities and other potential activities: \n \n" + urls
                st.session_state.messages.append({"role": "Walter", "content": res})
                st.markdown(res)
                
            feedback = "Are you satisfied with our recommendations? If not, type 'Again' to run the recommendation service again!"
            st.session_state.messages.append({"role": "Walter", "content": feedback})
            time.sleep(2)
            with st.chat_message("Walter"):
                st.markdown(feedback)

