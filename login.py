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

# 登录页面
def login():
    st.header("登录")
    st.divider()

    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")

    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.logged_in = True
            st.success("登录成功!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("用户名或密码错误")

def logout():
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()