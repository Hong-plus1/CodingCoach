import streamlit as st
import requests
from streamlit_ace import st_ace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

# Template for generating programming problems
template_problem = """请扮演一位资深的编程教练，您将负责为学生生成程算法题目，确保题目符合学生编程水平。
        1. 根据学生提供的知识点以及学生的编程水平满分为100，分析其相关性和难度。
        2. 确定与该知识点相关的一个经典编程题型，包括但不限于算法、数据结构、系统设计等方面。
        3. 为经典题型提供简要描述，确保描述清晰易懂。
        4. 输出的内容应包括题目名称、题目描述、输入输出要求及示例。
        5. 根据学生的回答代码进行分析，对编程水平进行加减，主要是针对本题目涉及的算法进行评分，细节上的错误仅做提示，并针对代码提出建议。
        6. 确保提供的建议不包括具体代码。"""
prompt_problem = ChatPromptTemplate.from_messages([("system", template_problem),
                                                   ("human", "{input}")])
model_problem = ChatOpenAI(model="gpt-4o-mini")
chain_problem = prompt_problem | model_problem | StrOutputParser()

# Template for evaluating code
template_evaluation = """请扮演一位资深的编程教练，您将负责对学生提交的代码进行评估。
        1. 根据学生提交的代码，分析其正确性和效率。
        2. 提供详细的反馈，包括代码的优点和需要改进的地方。
        3. 确保提供的反馈不包括具体代码。"""
prompt_evaluation = ChatPromptTemplate.from_messages([("system", template_evaluation),
                                                      ("human", "{code}")])
model_evaluation = ChatOpenAI(model="gpt-4o-mini")
chain_evaluation = prompt_evaluation | model_evaluation | StrOutputParser()

st.title('编程教练-生成题目')
with st.form(key='my_form'):
    input = st.text_input(label='输入知识点和学生编程水平')
    submit_button = st.form_submit_button(label='生成题目')
    if submit_button:
        st.info(chain_problem.invoke(input))

st.title('在线代码编辑和调试')
code = st_ace(language='python', theme='monokai', key='editor')
run_button = st.button('运行代码')

if run_button:
    try:
        response = requests.post('http://localhost:8000/execute', json={'code': code})
        if response.status_code == 200:
            st.success('代码运行成功')
            st.text(response.json()['output'])
            
            # Evaluate the code using the agent
            evaluation_result = chain_evaluation.invoke(code)
            st.info("代码评估结果：")
            st.info(evaluation_result)
        else:
            st.error('代码运行失败')
            st.text(response.json()['error'])
    except requests.ConnectionError:
        st.error('无法连接到后端服务，请确保后端服务正在运行。')

chain_problem.get_graph().print_ascii()