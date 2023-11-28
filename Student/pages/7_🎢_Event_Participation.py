import streamlit as st
import mysql.connector
from mysql.connector import Error
import qrcode
from PIL import Image
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


def has_volunteered(student_id, event_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM event_volunteers WHERE student_id = %s AND event_id = %s", (student_id, event_id))
        participation = cursor.fetchone()
        connection.close()
        return participation is not None


def generate_ticket(student_id, event_id, event_name, event_date):
    ticket_info = f"Event Ticket\nStudent ID: {student_id}\nEvent ID: {event_id}\nEvent Name: {event_name}\nEvent Date: {event_date}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,
        border=2,
    )

    qr.add_data(ticket_info)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    st.write(ticket_info)
    st.image("ticket_qr.png", caption="Scan QR Code for Ticket Details", use_column_width=None)



# Function to check if a student has already participated in an event
def has_participated(student_id, event_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM has_registered WHERE student_id = %s AND event_id = %s", (student_id, event_id))
        participation = cursor.fetchone()
        connection.close()
        return participation is not None


def participate_as_volunteer(student_id, selected_event_id, points):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        try:
            if not has_volunteered(student_id, selected_event_id):
                cursor.execute("SELECT COUNT(student_id)  FROM event_volunteers WHERE event_id = %s", (selected_event_id,))
                result = cursor.fetchone()
                current_volunteers_count = result[0]

                cursor.execute("SELECT no_of_volunteers FROM event WHERE event_id = %s", (selected_event_id,))
                allowed_volunteers_result = cursor.fetchone()

                if allowed_volunteers_result:
                    allowed_volunteers = allowed_volunteers_result[0]
                    if current_volunteers_count < allowed_volunteers:
                        cursor.execute("INSERT INTO event_volunteers (student_id, event_id) VALUES (%s, %s)", (student_id, selected_event_id))
                        cursor.callproc('AddPointsAndRecordTransaction', (student_id, points, 1))
                        connection.commit()
                        st.success("You have successfully joined the event as a volunteer!")
                    else:
                        st.write("There is no need for more volunteers")
                else:
                    st.warning("Failed to fetch the allowed number of volunteers.")
            else:
                st.warning("You have already volunteered for this event.")

        except Error as e:
            st.error(f"Error participating as a volunteer: {e}")

        finally:
            connection.close()



def event_participation():
    st.title("Event Participation")
    connection = create_connection()

    if connection:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM event")
        events = cursor.fetchall()
        st.write("Events Table:")
        st.table(events)

        # Select participation option
        participation_option = st.radio("Select Participation Option:", ["Participate", "Volunteer"])

        # Fetch events from the database
        cursor.execute("SELECT event_id FROM event")
        events = cursor.fetchall()
        # Create a list of event IDs for the selectbox
        event_ids = [event['event_id'] for event in events]
        # Select an event
        selected_event_id = st.selectbox("Select Event:", event_ids)

        # Fetch event details
        cursor.execute("SELECT * FROM event WHERE event_id = %s", (selected_event_id,))
        event = cursor.fetchone()

        if event:
            if participation_option == "Participate":
                st.write(f"Event Name: {event['event_name']}")
                st.write(f"Event Type: {event['type']}")
                st.write(f"Date: {event['date']}")
                st.write(f"Fee: {event['entry_fee']}")

                # Fetch the current number of participants for the selected event
                cursor.execute("SELECT COUNT(student_id) as count FROM has_registered WHERE event_id = %s", (selected_event_id,))
                participants_count_result = cursor.fetchone()
                participants_count = participants_count_result['count']

                if participants_count is not None and participants_count <= event['num_of_participants']:
                    if not has_volunteered(st.session_state.user_id, selected_event_id):
                        fee = event['entry_fee']
                        if st.button("Participate"):
                            cursor.execute("UPDATE student SET points_owned = points_owned - %s WHERE student_id = %s", (fee, st.session_state.user_id))
                            cursor.execute("INSERT INTO has_registered (student_id, event_id) VALUES (%s, %s)", (st.session_state.user_id, selected_event_id))
                            connection.commit()
                            st.success(f"You have successfully participated in the event! {fee} points deducted.")

                    else:
                        st.warning("You have already participated in this event.")
                else:
                    st.write("Tickets are sold out!!")

            elif participation_option == "Volunteer":
                st.write(f"Event Name: {event['type']}")
                st.write(f"Date: {event['date']}")
                st.write(f"Eligible Points: {event['eligible_points']}")

                # Check if the student can volunteer
                if not has_participated(st.session_state.user_id, selected_event_id):
                    if st.button("Volunteer"):
                        participate_as_volunteer(st.session_state.user_id, selected_event_id, event['eligible_points'])
                else:
                    st.warning("You have already participated in this event as a volunteer.")

            # Fetch registered events for the user
            st.header("Tickets for Registered events")
            cursor.execute("SELECT * FROM has_registered WHERE student_id=%s", (st.session_state.user_id,))
            registered_events = cursor.fetchall()
            registered_event_ids = [event['event_id'] for event in registered_events]

            # Display the ticket
            if registered_event_ids:
                selected_ticket_id = st.selectbox("Select the ticket for the event", registered_event_ids)
                cursor.execute("SELECT * FROM event WHERE event_id=%s", (selected_ticket_id,))
                selected_event_details = cursor.fetchone()
                if st.button("Generate Ticket"):
                    generate_ticket(st.session_state.user_id, selected_ticket_id, selected_event_details['type'], selected_event_details['date'])
            else:
                st.write("No Tickets Available!!")

            # Display volunteered events
            st.header("Volunteered in:")
            cursor.execute("SELECT event_id FROM event_volunteers WHERE student_id=%s", (st.session_state.user_id,))
            volunteered_in = cursor.fetchall()
            if volunteered_in:
                st.table(volunteered_in)
            else:
                st.write("NO events volunteered")

    connection.close()

if __name__ == "__main__":
    student_id = st.session_state.user_id  
    if student_id:
        event_participation()
    else:
        st.write("Please Login to your Account!!!")
