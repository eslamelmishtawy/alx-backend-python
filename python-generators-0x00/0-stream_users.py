"""
stream_users.py
A generator function to stream rows from the user_data table one by one using MySQL.
"""

from seed import TABLE_NAME, connect_to_prodev


def stream_users():
	"""Generator that streams rows from user_data table one by one."""
	connection = connect_to_prodev()
	cursor = connection.cursor(dictionary=True)
	cursor.execute(f"SELECT * FROM {TABLE_NAME}")
	while True:
		row = cursor.fetchone()
		if row is None:
			break
		yield row
	cursor.close()
	connection.close()
