import streamlit as st
import mysql.connector
from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool
from datetime import datetime

if 'user_id' not in st.session_state:
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

# Procedure to Deduct Points from Student
def deduct_points_from_student(student_id, points):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.callproc('DeductPointsFromStudent', [student_id, points])
            connection.commit()
        except Error as e:
            connection.rollback()
            st.warning(f"Failed to deduct points from student. Error: {e}")
        finally:
            connection.close()

# Procedure to Add Points to Vendor
def add_points_to_vendor(vendor_id, points):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.callproc('AddPointsToVendor', [vendor_id, points])
            connection.commit()
        except Error as e:
            connection.rollback()
            st.warning(f"Failed to add points to vendor. Error: {e}")
        finally:
            connection.close()

# Procedure to Record Vendor Transaction
def record_vendor_transaction(from_id, to_id, points):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.callproc('RecordVendorTransaction',
                            [from_id, to_id, points])
            connection.commit()
        except Error as e:
            connection.rollback()
            st.warning(f"Failed to record vendor transaction. Error: {e}")
        finally:
            connection.close()


# Procedure to Deduct Points from Buyer Student and Add Points to Seller Student
def deduct_points_and_add_to_seller(buyer_id, seller_id, points):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Get the current points of the buyer
            cursor.execute(
                "SELECT points_owned FROM student WHERE student_id = %s", (buyer_id,))
            buyer_points_result = cursor.fetchone()

            if not buyer_points_result:
                st.warning(
                    "Invalid buyer_id. Please check the student records.")
                return

            buyer_points = buyer_points_result[0]

            # Check if the buyer has enough points
            if buyer_points >= points:
                # Deduct points from the buyer
                cursor.callproc('DeductPointsFromBuyerAndAddPointsToSeller', [
                                buyer_id, seller_id, points])
                connection.commit()
            else:
                st.warning("Insufficient points for the transaction.")
        except Error as e:
            connection.rollback()
            st.warning(f"Failed to process transaction. Error: {e}")
        finally:
            connection.close()

# Procedure to Record Service Transaction
def record_service_transaction(buyer_id, seller_id, service_id, points):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Insert the transaction record
            cursor.callproc('RecordServiceTransaction', [
                            buyer_id, seller_id, service_id, points])
            connection.commit()
        except Error as e:
            connection.rollback()
            st.warning(f"Failed to record service transaction. Error: {e}")
        finally:
            connection.close()


# Function to get a list of shops
def get_shops():
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM stall")
        shops = cursor.fetchall()
        connection.close()
        return shops

# Function to get items for a specific shop
def get_items_in_shop(stall_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT i.*, si.quantity AS quantity_in_stall
            FROM item i
            LEFT JOIN stall_item si ON i.item_id = si.item_id
            WHERE si.stall_id = %s
        """, (stall_id,))
        items = cursor.fetchall()
        connection.close()
        return items

# Function to get services for a specific student
def get_services(student_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM available_services
            WHERE student_id != %s
        """, (student_id,))
        services = cursor.fetchall()
        connection.close()
        return services


# Function to buy an item with daily limit and funds check
def buy_item(student_id, item_id, points):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            connection.start_transaction()

            # Check if the item_id is valid
            cursor.execute("SELECT * FROM item WHERE item_id = %s", (item_id,))
            item_result = cursor.fetchone()

            if not item_result:
                st.warning("Invalid item_id. Please check the item records.")
                return

            # Check if the item is available in the stall
            cursor.execute("""
                SELECT v.vendor_id
                FROM stall s
                JOIN vendor v ON s.stall_id = v.stall_id
                JOIN stall_item si ON s.stall_id = si.stall_id
                WHERE si.item_id = %s
            """, (item_id,))

            vendor_result = cursor.fetchone()
            if not vendor_result:
                st.warning("Item not available in the selected stall.")
                return

            vendor_id = vendor_result[0]

            # Check daily limit
            cursor.execute(
                "SELECT daily_limit FROM student WHERE student_id = %s", (student_id,))
            daily_limit_result = cursor.fetchone()

            if not daily_limit_result:
                st.warning(
                    "Invalid student_id. Please check the student records.")
                return

            daily_limit = daily_limit_result[0]

            if daily_limit >= points:
                if check_sufficient_funds(student_id, points):

                    deduct_points_from_student(student_id, points)
                    add_points_to_vendor(vendor_id, points)
                    record_vendor_transaction(student_id, vendor_id, points)
                    cursor.execute(
                        "UPDATE student SET daily_limit = daily_limit - %s WHERE student_id = %s", (points, student_id))

                    connection.commit()
                    st.success(f"Item {item_id} purchased successfully!")
                else:
                    st.warning("Insufficient funds. Purchase canceled.")
            else:
                st.warning(
                    "Daily limit exceeded or insufficient funds. Purchase canceled.")
        except Error as e:
            connection.rollback()
            st.warning(f"Purchase canceled. Error: {e}")
        finally:
            connection.close()


