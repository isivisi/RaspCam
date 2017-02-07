# Database functions
# Author: John Iannandrea

import sqlite3
import hashlib
import uuid
import os

databaseFilename = "raspcam.db"

# Sets up the default database state
def default():
    conn = sqlite3.connect(databaseFilename)
    conn.execute('''CREATE TABLE users (userId INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT,
                    salt TEXT)''')
    conn.execute('''CREATE TABLE cameras (name text,
                    lastKnownLocation text)''')

    # Create default admin user
    passwordData = hashPass("admin")
    t = (passwordData["hash"], passwordData["salt"],)
    conn.execute('''INSERT INTO users (username, password, salt) VALUES ('admin', ?, ?)''', t)

    conn.commit()
    conn.close()

# Checks if username and password are in the database. This function takes in the unhashed password.
def userCheck(username, password):
    conn = sqlite3.connect(databaseFilename)
    t = (username,)
    rows = conn.execute("SELECT * FROM users WHERE username=?", t)
    for row in rows:
        passwordData = hashPass(password, salt=row[3])
        if passwordData["hash"] == row[2]:
            return True
    return False

# Hashes a given password with a unique salt or specified salt. Returns both the final hash and generated salt.
def hashPass(password, salt=uuid.uuid4().hex):
    pdata = {}
    pdata["salt"] = salt
    t_sha = hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8'))
    pdata["hash"] = t_sha.hexdigest()
    return pdata

# make sure database exists
if not os.path.isfile(databaseFilename):
    default()