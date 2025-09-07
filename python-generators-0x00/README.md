## Overview

This project demonstrates how to set up a MySQL database, create a table, and populate it with sample data from a CSV file using Python. It also shows how to stream data from the database efficiently using a generator.

### What happens in `seed.py`?

1. **Database Setup**: The script connects to a MySQL server and creates a database called `ALX_prodev` if it does not exist.
2. **Table Creation**: It creates a table named `user_data` with the following fields:
   - `user_id` (Primary Key, UUID, Indexed)
   - `name` (VARCHAR, NOT NULL)
   - `email` (VARCHAR, NOT NULL)
   - `age` (DECIMAL, NOT NULL)
3. **Data Population**: The script reads user data from `user_data.csv` and inserts each row into the database, skipping duplicates based on email.
4. **Streaming Data**: The function `stream_user_data(connection)` is a generator that streams rows from the `user_data` table one by one. This is memory-efficient and useful for processing large datasets.

### Why use `yield`?

Using `yield` in a generator function allows you to process data one item at a time (streaming), rather than loading all data into memory. This is especially important for large tables, as it keeps memory usage low and makes your code scalable.

### Example Usage

```python
conn = connect_to_prodev()
for row in stream_user_data(conn):
	print(row)  # Process each row
conn.close()
```

This will print each row from the database, one at a time.
