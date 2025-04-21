import streamlit as st
from DeepSeekLLM import DeepSeekLLM
from QwenCoderLLM import GLMLLM
from langchain.schema import HumanMessage, AIMessage
from langchain.prompts import (ChatPromptTemplate, PromptTemplate)
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
#from langchain.utilities import DuckDuckGoSearchAPIWrapper
#from langchain.chat_models import ChatOpenAI
import re
from coachDatabase import (load_dialogue_rounds, save_dialogue_round)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from dotenv import load_dotenv
# 加载环境变量
load_dotenv()
# search = DuckDuckGoSearchAPIWrapper()
# def search_tool(query: str) -> str:
#     """搜索相关资源,提供搜索摘要及网址链接"""
#     return search.run(query)
#deepseek_llm=ChatOpenAI(model="gpt-4o-mini")
deepseek_llm = DeepSeekLLM()
glm_llm = GLMLLM()
# ============== 相关方向链 ==============
def generate_learning_options(memory):
    ResponseSchemas = [
        ResponseSchema(name="option1", description="第一个编程知识点选项"),
        ResponseSchema(name="option2", description="第二个编程知识点选项"),
        ResponseSchema(name="option3", description="第三个编程知识点选项"),
    ]
    # 定义输出解析器
    option_parser = StructuredOutputParser.from_response_schemas(ResponseSchemas)
    # 定义解析器
    instruction = option_parser.get_format_instructions()

    conversation_history = memory.messages[-3:]  # 只使用近几条历史回答信息
    # 使用AI生成学习方向选项
    prompt_template = PromptTemplate(
        partial_variables={"instruction": instruction},
        input_variables=["conversation_history"],
        template="""作为一名编程教练，根据对话历史{conversation_history},直接给出三个可能的下一个知识点选项,\n{instruction}"""
        # 要求:
        # 直接回答,不要任何解释,前言或总结。eg."数据结构,算法,系统设计".
        # 选项要简短具有概括性,只需给出三个选项,
        # 选项之间用','隔开,禁止用'，','、'或其他符号隔开"""
    )
    options_chain = prompt_template | deepseek_llm | option_parser #CommaSeparatedListOutputParser() 
    options = options_chain.invoke({"conversation_history": conversation_history}).values()

    return options

# ============== 生成思考问题 ==============

def generate_thinking_question(memory):
    prompt_template = PromptTemplate(
            input_variables=["conversation_history"], 
            template="""根据对话历史{conversation_history},生成一个思考问题以帮助学生掌握知识或引出下一个知识,
                        要求:1.不出编程题 2.不给出答案 3.直接给出问题,不要任何解释,前言或总结。: """
        )
    max_retries = 3  # 最大重试次数
    conversation_history = memory.messages[-3:]
    question_chain = prompt_template | deepseek_llm | StrOutputParser()
    for i in range(max_retries):
        # 使用AI生成思考问题
        question = question_chain.invoke({"conversation_history": conversation_history}).strip() 
        # 验证生成的问题是否符合要求
        if is_valid_question(question):
            return question
        
    # 如果重试多次仍不满足要求，返回默认问题
    return "这个知识点在实际项目中可能会遇到哪些挑战？"


def is_valid_question(text: str) -> bool:
    """检查文本是否包含代码（基于常见代码特征）"""
    code_patterns = [
        r'\b(def|class|import|return|if|else|for|while|try|except)\b',  # 关键词
        r'[\+\-\*/%=<>!&|^~]={1,2}',  # 运算符（如 ==, +=）
        r'\(.*\)\s*\{',  # 函数/条件块（如 `if (x) {`）
        r'`.+`',  # 行内代码标记（Markdown）
        r'```[\s\S]*```',  # 代码块（Markdown）
        r'\w+\.\w+\(',  # 方法调用（如 `obj.method()`）
    ]
    if any(re.search(pattern, text) for pattern in code_patterns):
        return False
    if len(text) > 200:
        return False
    if "答案：" in text or "回答：" in text:
        return False
    return True

# ============== 生成答案 ==============
def generate_answer(question):
    max_retries = 3  # 最大重试次数
    for i in range(max_retries):
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "请回答下列问题,尽量用一段话回答,要求不超过200字:"),
                ("human", question),
            ]
        )
        answer_chain = answer_prompt | deepseek_llm | StrOutputParser()
        answer = answer_chain.invoke({"input": question}).strip()       
        # 验证生成的答案是否符合要求
        if is_valid_answer(answer):
            return answer
    # 如果重试多次仍不满足要求，返回答案
    return answer

def is_valid_answer(answer):
    """验证生成的答案是否符合要求"""
    # 检查答案长度是否超过300字
    if len(answer) > 300:
        return False
    return True
# ================== 创建对话链 ==================

