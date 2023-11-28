import streamlit as st
import mysql.connector
from mysql.connector import Error


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

# Function to get total number of students
def get_total_students():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM student")
        total_students = cursor.fetchone()[0]
        connection.close()
        return total_students

# Function to get details of all students
def get_all_students():
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student")
        students = cursor.fetchall()
        connection.close()
        return students

# Function to get services given by each student
def get_student_services():
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.*, st.name AS student_name
            FROM service s
            JOIN student st ON s.student_id = st.student_id
        """)
        services = cursor.fetchall()
        connection.close()
        return services

def get_student_username(student_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT username FROM student WHERE student_id = %s", (student_id,))
        student_username = cursor.fetchone()
        connection.close()
        return student_username['username'] if student_username else None

# Function to delete a student by ID
def delete_student(student_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        student_username = get_student_username(student_id)
        if student_username:
            cursor.execute("DELETE FROM student WHERE student_id = %s", (student_id,))
            cursor.execute("DELETE FROM login WHERE username= %s", (student_username,))
            connection.commit()
            connection.close()
        else:
            st.warning("Student not found.")


def manage_students():
    st.title("Manage Students (Admin)")

    # Total number of students
    total_students = get_total_students()
    st.write(f"Total Number of Students: {total_students}")

    # Table of all students
    st.write("Details of All Students:")
    students = get_all_students()
    st.table(students)

    # Services given by each student
    st.write("Services Given by Each Student:")
    services = get_student_services()
    st.table(services)

    # Dropdown to select student for deletion
    selected_student_id = st.selectbox("Select Student ID for Deletion:", [str(student['student_id']) for student in students])

    # Delete button
    if st.button("Delete Selected Student"):
        delete_student(selected_student_id)
        st.success(f"Student {selected_student_id} deleted successfully!")

if __name__ == "__main__":
    admin_id = st.session_state.user_id
    if admin_id:
        manage_students()
    else:
       st.warning("Please Login First")
