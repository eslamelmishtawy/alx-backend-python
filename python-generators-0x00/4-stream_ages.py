import mysql.connector

DB_NAME = 'ALX_prodev'
TABLE_NAME = 'user_data'

def stream_user_ages():
    """Generator that yields user ages one by one from the database."""
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # Update if needed
        database=DB_NAME
    )
    cursor = conn.cursor()
    cursor.execute(f"SELECT age FROM {TABLE_NAME}")
    for (age,) in cursor.fetchall():
        try:
            yield float(str(age))
        except (TypeError, ValueError):
            continue
    cursor.close()
    conn.close()

def compute_average_age():
    """Computes and prints the average age using the generator."""
    total = 0.0
    count = 0
    for age in stream_user_ages():
        total += age
        count += 1
    average = total / count if count > 0 else 0
    print(f"Average age of users: {average}")

if __name__ == "__main__":
    compute_average_age()
