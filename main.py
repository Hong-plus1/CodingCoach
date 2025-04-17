import streamlit as st
from coachGenerate import exercise
from problemCollection import wrongCollection,FavCollection,proSetting
from login import login,logout,register

st.set_page_config(page_title='编程教练', layout="wide", initial_sidebar_state="expanded")

def temp():
    st.title("欢迎来到编程教练平台")
    col1, col2, col3 = st.columns(3)
    col1.metric("Temperature", "70 °F", "1.2 °F")
    col2.metric("Wind", "9 mph", "-8%")
    col3.metric("Humidity", "86%", "4%")

# 初始化会话状态
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "userid" not in st.session_state:
    st.session_state.userid = None
if "show_register" not in st.session_state:
    st.session_state.show_register = False

if st.session_state.show_register:
    register()
else:
    login_page = st.Page(login, title="登录")
    logout_page = st.Page(logout, title="退出登录")
    WrongPage=st.Page(wrongCollection,title="错题集")
    FavPage=st.Page(FavCollection,title="收藏集")
    #CodingPage=st.Page("CodeEvaluate.py", title="代码编辑")
    CoachPage=st.Page("coach.py",title="编程教练")
    ChatPage=st.Page("Chat.py",title="答疑解惑")
    CodeExerpage=st.Page(exercise,title="代码练习")
    ProSettingPage=st.Page(proSetting,title="设置")

    pg = st.navigation([login_page])
    if st.session_state.logged_in:    
        pg = st.navigation(
            {
                "主页": [CoachPage],
                "编程练习": [CodeExerpage,ChatPage],
                "题目集": [WrongPage,FavPage,ProSettingPage],
                "账户管理": [logout_page],
            }
        )

    pg.run()


# addknowledgepoint() 数据库设置

# 个性化化定制
# 1. 问题生成：问题生成的模块可以根据用户输入的知识点和水平，生成不同难度的题目。

#聊天机器人
# duckduckgo

# 代码编辑器 代码内容点击apply消失问题
