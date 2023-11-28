import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import pandas as pd

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

# Function to get transaction history
def get_transaction_history(student_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM student_transactions
            WHERE from_id = %s OR to_id = %s
            UNION
            SELECT * FROM vendor_transactions
            WHERE from_id = %s OR to_id = %s
            ORDER BY transaction_time DESC
        """, (student_id, student_id, student_id, student_id))
        history = cursor.fetchall()
        connection.close()
        return history


# Function to get points spent in a day
def get_points_spent_in_day(student_id):
    connection = create_connection()
    if connection:
        today = datetime.now().strftime("%Y-%m-%d")
        cursor = connection.cursor()
        cursor.execute("""
            SELECT SUM(points) FROM (
                SELECT points FROM student_transactions
                WHERE (from_id = %s OR to_id = %s) AND from_entity = 'student'
                AND DATE(transaction_time) = %s
                UNION ALL
                SELECT points FROM vendor_transactions
                WHERE (from_id = %s OR to_id = %s) AND from_entity = 'student'
                AND DATE(transaction_time) = %s
            ) AS combined
        """, (student_id, student_id, today, student_id, student_id, today))
        spent_points = cursor.fetchone()[0] or 0
        connection.close()
        return spent_points

# Function to get points spent in a month
def get_points_spent_in_month(student_id):
    connection = create_connection()
    if connection:
        first_day_of_month = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        cursor = connection.cursor()
        cursor.execute("""
            SELECT SUM(points) FROM (
                SELECT points FROM student_transactions
                WHERE (from_id = %s OR to_id = %s) AND from_entity = 'student'
                AND DATE(transaction_time) >= %s
                UNION ALL
                SELECT points FROM vendor_transactions
                WHERE (from_id = %s OR to_id = %s) AND from_entity = 'student'
                AND DATE(transaction_time) >= %s
            ) AS combined
        """, (student_id, student_id, first_day_of_month, student_id, student_id, first_day_of_month))
        spent_points = cursor.fetchone()[0] or 0
        connection.close()
        return spent_points


# Display transaction history and points information
def display_transaction_history(student_id):
    st.title("Transaction History and Points Information")
    
    # Transaction history
    st.write("Transaction History:")
    history = get_transaction_history(student_id)

    # Prepare data for the table
    table_data = []
    for transaction in history:
        table_data.append({
            "Transaction ID": transaction['transaction_id'],
            "From": f"{transaction['from_name']} ({transaction['from_entity']})",
            "To": f"{transaction['to_name']} ({transaction['to_entity']})",
            "Points": transaction['points'],
            "Transaction Time": transaction['transaction_time']
        })

    st.table(pd.DataFrame(table_data))

    spent_today = get_points_spent_in_day(student_id)
    st.write(f"Points Spent Today: {spent_today}")
    spent_month = get_points_spent_in_month(student_id)
    st.write(f"Points Spent in the Month: {spent_month}")




if __name__== "__main__":
    student_id = st.session_state.user_id
    if student_id:
        display_transaction_history(student_id)
    else:
        st.write("Please Login to your Account!!!")