from typing import List, Dict, Optional, Any, Union
from mysql.connector import Error, MySQLConnection
from nl2sql import get_db_connection

def list_tables() -> List[str]:
    """
    List all available tables in the database.
    
    Returns:
        List[str]: List of table names
    """
    conn: Optional[MySQLConnection] = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables: List[str] = [table[0] for table in cursor.fetchall()]
    cursor.close()
    
    return tables

def get_table_schema_and_sample(table_name: str) -> str:
    """
    Given the table name, return schema and top 3 rows as string.
    
    Args:
        table_name (str): Name of the table
    
    Returns:
        str: Table schema and top 3 rows
    """
    conn: Optional[MySQLConnection] = get_db_connection()
    if not conn:
        return ""
    
    cursor = conn.cursor(dictionary=True)
    
    # Get table schema
    cursor.execute(f"DESCRIBE {table_name}")
    schema: List[Dict[str, Any]] = cursor.fetchall()
    
    # Get top 3 rows
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
    rows: List[Dict[str, Any]] = cursor.fetchall()
    
    cursor.close()
    
    # Format the output
    output: str = f"Table: {table_name}\n\nSchema:\n"
    for col in schema:
        output += f"{col['Field']} ({col['Type']})\n"
    
    output += "\nSample Data:\n"
    for row in rows:
        output += str(row) + "\n"
    
    return output

def validate_sql_query(query: str) -> bool:
    """
    Validate if the SQL query is valid.
    
    Args:
        query (str): SQL query to validate
    
    Returns:
        bool: True if the query is valid, False otherwise
    """
    conn: Optional[MySQLConnection] = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute(f"EXPLAIN {query}")
        cursor.fetchall()
        cursor.close()
        return True
    except Error:
        cursor.close()
        return False

def run_sql_query(query: str) -> str:
    """
    Run SQL query and return the result in text format.
    
    Args:
        query (str): SQL query to execute
    
    Returns:
        str: Query results in text format
    """
    conn: Optional[MySQLConnection] = get_db_connection()
    if not conn:
        return "Database connection error"
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query)
        results: List[Dict[str, Any]] = cursor.fetchall()
        cursor.close()
        
        if not results:
            return "Query executed successfully, but returned no results."
        
        # Format the output
        output: str = "Query Results:\n"
        for row in results:
            output += str(row) + "\n"
        
        return output
    except Error as e:
        cursor.close()
        return f"Error executing query: {str(e)}"

def get_table_relationships() -> str:
    """
    Get table relationships based on foreign keys.
    
    Returns:
        str: Table relationships in text format
    """
    conn: Optional[MySQLConnection] = get_db_connection()
    if not conn:
        return "Database connection error"
    
    cursor = conn.cursor(dictionary=True)
    query: str = """
    SELECT 
        TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
    FROM
        INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE
        REFERENCED_TABLE_SCHEMA = DATABASE()
        AND REFERENCED_TABLE_NAME IS NOT NULL
    ORDER BY
        TABLE_NAME, COLUMN_NAME;
    """
    
    try:
        cursor.execute(query)
        results: List[Dict[str, Any]] = cursor.fetchall()
        cursor.close()
        
        output: str = "Table Relationships:\n"
        for row in results:
            output += f"{row['TABLE_NAME']}.{row['COLUMN_NAME']} -> {row['REFERENCED_TABLE_NAME']}.{row['REFERENCED_COLUMN_NAME']}\n"
        
        return output
    except Error as e:
        cursor.close()
        return f"Error retrieving table relationships: {str(e)}"

def get_table_statistics(table_name: str) -> str:
    """
    Get statistics for a given table.
    
    Args:
        table_name (str): Name of the table
    
    Returns:
        str: Table statistics in text format
    """
    conn: Optional[MySQLConnection] = get_db_connection()
    if not conn:
        return "Database connection error"
    
    cursor = conn.cursor(dictionary=True)
    queries: List[str] = [
        f"SELECT COUNT(*) as row_count FROM {table_name}",
        f"SHOW COLUMNS FROM {table_name}",
        f"SHOW INDEX FROM {table_name}"
    ]
    
    try:
        output: str = f"Statistics for table '{table_name}':\n\n"
        
        # Row count
        cursor.execute(queries[0])
        row_count: int = cursor.fetchone()['row_count']
        output += f"Total rows: {row_count}\n\n"
        
        # Columns
        cursor.execute(queries[1])
        columns: List[Dict[str, Any]] = cursor.fetchall()
        output += "Columns:\n"
        for col in columns:
            output += f"- {col['Field']} ({col['Type']})\n"
        output += "\n"
        
        # Indexes
        cursor.execute(queries[2])
        indexes: List[Dict[str, Any]] = cursor.fetchall()
        output += "Indexes:\n"
        for idx in indexes:
            output += f"- {idx['Key_name']} ({idx['Column_name']})\n"
        
        cursor.close()
        return output
    except Error as e:
        cursor.close()
        return f"Error retrieving table statistics: {str(e)}"
