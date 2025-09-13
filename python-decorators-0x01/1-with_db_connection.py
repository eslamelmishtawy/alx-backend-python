"""Decorator example: automatically open and close a SQLite connection.

Provides a ``with_db_connection`` decorator that:
1. Opens a SQLite connection (users.db)
2. Injects it into the wrapped function via a ``conn`` keyword argument
3. Closes it after the function finishes (even if an error occurs)

Usage:
@with_db_connection
def get_user_by_id(user_id: int, conn=None):
	...

user = get_user_by_id(user_id=1)
"""

import functools
import sqlite3


def with_db_connection(func):
	"""Decorator to manage a per-call SQLite connection.

	If the caller supplies an existing ``conn`` keyword argument (and it's a
	sqlite3.Connection), that connection is reused and NOT closed by the
	decorator. Otherwise a new connection is created and injected.
	"""

	@functools.wraps(func)
	def wrapper(*args, **kwargs):
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


@with_db_connection
def get_user_by_id(user_id: int, conn=None):
	cursor = conn.cursor()  # type: ignore[union-attr]
	cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
	return cursor.fetchone()


if __name__ == "__main__":
	user = get_user_by_id(user_id=1)
	print(user)

