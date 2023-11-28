import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import datetime

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

# Function to get recharge transactions
def get_all_recharge_transactions():
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student_recharge")
        transactions = cursor.fetchall()
        connection.close()
        return transactions

def get_all_students():
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student")
        students = cursor.fetchall()
        connection.close()
        return students

# Call the procedure to add points and record transaction
def add_points_to_student_procedure(student_id, points_to_add):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.callproc('AddPointsAndRecordTransaction', (student_id, points_to_add, admin_id))
            connection.commit()
            st.success(f"{points_to_add} points added successfully to the student!")
        except Error as e:
            st.error(f"Error calling procedure: {e}")
        finally:
            connection.close()

# Admin panel to add points to a student
def add_points_to_student():
    st.title("Admin - Add Points to Student")

    st.write("Details of All Students:")
    students = get_all_students()

    selected_student_id = st.selectbox("Select Student ID for Adding Points:", [str(student['student_id']) for student in students])

    # Retrieve student details
    student = get_student_details(selected_student_id)

    if student:
        st.write(f"Selected Student: {student['name']} (ID: {student['student_id']})")
        current_points = student['points_owned']
        st.write(f"Current Points: {current_points}")

        # Input field for entering points to be added
        points_to_add = st.number_input("Enter Points to Add:", min_value=0)

        if st.button("Add Points"):
            add_points_to_student_procedure(selected_student_id, points_to_add)

        st.write("Recharge Transactions:")
            
        transactions = get_all_recharge_transactions()
            
            # Display the transactions table
        if transactions:
            st.table(transactions)
        else:
            st.warning("No recharge transactions found.")

if __name__ == "__main__":
    admin_id = st.session_state.user_id
    if admin_id:
        add_points_to_student()
    else:
       st.warning("Please Login First")
