"""Database connection context manager example.

Creates a simple class based context manager `DatabaseConnection` that
opens an sqlite3 database and ensures the connection is properly closed.

Usage:
	with DatabaseConnection('example.db') as cursor:
		cursor.execute('SELECT * FROM users')
		for row in cursor.fetchall():
			print(row)
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Optional, Type


class DatabaseConnection:
	"""Class-based context manager for an SQLite database.

	Responsibilities:
	- Open connection on enter and return a cursor.
	- Commit if no exception; rollback if an exception occurs.
	- Always close the cursor and connection on exit.
	"""

	def __init__(self, db_path: str | Path):
		self.db_path = str(db_path)
		self._conn: Optional[sqlite3.Connection] = None
		self._cursor: Optional[sqlite3.Cursor] = None

	def __enter__(self) -> sqlite3.Cursor:
		self._conn = sqlite3.connect(self.db_path)
		# Return rows as dictionaries for nicer printing (optional)
		self._conn.row_factory = sqlite3.Row
		self._cursor = self._conn.cursor()
		return self._cursor

	def __exit__(
		self,
		exc_type: Optional[Type[BaseException]],
		exc: Optional[BaseException],
		exc_tb: Optional[Any],
	) -> bool:
		# If an exception occurred, rollback; else commit
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

		# Returning False so any exception propagates after cleanup
		return False


def _ensure_users_seed(db_file: str = "example.db") -> None:
	"""Create a users table with seed data if it does not already exist."""
	with DatabaseConnection(db_file) as cur:
		cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS users (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				name TEXT NOT NULL,
				email TEXT NOT NULL UNIQUE
			)
			"""
		)
		# Check if table already has data
		cur.execute("SELECT COUNT(*) AS count FROM users")
		count = cur.fetchone()[0]
		if count == 0:
			cur.executemany(
				"INSERT INTO users (name, email) VALUES (?, ?)",
				[
					("Alice", "alice@example.com"),
					("Bob", "bob@example.com"),
					("Charlie", "charlie@example.com"),
				],
			)


def main():
	db_file = "example.db"
	_ensure_users_seed(db_file)

	print("Users table rows:")
	with DatabaseConnection(db_file) as cursor:
		cursor.execute("SELECT * FROM users")
		rows = cursor.fetchall()
		for row in rows:
			# row is sqlite3.Row (acts like mapping)
			print(dict(row))


if __name__ == "__main__":
	main()

