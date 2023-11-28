import streamlit as st
import mysql.connector
from mysql.connector import Error
import sys 
from streamlit_extras.switch_page_button import switch_page 


if 'user_id' not in st.session_state:
    st.session_state.user_id=None

# Function to create a connection to the MySQL database
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

# Function to get student details
def get_student_details(student_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        connection.close()
        return student

# Student Dashboard
def student_dashboard(student_id):
    st.title("Student Dashboard")

    # Get student details
    student = get_student_details(student_id)

    if student:
        st.write(f"Welcome, {student['name']}!")
        st.write(f"Username: {student['username']}")
        st.write(f"Student ID: {student['student_id']}")
        st.write(f"Year of Study: {student['year_of_study']}")
        st.write(f"Points Owned: {student['points_owned']}")
    

    if st.button("Logout"):
        st.session_state.user_id = None
        switch_page("login")


if __name__== "__main__":
    student_id = st.session_state.user_id
    if student_id:
        student_dashboard(student_id)
    else:
        st.write("Please Login to your Account!!!")
