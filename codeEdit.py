#linux 可进行
import streamlit as st
import requests
from streamlit_ace import st_ace
from dotenv import load_dotenv
load_dotenv()

st.title('在线代码编辑和调试')
code = st_ace(language='python', theme='monokai', key='editor')
run_button = st.button('运行代码')

if run_button:
    try:
        response = requests.post('http://localhost:8000/execute', json={'code': code})
        if response.status_code == 200:
            st.success('代码运行成功')
            st.text(response.json()['output'])
        else:
            st.error('代码运行失败')
            st.text(response.json()['error'])
    except requests.ConnectionError:
        st.error('无法连接到后端服务，请确保后端服务正在运行。')
