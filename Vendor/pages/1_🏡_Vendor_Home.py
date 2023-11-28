import streamlit as st
import mysql.connector
from mysql.connector import Error
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

# Function to get vendor details including shop name and location
def get_vendor_details(vendor_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT v.*, s.stall_name, s.location
            FROM vendor v
            JOIN stall s ON v.stall_id = s.stall_id
            WHERE v.vendor_id = %s
        """, (vendor_id,))
        vendor = cursor.fetchone()
        connection.close()
        return vendor

# Vendor Home Dashboard
def vendor_home(vendor_id):
    st.title("Vendor Home")

    # Get vendor details
    vendor = get_vendor_details(vendor_id)

    if vendor:
        st.write(f"Welcome, {vendor['vendor_name']}!")
        st.write(f"Username: {vendor['username']}")
        st.write(f"Vendor ID: {vendor['vendor_id']}")
        st.write(f"Stall ID: {vendor['stall_id']}")
        st.write(f"Shop Name: {vendor['stall_name']}")
        st.write(f"Stall Location: {vendor['location']}")
        st.write(f"Profits: {vendor['profits']}")

    if st.button("Logout"):
        st.session_state.user_id = None
        switch_page("login")


if __name__ == "__main__":
    vendor_id =st.session_state.user_id# Replace with the actual vendor ID
    if vendor_id:
        vendor_home(vendor_id)
    else:
        st.write("Please Login to your Account!!!")
