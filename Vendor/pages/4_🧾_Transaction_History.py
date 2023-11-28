import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import pandas as pd


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

# Function to get transaction history for vendor
def get_vendor_transaction_history(vendor_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM vendor_transactions
            WHERE to_id = %s
            ORDER BY transaction_time DESC
        """, (vendor_id,))
        history = cursor.fetchall()

        # Convert history to a Pandas DataFrame
        df = pd.DataFrame(history)

        connection.close()
        return df

# Function to calculate and update profits for the day and month
def calculate_and_update_profits(vendor_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        # Calculate profits for the day
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT SUM(points) FROM vendor_transactions
            WHERE to_id = %s
            AND DATE(transaction_time) = %s
        """, (vendor_id, today))
        daily_profits = cursor.fetchone()[0] or 0

        # Calculate profits for the month
        first_day_of_month = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT SUM(points) FROM vendor_transactions
            WHERE to_id = %s
            AND DATE(transaction_time) >= %s
        """, (vendor_id, first_day_of_month))
        monthly_profits = cursor.fetchone()[0] or 0

        # Update the vendor's profits
        cursor.execute("""
            UPDATE vendor
            SET profits = profits + %s
            WHERE vendor_id = %s
        """, (daily_profits, vendor_id))

        connection.commit()
        connection.close()

        return daily_profits, monthly_profits

# Display transaction history and profits for the day and month
def display_vendor_details(vendor_id):
    st.title("Vendor Details and Transaction History")

    # Transaction history
    st.write("Transaction History:")
    history = get_vendor_transaction_history(vendor_id)

    # Display the history as a table
    st.dataframe(history)

    # Calculate and display profits
    daily_profits, monthly_profits = calculate_and_update_profits(vendor_id)
    st.write(f"Profits for the Day: {daily_profits}")
    st.write(f"Profits for the Month: {monthly_profits}")

if __name__ == "__main__":
    # Replace with the actual vendor ID
    vendor_id =st.session_state.user_id
    if vendor_id:
        display_vendor_details(vendor_id)
    else:
        st.write("Please Login to your Account!!!")