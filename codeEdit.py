# linux 可进行
import streamlit as st
import requests
from dotenv import load_dotenv
load_dotenv()

def codeEdit(code):
    run_button = st.button('运行代码',key='runcode')
    if run_button:
        try:
            response = requests.post('http://localhost:8000/execute', json={'code': code})
            if response.status_code == 200:
                st.success('代码运行成功')
                result = response.json()
                if 'output' in result:
                    st.text(result['output'])
                else:
                    st.error('响应中没有找到输出结果')
            else:
                st.error('代码运行失败')
                st.text(response.json()['error'])
        except requests.ConnectionError:
            st.error('无法连接到后端服务，请确保后端服务正在运行。')
