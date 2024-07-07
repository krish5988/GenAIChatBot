import streamlit as st
import random
import time
from geminiResponse import geminiResponseGenerator
from io import StringIO
import os
import base64
from queryFromDocs import queryDocs
from dotenv import load_dotenv
import pickle
import datetime
load_dotenv()
st.set_page_config(page_title="Q&A AutoMate",
                   page_icon="qaauto.ico")
st.title("QA Testcase Maker")
st.sidebar.image("qaauto.ico", use_column_width=True)
geminiResponse=geminiResponseGenerator()
queryDocument=queryDocs()

# Initialize chat history
if os.getenv("FILE_UPLOAD_STATUS") != "1":
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        os.environ['FILE_UPLOAD_STATUS']="0"
        st.session_state.messages.append({"role":"FileUploader", "content":"No File Uploaded"})
    
    


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["content"]!="File Uploaded":
        if geminiResponseGenerator.response=="":
            uploaded_file = st.file_uploader("Choose a file",key=1)
            if uploaded_file is not None:
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                string_data = stringio.read()
                resp=geminiResponse.getResponseForQuery(string_data)
                st.markdown("Response :",unsafe_allow_html=True)
                
                queryDocument.augmentedUserQuery(string_data)
                st.session_state.messages.append({"role":"ResponseGemini", "content":geminiResponseGenerator.response})
                st.session_state.messages.append({"role":"FileUploader", "content":"File Uploaded"})
                os.environ['FILE_UPLOAD_STATUS']="1"
                with st.spinner('Waiting for document to be prepared...'):
                    time.sleep(5)
                st.success('Document prepared.')
        
    if message["role"]!="FileUploader":   
        if message["role"]=="ResponseGemini":
            st.markdown(message["content"])
            st.download_button('Download Test Cases', geminiResponseGenerator.response, "BusinessTestCases.txt",'text/plain',key=datetime.datetime.now().strftime("%c"))
        elif message["role"]=="user":
            st.markdown(":orange[User] : "+message["content"])
        elif message["role"]=="bot":
            st.markdown(":green[Bot] : "+message["content"])
        

    
#         if len(message["content"])>0:
#             st.markdown("hello")


# Accept user input
if prompt := st.chat_input("Query uploaded documents.."):

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
    botmsg=st.chat_message("bot")
    botmsg.write(queryDocument.getQueryResponse(prompt)["output_text"])
    # with st.chat_message("bot"):
    #     time.sleep(1)
    #     st.markdown(queryDocument.getQueryResponse(prompt)["output_text"])
    st.session_state.messages.append({"role": "bot", "content": queryDocument.getQueryResponse(prompt)["output_text"]})
    # st.session_state.messages.append({"role": "user", "content": prompt})

    # Add user message to chat history
