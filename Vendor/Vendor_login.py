
import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector
from mysql.connector import Error
from streamlit_extras.switch_page_button import switch_page 

st.session_state.user_id = None

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


def validate_common_registration_data(username, password):
    if len(username) < 3:
        raise ValueError("Username must be at least 3 characters long.")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")


# Function to validate vendor-specific registration data
# def validate_vendor_registration_data(stall_id):
#     if not stall_id.isdigit() or int(stall_id) <= 0:
#         raise ValueError("Invalid stall ID. Please enter a positive integer.")

# Placeholder function to check if the username already exists in the database
def username_exists(username):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM login WHERE username = %s", (username,))
        count = cursor.fetchone()[0]
        connection.close()
        return count > 0

# Placeholder function to get the next vendor ID from the database
def get_next_vendor_id():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(vendor_id) FROM vendor")
        max_vendor_id = cursor.fetchone()[0]
        connection.close()
        return max_vendor_id + 1 if max_vendor_id is not None else 1

def next_stall_id():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(stall_id) FROM STALL")
        max_stall_id = cursor.fetchone()[0]
        connection.close()
        return max_stall_id + 1 if max_stall_id is not None else 1

# Registration page
def register_page():
    st.title("Registration")

    user_type ="vendor"
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    try:
        validate_common_registration_data(username, password)

        if username_exists(username):
            st.warning("Username already exists. Please choose a different username.")
            return

        if user_type == "vendor":
            name = st.text_input("Vendor Name:")
            stall_id = next_stall_id()
            stall_name=st.text_input("Stall Name:")
            stall_type = st.selectbox("Stall Type:", ["Food", "Clothing", "Electronics", "Stationary","Others"])
            location = st.selectbox("Stall Location:", ["Block A", "Block B","Block C","Block D","Main Block"])

            # validate_vendor_registration_data(stall_id)

        if st.button("Register"):
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                try:
                    # Insert into login table
                    cursor.execute("INSERT INTO login (username, password, user_type) VALUES (%s, %s, %s)",
                                (username, password, user_type))
                    if user_type == "vendor":
                        # Insert into vendor table
                        cursor.execute("INSERT INTO STALL(stall_id,stall_name,type,location) VALUES(%s,%s,%s,%s) ",(stall_id,stall_name,stall_type,location))
                        cursor.execute("INSERT INTO vendor (vendor_id, username, vendor_name, stall_id) VALUES (%s, %s, %s, %s)",
                                    (get_next_vendor_id(), username, name, stall_id))

                    connection.commit()
                    st.success("Registration successful!")

                except mysql.connector.IntegrityError as e:
                    st.warning("Error is "+str(e))

                except Exception as e:
                    st.error(f"Error: {e}")
                    st.warning("Please check the entered data and try again.")
                finally:
                    connection.close()
    except ValueError as ve:

        st.error(f"Error: {ve}")
        st.warning("Please check the entered data and try again.")


def login_page():
    st.title("Vendor Management")

    with st.sidebar:
        selected = option_menu("Student Finance", ["Login", "Register"])

    if selected == "Login":
        st.subheader("Login")
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")

        if st.button("Login"):
            connection = create_connection()
            try:
                if connection:
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM login WHERE username = %s", (username,))
                    user = cursor.fetchone()
                    
                if user and user['password'] == password:
                    if user['user_type'] == 'vendor':
                        vendor = cursor.execute("SELECT vendor_id FROM vendor WHERE username = %s", (username,))
                        vendor=cursor.fetchone()
                        st.success("Login successful! Redirecting to vendor dashboard...")
                        st.session_state.user_id = vendor['vendor_id']
                        switch_page('Vendor_Home')

                else:
                    st.error("Incorrect credentials. Please try again.")
                connection.close()

            # if st.button("Logout"):
            #     st.session_state.user_id = None
            
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if connection.is_connected():
                    connection.close()
        
    elif selected == "Register":
        register_page()

if __name__ == "__main__":
    login_page()
