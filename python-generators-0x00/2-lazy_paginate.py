from seed import connect_to_prodev

DB_NAME = 'ALX_prodev'
TABLE_NAME = 'user_data'

def paginate_users(page_size, offset):
	"""
	Fetches a page of users from the MySQL database starting at the given offset.
	"""
	conn = connect_to_prodev()
	cursor = conn.cursor(dictionary=True)
	query = f"SELECT name, email, age FROM {TABLE_NAME} ORDER BY user_id LIMIT %s OFFSET %s"
	cursor.execute(query, (page_size, offset))
	users = cursor.fetchall()
	cursor.close()
	conn.close()
	return users

def lazy_paginate(page_size):
	"""
	Generator that yields pages of users lazily from the MySQL database.
	"""
	offset = 0
	while True:
		page = paginate_users(page_size, offset)
		if not page:
			break
		yield page
		offset += page_size
