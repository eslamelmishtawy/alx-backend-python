"""Reusable context manager that both manages DB connection and executes a query.

Objective:
	Provide a class-based context manager `ExecuteQuery` that:
	- Accepts a database path, a SQL query with placeholders, and parameters.
	- Opens the connection and executes the query in `__enter__`.
	- Returns the fetched results (all rows) from `__enter__`.
	- Commits if successful, rolls back on exception, and closes connection in `__exit__`.

Example:
	with ExecuteQuery("example.db", "SELECT * FROM users WHERE age > ?", (25,)) as rows:
		for row in rows:
			print(dict(row))
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence, Type


class ExecuteQuery:
	"""Context manager that executes a read-only (or modifying) query automatically.

	Parameters:
		db_path: Path to the sqlite database file.
		query: SQL string (may contain placeholders ? )
		params: Optional sequence of parameters matching placeholders.

	Behavior:
		- Opens connection and cursor in __enter__.
		- Executes the query immediately.
		- Fetches all rows (for SELECT) and returns them.
		- On exit, commits if no exception else rolls back, and closes.
	"""

	def __init__(self, db_path: str | Path, query: str, params: Optional[Sequence[Any]] = None):
		self.db_path = str(db_path)
		self.query = query
		self.params = params or []
		self._conn: Optional[sqlite3.Connection] = None
		self._cursor: Optional[sqlite3.Cursor] = None
		self._results: Optional[list[sqlite3.Row]] = None

	def __enter__(self) -> Iterable[sqlite3.Row]:  # returns rows
		self._conn = sqlite3.connect(self.db_path)
		self._conn.row_factory = sqlite3.Row
		self._cursor = self._conn.cursor()
		self._cursor.execute(self.query, self.params)

		# For SELECT-like statements, fetch results
		if self.query.strip().lower().startswith("select"):
			self._results = self._cursor.fetchall()
			return self._results
		# For non-select statements, return affected rowcount (wrapped) for consistency
		self._results = []
		return self._results

	def __exit__(
		self,
		exc_type: Optional[Type[BaseException]],
		exc: Optional[BaseException],
		exc_tb: Optional[Any],
	) -> bool:
		if self._conn is not None:
			try:
				if exc_type is None:
					self._conn.commit()
				else:
					self._conn.rollback()
			finally:
				if self._cursor is not None:
					self._cursor.close()
				self._conn.close()
		# Propagate exception if any
		return False


def _ensure_age_and_seed(db_file: str = "example.db") -> None:
	"""Ensure users table exists, has an age column, and sample ages populated."""
	conn = sqlite3.connect(db_file)
	try:
		cur = conn.cursor()
		# Ensure table exists (mirrors earlier file but idempotent)
		cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS users (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				name TEXT NOT NULL,
				email TEXT NOT NULL UNIQUE
			)
			"""
		)
		# Check for age column existence
		cur.execute("PRAGMA table_info(users)")
		columns = [row[1] for row in cur.fetchall()]
		if "age" not in columns:
			cur.execute("ALTER TABLE users ADD COLUMN age INTEGER")

		# Populate ages where NULL
		cur.execute("UPDATE users SET age = 20 WHERE age IS NULL AND name = 'Alice'")
		cur.execute("UPDATE users SET age = 30 WHERE age IS NULL AND name = 'Bob'")
		cur.execute("UPDATE users SET age = 40 WHERE age IS NULL AND name = 'Charlie'")
		conn.commit()
	finally:
		conn.close()


def main():
	db = "example.db"
	_ensure_age_and_seed(db)

	query = "SELECT * FROM users WHERE age > ?"
	param = (25,)
	print(f"Executing: {query} {param}")
	with ExecuteQuery(db, query, param) as rows:
		for row in rows:
			print(dict(row))


if __name__ == "__main__":
	main()

