import sqlite3

connection = sqlite3.connect('products.db')
cursor = connection.cursor()


def get_all_products():
    cursor.execute('SELECT * FROM Products')
    return cursor.fetchall()


def __add_products():
    for i in range(1, 5):
        cursor.execute(
            f"INSERT INTO Products (title, description, price) VALUES ('Продукт {i}', 'Описание {i}', {i * 100})"
        )
    # connection.commit()


def add_user(username, email, age, balance=1000):
    cursor.execute(
        f"INSERT INTO Users (username, email, age, balance) VALUES ('{username}', '{email}', {age}, {balance})"
    )
    connection.commit()


def is_included(username):
    count = cursor.execute(f"SELECT COUNT(*) FROM Users WHERE username = '{username}'").fetchone()
    return count[0] > 0


def initiate_db():
    cursor.execute('''
CREATE TABLE IF NOT EXISTS Products(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL
)
''')
    cursor.execute('''
CREATE TABLE IF NOT EXISTS Users(
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    age INTEGER NOT NULL,
    balance INTEGER NOT NULL
)
''')
    if len(get_all_products()) == 0:
        __add_products()
    connection.commit()


initiate_db()
# connection.commit()
# connection.close()