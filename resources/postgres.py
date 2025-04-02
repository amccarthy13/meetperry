import os

import psycopg2


class PostgreSQL:

    def __init__(self):
        self.conn = None
        self.DB_HOST = os.getenv("DB_HOST", "host.docker.internal")
        self.DB_PORT = os.getenv("DB_PORT", "5432")
        self.DB_USER = os.getenv("DB_USER", "postgres")
        self.DB_NAME = os.getenv("DB_NAME", "meetperry")

    def set_db_connection(self):
        conn = psycopg2.connect(
            host=self.DB_HOST,
            port=self.DB_PORT,
            dbname=self.DB_NAME,
            user=self.DB_USER,
        )
        self.conn = conn

    def execute(self, query, params=None):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params)
            cursor.close()
            self.conn.commit()
        except Exception as e:
            cursor.close()
            self.conn.commit()
            raise e


    def execute_one(self, query: str, params=None):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params)
            row = cursor.fetchone()
            cursor.close()
            self.conn.commit()
            return row
        except Exception as e:
            cursor.close()
            self.conn.commit()
            raise e

    def execute_many(self, query: str, params=None):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()
            self.conn.commit()
            return rows
        except Exception as e:
            cursor.close()
            self.conn.commit()
            raise e

    def exists(self, query: str, params=None):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params)
            row = cursor.fetchone()
            cursor.close()
            self.conn.commit()
            return bool(row[0])
        except Exception as e:
            cursor.close()
            self.conn.commit()
            raise e