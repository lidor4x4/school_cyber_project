import bcrypt
import sqlite3
from cryptography.fernet import Fernet
import os
from globals import globals


class Utils:
    global sqlite_file
    global fernet
    sqlite_file = r"C:\Users\Pc2\Desktop\school_cyber_project\DB\final_project_db.sqlite"
    
    FERNET_KEY = b'WmNayxAvMomFuoWRSyEtFaHhptS-nrodlSnZsvHpeoI='
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

    def decrypt_message(self, message):
        return fernet.decrypt(message).decode()

    def handle_signup(self, email, password, username, user_type): 
        try:
            bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            verified = True
            hashed_password = bcrypt.hashpw(bytes, salt)
            if user_type == "dr":
                verified = False
            conn = sqlite3.connect(sqlite_file)
            db_cursor = conn.cursor()
            db_cursor.execute("""INSERT INTO Users (email, password, username, role, verified)
    VALUES (?, ?, ?, ?, ?);""", (email, str(hashed_password.decode()), username, user_type, verified))

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

        db_cursor.execute(f"""SELECT username FROM Users WHERE email = '{email}'""")
        username_tup = db_cursor.fetchone()
        if username_tup:
            conn.commit()
            conn.close()
            return username_tup[0]

    def get_email_by_username(self, username):
        conn = sqlite3.connect(sqlite_file)
        db_cursor = conn.cursor()

        db_cursor.execute("SELECT email FROM Users WHERE username=?", (username,))
        email_tup = db_cursor.fetchone()
        if email_tup:
            conn.commit()
            conn.close()
            return email_tup[0]

    def get_verified_by_username(self, username):
        try:
            conn = sqlite3.connect(sqlite_file)
            db_cursor = conn.cursor()
            username = username.replace(" ", "", 1)
            db_cursor.execute("SELECT verified FROM Users WHERE username=?", (username,))
            verified_tup = db_cursor.fetchone()
            print(verified_tup[0])
            if verified_tup:
                conn.commit()
                conn.close()
                return verified_tup[0]

        except Exception as e:
            print(f"Error getting verified user: {e}")
            return 0        

    def get_unverified_users(self):
        try:
            conn = sqlite3.connect(sqlite_file)
            cursor = conn.cursor()

            cursor.execute("""SELECT email FROM Users WHERE verified = 0 AND (rejected IS NULL OR rejected = 0)""")
            emails = [row[0] for row in cursor.fetchall()]
            conn.close()
            return emails

        except Exception as e:
            print(f"Error fetching unverified users: {e}")
            return []


    def get_verified_dr_users(self):
        try:
            conn = sqlite3.connect(sqlite_file)
            cursor = conn.cursor()

            cursor.execute("""SELECT username FROM Users WHERE verified = 1 AND role = 'dr' """)

            emails = [row[0] for row in cursor.fetchall()]
            conn.close()
            return emails

        except Exception as e:
            print(f"Error fetching verified users: {e}")
            return []


    def verify_user(self, email, verify):
        try:
            conn = sqlite3.connect(sqlite_file)
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET verified = ? WHERE email = ?", (1 if verify else 0, email))
            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error verifying user {email}: {e}")


    def reject_user(self, email):
        try:
            conn = sqlite3.connect(sqlite_file) 
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET rejected = 1 WHERE email = ?",(email,))
            conn.commit()
            conn.close()
            print(f"User {email} marked as rejected.")
        except Exception as e:
            print(f"Error rejecting user {email}: {e}")

    def get_role_by_email(self, email):
        try:
            conn = sqlite3.connect(sqlite_file) 
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM Users WHERE email = ?",(email,))
            role_tup = cursor.fetchone()
            if role_tup:
                conn.commit()
                conn.close()
                return role_tup[0]
        
        except Exception as e:
            print(f"Error fetching user role: {e}")
            return 

    def get_dr_queue_by_username(self, username):
        try:
            conn = sqlite3.connect(sqlite_file) 
            cursor = conn.cursor()
            cursor.execute("SELECT clients_in_line FROM Users WHERE username = ?",(username,))
            queue_tup = cursor.fetchone()
            if queue_tup and queue_tup[0] != None:
                conn.commit()
                conn.close()
                return queue_tup[0]
            
            else:
                conn.commit()
                conn.close()
                return "The queue is empty"
            
        except Exception as e:
            print(f"Error fetching dr queue: {e}")
            return 
        
    def add_to_dr_queue(self, dr_username, username):
        try:
            
            conn = sqlite3.connect(sqlite_file) 
            cursor = conn.cursor()

            cursor.execute("SELECT clients_in_line FROM Users WHERE username = ?",(dr_username,))
            dr_queue = cursor.fetchone()[0]

            # "fdfsf, fdsfdf, fdsf"
            
            if dr_queue == "" or dr_queue is None:
                dr_queue = username
            else:
                if username in dr_queue.split(","):
                    print("User already in queue")
                    conn.close()
                    return "User already in queue"
                
                dr_queue += f",{username}"   

            cursor.execute("UPDATE Users SET clients_in_line = ? WHERE username = ?",(dr_queue, dr_username))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error fetching dr queue: {e}")
            return

    

test = Utils()
# test.createDB()
# test.create_table("Users", "email TEXT PRIMARY KEY, password TEXT")
