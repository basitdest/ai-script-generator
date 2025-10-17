import streamlit as st
import requests
import os
from dotenv import load_dotenv
load_dotenv()


API_URL = os.getenv('API_URL', 'http://localhost:8000')


st.set_page_config(page_title='AI Script Generator', layout='wide')


st.header('AI-Powered Script Generator')