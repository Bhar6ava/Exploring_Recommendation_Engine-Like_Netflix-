import psycopg2
from psycopg2 import sql

# Database connection settings
db_settings = {
    "dbname": "capstone_netflix",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost"
}

def create_database():
    conn = psycopg2.connect(**db_settings)
    conn.autocommit = True  # Enable autocommit for creating databases
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE capstone_netflix")
    cursor.close()
    conn.close()

def create_table():
    conn = psycopg2.connect(**db_settings)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            genre VARCHAR(255),
            description TEXT,
            thumbnail_path VARCHAR(255)
            
        )
    """)
    
    '''
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_auth (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255),
            password VARCHAR(255)
        )               
    """)
    '''

    conn.commit()
    cursor.close()
    conn.close()

def drop_table():
    conn = psycopg2.connect(**db_settings)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS movies")
    conn.commit()
    cursor.close()
    conn.close()

def drop_database():
    conn = psycopg2.connect(**db_settings)
    conn.autocommit = True  # Enable autocommit for dropping databases
    cursor = conn.cursor()
    cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(
        sql.Identifier("mydatabase")
    ))
    cursor.close()
    conn.close()

def list_databases():
    conn = psycopg2.connect(**db_settings)
    cursor = conn.cursor()
    cursor.execute("SELECT datname FROM pg_database")
    databases = [record[0] for record in cursor.fetchall()]
    cursor.close()
    conn.close()
    return databases

def list_tables():
    conn = psycopg2.connect(**db_settings)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)
    tables = [record[0] for record in cursor.fetchall()]
    cursor.close()
    conn.close()
    return tables

# Example usage:
if __name__ == "__main__":
    #create_database()
    create_table()
    #drop_table()
    #drop_database()
    #print(list_databases())
    #print(list_tables())