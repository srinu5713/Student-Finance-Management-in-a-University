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


# Function to get vendor details
def get_vendor_details(vendor_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT v.*, s.stall_name
            FROM vendor v
            JOIN stall s ON v.stall_id = s.stall_id
            WHERE v.vendor_id = %s
        """, (vendor_id,))
        vendor = cursor.fetchone()
        connection.close()
        return vendor


# Function to update vendor details
def update_vendor_details(vendor_id, new_name, new_shop_name, new_password):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        vendor = get_vendor_details(vendor_id)

        # Update vendor details
        cursor.execute("""
            UPDATE vendor
            SET vendor_name = %s
            WHERE vendor_id = %s
        """, (new_name, vendor_id))

        # Update stall details
        cursor.execute("""
            UPDATE stall
            SET stall_name = %s
            WHERE stall_id = %s
        """, (new_shop_name, vendor['stall_id']))

        # Update password in the login table (assuming there's a login table)
        cursor.execute("""
            UPDATE login
            SET password = %s
            WHERE username = %s
        """, (new_password, vendor['username']))

        connection.commit()
        connection.close()

        # Trigger a rerun to update the displayed values
        st.experimental_rerun()

# Vendor Account Management
def vendor_account_management(vendor_id):
    st.title("Vendor Account Management")

    # Get vendor details
    vendor = get_vendor_details(vendor_id)

    if vendor:
        st.write(f"Current Name: {vendor['vendor_name']}")
        st.write(f"Current Shop Name: {vendor['stall_name']}")
        st.write(f"Current Username: {vendor['username']}")

        # Input fields for updating vendor details
        new_name = st.text_input("Enter New Name:", vendor['vendor_name'])
        new_shop_name = st.text_input(
            "Enter New Shop Name:", vendor['stall_name'])
        new_password = st.text_input("Enter New Password:", type="password")

        update_details_placeholder = st.empty()

        if st.button("Update Details"):
            # Update vendor details
            update_vendor_details(vendor_id, new_name,
                                  new_shop_name, new_password)

            # Display updated details
            update_details_placeholder.success("Details updated successfully!")

            # Clear input fields
            st.text_input("Enter New Name:", "")
            st.text_input("Enter New Shop Name:", "")
            st.text_input("Enter New Password:", type="password")

if __name__ == "__main__":
    vendor_id =st.session_state.user_id
    if vendor_id:
        vendor_account_management(vendor_id)
    else:
        st.write("Please Login to your Account!!!")
