

from seed import TABLE_NAME, connect_to_prodev


def stream_users_in_batches(batch_size):
	"""
	Generator that yields batches of users from MySQL database
	"""
	conn = connect_to_prodev()
	cursor = conn.cursor(dictionary=True)
	offset = 0
	while True:
		cursor.execute("SELECT * FROM user_data LIMIT %s OFFSET %s", (batch_size, offset))
		batch = cursor.fetchall()
		if not batch:
			break
		yield batch
		offset += batch_size
	cursor.close()
	conn.close()
	return


def batch_processing(batch_size):
	"""
	Processes each batch to filter users over the age of 25
	"""
	for batch in stream_users_in_batches(batch_size):
		filtered = []
		for user in batch:
			try:
				age = float(user['age'])
				if age > 25:
					filtered.append(user)
			except (KeyError, ValueError, TypeError):
				continue
		yield filtered

