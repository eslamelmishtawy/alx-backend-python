"""
stream_users.py
A generator function to stream rows from the user_data table one by one using MySQL.
"""
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Update with your MySQL root password if needed
    'database': 'ALX_prodev'
}
TABLE_NAME = 'user_data'


def stream_user_data():
	"""Generator that streams rows from user_data table one by one."""
	connection = mysql.connector.connect(**DB_CONFIG)
	cursor = connection.cursor(dictionary=True)
	cursor.execute(f"SELECT * FROM {TABLE_NAME}")
	while True:
		row = cursor.fetchone()
		if row is None:
			break
		yield row
	cursor.close()
	connection.close()
