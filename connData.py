import pymysql
import streamlit as st

def connect_to_db():
    try:
        conn = pymysql.connect(
            host="172.16.0.0/12",
            user="root",
            password="Hjy879137267",
            database="codecoach"
        )
        return conn
    except pymysql.Error as err:
        st.error(f"数据库连接失败: {err}")
        return None
