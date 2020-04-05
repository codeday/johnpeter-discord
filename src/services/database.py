import mysql.connector


class Database:
    def __init__(self, user, password, host, database):
        self.user=user
        self.password=password
        self.host=host
        self.database=database
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = mysql.connector.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            database=self.database)
        self.cursor = self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        self.conn = None
        self.cursor = None

    def add_row(self, table, headers: list, values: list):
        exc = (f"INSERT INTO {table} "
               f"({str(headers)[1:-1]}) "
               f"VALUES ({str(values)[1:-1]})")
        with self:
            self.cursor.execute(exc)
