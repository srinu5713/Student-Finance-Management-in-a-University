import streamlit as st
import mysql.connector
from mysql.connector import Error

if 'user_id' not in st.session_state:
    st.session_state.user_id = None

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

# Function to get total number of vendors
def get_total_vendors():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM vendor")
        total_vendors = cursor.fetchone()[0]
        connection.close()
        return total_vendors

# Function to get details of all vendors
def get_all_vendors():
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vendor")
        vendors = cursor.fetchall()
        connection.close()
        return vendors

def get_vendor_username(vendor_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT username FROM vendor WHERE vendor_id = %s", (vendor_id,))
        vendor_username = cursor.fetchone()
        connection.close()
        return vendor_username['username'] if vendor_username else None

# Function to delete a vendor by ID
def delete_vendor(vendor_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        vendor_username = get_vendor_username(vendor_id)
        if vendor_username:
            cursor.execute("DELETE FROM vendor WHERE vendor_id = %s", (vendor_id,))
            cursor.execute("DELETE FROM login WHERE username = %s", (vendor_username,))
            # Get stall_id associated with the vendor
            cursor.execute("SELECT stall_id FROM vendor WHERE vendor_id = %s", (vendor_id,))
            stall_id = cursor.fetchone()
            # Delete stall associated with the vendor
            if stall_id:
                cursor.execute("DELETE FROM stall_item WHERE stall_id = %s", (stall_id,))
                cursor.execute("DELETE FROM stall WHERE stall_id = %s", (stall_id,))
            connection.commit()
            connection.close()
            st.success(f"Vendor {vendor_id} and associated stall deleted successfully!")
        else:
            st.warning("Vendor not found.")

def manage_vendors():
    st.title("Manage Vendors (Admin)")

    # Total number of vendors
    total_vendors = get_total_vendors()
    st.write(f"Total Number of Vendors: {total_vendors}")

    # Table of all vendors
    st.write("Details of All Vendors:")
    vendors = get_all_vendors()
    st.table(vendors)

    # Dropdown to select vendor for detailed view and deletion
    selected_vendor_id = st.selectbox("Select Vendor for Details/Deletion:", [vendor['vendor_id'] for vendor in vendors])

    # Display details of the selected vendor
    selected_vendor = next((vendor for vendor in vendors if vendor['vendor_id'] == selected_vendor_id), None)
    if selected_vendor:
        st.write(f"Details of Vendor ID: {selected_vendor_id}")
        st.write(f"Vendor Name: {selected_vendor['vendor_name']}")
        st.write(f"Username: {selected_vendor['username']}")
        st.write(f"Profits: {selected_vendor['profits']}")
        st.write(f"Stall ID: {selected_vendor['stall_id']}")
        st.markdown("---")

        # Delete button for the selected vendor
        if st.button("Delete Selected Vendor"):
            delete_vendor(selected_vendor_id)

if __name__ == "__main__":
    admin_id = st.session_state.user_id
    if admin_id:
        manage_vendors()
    else:
        st.warning("Please Login First")
