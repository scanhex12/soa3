import sqlite3
from flask import Flask, request, make_response
import json
from settings import HTTP_DATABASE_PORT_1

class DatabaseHandler:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def open_connection(self):
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.connection.commit()

    def execute_read_query(self, query, params=None):
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()

    def create_table(self, name, columns):
        self.execute_query(f"CREATE TABLE IF NOT EXISTS {name} ({columns})")

    def insert_row(self, table_name, row_values):
        columns_count = len(row_values)
        placeholders = ', '.join(['?'] * columns_count)
        query = f"REPLACE INTO {table_name} VALUES ({placeholders})"
        self.execute_query(query, row_values)

    def update_row(self, table_name, key_name, key_value, column, value):
        query = f"UPDATE {table_name} SET {column} = ? WHERE {key_name} = ?"
        self.execute_query(query, (value, key_value))

    def get_row(self, table_name, key_name, key_value):
        query = f"SELECT * FROM {table_name} WHERE {key_name} = ?"
        return self.execute_read_query(query, (key_value,))

app = Flask(__name__)

db_handler = DatabaseHandler("database.db")

@app.route('/auth', methods=['GET', 'POST'])
def password():
    db_handler.open_connection()
    body = json.loads(request.data)
    login = body.get('login')

    if request.method == 'GET':
        password = db_handler.get_row("passwords", "login", login)
        db_handler.close_connection()
        if not password:
            return make_response('', 403)
        return make_response(password[0][1].strip(), 200)
    else:
        password = body.get('password')
        existing_password = db_handler.get_row("passwords", "login", login)
        if existing_password:
            db_handler.close_connection()
            return make_response('', 403)

        db_handler.insert_row("passwords", (login, password))
        db_handler.close_connection()
        return make_response('', 200)

@app.route('/data', methods=['GET'])
def data():
    db_handler.open_connection()
    body = json.loads(request.data)
    login = body.get('login')
    row = db_handler.get_row("users_data", "login", login)
    
    if not row:
        db_handler.close_connection()
        return make_response('User not found', 404)
    
    metadata_keys = ['firstName', 'lastName', 'birthDate', 'mail', 'phoneNumber']
    metadata = {}
    
    if row:
        for i, key in enumerate(metadata_keys):
            value = row[0][i + 1] if i + 1 < len(row[0]) else None
            metadata[key] = value if value else 'inc key'
    
    db_handler.close_connection()
    
    return make_response(json.dumps(metadata), 200)

@app.route('/data/add', methods=['POST'])
def add_user():
    db_handler.open_connection()
    
    body = json.loads(request.data)
    
    login = body.get('login')
    first_name = body.get('firstName')
    last_name = body.get('lastName')
    birth_date = body.get('birthDate')
    mail = body.get('mail')
    phone_number = body.get('phoneNumber')
    
    user_data = (login, first_name, last_name, birth_date, mail, phone_number)
    
    db_handler.insert_row("users_data", user_data)
    
    db_handler.close_connection()
    
    return make_response('User added successfully', 200)

def main():
    db_handler.open_connection()
    db_handler.create_table("passwords", "login TEXT PRIMARY KEY, password TEXT")
    db_handler.create_table("users_data", "login TEXT PRIMARY KEY, firstName TEXT, lastName TEXT, birthDate DATE, mail TEXT, phoneNumber TEXT")
    db_handler.close_connection()

    app.run(host='0.0.0.0', port=HTTP_DATABASE_PORT_1, debug=True)

if __name__ == "__main__":
    main()
