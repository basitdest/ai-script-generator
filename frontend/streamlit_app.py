import streamlit as st
import requests
import os
from dotenv import load_dotenv
load_dotenv()

API_URL = "http://127.0.0.1:8000/generate"

st.set_page_config(page_title='AI Script Generator', layout='wide')

st.header('AI-Powered Script Generator')

with st.sidebar:
    st.markdown('**Options**')
    lang = st.selectbox('Language', ['python', 'powershell'])
    run_locally = st.checkbox('Enable Run (LOCAL)', value=False)
    max_tokens = st.slider('Model response size (tokens)', 200, 2000, 900)
    st.markdown('**Security**')
    st.markdown('Generated scripts are potentially dangerous. Use a disposable environment (Docker).')

prompt = st.text_area('Describe what you want the script to do', height=160, value='Fetch the last OTP email and store in a text file.')

col1, col2 = st.columns([2,1])

with col1:
    if st.button('Generate'):
        payload = {'prompt': prompt, 'language': lang, 'run': False}
        with st.spinner('Generating…'):
            r = requests.post(f'{API_URL}/generate', json=payload, timeout=60)
        if r.status_code != 200:
            st.error(f'Error: {r.text}')
        else:
            j = r.json()
            if not j.get('ok'):
                st.warning('Generation returned safety warning or error')
                st.json(j)
            else:
                code = j['code']
                st.session_state['last_code'] = code
                st.session_state['last_meta'] = j.get('meta')
                st.success('Generated — preview below')

    if 'last_code' in st.session_state:
        st.subheader('Script Preview')
        st.code(st.session_state['last_code'], language='python' if lang=='python' else 'powershell')

with col2:
    st.subheader('Actions')
    if 'last_code' in st.session_state:
        st.download_button('Download script', data=st.session_state['last_code'], file_name=(st.session_state.get('last_meta', {}).get('filename') or f'script.{"py" if lang=="python" else "ps1"}'))
        if run_locally:
            if st.button('Run Locally (Unsafe — use Docker)'):
                payload = {'prompt': prompt, 'language': lang, 'run': True}
                with st.spinner('Running…'):
                    r = requests.post(f'{API_URL}/generate', json=payload, timeout=120)
                if r.status_code==200:
                    j = r.json()
                    if j.get('run_output'):
                        st.subheader('Run Output')
                        st.text('Returncode: ' + str(j['run_output'].get('returncode')))
                        st.text('Stdout:')
                        st.text(j['run_output'].get('stdout') or '')
                        st.text('Stderr:')
                        st.text(j['run_output'].get('stderr') or '')
                else:
                    st.error(r.text)
    else:
        st.info('Generate a script to unlock download/run actions')

st.markdown('---')
st.markdown('**Logs / Raw LLM output**')
if st.checkbox('Show raw LLM output'):
    st.text_area('Raw', value=st.session_state.get('last_raw', ''), height=200)