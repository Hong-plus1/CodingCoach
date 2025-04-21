from connData import connect_to_db
from pymysql import MySQLError
import json

#保存对话轮次及历史
def save_dialogue_round(user_id, round_number, messages):
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            messages_json = json.dumps(messages, ensure_ascii=False) 
            query = """
                INSERT INTO dialogue_rounds (round_number, user_id, messages)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (round_number, user_id, messages_json))
            conn.commit()
        except MySQLError as e:
            print(f"保存对话轮次失败：{e}")
        finally:
            cursor.close()
            conn.close()

#加载对话轮次及历史
def load_dialogue_rounds(user_id):
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT round_number, messages
                FROM dialogue_rounds
                WHERE user_id = %s
                ORDER BY round_number ASC
            """
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            dialogue_rounds = {
                round_number: json.loads(messages)
                for round_number, messages in results
            }
            return dialogue_rounds
        except MySQLError as e:
            print(f"加载对话轮次失败：{e}")
            return {}
        finally:
            cursor.close()
            conn.close()
