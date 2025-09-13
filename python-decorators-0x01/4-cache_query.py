"""Cache query decorator example.

Implements:
1. with_db_connection - opens/closes SQLite connection per call.
2. cache_query - caches results of SELECT queries based on the SQL string.

Notes:
- Cache key is the raw query string (normalized stripping whitespace). If you
  need param-based caching, extend to include params.
- Only caches successful executions; exceptions bypass caching.
- Returns a shallow copy of the cached list to avoid accidental mutation.
"""

import functools
import sqlite3
from typing import Any, Callable

query_cache: dict[str, Any] = {}


def with_db_connection(func: Callable) -> Callable:
	"""Decorator to manage a per-call SQLite connection."""

	@functools.wraps(func)
	def wrapper(*args: Any, **kwargs: Any):
		existing = kwargs.get("conn")
		if isinstance(existing, sqlite3.Connection):
			return func(*args, **kwargs)
		conn = sqlite3.connect("users.db")
		try:
			kwargs["conn"] = conn
			return func(*args, **kwargs)
		finally:
			conn.close()

	return wrapper


def cache_query(func: Callable) -> Callable:
	"""Cache results of a query function based solely on the SQL string.

	Assumes the wrapped function signature includes (conn, query) or
	keyword argument `query`.
	"""

	@functools.wraps(func)
	def wrapper(*args: Any, **kwargs: Any):
		# Attempt to obtain 'query' from kwargs or positional args
		query = kwargs.get("query")
		if query is None:
			# Assume positional after possible conn: (conn, query) or (query,)
			if len(args) == 0:
				raise ValueError("cache_query decorator couldn't locate the SQL query argument")
			# If first arg is a connection, query should be second
			if isinstance(args[0], sqlite3.Connection):
				if len(args) < 2:
					raise ValueError("Expected query argument after connection parameter")
				query = args[1]
			else:
				query = args[0]

		if not isinstance(query, str):
			raise TypeError("Query must be a string for caching")

		key = " ".join(query.split())  # simple normalization (collapse whitespace)

		if key in query_cache:
			cached = query_cache[key]
			# Return a shallow copy for safety (lists/tuples expected)
			if isinstance(cached, list):
				return list(cached)
			if isinstance(cached, tuple):
				return tuple(cached)
			return cached

		result = func(*args, **kwargs)
		query_cache[key] = result
		return result

	return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query: str):
	cursor = conn.cursor()
	cursor.execute(query)
	return cursor.fetchall()


if __name__ == "__main__":
	# First call - executes query and caches
	users = fetch_users_with_cache(query="SELECT * FROM users")
	print("First call rows:", users)
	# Second call - served from cache
	users_again = fetch_users_with_cache(query="SELECT * FROM users")
	print("Second call (cached) rows:", users_again)
