import logging
import sqlite3
from functools import wraps

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s - %(message)s')
logger = logging.getLogger(__name__)


def log_queries(func):
	"""Decorator that logs the SQL query before executing the wrapped function.

	It looks for a 'query' keyword argument; if absent, assumes the first
	positional argument is the SQL query.
	"""
	@wraps(func)
	def wrapper(*args, **kwargs):
		query = kwargs.get("query")
		if query is None and args:
			query = args[0]
		logger.info("Executing query: %s", query)
		return func(*args, **kwargs)
	return wrapper


@log_queries
def fetch_all_users(query):
	conn = sqlite3.connect('users.db')
	try:
		cursor = conn.cursor()
		cursor.execute(query)
		results = cursor.fetchall()
	finally:
		conn.close()
	return results


if __name__ == "__main__":
	# Example (will log query; may raise if DB or table doesn't exist)
	try:
		users = fetch_all_users(query="SELECT * FROM users")
		logger.info("Fetched %d rows", len(users))
	except sqlite3.Error as e:
		logger.error("Database error: %s", e)
