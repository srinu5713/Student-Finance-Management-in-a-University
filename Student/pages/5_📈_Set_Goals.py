import streamlit as st
import mysql.connector
from mysql.connector import Error

if 'user_id' not in st.session_state:
    st.session_state.user_id=None


def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="wasd",
            database="StudentFinance"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        st.error(f"Error: {e}")
        return None

def set_goals(student_id):
    st.title("Set Goals")

    # Fetch student details from the database
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        connection.close()

    if student:
        st.write(f"Set Goals, {student['name']}!")
        st.write(f"Points Owned: {student['points_owned']}")

        st.header("Set Daily Spending Limit")

        current_limit = student.get('daily_limit', None)

        st.write(f"Current Points: {student['points_owned']}")

        new_limit = st.slider("Set Daily Spending Limit", min_value=0, max_value=student['points_owned'], value=current_limit)


        st.write(f"Current Daily Spending Limit: {current_limit}")
        

        if st.button("Set Daily Limit"):
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("UPDATE student SET daily_limit = %s WHERE student_id = %s", (new_limit, student_id))
                connection.commit()
                st.success("Daily limit set successfully!")
                connection.close()

            # st.experimental_rerun()


if __name__== "__main__":
    student_id = st.session_state.user_id
    if student_id:
        set_goals(student_id)
    else:
        st.write("Please Login to your Account!!!")