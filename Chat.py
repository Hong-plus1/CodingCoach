#对于代码编辑器里的代码提供实时的代码高亮、语法检查和错误提示
#侧栏的对话机器人可以提供代码编辑器的帮助

import streamlit as st

from DeepSeekLLM import DeepSeekLLM
from langchain_openai import ChatOpenAI
from langchain.memory import (ConversationBufferMemory,ConversationSummaryMemory)
from langchain.prompts import (ChatPromptTemplate,HumanMessagePromptTemplate,MessagesPlaceholder,SystemMessagePromptTemplate,PromptTemplate)
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
from connData import connect_to_db
from pymysql import MySQLError

# 加载环境变量
load_dotenv()

def save_dialogue(content):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO dialogue (dialogueSummary) VALUES (%s)", (content,))
            #获取该记录id
            cursor.execute("SELECT LAST_INSERT_ID()")
            dialogueId = cursor.fetchone()[0]
            conn.commit()
            
        except MySQLError as err:
            st.error(f"消息保存失败: {err}")
        finally:
            cursor.close()
            conn.close()
        return dialogueId

def update_message(diaid):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE messages SET DialogueId=%s WHERE DialogueId=0", (diaid,))
            conn.commit()
        except MySQLError as err:
            st.error(f"消息更新失败: {err}")
        finally:
            cursor.close()
            conn.close()

def save_message(role, content):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO messages (ChatRole, ChatContent) VALUES (%s, %s)", (role, content))
            conn.commit()
        except MySQLError as err:
            st.error(f"消息保存失败: {err}")
        finally:
            cursor.close()
            conn.close()

def load_messages():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT ChatRole, ChatContent, ChatId, DialogueId FROM messages ORDER BY timestamp ASC")
            messages = cursor.fetchall()
            return [{"role": role, "content": content, "id": id, "did": did} for role, content, id, did in messages]
        except MySQLError as err:
            st.error(f"消息加载失败: {err}")
            return []
        finally:
            cursor.close()
            conn.close()
    return []
    
llm=DeepSeekLLM()
#ChatOpenAI(model="gpt-4o-mini")

prompt=ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template("""你是一位资深的编程教练，您将负责辅助学生完成代码{code}的编写，包括补全代码、给代码注释等功能。
        1. 读取用户输入的代码，确保理解其功能和结构。
        2. 如果用户要求补全代码，分析现有代码的逻辑，确定缺失的部分，并根据编程语言的语法和最佳实践进行补全。
        3. 如果用户提供了代码并要求注释，逐行或逐块分析代码，添加清晰、简洁的注释，解释每一部分的功能和目的。
        4. 确保输出的注释和补全代码符合用户的需求，保持代码的可读性和可维护性。"""),
        MessagesPlaceholder(variable_name="chat_history"),#动态插入聊天历史
        HumanMessagePromptTemplate.from_template("{question}"),
    ]
)
conv_memory=ConversationBufferMemory(memory_key="chat_history",return_messages=True)

chain={
    "question":lambda x: x["question"],
    "code":lambda x: x["code"],
    "chat_history":lambda x: conv_memory.load_memory_variables(x)["chat_history"],
}|prompt|llm|StrOutputParser()

def chat_coach(question,code):
    # 调用链
    response=chain.invoke({"question":question,"code":code})
    # 更新聊天历史
    conv_memory.save_context({"question":question},{"output":response})
    return response

# 初始化 session_state
if "code" not in st.session_state:
    st.session_state["code"] = ""

# 初始化 session_state 从数据库获取历史数据
if "messages" not in st.session_state:
    st.session_state.messages = load_messages()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input(placeholder='请输入提问内容')
if user_input:
    st.chat_message('human').write(user_input)
    save_message("user", user_input)
    st.session_state.messages.append({"role": "user", "content": user_input, 'id': len(st.session_state.messages),"did":0})
    
    with st.chat_message('ai'):
        # 会在界面上显示中间步骤，如搜索、思考等，但只限当前提问
        # 下一轮提问时，这里显示的步骤将不会存在
        # 所以在上方会再一次将中间步骤添加到聊天列表中，
        # 这样中间步骤将会一直保留在聊天列表中
        code=st.session_state["code"]
        response = chat_coach(user_input, code)
        st.write(response)
        save_message("assistant",response)
        st.session_state.messages.append({"role": "assistant", "content": response, 'id': len(st.session_state.messages), 'did': 0})

if st.button("开启新一轮对话"):
    # 实例化 ConversationSummaryMemory
    summary_memory = ConversationSummaryMemory(
        llm=llm,
        # 如果你希望在实例化时就添加一些历史消息作为总结，则可以设置这个值
        buffer=''
    )
    
    for message in st.session_state.messages:
        if message["did"] == 0:
            if message["role"] == "user":
                user_summ=message["content"]
            elif message["role"] == "assistant":
                summary_memory.save_context({"input": user_summ}, {"output": message["content"]})


    dialogueContent=summary_memory.load_memory_variables({"max_length": 200}) # 从数据库加载历史数据
    dialogueContentStr=str(dialogueContent)

    dialogueId=save_dialogue(dialogueContentStr)
    update_message(dialogueId)
    conv_memory.clear()

