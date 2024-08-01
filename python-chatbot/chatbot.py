import streamlit as st
import time

st.title("I'm Walter from WaterAid!")

### HELPER FUNCTIONS #################
def validate_age_not_num(age): #returns True if age is not numeric
    if not age.isnumeric():
        return True
    else:
        return False
    
def validate_age_not_valid(age): #returns True if age is not valid
    if int(age) < 13 or int(age) > 120:
        return True
    else:
        return False

#######################################

# Initialise chat history
if "messages" not in st.session_state:
    # st.session_state.messages = []
    st.session_state.messages = [{"role": "Walter", "content": "Whereabouts are you based in? Which location would you prefer?"}]
if "question_index" not in st.session_state:
    st.session_state.question_index = 1

# Define the questions
questions = [
    "Whereabouts are you based in? Which location would you prefer?",
    "How old are you? Type a number!",
    "What do you do for a living?",
    "Do you have any past work experiences? Separate by comma if you have multiple experiences. Use 'NA' if you do not have any experience.",
    "What skills (hard/soft) do you have? Separate by comma if you have multiple skills.",
    "What do you like to do in your free time? Separate by comma if you have multiple interests/hobbies."
]

welc = "Welcome, I’m Walter from WaterAid. Help me answer a few questions and I can help you find activities that you may enjoy while contributing to our cause!"
st.markdown("Welcome, I’m Walter from WaterAid. Help me answer a few questions and I can help you find activities that you may enjoy while contributing to our cause!")
st.divider()

# Build Q&A dialogue conversation & Accept User input
def chat():
    prompt = st.chat_input("Type something...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Get correct question index - If user input asks to run recommendation again
        if st.session_state.messages[-2]["content"] != "What do you like to do in your free time? Separate by comma if you have multiple interests/hobbies.":
            if prompt == "Again" or prompt == "again":
                st.session_state.question_index = 0

        if st.session_state.question_index < len(questions):
            # Validate user inputs to qn on age
            if st.session_state.question_index == 2: 
                last_msg = st.session_state.messages[-1]["content"]
                if validate_age_not_num(last_msg):
                    warning = "Please enter a number!"
                    st.session_state.messages.append({"role": "Walter", "content": warning})
                else:
                    if validate_age_not_valid(last_msg):
                        warning = "Your age must be between 13 to 120 (inclusive)!"
                        st.session_state.messages.append({"role": "Walter", "content": warning})
                    else:
                        Walter_res = questions[st.session_state.question_index]
                        st.session_state.messages.append({"role": "Walter", "content": Walter_res})
                        st.session_state.question_index += 1
            
            else:
                Walter_res = questions[st.session_state.question_index]
                st.session_state.messages.append({"role": "Walter", "content": Walter_res})
                st.session_state.question_index += 1
        else:
            if st.session_state.messages[-2]["content"] != "What do you like to do in your free time? Separate by comma if you have multiple interests/hobbies.":
                if prompt != "Again" or prompt != "again":
                    bye_msg = "Thank you for using our recommendation service! Type 'Again' anytime to restart the service"
                    st.session_state.messages.append({"role": "Walter", "content": bye_msg})

            else: # No more questions, provide recommendations
                summary = "Based on your responses, here are the top 3 activities recommended for you:"
                st.session_state.messages.append({"role": "Walter", "content": summary})
                
                feedback = "Are you satisfied with our recommendations? If not, type 'Again' to run the recommendation service again!"
                st.session_state.messages.append({"role": "Walter", "content": feedback})
            

chat()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message['content'] == "Are you satisfied with our recommendations? If not, type 'Again' to run the recommendation service again!":
        time.sleep(3)
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

