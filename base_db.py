import sqlite3


class DataBase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def disconnect(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()

    def execute_query(self, query, params=None):
        if params:
            self.connect()
            self.cursor.execute(query, params)
        else:
            self.connect()
            self.cursor.execute(query)
        self.connection.commit()
        self.disconnect()

    def fetch_all(self, query, params=None):
        if params:
            self.connect()
            self.cursor.execute(query, params)
        else:
            self.connect()
            self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def fetch_one(self, query, params=None):
        if params:
            self.connect()
            self.cursor.execute(query, params)
        else:
            self.connect()
            self.cursor.execute(query)
        return self.cursor.fetchone()

    def create_table_task_usd(self):
        query = """
        CREATE TABLE IF NOT EXISTS task_usd
        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER, 
        symbol_usd TEXT, 
        amount_usd INTEGER, 
        task_type_usd INTEGER)
        """
        self.execute_query(query)

    def create_table_parser_usd(self):
        query = """
        CREATE TABLE IF NOT EXISTS parser_usd
        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
        price_usd INTEGER, 
        symbol_usd TEXT)
        """
        self.execute_query(query)


db = DataBase('db.db')
db.connect()
db.create_table_task_usd()
db.create_table_parser_usd()
