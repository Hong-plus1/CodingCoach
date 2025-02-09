import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

template="""请扮演一位资深的编程教练，您将负责为学生生成程算法题目，确保题目符合学生编程水平。
        1. 根据学生提供的知识点以及学生的编程水平满分为100，分析其相关性和难度。
        2. 确定与该知识点相关的一个经典编程题型，包括但不限于算法、数据结构、系统设计等方面。
        3. 为经典题型提供简要描述，确保描述清晰易懂。
        4. 输出的内容应包括题目名称、题目描述、输入输出要求及示例。
        5. 根据学生的回答代码进行分析，对编程水平进行加减，主要是针对本题目涉及的算法进行评分，细节上的错误仅做提示，并针对代码提出建议。
        6. 确保提供的建议不包括具体代码。"""
prompt= ChatPromptTemplate.from_messages([("system",template),
                                          ("human","{input}")])
model=ChatOpenAI(model="gpt-4o-mini")
chain=prompt|model|StrOutputParser()

st.title('编程教练-生成题目')
with st.form(key='my_form'):
    input = st.text_input(label='输入知识点和学生编程水平')
    submit_button = st.form_submit_button(label='生成题目')
    if submit_button:
        st.info(chain.invoke(input))

chain.get_graph().print_ascii()