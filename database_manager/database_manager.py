import sqlite3
import logging
from cryptography.fernet import Fernet
KEY = b'gkqJ7l5FqJvqe7MqaQSKG5Pl2KZvj2ho5Vgbv4E6UJQ='

class DatabaseManager:
    def __init__(self, db_path='historical_data.db'):
        self.db_path = db_path
        self.create_user_config_table()

    def _get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")
            raise
        return conn

    def create_user_config_table(self):
        try:
            with self._get_connection() as conn:
                conn.execute(f'''CREATE TABLE IF NOT EXISTS user_config
                                  (id INTEGER PRIMARY KEY,
                                   api_key TEXT NOT NULL,
                                   api_secret TEXT NOT NULL,
                                   paper BOOLEAN NOT NULL DEFAULT 0)''')
        except sqlite3.Error as e:
            logging.error(f"Error creating table user_config: {e}")
            raise

    def create_table(self, table_name):
        try:
            with self._get_connection() as conn:
                conn.execute(f'''CREATE TABLE IF NOT EXISTS {table_name}
                                  (timestamp TEXT PRIMARY KEY, data BLOB)''')
        except sqlite3.Error as e:
            logging.error(f"Error creating table {table_name}: {e}")
            raise

    def select_data(self, table_name, start=None, end=None):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'SELECT data FROM {table_name} WHERE timestamp BETWEEN ? AND ?', (start, end))
                return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error selecting data from {table_name}: {e}")
            raise

    def insert_data(self, table_name, data):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(f'INSERT OR REPLACE INTO {table_name} VALUES (?, ?)', data)
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error inserting data into {table_name}: {e}")
            raise

    def store_user_config(self, api_key, api_secret, paper):
        encrypted_key = self.encrypt(api_key)
        encrypted_secret = self.encrypt(api_secret)
        self.delete_user_config()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'INSERT INTO user_config (api_key, api_secret, paper) VALUES (?, ?, ?)',
                           (encrypted_key, encrypted_secret, int(paper)))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error storing user config: {e}")
            raise

    def delete_user_config(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'DELETE FROM user_config')
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error deleting user config: {e}")
            raise

    def retrieve_user_config(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'SELECT api_key, api_secret, paper FROM user_config')
                row = cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Error retrieving user config: {e}")
            raise

        if row is None:
            # Return default values (or raise an error, or whatever you prefer)
            return None, None, False

        encrypted_key, encrypted_secret, paper = row
        decrypted_key = self.decrypt(encrypted_key)
        decrypted_secret = self.decrypt(encrypted_secret)
        return decrypted_key, decrypted_secret, bool(paper)

    @staticmethod
    def encrypt(data):
        fernet = Fernet(KEY)
        # Ensure data is bytes
        data = data.encode() if isinstance(data, str) else data
        return fernet.encrypt(data).decode()  # Return as a string for storage in the DB

    @staticmethod
    def decrypt(data):
        fernet = Fernet(KEY)
        # Ensure data is bytes
        data = data.encode() if isinstance(data, str) else data
        return fernet.decrypt(data).decode()  # Return as a string


db_manager = DatabaseManager()
