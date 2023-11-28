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


def validate_student_registration_data(student_id, name, year_of_study):
    if not student_id.isdigit() or int(student_id) <= 0:
        raise ValueError("Invalid student ID. Please enter a positive integer.")
    if len(name) < 3:
        raise ValueError("Name must be at least 3 characters long.")
    if not 1 <= year_of_study <= 4:
        raise ValueError("Year of study must be between 1 and 4.")


def username_exists(username):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM login WHERE username = %s", (username,))
        count = cursor.fetchone()[0]
        connection.close()
        return count > 0


def register_page():
    st.title("Student Registration")

    user_type ="student"

    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    try:
        validate_common_registration_data(username, password)

        if username_exists(username):
            st.warning("Username already exists. Please choose a different username.")
            return

        if user_type == "student":
            student_id = st.text_input("Student ID:")
            name = st.text_input("Name:")
            year_of_study = st.number_input("Year of Study:", min_value=1, max_value=4)

            validate_student_registration_data(student_id, name, year_of_study)


        if st.button("Register"):
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                try:
                    # Insert into login table
                    cursor.execute("INSERT INTO login (username, password, user_type) VALUES (%s, %s, %s)",
                                (username, password, user_type))

                    if user_type == "student":
                        # Insert into student table
                        cursor.execute("INSERT INTO student (student_id, username, name,points_owned ,year_of_study,daily_limit) VALUES (%s, %s, %s, %s,%s,%s)",
                                    (student_id, username, name, 0,year_of_study,1000))
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
        # Handle invalid data error
        st.error(f"Error: {ve}")
        st.warning("Please check the entered data and try again.")


# Streamlit app
def login_page():
    st.title("Student Dashboard")

    with st.sidebar:
        selected = option_menu("Student Finance", ["Login", "Register"])

    if selected == "Login":
        st.subheader("Login")
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")

        # Login button
        if st.button("Login"):
            connection = create_connection()
            try:
                if connection:
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM login WHERE username = %s", (username,))
                    user = cursor.fetchone()
                    if user and user['password'] == password:
                        if user['user_type'] == 'student':
                            cursor.execute("SELECT student_id FROM student WHERE username = %s", (username,))
                            student = cursor.fetchone()
                            if student:
                                st.success("Login successful! Redirecting to student dashboard...")
                                st.session_state.user_id = student['student_id']
                                print(st.session_state.user_id)
                                switch_page('Student_Home')
                            else:
                                st.warning("Student data not found. Please check your credentials.")
                    else:
                        st.error("Incorrect credentials. Please try again.")


            
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if connection.is_connected():
                    connection.close()
        
    elif selected == "Register":
        register_page()

if __name__ == "__main__":
    login_page()