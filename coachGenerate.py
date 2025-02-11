import streamlit as st
from streamlit_ace import st_ace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

# 生成题目
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


st.title('编程教练-生成题目')
with st.form(key='my_form'):
    input = st.text_input(label='输入知识点和学生编程水平')
    submit_button = st.form_submit_button(label='生成题目')
    if submit_button:
        problem=chain_problem.invoke(input)
        st.session_state['problem'] = problem 
        st.info(problem)

# if 'problem' in st.session_state:
#      st.text_area('题目', value=st.session_state['problem'],height=None)

# 分析代码
st.title('分析代码')
code = st_ace(language='python', theme='monokai', key='editor')
evaluate_button = st.button('评估代码')

template_evaluation = """请扮演一位资深的编程教练，您将负责评估有关问题{problem}，学生的程序代码是否正确。
        1. 仔细阅读学生提供的代码，检查其功能和实现逻辑，是否符合题目要求。
        2. 分析代码的算法框架，识别主要的算法步骤和数据结构的使用，分析其正确性和效率。
        3. 针对代码的逻辑和实现，提出代码的优点和可能的改进方向，包括性能优化、可读性提升等。
        4. 设计一组测试用例，确保覆盖代码的主要功能和边界情况，以验证代码的正确性。
        5. 将分析结果、改进建议和测试用例整理成清晰的文本，确保用户能够轻松理解。"""

prompt_evaluation = ChatPromptTemplate.from_messages([("system", template_evaluation),
                                                      ("human", "{code}")])
model_evaluation = ChatOpenAI(model="gpt-4o-mini")
chain_evaluation = prompt_evaluation | model_evaluation | StrOutputParser()

if evaluate_button:
    problem=st.session_state['problem']
    evaluation_result = chain_evaluation.invoke({"code":code,"problem":problem})
    st.info("代码评估结果：")
    st.info(evaluation_result)