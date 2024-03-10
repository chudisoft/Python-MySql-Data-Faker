import mysql.connector  #pip install mysql-connector
from faker import Faker #pip install faker
import random
from datetime import datetime


# Database configuration
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'university_erp'
}

# Establishing a database connection
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Create Faker instance
fake = Faker()

# Function to generate fake data based on column type
def generate_data(column_type):
    if 'varchar' in column_type or 'text' in column_type:
        return fake.word() if 'varchar' in column_type else fake.text()
    elif 'int' in column_type:
        return random.randint(1, 100)
    elif 'date' in column_type:
        return fake.date()
    elif 'year' in column_type:
        return random.randint(2000, datetime.now().year)
    elif 'enum' in column_type:
        enum_values = column_type.split("enum('")[1].rstrip("')").split("','")
        return random.choice(enum_values)
    elif 'decimal' in column_type:
        precision, scale = map(int, column_type.split('(')[1].split(')')[0].split(','))
        return round(random.uniform(0, 10**precision), scale)
    elif 'boolean' in column_type:
        return random.choice([True, False])
    else:
        return None


# Function to generate and insert data for a given table
def generate_and_insert_data(table_name):
    cursor.execute(f"DESCRIBE {table_name}")
    columns = cursor.fetchall()

    # Generate data for each row
    for _ in range(10):  # Generate 10 rows of data for each table
        row_data = []
        for column in columns:
            column_name, column_type = column[0], column[1]
            row_data.append(generate_data(column_type))

        # Insert data into table
        placeholders = ', '.join(['%s'] * len(row_data))
        cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", tuple(row_data))
    conn.commit()

# Main script execution
try:
    # Get list of tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    # Generate and insert data for each table
    for table in tables:
        table_name = table[0]
        generate_and_insert_data(table_name)

    print("Data insertion successful.")

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    cursor.close()
    conn.close()
