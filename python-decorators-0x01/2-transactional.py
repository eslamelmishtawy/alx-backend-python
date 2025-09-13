"""Transactional decorator example.

Includes:
1. `with_db_connection` - copied from previous task (opens/closes SQLite connection)
2. `transactional` - wraps a DB operation in a transaction, committing on success
   and rolling back on exception.

Behavior of `transactional`:
- Expects the wrapped function to accept a `conn` keyword argument or have it
  injected by `with_db_connection` earlier in the decorator stack.
- Starts a transaction implicitly (SQLite starts one on first write). We
  explicitly call `conn.execute("BEGIN")` to ensure a transaction boundary.
- On success: commits.
- On failure: rolls back then re-raises the exception.

Usage order:
@with_db_connection
@transactional
def create_user(name: str, email: str, conn=None):
	...

The outermost decorator should manage the connection (with_db_connection),
so it appears closest to the function (applied last). This ensures
`transactional` sees a `conn` supplied via kwargs.
"""

import functools
import sqlite3
from typing import Any, Callable


def with_db_connection(func: Callable) -> Callable:
	"""Decorator to manage a per-call SQLite connection.

	If the caller supplies an existing ``conn`` keyword argument (and it's a
	sqlite3.Connection), that connection is reused and NOT closed by the
	decorator. Otherwise a new connection is created and injected.
	"""

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


def transactional(func: Callable) -> Callable:
	"""Wrap function execution in a DB transaction.

	Assumes a sqlite3.Connection is available via the `conn` kwarg (injected by
	`with_db_connection`). If none is found, raises a RuntimeError.
	"""

	@functools.wraps(func)
	def wrapper(*args: Any, **kwargs: Any):
		conn = kwargs.get("conn")
		if not isinstance(conn, sqlite3.Connection):
			raise RuntimeError("transactional decorator requires a 'conn' keyword argument (use with_db_connection above it)")

		# Start explicit transaction
		conn.execute("BEGIN")
		try:
			result = func(*args, **kwargs)
			conn.commit()
			return result
		except Exception:
			conn.rollback()
			raise

	return wrapper


@with_db_connection
@transactional
def create_user(name: str, email: str, conn=None):  # type: ignore[annotation-unchecked]
	"""Insert a user row; will commit or rollback automatically."""
	cursor = conn.cursor()  # type: ignore[union-attr]
	cursor.execute(
		"INSERT INTO users (name, email) VALUES (?, ?)",
		(name, email),
	)
	return cursor.lastrowid


@with_db_connection
def ensure_schema(conn=None):  # type: ignore[annotation-unchecked]
	cursor = conn.cursor()  # type: ignore[union-attr]
	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY,
			name TEXT NOT NULL,
			email TEXT NOT NULL UNIQUE
		)
		"""
	)


if __name__ == "__main__":
	ensure_schema()
	try:
		user_id = create_user("Bob", "bob@example.com")
		print("Inserted user id:", user_id)
	except sqlite3.IntegrityError as e:
		print("Integrity error:", e)
