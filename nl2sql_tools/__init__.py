import mysql.connector
from mysql.connector import Error

db_connection = None

def initialize_db_connection(host, user, password, database):
    """
    Initialize the global database connection.
    
    Args:
    host (str): The hostname of the MySQL server
    user (str): The username for the MySQL server
    password (str): The password for the MySQL server
    database (str): The name of the database to connect to
    
    Returns:
    None
    """
    global db_connection
    try:
        db_connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        print("Database connection successful")
    except Error as e:
        print(f"Error connecting to the database: {e}")

def get_db_connection():
    """
    Get the global database connection.
    
    Returns:
    mysql.connector.connection.MySQLConnection: The database connection object
    """
    global db_connection
    if db_connection is None or not db_connection.is_connected():
        print("Database connection is not initialized or has been closed.")
        return None
    return db_connection

def close_db_connection():
    """
    Close the global database connection.
    
    Returns:
    None
    """
    global db_connection
    if db_connection and db_connection.is_connected():
        db_connection.close()
        print("Database connection closed")