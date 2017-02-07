import sqlite3
import hashlib
import uuid
import os

databaseFilename = "raspcam.db"

def default():
    conn = sqlite3.connect(databaseFilename)
    conn.execute('''CREATE TABLE users (userId INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, salt TEXT)''')

    passwordData = hashPass("admin")
    t = (passwordData["hash"], passwordData["salt"],)
    conn.execute('''INSERT INTO users (username, password, salt) VALUES ('admin', ?, ?)''', t)
    conn.execute('''CREATE TABLE cameras (name text, lastKnownLocation text)''')
    conn.commit()
    conn.close()

def userCheck(username, password):
    conn = sqlite3.connect(databaseFilename)
    t = (username,)
    rows = conn.execute("SELECT * FROM users WHERE username=?", t)
    for row in rows:
        passwordData = hashPass(password, salt=row[3])
        if passwordData["hash"] == row[2]:
            return True
    return False

def hashPass(password, salt=uuid.uuid4().hex):
    pdata = {}
    pdata["salt"] = salt
    t_sha = hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8'))
    pdata["hash"] = t_sha.hexdigest()
    return pdata

# make sure database exists
if not os.path.isfile(databaseFilename):
    default()