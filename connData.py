import pymysql
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()


def connect_to_db():
    try:
        conn = pymysql.connect(
            host=os.getenv(DB_HOST),
            user=os.getenv(DB_USERNAME),
            password=os.getenv(DB_PASSWORD),
            database="codecoach"
        )
        return conn
    except pymysql.Error as err:
        st.error(f"数据库连接失败: {err}")
        return None
