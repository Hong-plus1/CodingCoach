import streamlit as st
from DeepSeekLLM import DeepSeekLLM
from langchain.prompts import (ChatPromptTemplate, PromptTemplate)
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# search = DuckDuckGoSearchAPIWrapper()
# def search_tool(query: str) -> str:
#     """搜索相关资源,提供搜索摘要及网址链接"""
#     return search.run(query)

deepseek_llm = DeepSeekLLM()

# ============== 相关方向链 ==============

def generate_learning_options(memory):
    conversation_history = memory.messages
    # 使用AI生成学习方向选项
    prompt_template = PromptTemplate(
        input_variables=["conversation_history"],
        template="""作为一名编程教练，根据对话历史{conversation_history},直接给出三个可能的下一个知识点选项,
        要求:
        直接回答,不要任何解释,前言或总结。eg."数据结构,算法,系统设计".
        选项要简短具有概括性,只需给出三个选项,
        选项之间用','隔开,禁止用'，','、'或其他符号隔开"""
    )
    options_chain = prompt_template | deepseek_llm | CommaSeparatedListOutputParser()
    options = options_chain.invoke({"conversation_history": conversation_history})
    return options

# ============== 生成思考问题 ==============
def generate_thinking_question(memory):
    conversation_history = memory.messages
    # 使用AI生成思考问题
    prompt_template = PromptTemplate(
        input_variables=["conversation_history"],
        template="""根据对话历史{conversation_history},生成一个思考问题以帮助学生掌握知识或引出下一个知识,
                    要求:1.不出编程题 2.不给出答案 3.直接给出问题,不要任何解释,前言或总结。: """
    )
    question_chain = prompt_template | deepseek_llm | StrOutputParser()
    question = question_chain.invoke({"conversation_history": conversation_history})
    return question.strip()

# ============== 生成答案 ==============
def generate_answer(question):
    answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "请回答下列问题,尽量用一段话回答,要求不超过200字:"),
            ("human", question),
        ]
    )
    answer_chain = answer_prompt | deepseek_llm | StrOutputParser()
    answer = answer_chain.invoke({"input": question})
    return answer

# ================== 创建对话链 ==================
# 定义对话提示模板
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个编程教练,循序渐进地教授学生知识."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ]
)
# 管理聊天历史
history = InMemoryChatMessageHistory()
# 获取历史函数
def get_history():
    return history
# 创建对话链
chain = prompt | deepseek_llm | StrOutputParser()
# 包裹链以管理会话历史
wrapped_chain = RunnableWithMessageHistory(
    chain,
    get_history,
    history_messages_key="chat_history",
    stream=True,  # 设置stream参数
)

# ============== Streamlit界面 ==============
# 使用Streamlit显示结果
st.title("编程教练")

# 初始化对话历史
if "lead_messages" not in st.session_state:
    st.session_state.lead_messages = []

# 初始化选项
if "option" not in st.session_state:
    st.session_state.option = None

# 初始化思考问题和答案
if "thinking_question" not in st.session_state:
    st.session_state.thinking_question = None
if "thinking_answer" not in st.session_state:
    st.session_state.thinking_answer = None

# 显示对话历史
for message in st.session_state.lead_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if "show_buttons" not in st.session_state:  # 控制按钮显示
    st.session_state.show_buttons = False        

user_input = st.chat_input(placeholder='你想了解什么编程知识？')
if st.session_state.option:
    user_input = st.session_state.option
    st.session_state.option = None
    st.session_state.show_buttons = False

if user_input:
    st.chat_message('user').write(user_input)
    st.session_state.lead_messages.append({"role": "user", "content": user_input})
    
    with st.chat_message('assistant'):
        result = wrapped_chain.invoke({"input": user_input})
        st.write(result)
    st.session_state.lead_messages.append({"role": "assistant", "content": result})
    # 当前轮次对话完成，显示按钮
    st.session_state.show_buttons = True

@st.fragment
def thinking_section():
    submitted = st.form_submit_button("停下来思考")
    if submitted:
        st.session_state.thinking_question = generate_thinking_question(history)
        st.write(st.session_state.thinking_question)
        with st.expander("显示答案"):            
            st.session_state.thinking_answer = generate_answer(st.session_state.thinking_question)
            st.write(st.session_state.thinking_answer)

    # 学习方向部分
@st.fragment
def learning_options_section():
    st.write("你是否想了解:")
    options = generate_learning_options(history)
    cols = st.columns(len(options))  # 创建列以水平排列选项按钮
    for col, option in zip(cols, options):
        with col:
            if st.form_submit_button(option):
                st.session_state.option = option
                st.session_state.show_buttons = False
                st.rerun()
            
if st.session_state.show_buttons:
    with st.form("interaction_form"):
    # 停下来思考部分
        thinking_section()
    with st.form("AaQ_form"):
    # 学习方向部分
        learning_options_section()
      

# markdown卡片？如何操作
# 搜索链接 点击后传送
# 选项有时格式不对 且内容偏移 比如出现化学、生物等
