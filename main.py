import string
import mysql.connector
from faker import Faker
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

# Dictionary to store primary key records for each table (both existing and newly generated)
table_records = {}
# Global sets to store unique values for Username, names and emails
unique_names = set()
unique_emails = set()
unique_usernames = set()
unique_coursecodes = set()

def generate_unique_value(pattern, existing_set):
    if 'Name' in pattern:
        value = fake.name()
        while value in existing_set:
            value = fake.name()
        existing_set.add(value)
        return value
    elif 'Email' in pattern:
        value = fake.email()
        while value in existing_set:
            value = fake.email()
        existing_set.add(value)
        return value
    elif 'Username' in pattern:
        value = fake.user_name()
        while value in existing_set:
            value = fake.user_name()
        existing_set.add(value)
        return value
    elif 'CourseCode' in pattern:
        value = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        while value in existing_set:
            value = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        existing_set.add(value)
        return value
    return None


# Function to preload existing unique names and emails
def preload_unique_values():
    cursor.execute("SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s", (db_config['database'],))
    for table_name, column_name in cursor.fetchall():
        if 'Name' in column_name or 'Email' in column_name or 'Username' in column_name or 'CourseCode' in column_name:
            cursor.execute(f"SELECT DISTINCT {column_name} FROM {table_name}")
            for (value,) in cursor.fetchall():
                if 'Name' in column_name:
                    unique_names.add(value)
                elif 'Email' in column_name:
                    unique_emails.add(value)
                elif 'Username' in column_name:
                    unique_usernames.add(value)
                elif 'CourseCode' in column_name:
                    unique_coursecodes.add(value)

# Call this function after establishing the database connection
preload_unique_values()

# Function to generate fake data based on column type
def generate_data(column_type, table_name=None, column_name=None):
    # Check for patterns in column names
    if 'Name' in column_name or 'Email' in column_name or 'Username' in column_name or 'CourseCode' in column_name:
        appropriate_set = unique_usernames if 'Username' in column_name else unique_coursecodes if 'CourseCode' in column_name else unique_emails if 'Email' in column_name else unique_names
        return generate_unique_value(column_name, appropriate_set)

    # For foreign key columns, choose from existing values in the related table
    if table_name and column_name and (table_name, column_name) in foreign_keys_info:
        fk_table, fk_column = foreign_keys_info[(table_name, column_name)]
        if table_records[fk_table][fk_column]:
            return random.choice(list(table_records[fk_table][fk_column]))
        else:
            return None

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

# Function to get primary key columns for a table
def get_primary_key_columns(table_name):
    cursor.execute("""
        SELECT column_name
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE table_name = %s AND table_schema = %s
        AND constraint_name = 'PRIMARY'
    """, (table_name, db_config['database']))
    return [row[0] for row in cursor.fetchall()]

# Function to get foreign key information
def get_foreign_keys_info():
    cursor.execute("""
        SELECT 
            table_name, 
            column_name, 
            referenced_table_name, 
            referenced_column_name 
        FROM 
            information_schema.KEY_COLUMN_USAGE 
        WHERE 
            referenced_table_schema = %s 
            AND referenced_table_name IS NOT NULL;
    """, (db_config['database'],))
    return {(row[0], row[1]): (row[2], row[3]) for row in cursor.fetchall()}

# Get foreign key information
foreign_keys_info = get_foreign_keys_info()

# Function to load existing primary key values for each table
def load_existing_pk_values():
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        pk_columns = get_primary_key_columns(table_name)
        table_records[table_name] = {pk: set() for pk in pk_columns}
        if pk_columns:
            cursor.execute(f"SELECT {', '.join(pk_columns)} FROM {table_name}")
            for row in cursor.fetchall():
                for i, pk in enumerate(pk_columns):
                    table_records[table_name][pk].add(row[i])

# Load existing primary key values
load_existing_pk_values()

# Function to generate and insert data for a given table
def generate_and_insert_data(table_name):
    cursor.execute(f"DESCRIBE {table_name}")
    columns = cursor.fetchall()
    primary_keys = get_primary_key_columns(table_name)
    new_records = []

    # Generate data for each row
    for _ in range(10):  # Generate 10 rows of data for each table
        row_data = []
        for column in columns:
            column_name, column_type = column[0], column[1]
            data = generate_data(column_type, table_name, column_name)
            if column_name in primary_keys:
                # Ensure primary key uniqueness
                while data in table_records[table_name][column_name]:
                    data = generate_data(column_type, table_name, column_name)
                table_records[table_name][column_name].add(data)
            row_data.append(data)

        new_records.append(tuple(row_data))

    # Insert data into table
    if new_records:
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f"INSERT INTO {table_name} ({', '.join(column[0] for column in columns)}) VALUES ({placeholders})"
        try:
            cursor.executemany(insert_query, new_records)
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            conn.rollback()  # Rollback in case of an error

# Main script execution
try:
    # Disable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    conn.commit()

    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    # Generate and insert data for each table
    for table in tables:
        table_name = table[0]
        generate_and_insert_data(table_name)

    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conn.commit()

    print("Data insertion successful.")

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    cursor.close()
    conn.close()
