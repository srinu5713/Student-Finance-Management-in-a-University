# pages/manage_services.py
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

def manage_services(student_id):
    st.title("Manage Services")

    # Add new service
    st.header("Add New Service")
    add_service()

    # View and manage existing services
    st.header("Your Services")
    view_services(student_id)

def add_service():
    # Get the last service ID and increment it for the new service
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(service_id) FROM service")
        last_service_id = cursor.fetchone()[0]
        new_service_id = last_service_id + 1 if last_service_id else 1
        connection.close()

    # Input fields for adding a new service
    type_options = ["Academic", "Co-curricular", "Personal","Lending Things","Others"]  # Add more options as needed
    new_type = st.selectbox("Service Type:", type_options)
    new_name = st.text_input("Service Name:")
    new_price = st.number_input("Service Price:", min_value=0.0)

    if st.button("Add Service"):
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO service (service_id, type, name, price, student_id) VALUES (%s, %s, %s, %s, %s)",
                           (new_service_id, new_type, new_name, new_price, student_id))
            connection.commit()
            st.success("Service added successfully!")
            connection.close()

def view_services(student_id):
    # Fetch and display existing services for the current student
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM service WHERE student_id = %s", (student_id,))
        services = cursor.fetchall()
        connection.close()

        if services:
            for service in services:
                st.write(f"Service ID: {service['service_id']}")
                st.write(f"Type: {service['type']}")
                st.write(f"Name: {service['name']}")
                st.write(f"Price: {service['price']}")
                st.button(f"Delete Service {service['service_id']}", on_click=delete_service, args=(service['service_id'],))
                # if st.button(f"Go Online: {service['service_id']}", key=f"go_online_{service['service_id']}"):
                    # go_online(service['service_id'])
                st.write("---")
        else:
            st.warning("No services found.")

def delete_service(service_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM service WHERE service_id = %s", (service_id,))
        connection.commit()
        st.success("Service deleted successfully!")
        connection.close()

def go_online(service_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE service SET online = NOT online WHERE service_id = %s", (service_id,))
        connection.commit()
        connection.close()

# if __name__ == "__main__":
#     # student_id = 123  # Replace with the actual student ID
#     student_id = 132
#     manage_services(student_id)


if __name__== "__main__":
    student_id = st.session_state.user_id
    if student_id:
        manage_services(student_id)
    else:
        st.write("Please Login to your Account!!!")