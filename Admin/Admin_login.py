import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector
from mysql.connector import Error
from streamlit_extras.switch_page_button import switch_page 

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

# Function to hash the password (in a real-world scenario, use a proper hashing library)
def hash_password(password):
    return password  # For simplicity, returning the password as is (not secure)

# Placeholder function to check if the username already exists in the database
def username_exists(username):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM login WHERE username = %s", (username,))
        count = cursor.fetchone()[0]
        connection.close()
        return count > 0


# Streamlit app
def login_page():
        st.title("Admin Page")
        st.subheader("Login")
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")

        # Login button
        if st.button("Login"):
            connection = create_connection()
            if connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM login WHERE username = %s", (username,))
                user = cursor.fetchone()
                if user and user['password'] == password:
                    if user['user_type'] == 'admin':
                        admin= cursor.execute("SELECT admin_id FROM recharge_point WHERE username = %s", (username,))
                        admin = cursor.fetchone()
                        st.session_state.user_id = admin['admin_id']
                        st.success("Login successful! Redirecting to admin dashboard...")
                        switch_page('Manage_Students')

                else:
                    st.error("Incorrect credentials. Please try again.")

                connection.close()
    
        # Logout button
        if st.button("Logout"):
        # Clear the user_id and switch back to the login page
            st.session_state.user_id = None


if __name__ == "__main__":
    login_page()
