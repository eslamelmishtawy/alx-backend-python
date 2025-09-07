import csv
import uuid

import mysql.connector
from mysql.connector import errorcode

CSV_FILE = '../user_data.csv'
DB_NAME = 'ALX_prodev'
TABLE_NAME = 'user_data'

def connect_db():
	"""Connects to the MySQL server (not to a specific database)."""
	return mysql.connector.connect(
		host='localhost',
		user='root',
		password=''  # Update with your MySQL root password if needed
	)

def create_database(connection):
	"""Creates the database ALX_prodev if it does not exist."""
	cursor = connection.cursor()
	try:
		cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
	finally:
		cursor.close()

def connect_to_prodev():
	"""Connects to the ALX_prodev database."""
	return mysql.connector.connect(
		host='localhost',
		user='root',
		password='',  # Update with your MySQL root password if needed
		database=DB_NAME
	)

def create_table(connection):
	"""Creates the user_data table if it does not exist."""
	cursor = connection.cursor()
	table_sql = f'''
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
	user_id CHAR(36) PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	email VARCHAR(255) NOT NULL,
	age DECIMAL NOT NULL,
	INDEX(user_id)
)
'''
	try:
		cursor.execute(table_sql)
	finally:
		cursor.close()

def insert_data(connection, data):
	"""Inserts data into the user_data table if it does not exist."""
	cursor = connection.cursor()
	select_sql = f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE email=%s"
	insert_sql = f"INSERT INTO {TABLE_NAME} (user_id, name, email, age) VALUES (%s, %s, %s, %s)"
	for row in data:
		cursor.execute(select_sql, (row['email'],))
		exists = cursor.fetchone()[0]
		if not exists:
			cursor.execute(insert_sql, (str(uuid.uuid4()), row['name'], row['email'], row['age']))
	connection.commit()
	cursor.close()

def read_csv(csv_file):
	"""Reads user data from CSV file."""
	with open(csv_file, newline='', encoding='utf-8') as f:
		reader = csv.DictReader(f)
		return [row for row in reader]

def stream_user_data(connection):
	"""Generator that streams rows from user_data table one by one."""
	cursor = connection.cursor(dictionary=True)
	cursor.execute(f"SELECT * FROM {TABLE_NAME}")
	for row in cursor:
		yield row
	cursor.close()

if __name__ == "__main__":
	conn = connect_db()
	create_database(conn)
	conn.close()
	conn = connect_to_prodev()
	create_table(conn)
	data = read_csv(CSV_FILE)
	insert_data(conn, data)
	conn.close()
