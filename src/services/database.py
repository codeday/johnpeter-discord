import mysql.connector


class Database:
    def __init__(self, user, password, host, database):
        self.user=user
        self.password=password
        self.host=host
        self.database=database
        self.conn = None

    def __enter__(self):
        self.conn = mysql.connector.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            database=self.database)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
