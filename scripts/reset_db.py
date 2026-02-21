import psycopg2
import sys

DB_NAME = 'campo_db'
DB_USER = 'postgres'
DB_PASS = '123456'
DB_HOST = 'localhost'
DB_PORT = 5432

def main():
    try:
        conn = psycopg2.connect(dbname='postgres', user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        cur.execute(f"CREATE DATABASE {DB_NAME}")
        cur.close()
        conn.close()
        print('Database reset successful')
    except Exception as e:
        print('Error resetting database:', e)
        sys.exit(1)

if __name__ == '__main__':
    main()