def wrapped_chain(user_input):
    # 定义对话提示模板
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """你是一名编程教练，专注于帮助初学者学习编程。你的教学方式是循序渐进的，
             从基础概念开始，通过生动的例子和类比来帮助学生理解。
             当学生提出问题时，你会先解释相关的背景知识，然后逐步深入，
             并在适当的时候提供简单的代码示例或类比来帮助理解。
             请确保你的回答简洁明了，避免使用复杂的术语。"""),
            ("placeholder", "{chat_history}"), 
            ("human", "{input}"),
        ]
    )
    # 创建对话链
    chain = prompt | glm_llm | StrOutputParser()
    # 包裹链以管理会话历史
    wrapped_chain = RunnableWithMessageHistory(
        chain,
        lambda:history, # 使用全局 history 变量
        streaming=False,
    )
    
    result= wrapped_chain.invoke({"input": user_input})
    return result

# ================== 转换轮次 ==================    
def switch_round(round_number):
    st.session_state.current_round = round_number
    st.session_state.lead_messages = st.session_state.dialogue_rounds[round_number]
    # 更新history为当前轮次的近三条记录
    global history 
    history = InMemoryChatMessageHistory(
        messages=[
            HumanMessage(content=msg["content"]) if msg["role"] == "user" else AIMessage(content=msg["content"])
            for msg in st.session_state.lead_messages[-3:]
        ]
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
if "show_buttons" not in st.session_state:  # 控制按钮显示
    st.session_state.show_buttons = False
if "options" not in st.session_state:  # 控制按钮显示
    st.session_state.options = None

# 初始化对话轮次
if "dialogue_rounds" not in st.session_state:
    st.session_state.dialogue_rounds = load_dialogue_rounds(user_id=st.session_state.userid)
    
if "current_round" not in st.session_state:
    st.session_state.current_round = max(st.session_state.dialogue_rounds.keys(), default=1)


# 初始化 history 为当前轮次的最近三条记录
if st.session_state.dialogue_rounds!={}:
    history = InMemoryChatMessageHistory(
        messages=[
            HumanMessage(content=msg["content"]) if msg["role"] == "user" else AIMessage(content=msg["content"])
            for msg in st.session_state.dialogue_rounds[st.session_state.current_round][-3:]
        ]
    )
else:
    history = InMemoryChatMessageHistory(messages=[])

st.sidebar.write("对话轮次")
for round_number in sorted(st.session_state.dialogue_rounds.keys()):
        if st.sidebar.button(f"切换到轮次 {round_number}", key=f"round_{round_number}"):
            switch_round(round_number)

# 开启新轮次
if st.sidebar.button("开启新轮次"):
    st.session_state.current_round = max(st.session_state.dialogue_rounds.keys(), default=1)+1
    st.session_state.lead_messages = []
    st.session_state.options = None
    st.session_state.thinking_question = None
    st.session_state.thinking_answer = None
    history.clear()
    st.session_state.dialogue_rounds[st.session_state.current_round] = []

for message in st.session_state.lead_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input(placeholder='你想了解什么编程知识？')
if st.session_state.option:
    user_input = st.session_state.option
    st.session_state.option = None
    st.session_state.show_buttons = False

if user_input:
    st.chat_message('user').write(user_input)
    history.add_message(HumanMessage(content=user_input))
    # 保存用户输入到会话历史中
    st.session_state.lead_messages.append({"role": "user", "content": user_input})
    with st.chat_message('assistant'):
        result = wrapped_chain(user_input)
        history.add_message(AIMessage(content=result))
        st.write(result)
    st.session_state.lead_messages.append({"role": "assistant", "content": result})
    # 保存当前轮次的状态
    st.session_state.dialogue_rounds[st.session_state.current_round] = []

    save_dialogue_round(
        user_id=st.session_state.userid,  # 替换为实际用户 ID
        round_number=st.session_state.current_round,
        messages=st.session_state.lead_messages
    )
    ########################################
    st.session_state.dialogue_rounds[st.session_state.current_round] = st.session_state.lead_messages.copy()
    st.session_state.show_buttons = True

def handle_option_click(option):
    st.session_state.option = option
    st.session_state.show_buttons = False

# 学习方向部分
def learning_options_section():
    st.write("你是否想了解:")
    st.session_state.options = generate_learning_options(history)
    
    cols=st.columns(3)
    for col,option in zip(cols, st.session_state.options):
        with col:
            st.button(option, on_click=handle_option_click, args=(option,))
   

# 思考卡片部分
@st.fragment
def thinking_section():
    submitted = st.form_submit_button("停下来思考")
    if submitted:
        st.session_state.thinking_question = generate_thinking_question(history)
        st.write(st.session_state.thinking_question)
        with st.expander("显示答案"):
            st.session_state.thinking_answer = generate_answer(st.session_state.thinking_question)
            st.write(st.session_state.thinking_answer)

if st.session_state.show_buttons:
    with st.form("interaction_form"):
    # 停下来思考部分
        thinking_section()
    # 学习方向部分
    learning_options_section()
      

# 搜索链接 点击后传送
# wrapped_chain.invoke({"input": user_input}) 生成的内容不完整

