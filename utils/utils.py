import bcrypt
import sqlite3


class Utils:
    global sqlite_file
    sqlite_file = r"C:\Users\Pc2\Desktop\cyber_final_project\DB\final_project_db.sqlite"

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

    def handle_signup(self, email, password):
        try:
            bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()

            hashed_password = bcrypt.hashpw(bytes, salt)

            conn = sqlite3.connect(sqlite_file)
            db_cursor = conn.cursor()
            db_cursor.execute(f"""INSERT INTO Users (email, password)
    VALUES ('{email}', '{str(hashed_password.decode())}');""")

            conn.commit()
            conn.close()
            return "200"

        except:
            return "500"

    def handle_login(self, email, password):
        conn = sqlite3.connect(sqlite_file)
        db_cursor = conn.cursor()

        db_cursor.execute(f"""
SELECT password FROM Users WHERE email = '{email}'
""")
        hashed_password = db_cursor.fetchone()[0]
        conn.commit()
        conn.close()

        if bcrypt.checkpw(password.encode(), hashed_password.encode()):
            return "200"

        return "401"


test = Utils()
# test.createDB()
# test.create_table("Users", "email TEXT PRIMARY KEY, password TEXT")
