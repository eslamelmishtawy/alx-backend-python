"""Retry decorator example for transient SQLite errors.

Includes:
1. with_db_connection - copied from earlier task
2. retry_on_failure(retries=3, delay=2) - retries on Exception with sleep

Example:
@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
	...
"""

import functools
import sqlite3
import time
from typing import Any, Callable


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


def retry_on_failure(retries: int = 3, delay: float = 2.0, exceptions: tuple[type[BaseException], ...] = (Exception,)):
	"""Retry a function if it raises one of the specified exceptions.

	Parameters
	----------
	retries : int
		Maximum number of attempts (initial try + (retries-1) more). If <= 0, runs once.
	delay : float
		Seconds to sleep between attempts.
	exceptions : tuple[type[BaseException], ...]
		Exception types that trigger a retry.
	"""

	def decorator(func: Callable) -> Callable:
		@functools.wraps(func)
		def wrapper(*args: Any, **kwargs: Any):
			attempts = max(1, retries)
			last_exc: BaseException | None = None
			for attempt in range(1, attempts + 1):
				try:
					return func(*args, **kwargs)
				except exceptions as exc:  # type: ignore[misc]
					last_exc = exc
					if attempt == attempts:
						break
					time.sleep(delay)
			# If we exit loop without returning, re-raise last exception
			assert last_exc is not None
			raise last_exc

		return wrapper

	return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn=None):  # type: ignore[annotation-unchecked]
	cursor = conn.cursor()  # type: ignore[union-attr]
	cursor.execute("SELECT * FROM users")
	return cursor.fetchall()


if __name__ == "__main__":
	try:
		users = fetch_users_with_retry()
		print(users)
	except Exception as e:
		print("Failed after retries:", e)
