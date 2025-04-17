import streamlit as st
import time
from connData import connect_to_db
from pymysql import MySQLError


def authenticate_user(userid, password):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE userid=%s AND password=%s", (userid, password))
            user = cursor.fetchone()
            return user is not None
        except MySQLError as err:
            st.error(f"用户验证失败: {err}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False

def register_user(userid, password):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE userid=%s", (userid,))
            if cursor.fetchone():
                st.error("用户名已存在，请选择其他用户名")
                return False
            cursor.execute("INSERT INTO users (userid, password) VALUES (%s, %s)", (userid, password))
            conn.commit()
            st.success("注册成功！请返回登录页面登录")
            return True
        except MySQLError as err:
            st.error(f"注册失败: {err}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False

# 登录页面
def login():
    st.header("登录")
    st.divider()

    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")

    col1,col2=st.columns(2)
    with col1:
        if st.button("登录"):
            if authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.userid=username
                st.success("登录成功!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("用户名或密码错误")
    with col2:
        if st.button("注册"):
            st.session_state.show_register = True
            st.rerun()

def logout():
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.userid=None
        st.rerun()

def register():
    st.header("注册")
    st.divider()

    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")
    confirm_password = st.text_input("确认密码", type="password")

    if st.button("Register"):
        if password != confirm_password:
            st.error("两次输入的密码不一致")
        elif register_user(username, password):
            st.session_state.show_register = False
            time.sleep(0.5)
            st.rerun()
