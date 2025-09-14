"""Run multiple database queries concurrently using asyncio.gather and aiosqlite.

Requirements:
 - async_fetch_users(): fetch all users
 - async_fetch_older_users(): fetch users older than 40
 - fetch_concurrently(): run both concurrently and print results
 - Use asyncio.run(fetch_concurrently()) entrypoint

This script assumes an SQLite database file 'example.db' used by earlier examples.
It will create / migrate the `users` table and seed sample data (idempotent).
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, List

import aiosqlite

DB_FILE = "example.db"


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	email TEXT NOT NULL UNIQUE,
	age INTEGER
)
"""

SEED_USERS = [
	("Alice", "alice@example.com", 20),
	("Bob", "bob@example.com", 30),
	("Charlie", "charlie@example.com", 40),
	("Diana", "diana@example.com", 45),
	("Edward", "edward@example.com", 55),
]


async def ensure_seed() -> None:
	"""Ensure table exists and seed sample data if empty."""
	async with aiosqlite.connect(DB_FILE) as db:
		await db.execute(CREATE_TABLE_SQL)
		# Count existing rows
		async with db.execute("SELECT COUNT(*) FROM users") as cursor:
			(count,) = await cursor.fetchone()
		if count == 0:
			await db.executemany(
				"INSERT INTO users (name, email, age) VALUES (?, ?, ?)", SEED_USERS
			)
		await db.commit()


async def async_fetch_users() -> List[Dict[str, Any]]:
	"""Fetch all users asynchronously."""
	async with aiosqlite.connect(DB_FILE) as db:
		db.row_factory = aiosqlite.Row  # type: ignore[attr-defined]
		async with db.execute("SELECT * FROM users") as cursor:
			rows = await cursor.fetchall()
			return [dict(r) for r in rows]


async def async_fetch_older_users() -> List[Dict[str, Any]]:
	"""Fetch users older than 40 (fixed threshold per spec)."""
	age_threshold = 40
	async with aiosqlite.connect(DB_FILE) as db:
		db.row_factory = aiosqlite.Row  # type: ignore[attr-defined]
		async with db.execute("SELECT * FROM users WHERE age > ?", (age_threshold,)) as cursor:
			rows = await cursor.fetchall()
			return [dict(r) for r in rows]


async def fetch_concurrently() -> None:
	await ensure_seed()
	all_users_task = async_fetch_users()
	older_users_task = async_fetch_older_users()
	all_users, older_users = await asyncio.gather(all_users_task, older_users_task)

	print("All Users ({}):".format(len(all_users)))
	for u in all_users:
		print(u)
	print("\nUsers older than 40 ({}):".format(len(older_users)))
	for u in older_users:
		print(u)


if __name__ == "__main__":
	asyncio.run(fetch_concurrently())

