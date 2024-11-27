import streamlit as st
from PIL import Image
import requests
import os
import json
import shutil

st.set_page_config(layout="wide")
st.title("Linkedln Post Generator")
columns = st.columns(2)

if 'app_name' not in st.session_state:
    st.session_state.app_name = ''

if 'app_context' not in st.session_state:
    st.session_state.app_context = ''

if 'app_images' not in st.session_state:
    st.session_state.app_images = None

if 'tech_stack' not in st.session_state:
    st.session_state.tech_stack = None

if 'generate_text' not in st.session_state:
    st.session_state.generate_text = None
url = "http://127.0.0.1:8000"

def generate_text_col():
    st.subheader("Generated Text")
    if st.session_state.generate_text is not None:
        title_textbox = st.text_input("title",value=st.session_state.generate_text['title'])
        body_textbox = st.text_area("body",value=st.session_state.generate_text['body'],height=300)
    else:
        st.write("Enter data first")
def data_input_form():
    st.subheader("Data Input")
    with st.form("data_form"):
        
        st.session_state.app_name = st.text_input("App name")
        st.session_state.app_context = st.text_area("App context")
        st.session_state.tech_stack = st.text_area("Tech stack")

        app_images = st.file_uploader("Choose images", type=["jpg", "jpeg", "png"])

        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 2])  # Adjust ratios for spacing
            with col2:
                generate = st.form_submit_button("Generate")
            with col5:
                publish = st.form_submit_button("Publish")

        if generate:
            generate_url = url+"/llm"
            
            st.session_state.generate_text = requests.post(generate_url, json={"app_name": st.session_state.app_name, "app_context": st.session_state.app_context,"tech_stack":st.session_state.tech_stack}).json()
            
        if publish:
            linkedin_url = url+"/api"
            data = {"title": st.session_state.generate_text['title'], "content": st.session_state.generate_text['body']}

            if not os.path.exists("temp"):
                os.mkdir("temp")
                    

            if app_images is not None:
                files = {}
                image_bytes = app_images.read()

                files['images']= ('image.png', image_bytes, 'image/png')
                
                

                response = requests.post(linkedin_url,data=data,files=files)
            else:
                response = requests.post(linkedin_url, data=data)
                

            

            if response['success'] == 200:
                st.snow()



with columns[0]:
    data_input_form()
    
with columns[1]:
    generate_text_col()