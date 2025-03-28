import streamlit as st
from streamlit_ace import st_ace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import CommaSeparatedListOutputParser
from DeepSeekLLM import DeepSeekLLM
from langchain.prompts import PromptTemplate
from problemCollection import collectionAdded
from Evaluate import save_final_evaluation
from dotenv import load_dotenv
from codeEdit import codeEdit
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
model_problem = DeepSeekLLM()
#ChatOpenAI(model="gpt-4o-mini")  #deepseek-ai/DeepSeek-V3
chain_problem = prompt_problem | model_problem | StrOutputParser()

@st.fragment
def problem_generate():
     st.write("<span style='font-size:28px; font-weight:bold;'>生成题目</span>", unsafe_allow_html=True)
     with st.form(key='my_form'):
        input = st.text_input(label='输入知识点和学生编程水平')
        submit_button = st.form_submit_button(label='生成题目')
        if submit_button:
             problem=chain_problem.invoke(input)
             st.session_state['problem'] = problem 
             st.rerun(scope="fragment")
     if 'problem' in st.session_state:
         st.info(st.session_state['problem'])
         collectionAdded('problem')
         

template_evaluation = """请扮演一位资深的编程教练，您将负责评估有关问题{problem}，学生的程序代码是否正确。
        1. 仔细阅读学生提供的代码，检查其功能和实现逻辑，是否符合题目要求。
        2. 分析代码的算法框架，识别主要的算法步骤和数据结构的使用，分析其正确性和效率。
        3. 针对代码的逻辑和实现，提出代码的优点和可能的改进方向，包括性能优化、可读性提升等。
        4. 设计一组测试用例，确保覆盖代码的主要功能和边界情况，以验证代码的正确性。
        5. 将分析结果、改进建议和测试用例整理成清晰的文本，确保用户能够轻松理解。"""

prompt_evaluation = ChatPromptTemplate.from_messages([("system", template_evaluation),
                                                      ("human", "{code}")])
model_evaluation = DeepSeekLLM()
#ChatOpenAI(model="gpt-3.5-turbo")
chain_evaluation = prompt_evaluation | model_evaluation | StrOutputParser()

output_parser = CommaSeparatedListOutputParser()
instructions = output_parser.get_format_instructions()
template_finalEvalu="""请扮演一位资深的编程教练，您将负责评估有关问题{problem},对于学生的代码{code}，
    给出其掌握的知识点(20字内)，及该知识点完成的百分制分数,eg:“二叉树,80”.\n{instructions}"""
    

prompt_finalEvalu = PromptTemplate(
    input_variables=['code', 'problem'],
    template=template_finalEvalu
    )

chain_finalEvalu=prompt_finalEvalu|model_evaluation|CommaSeparatedListOutputParser()

@st.fragment
def code_evaluate(code):
     evaluate_button = st.button('评估代码')
     if 'problem' not in st.session_state:
        st.warning("请先生成题目")
        return     
     
     if evaluate_button:
        problem=st.session_state['problem']
        evaluation_result = chain_evaluation.invoke({"code":code,"problem":problem})
        #finalEvalu_result = chain_finalEvalu.invoke({"code": code, "problem": problem,'instructions':instructions})

        # Save the knowledge point and score to the database
        # print(finalEvalu_result)
        # knowledge_point = finalEvalu_result.split(',')[0].strip()
        # score = finalEvalu_result.split(',')[1].strip()
        # save_final_evaluation(knowledge_point, score)

        st.session_state['evaluation_result'] = evaluation_result
        st.rerun(scope="fragment")
     if 'evaluation_result' in st.session_state:
        st.info(st.session_state['evaluation_result'])


def exercise():
    # 添加问题生成模块
    problem_generate()
    # 添加代码编辑模块
    st.write("<span style='font-size:28px; font-weight:bold;'>代码编辑器</span>", unsafe_allow_html=True)
    st.session_state["code"]= st_ace(language='python', theme='monokai', key='editor')
    code=st.session_state["code"]
    codeEdit(code)
    # 添加代码评估模块
    code_evaluate(code) 