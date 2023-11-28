import mysql.connector
from mysql.connector import Error
import streamlit as st

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
    
def get_student_details(student_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        connection.close()
        return student

def manage_account(student_id):
    st.title("Manage Account")

    # Fetch student details from the database
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        connection.close()

    if student:
        # Section to view points
        st.header("View Points")
        view_points(student_id)

        # Section to reset password
        st.header("Reset Password")
        reset_password(student_id)

        # Section to manage profile
        st.header("Manage Profile")
        manage_profile(student_id, student['name'], student['username'], student['year_of_study'])


def reset_password(student_id):
    # Reset password functionality
    new_password = st.text_input("Enter New Password:", type="password")
    if st.button("Reset Password"):
        # Update the password in the login table
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            student = get_student_details(student_id)
            cursor.execute("UPDATE login SET password = %s WHERE username = %s", (str(new_password), student['username']))
            connection.commit()
            st.success("Password reset successful!")
            connection.close()

# Function to view points
def view_points(student_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT points_owned FROM student WHERE student_id = %s", (student_id,))
        result = cursor.fetchone()
        connection.close()
        if result:
            st.write(f"Points Owned: {result['points_owned']}")
        else:
            st.warning("Unable to retrieve points information.")

# Function to manage profile
def manage_profile(student_id, current_name, current_username, current_year_of_study):
    st.subheader("Update Profile")

    # Change name
    new_name = st.text_input("Change Name:", value=current_name)
    
    # Change year of study with a limit of 1 to 4
    new_year_of_study = st.number_input("Change Year of Study:", min_value=1, max_value=4, value=current_year_of_study, step=1)

    if st.button("Update Profile"):
        # Update values in the student table
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            student = get_student_details(student_id)
            
            cursor.execute("UPDATE student SET name = %s, year_of_study = %s WHERE student_id = %s",
                           (new_name, new_year_of_study, student_id))

            connection.commit()

            st.success("Profile updated successfully!")
            connection.close()


if __name__== "__main__":
    student_id = st.session_state.user_id
    if student_id:
        manage_account(student_id)
    else:
        st.write("Please Login to your Account!!!")
