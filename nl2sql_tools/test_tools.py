import unittest
from dotenv import load_dotenv
from nl2sql_tools import initialize_db_connection, close_db_connection
from nl2sql_tools.tools import (
    list_tables,
    get_table_schema_and_sample,
    validate_sql_query,
    run_sql_query,
    get_table_relationships,
    get_table_statistics,
)
import os

load_dotenv()

class TestDatabaseUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize database connection
        initialize_db_connection('localhost', 'root', os.environ.get("DB_Password"), 'sakila')

    @classmethod
    def tearDownClass(cls):
        # Close database connection
        close_db_connection()

    # def test_narrow_xml_scope(self):
    #     # This test assumes you have a sample XML file
    #     table_names = ['film', 'actor']
    #     result = narrow_xml_scope(table_names)
    #     self.assertIsInstance(result, str)
    #     self.assertIn('film', result)
    #     self.assertIn('actor', result)
    #     # self.assertNotIn('customer', result)

    def test_list_tables(self):
        tables = list_tables()
        self.assertIsInstance(tables, list)
        self.assertIn('film', tables)
        self.assertIn('actor', tables)

    def test_get_table_schema_and_sample(self):
        result = get_table_schema_and_sample('film')
        self.assertIsInstance(result, str)
        self.assertIn('film_id', result)
        self.assertIn('title', result)
        self.assertIn('Sample Data:', result)

    def test_validate_sql_query(self):
        valid_query = "SELECT * FROM film LIMIT 5"
        invalid_query = "SELECT * FROM non_existent_table"
        self.assertTrue(validate_sql_query(valid_query))
        self.assertFalse(validate_sql_query(invalid_query))

    def test_run_sql_query(self):
        query = "SELECT film_id, title FROM film LIMIT 3"
        result = run_sql_query(query)
        self.assertIsInstance(result, str)
        self.assertIn('film_id', result)
        self.assertIn('title', result)

    def test_get_table_relationships(self):
        result = get_table_relationships()
        self.assertIsInstance(result, str)
        self.assertIn('film', result)
        self.assertIn('actor', result)

    def test_get_table_statistics(self):
        result = get_table_statistics('film')
        self.assertIsInstance(result, str)
        self.assertIn('Total rows:', result)
        self.assertIn('Columns:', result)
        self.assertIn('Indexes:', result)

if __name__ == '__main__':
    unittest.main()