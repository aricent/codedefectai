"""
MariaDB Class performs
1. connects to database
2. executes queries
3. inserts data
"""

import mysql.connector as maria_db


class MariaDB:

    def __init__(self, host, port, database, user_name, password):
        self.conn = maria_db.connect(user=user_name, password=password, database=database, host=host, port=port, ssl_ca='/cdpscheduler/certificate/BaltimoreCyberTrustRoot.crt.pem', ssl_verify_cert=True, use_pure=True)
        #self.conn = maria_db.connect(user=user_name, password=password, database=database, host=host, port=port)
        self.conn.autocommit = True

    def close_connection(self):
        self.conn.close()

    def execute_query(self, query):
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor

    def update_query(self, query, values):
        cursor = self.conn.cursor()
        cursor.execute(query, values, multi=True)
        self.conn.commit()
        return cursor

    def insert_query(self, query, values):
        cursor = self.conn.cursor()
        cursor.execute(query, values)
        self.conn.commit()

    def commit(self):
        self.conn.commit()
