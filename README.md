# Student Finance Management System

## Prerequisites
- Python 3.7 or higher
- Install the following dependencies using pip:
  - Streamlit
  - Streamlit-extras
  - mysql.connector

## Getting Started

### 1. Source the Database
- Open a terminal window and navigate to the directory containing the `database.sql` file.
- Execute the following command:

```bash
source database.sql 
```

## 2. Run the Admin Login Application
- Go to the admin folder.
- Execute the following command:
```bash
streamlit run Admin_login.py
```
- Open the URL displayed in the terminal window to launch the Admin Login application.


## 3. Run the student Login Application
- Go to the student folder.
- Execute the following command:
```bash
streamlit run Student_login.py
```
- Open the URL displayed in the terminal window to launch the Admin Login application.

## 3. Run the Vendor Login Application
- Go to the vendor folder.
- Execute the following command:
```bash
streamlit run Vendor_login.py
```
- Open the URL displayed in the terminal window to launch the Admin Login application.

## Interacting with the Web Applications
- For each application, access the respective links shown in the terminal window.
    Use the provided GUIs to interact with the database, including:
    Managing student accounts
    Managing vendor accounts
    Managing services and items
    Viewing and managing transactions
    Generating reports

## Making Changes to the Database
    Any changes made to the database using the provided GUIs will be reflected directly in the database.
    Note: Change the database password and name of the database in all files according to your MySQL credentials.

## Feel free to customize it further based on additional details or specific information