import streamlit as st
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
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


def get_all_events_with_volunteers():
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        # Query to get all events and total volunteers for each event
        cursor.execute("""
            SELECT e.*, 
                   (SELECT COUNT(*) FROM event_volunteers ev WHERE ev.event_id = e.event_id) as total_volunteers
            FROM event e
        """)
        events = cursor.fetchall()
        connection.close()
        return events


# Function to get statistics about events
def get_event_statistics():
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        # Nested query to get event statistics
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM event) as total_events,
                (SELECT SUM(num_of_participants) FROM event) as total_participants,
                (SELECT COUNT(*) FROM event_volunteers) as total_volunteers
        """)
        statistics = cursor.fetchone()
        connection.close()
        return statistics
    


# Function to get spending data for a specific day
def get_spending_data_by_day(selected_date):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT SUM(points) AS total_spent
            FROM student_transactions
            WHERE transaction_time >= %s AND transaction_time < %s
        """, (selected_date, selected_date + pd.DateOffset(days=1)))
        spending_data = cursor.fetchone()
        connection.close()
        return spending_data['total_spent'] if spending_data and spending_data['total_spent'] else 0

def get_total_spending_data_by_month(selected_month):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT DAY(transaction_time) AS day, SUM(points) AS total_spent
            FROM student_transactions
            WHERE MONTH(transaction_time) = %s
            GROUP BY day
        """, (selected_month,))
        spending_data = cursor.fetchall()
        connection.close()
        return spending_data

def get_other_stats():
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total_students FROM student")
        result = cursor.fetchone()
        connection.close()
        return result['total_students'] if result and result['total_students'] else 0

def plot_spending_data(spending_data, title, xlabel, ylabel):
    fig, ax = plt.subplots()
    days = [entry['day'] for entry in spending_data]
    total_spent = [entry['total_spent'] for entry in spending_data]

    ax.plot(days, total_spent, marker='o', linestyle='-', color='b')
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    st.pyplot(fig)

def stats_page():
    st.title("Stats - Student Spendings")

    selected_date = st.date_input("Select Date to View Daily Spending:", datetime.today())
    daily_spending = get_spending_data_by_day(selected_date)
    st.metric("Daily Spending", f"{daily_spending} points")

    selected_month = st.selectbox("Select Month to View Monthly Spending:", range(1, 13), index=datetime.today().month - 1)
    monthly_spending_data = get_total_spending_data_by_month(selected_month)
    st.write("Monthly Spending Data:")
    st.write(pd.DataFrame(monthly_spending_data))

    plot_spending_data(monthly_spending_data, "Monthly Spending", "Day", "Total Points Spent")

    total_students = get_other_stats()
    st.metric("Total Students", total_students)

    events_with_vols = get_all_events_with_volunteers()

    if events_with_vols:
        st.table(events_with_vols)
    else:
        st.warning("No events found.")
    
    st.header("Event Statistics")
    event_statistics = get_event_statistics()
    
    if event_statistics:
        st.write(f"Total Events: {event_statistics['total_events']}")
        st.write(f"Total Participants: {event_statistics['total_participants']}")
        st.write(f"Total Volunteers: {event_statistics['total_volunteers']}")
    else:
        st.warning("No event statistics found.")

if __name__ == "__main__":
    admin_id = st.session_state.user_id
    if admin_id:
        stats_page()
    else:
       st.warning("Please Login First")
