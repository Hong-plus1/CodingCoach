import streamlit as st
from connData import connect_to_db
from pymysql import MySQLError
from datetime import datetime, timedelta



# 根据coachGeneration的code_evaluate函数得到的结果(即对学生代码的评估)，
# 以及学生与编程教练的对话，推断出学生的编程水平，并且统计学生的练习频率，
# 在主页显示相关数据

def get_coding_level(user_id):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT AVG(coding_level) FROM evaluations WHERE user_id=%s", (user_id,))
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0
        except MySQLError as err:
            st.error(f"获取编程水平失败: {err}")
            return 0
        finally:
            cursor.close()
            conn.close()
    return 0

def get_practice_frequency(user_id):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM evaluations WHERE userId=%s AND timestamp >= %s", 
                           (user_id, datetime.now() - timedelta(days=30)))
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0
        except MySQLError as err:
            st.error(f"获取练习频率失败: {err}")
            return 0
        finally:
            cursor.close()
            conn.close()
    return 0

def temp():
    st.title("欢迎来到编程教练平台")

    user_id = 1  # 假设用户 ID 为 1，您可以根据实际情况进行修改

    coding_level = get_coding_level(user_id)
    practice_frequency = get_practice_frequency(user_id)

    col1, col2 = st.columns(2)
    col1.metric("编程水平", f"{coding_level:.2f} / 100")
    col2.metric("30天内练习次数", f"{practice_frequency} 次")

# 使用langchain，结合学生的历史数据，推断出学生的编程水平

import streamlit as st
from pymysql import MySQLError
from datetime import datetime, timedelta

def get_coding_level(user_id):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT code FROM evaluations WHERE user_id=%s", (user_id,))
            results = cursor.fetchall()
            code = "\n".join(result[0] for result in results)
            langchain = LangChain()
            langchain.train(code)
            return langchain.predict()
        except MySQLError as err:
            st.error(f"获取编程水平失败: {err}")
            return 0
        finally:
            cursor.close()
            conn.close()
    return 0



### evaluate 数据库

def save_final_evaluation(knowledge_point, score):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO evaluation (evaluKnow, evaluScore) VALUES (%s, %s)", (knowledge_point, score))
            conn.commit()
        except MySQLError as err:
            st.error(f"保存评估结果失败: {err}")
        finally:
            cursor.close()
            conn.close()
