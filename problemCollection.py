import streamlit as st
from connData import connect_to_db
from pymysql import MySQLError
import time


# 将题目保存到数据库
def save_problem(problem_type, content, knowledge_point="", annotation=""):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO problems (type, content, knowledge_point, annotation) VALUES (%s, %s, %s, %s)",
                  (problem_type, content, knowledge_point, annotation)
            )
            conn.commit()
            st.success("题目保存成功！")
        except MySQLError as err:
            st.error(f"题目保存失败: {err}")
        finally:
            cursor.close()
            conn.close()

#更改数据库id为id的题目的内容
def update_problem(id, content, annotation, knowledge_point=""):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE problems SET content=%s, annotation=%s, knowledge_point=%s WHERE id=%s",
                (content, annotation, knowledge_point, id)
            )
            conn.commit()
            st.success("题目更新成功！")
        except MySQLError as err:
            st.error(f"题目更新失败: {err}")
        finally:
            cursor.close()
            conn.close()

# 删除数据库id为id的题目
def delete_problem(id):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM problems WHERE id=%s", (id,))
            conn.commit()
            st.success("题目删除成功！")
        except MySQLError as err:
            st.error(f"题目删除失败: {err}")
        finally:
            cursor.close()
            conn.close()

# 根据问题类别从数据库读取题目及其批注
def load_problems(problem_type):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT content,annotation,knowledge_point,id FROM problems WHERE type=%s", 
                           (problem_type,)
            )
            problems = cursor.fetchall()
            return problems
        except MySQLError as err:
            st.error(f"题目读取失败: {err}")
            return []
        finally:
            cursor.close()
            conn.close()
    return []

#添加题目到错题集和收藏集
@st.fragment
def collectionAdded(pro_sort):
    # 添加按钮将题目加入到错题集和收藏集
    if pro_sort in st.session_state:
        # 增加批注 
        st.text_area('批注', key='annotation')
        if st.button('加入错题集'):
            save_problem('wrong', st.session_state[pro_sort], annotation=st.session_state.get('annotation',""))
            st.success('题目已加入错题集')
            time.sleep(3)
            st.rerun(scope="fragment")

        if st.button('加入收藏集'):
            st.session_state['add_to_fav']=True
        
        if st.session_state.get('add_to_fav',False): 
            #增加知识点
            know_p=st.text_input('知识点', key='knowledge_point')
            col1,col2=st.columns(2)
            with col1:
                if st.button('确认'):
                    save_problem('favorite', st.session_state[pro_sort], annotation=st.session_state.get('annotation',""), knowledge_point=know_p)
                    st.success('题目已加入收藏集')
                    st.session_state['add_to_fav']=False
                    time.sleep(3)
                    st.rerun()
            with col2:
                if st.button('取消'):
                    st.session_state['add_to_fav']=False
                    st.rerun()

def wrongCollection():
    st.title("错题集")
    problems=load_problems('wrong')
    for i, problem in enumerate(problems):
        st.write(f"题目 {i + 1}:")

        if f"edit_mode_{i}" not in st.session_state:
            st.session_state[f"edit_mode_{i}"] = False

        if st.session_state[f"edit_mode_{i}"]:
            st.text_area(f"题目 {i + 1}", value=problem[0], height=None, key=f"wrong_problem_{i}")
            st.text_area(f"批注 {i + 1}", value=problem[1], key=f"wrong_annotation_{i}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"更新题目 {i + 1}"):
                    update_problem(problem[3], st.session_state[f"wrong_problem_{i}"], st.session_state.get(f"wrong_annotation_{i}", ""))
                    st.session_state[f"edit_mode_{i}"] = False
                    st.rerun()
            with col2:
                if st.button(f"取消编辑 {i + 1}"):
                    st.session_state[f"edit_mode_{i}"] = False
                    st.rerun()
        else:
            st.info(problem[0])
            st.write(f"批注 {i + 1}:")
            st.info(problem[1])
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"编辑题目 {i + 1}"):
                    st.session_state[f"edit_mode_{i}"] = True
                    st.rerun()
            with col2:
                if st.button(f"删除题目 {i + 1}"):
                    delete_problem(problem[3])
                    st.rerun()

def FavCollection():
    st.title("收藏集")
    problems = load_problems('favorite')
    knowid=0
    for knowledge_p in set([p[2] for p in problems]):
        knowid=knowid+1
        st.header(f"知识点: {knowledge_p}")

        for i, problem in enumerate([pro for pro in problems if pro[2] == knowledge_p]):
            st.write(f"题目 {i + 1}:")

            if f"edit_mode_{i}" not in st.session_state:
                st.session_state[f"edit_mode_{i}"] = False

            if st.session_state[f"edit_mode_{i}"]:
                st.text_area(f"题目 {i + 1}", value=problem[0], height=None, key=f"favorite_problem_{problem[3]}_{i}")
                st.text_area(f"批注 {i + 1}", value=problem[1], key=f"favorite_annotation_{problem[3]}_{i}")
                st.text_area(f"知识点 {i + 1}", value=problem[2], key=f"knowledge_point_{problem[3]}_{i}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"更新题目 {knowid}_{i + 1}"):
                        update_problem(problem[3], st.session_state[f"favorite_problem_{problem[3]}_{i}"], st.session_state.get(f"favorite_annotation_{problem[3]}_{i}", ""), st.session_state.get(f"knowledge_point_{problem[3]}_{i}", ""))
                        st.session_state[f"edit_mode_{i}"] = False
                        st.rerun()
                with col2:
                    if st.button(f"取消编辑 {knowid}_{i + 1}"):
                        st.session_state[f"edit_mode_{i}"] = False
                        st.rerun()

            else:
                st.info(problem[0])
                st.write(f"批注 {i + 1}:")
                st.info(problem[1])
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"编辑题目 {knowid}_{i + 1}"):
                        st.session_state[f"edit_mode_{i}"] = True
                        st.rerun()
                with col2:
                    if st.button(f"删除题目 {knowid}_{i + 1}"):
                        delete_problem(problem[3])
                        st.rerun()

def addKnowledgePoint():
    st.write("<span style='font-size:28px; font-weight:bold;'>添加知识点</span>", unsafe_allow_html=True)
    new_knowledge_point = st.text_input("输入新的知识点")
    if st.button("添加知识点"):
        if new_knowledge_point and new_knowledge_point not in st.session_state.get('knowledge_points', []):
            st.session_state.setdefault('knowledge_points', []).append(new_knowledge_point)
            st.success(f"知识点 '{new_knowledge_point}' 已添加")
        else:
            st.warning("知识点已存在或输入为空")

            
#自定义题目加入到集合中
def studentProblem():
    st.write("<span style='font-size:28px; font-weight:bold;'>添加自定义题目</span>", unsafe_allow_html=True)
    st.text_area('题目',key='stu_problem')
    collectionAdded('stu_problem')
    

def proSetting():
    st.title("设置")
    addKnowledgePoint()
    studentProblem()
