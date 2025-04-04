#对于代码编辑器里的代码提供实时的代码高亮、语法检查和错误提示
#侧栏的对话机器人可以提供代码编辑器的帮助

import streamlit as st

from DeepSeekLLM import DeepSeekLLM
from langchain.memory import (ConversationBufferMemory,ConversationSummaryMemory)
from langchain.prompts import (ChatPromptTemplate,HumanMessagePromptTemplate,MessagesPlaceholder,SystemMessagePromptTemplate,PromptTemplate)
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
from connData import connect_to_db
from pymysql import MySQLError

# 加载环境变量
load_dotenv()

# 获取用户的最新对话
def get_latest_dialogue():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            # 查询当前用户的最新对话
            cursor.execute("SELECT dialogueId FROM dialogue WHERE userid=%s ORDER BY DialogueTimestamp DESC LIMIT 1", (st.session_state.userid,))# 从dialogue数据表按照时间戳降序排列，获取最新的对话
            result = cursor.fetchone()
            return result[0] if result else None
        except MySQLError as err:
            st.error(f"加载最新对话失败: {err}")
        finally:
            cursor.close()
            conn.close()
    return None

def load_messages(dialogue_id):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT ChatRole, ChatContent FROM messages WHERE userid=%s AND DialogueId=%s ORDER BY timestamp ASC",(st.session_state.userid,dialogue_id))
            messages = cursor.fetchall()
            return [{"role": role, "content": content} for role, content in messages]
        except MySQLError as err:
            st.error(f"消息加载失败: {err}")
            return []
        finally:
            cursor.close()
            conn.close()
    return []
# 需要返回吗
def save_dialogue(content):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO dialogue (dialogueSummary, userid) VALUES (%s, %s)", (content,st.session_state.userid))
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

def save_message(role, content, dialogue_id):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO messages (ChatRole, ChatContent, userid, DialogueID) VALUES (%s, %s, %s, %s)", (role, content, st.session_state.userid, dialogue_id))
            conn.commit()
        except MySQLError as err:
            st.error(f"消息保存失败: {err}")
        finally:
            cursor.close()
            conn.close()


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
if "dialogue_id" not in st.session_state:
    st.session_state.dialogue_id = get_latest_dialogue()  # 获取最新对话 ID
    print(st.session_state.dialogue_id)

if "messages" not in st.session_state:
    if st.session_state.dialogue_id:
        st.session_state.messages = load_messages(st.session_state.dialogue_id)  # 加载最新对话的消息
    else:
        st.session_state.messages = []

# 初始化 session_state
if "code" not in st.session_state:
    st.session_state["code"] = ""

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input(placeholder='请输入提问内容')
if user_input:
    st.chat_message('human').write(user_input)
    save_message("user", user_input, st.session_state.dialogue_id)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message('ai'):
        # 会在界面上显示中间步骤，如搜索、思考等，但只限当前提问
        # 下一轮提问时，这里显示的步骤将不会存在
        # 所以在上方会再一次将中间步骤添加到聊天列表中，
        # 这样中间步骤将会一直保留在聊天列表中
        code=st.session_state["code"]
        response = chat_coach(user_input, code)
        st.write(response)
        save_message("assistant",response,st.session_state.dialogue_id)
        st.session_state.messages.append({"role": "assistant", "content": response})

if st.button("开启新一轮对话"):
    # 实例化 ConversationSummaryMemory
    summary_memory = ConversationSummaryMemory(
        llm=llm,
        # 如果你希望在实例化时就添加一些历史消息作为总结，则可以设置这个值
        buffer=''
    )
    
    for message in st.session_state.messages:
        if message["role"] == "user":
            user_summ=message["content"]
        elif message["role"] == "assistant":
            summary_memory.save_context({"input": user_summ}, {"output": message["content"]})


    dialogueContent=summary_memory.load_memory_variables({"max_length": 200}) # 从数据库加载历史数据
    dialogueContentStr=str(dialogueContent)

    # 创建新对话
    new_dialogue_id = save_dialogue(dialogueContentStr)
    if new_dialogue_id:
        st.session_state.dialogue_id = new_dialogue_id  # 更新当前对话 ID
        st.session_state.messages = []  # 清空消息历史
        conv_memory.clear()  # 清空对话链
    

