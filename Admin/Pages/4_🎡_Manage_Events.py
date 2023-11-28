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
    
def get_next_event_id():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(event_id) FROM event")
        max_event_id = cursor.fetchone()[0]
        connection.close()
        return max_event_id + 1 if max_event_id is not None else 1


# Function to add a new event
def add_event(event_name, no_of_hours, event_type, date, eligible_points, entry_fee, num_of_participants, no_of_volunteers, place):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        try:
            # Add a new event
            cursor.execute("""
                INSERT INTO event (event_id,event_name, no_of_hours, type, date, eligible_points, entry_fee, num_of_participants, no_of_volunteers, place)
                VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (get_next_event_id(),event_name, no_of_hours, event_type, date, eligible_points, entry_fee, num_of_participants, no_of_volunteers, place))

            # Commit the changes
            connection.commit()
            st.success("Event added successfully!")

        except Error as e:
            st.error(f"Error adding event: {e}")

        finally:
            connection.close()

def get_all_events():
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        # Delete associated records from has_registered
        cursor.execute("DELETE FROM has_registered WHERE event_id IN (SELECT event_id FROM event WHERE date < CURDATE())")
        # Delete associated records from event_volunteers
        cursor.execute("DELETE FROM event_volunteers WHERE event_id IN (SELECT event_id FROM event WHERE date < CURDATE())")
        # Delete events from the event table where date has passed
        cursor.execute("DELETE FROM event WHERE date < CURDATE()")
        # Select the remaining events
        cursor.execute("SELECT * FROM event")
        events = cursor.fetchall()
        connection.commit()
        connection.close()
        return events


# Admin panel to manage events
def manage_events():
    st.title("Admin - Manage Events")

    # Add a new event
    st.header("Add a New Event")
    event_name = st.text_input("Event Name:")
    no_of_hours = st.number_input("Number of Hours:", min_value=1)
    event_type = st.text_input("Event Type:")
    date = st.date_input("Event Date:", datetime.today())
    eligible_points = st.number_input("Eligible Points:", min_value=0)
    entry_fee = st.number_input("Entry Fee:", min_value=0)
    num_of_participants = st.number_input("Number of Participants:", min_value=0)
    no_of_volunteers = st.number_input("Number of Volunteers:", min_value=0)
    place = st.text_input("Event Place:")

    if st.button("Add Event"):
        add_event(event_name, no_of_hours, event_type, date, eligible_points, entry_fee, num_of_participants, no_of_volunteers, place)

    # Display existing events
    st.header("Existing Events")
    events = get_all_events()

    if events:
        st.table(events)
    else:
        st.warning("No events found.")

    # Display volunteers for a selected event
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT DISTINCT event_id FROM event_volunteers")
            # event_ids = [event['event_id'] for event in cursor.fetchall()]
            event_ids = [event[0] for event in cursor.fetchall()]

        except Error as e:
            st.error(f"Error getting event IDs: {e}")

        if event_ids:
            selected_event_id = st.selectbox("Select Event:", event_ids)
            try:
                cursor.execute("SELECT student_id FROM event_volunteers WHERE event_id = %s", (selected_event_id,))
                volunteers = cursor.fetchall()
            except Error as e:
                st.error(f"Error getting volunteers: {e}")
                volunteers = []

            if volunteers:
                st.write("Volunteers Table:")
                st.table(volunteers)
            else:
                st.warning("No volunteers found for the selected event.")
        else:
            st.warning("No volunteers exist")
        
        connection.close()


if __name__ == "__main__":
    admin_id = st.session_state.user_id
    if admin_id:
        manage_events()
    else:
       st.warning("Please Login First")