# Function to buy a service with daily limit and funds check
def buy_service(student_id, service_id, points):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            connection.start_transaction()

            # Get the seller_id from the service table
            cursor.execute(
                "SELECT student_id FROM service WHERE service_id = %s", (service_id,))
            seller_id_result = cursor.fetchone()

            if not seller_id_result:
                st.warning(
                    "Invalid service_id. Please check the service records.")
                return

            seller_id = seller_id_result[0]

            # Check daily limit
            cursor.execute(
                "SELECT daily_limit FROM student WHERE student_id = %s", (student_id,))
            daily_limit_result = cursor.fetchone()

            if not daily_limit_result:
                st.warning(
                    "Invalid student_id. Please check the student records.")
                return

            daily_limit = daily_limit_result[0]

            # Check if the points for the service purchase are within the daily limit
            if daily_limit >= points:
                if check_sufficient_funds(student_id, points):
                    deduct_points_and_add_to_seller(
                        student_id, seller_id, points)
                    record_service_transaction(
                        student_id, seller_id, service_id, points)

                    # Update the daily limit after the purchase
                    cursor.execute(
                        "UPDATE student SET daily_limit = daily_limit - %s WHERE student_id = %s", (points, student_id))

                    connection.commit()
                    st.success(f"Service {service_id} purchased successfully!")
                else:
                    st.warning("Insufficient funds. Purchase canceled.")
            else:
                st.warning("Daily limit exceeded. Purchase canceled.")
        except Error as e:
            connection.rollback()
            st.warning(f"Purchase canceled. Error: {e}")
        finally:
            connection.close()


# Function to check if the student has sufficient funds
def check_sufficient_funds(student_id, points):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT points_owned FROM student WHERE student_id = %s", (student_id,))
            points_owned_result = cursor.fetchone()

            if not points_owned_result:
                st.warning(
                    "Invalid student_id. Please check the student records.")
                return False

            points_owned = points_owned_result[0]

            return points_owned >= points
        except Error as e:
            st.warning(f"Error checking funds: {e}")
            return False
        finally:
            connection.close()


def marketplace(student_id):
    st.title("Student Marketplace")

    shops = get_shops()

    if shops:
        selected_shop = st.selectbox(
            "Select a Shop:", shops, format_func=lambda x: x['stall_name'])

        items_in_shop = get_items_in_shop(selected_shop['stall_id'])

        st.write(f"Available Items in {selected_shop['stall_name']}:")
        for item in items_in_shop:
            st.write(f"Item ID: {item['item_id']}")
            st.write(f"Item Name: {item['item_name']}")
            st.write(f"Price: {item['price']}")
            st.write(f"Quantity in Stall: {item['quantity_in_stall']}")

            if st.button(f"Buy Item {item['item_id']}"):
                buy_item(student_id, item['item_id'], item['price'])

            st.markdown("---")

        services = get_services(student_id)

        if services:
            selected_service = st.selectbox(
                "Select a Service:", services, format_func=lambda x: x['name'])

            st.write(f"Selected Service: {selected_service['name']}")
            st.write(f"Price: {selected_service['price']}")

            if st.button(f"Buy Service {selected_service['service_id']} for {selected_service['price']} points"):
                buy_service(
                    student_id, selected_service['service_id'], selected_service['price'])
        else:
            st.warning("No available services.")
    else:
        st.warning("No available shops.")


if __name__ == "__main__":
    student_id = st.session_state.user_id
    if student_id:
        marketplace(student_id)
    else:
        st.write("Please Login to your Account!!!")
