import pymysql
import streamlit as st

def connect_to_db():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            database="codecoach"
        )
        return conn
    except pymysql.Error as err:
        st.error(f"数据库连接失败: {err}")
        return None