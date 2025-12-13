import bcrypt
import sqlite3
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import os
import base64


class Utils:
    global sqlite_file
    global fernet
    sqlite_file = r"C:\Users\lidor\Desktop\school_cyber_project-master\DB\final_project_db.sqlite"
    FERNET_KEY = b'ZsX3c8oaPpQozRaFVqFn3sDN1eQ0dB08eBlt2hJXqa8='
    fernet = Fernet(FERNET_KEY)

    def createDB(self):
        conn = sqlite3.connect(sqlite_file)
        conn.commit()
        conn.close()

    def create_table(self, table_name, items):
        conn = sqlite3.connect(sqlite_file)
        db_cursor = conn.cursor()

        db_cursor.execute(f"""CREATE TABLE {table_name}
                  ({items})""")

        conn.commit()
        conn.close()

    def encrypt_message(self, message):
        return fernet.encrypt(message.encode())

    def decrypt_message(self, token ):
        return fernet.decrypt(token).decode()

    def handle_signup(self, email, password, username):
        try:
            bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()

            hashed_password = bcrypt.hashpw(bytes, salt)

            conn = sqlite3.connect(sqlite_file)
            db_cursor = conn.cursor()
            db_cursor.execute("""INSERT INTO Users (email, password, username)
    VALUES (?, ?, ?);""", (email, str(hashed_password.decode()), username))

            conn.commit()
            conn.close()
            return "200"

        except Exception as e :
            return f"{e}"

    def handle_login(self, email, password):
        conn = sqlite3.connect(sqlite_file)
        db_cursor = conn.cursor()

        db_cursor.execute(f"""
SELECT password FROM Users WHERE email = '{email}'
""")
        hashed_password_tup = db_cursor.fetchone()
        if hashed_password_tup is not None:
            # Found a user with that email.
            hashed_password = hashed_password_tup[0]
            conn.commit()
            conn.close()

            if bcrypt.checkpw(password.encode(), hashed_password.encode()):
                return "200"
            else:
                # wrong password
                return "401"

        return "There isn't a user with that email"

    def get_username(self, email):
        conn = sqlite3.connect(sqlite_file)
        db_cursor = conn.cursor()

        db_cursor.execute(f"""SELECT username FROM USERS WHERE email = '{email}'""")
        username_tup = db_cursor.fetchone()
        if username_tup:
            conn.commit()
            conn.close()
            return username_tup[0]

test = Utils()
# test.createDB()
# test.create_table("Users", "email TEXT PRIMARY KEY, password TEXT")
