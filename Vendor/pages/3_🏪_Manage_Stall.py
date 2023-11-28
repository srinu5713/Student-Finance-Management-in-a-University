import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import datetime, date

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


def get_stall_id(vendor_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT stall_id FROM vendor WHERE vendor_id = %s", (vendor_id,))
        stall = cursor.fetchone()
        connection.close()
        return stall['stall_id'] if stall else None


# Function to update stall closing time
def update_stall_times(stall_id, new_opening_time, new_closing_time):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        # Convert new_opening_time and new_closing_time to datetime if needed
        if not isinstance(new_opening_time, datetime):
            new_opening_time = datetime.combine(date.today(), new_opening_time)
        if not isinstance(new_closing_time, datetime):
            new_closing_time = datetime.combine(date.today(), new_closing_time)

        # Update the opening and closing times in the stall table
        cursor.execute("""
            UPDATE stall
            SET open_time = %s, close_time = %s
            WHERE stall_id = %s
        """, (new_opening_time, new_closing_time, stall_id))

        connection.commit()
        connection.close()

# Function to get stall items
def get_stall_items(stall_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT i.*, si.quantity
            FROM item i
            JOIN stall_item si ON i.item_id = si.item_id
            WHERE si.stall_id = %s
        """, (stall_id,))
        items = cursor.fetchall()
        connection.close()
        return items

# Function to add new item to stall
def add_new_item(stall_id, item_name, quantity, price):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        cursor.execute("SELECT MAX(item_id) FROM item")
        max_item_id = cursor.fetchone()[0] or 0
        new_item_id = max_item_id + 1

        cursor.execute("""
            INSERT INTO item (item_id, item_name, price)
            VALUES (%s, %s, %s)
        """, (new_item_id, item_name, price))

        cursor.execute("""
            INSERT INTO stall_item (stall_id, item_id, quantity)
            VALUES (%s, %s, %s)
        """, (stall_id, new_item_id, quantity))

        connection.commit()
        connection.close()

# Function to delete item from stall
def delete_item(stall_id, item_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM stall_item
            WHERE stall_id = %s AND item_id = %s
        """, (stall_id, item_id))

        cursor.execute("""
            DELETE FROM item
            WHERE item_id = %s
            AND NOT EXISTS (
                SELECT 1 FROM stall_item WHERE item_id = %s
            )
        """, (item_id, item_id))

        connection.commit()
        connection.close()

# Function to update item quantity
def update_item_quantity(stall_id, item_id, new_quantity):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        # Update the item quantity in stall_item table
        cursor.execute("""
            UPDATE stall_item
            SET quantity = %s
            WHERE stall_id = %s AND item_id = %s
        """, (new_quantity, stall_id, item_id))

        connection.commit()
        connection.close()

# Manage Stall Items
def manage_stall_items(vendor_id):

    st.title("Manage Stall Items")
    stall_id = get_stall_id(vendor_id)
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vendor WHERE vendor_id = %s", (vendor_id,))
        vendor = cursor.fetchone()
    # Display existing stall items
    existing_items = get_stall_items(stall_id)
    st.write("Existing Items:")
    for item in existing_items:
        st.write(f"Item ID: {item['item_id']}")
        st.write(f"Item Name: {item['item_name']}")
        st.write(f"Price: {item['price']}")
        st.write(f"Quantity: {item['quantity']}")
        
        # Slider for updating item quantity
        new_quantity = st.slider(
            f"New Quantity for Item {item['item_id']}",
            min_value=0, max_value=100,
            value=item['quantity']
        )
                    
        if st.button(f"Update Quantity for Item {item['item_id']}"):
            update_item_quantity(stall_id, item['item_id'], new_quantity)
            st.success(f"Quantity for Item {item['item_id']} updated successfully!")

        # Delete button for each item
        if st.button(f"Delete Item {item['item_id']}"):
            delete_item(stall_id, item['item_id'])
            st.success(f"Item {item['item_id']} deleted successfully!")

        # Line separator between items
        st.markdown("---")

    # Input fields for adding new item
    new_item_name = st.text_input("Enter New Item Name:")
    new_quantity = st.slider("Enter Quantity for New Item:", min_value=0, max_value=100, value=0)
    new_price = st.number_input("Enter Price for New Item:")

    if st.button("Add New Item"):
        # Add new item to stall
        add_new_item(stall_id, new_item_name, new_quantity, new_price)
        st.success("New item added successfully!")
    
    new_opening_time=st.time_input("Enter New Opening Time:")
    new_closing_time = st.time_input("Enter New Closing Time:")
    
    if st.button("Update Opening and Closing Times"):
        # Update the opening and closing times for the stall
        update_stall_times(vendor['stall_id'], new_opening_time, new_closing_time)
        st.success("Opening and closing times updated successfully!")
    # st.experimental_rerun()

if __name__ == "__main__":
    # Replace with the actual stall ID
    vendor_id =st.session_state.user_id
    if vendor_id:
            manage_stall_items(vendor_id)
    else:
        st.write("Please Login to your Account!!!")