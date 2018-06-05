# Database functions
# Author: John Iannandrea

import sqlite3
import hashlib
import uuid
import os
import raspcam.models
import uuid

databaseFilename = "raspcam.db"

# Sets up the default database state
def default():
    conn = sqlite3.connect(databaseFilename)
    conn.execute('''CREATE TABLE settings (key TEXT,
                    value TEXT,
                    type TEXT,
                    canModify BOOLEAN)''')
    conn.execute('''CREATE TABLE users (userId INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    salt TEXT,
                    isAdmin BOOLEAN)''')
    conn.execute('''CREATE TABLE cameras (name TEXT,
                    lastKnownLocation TEXT,
                    privacy BOOLEAN,
                    uniqueid TEXT PRIMARY KEY,
                    rotation INTEGER)''')

    # Create default admin user
    passwordData = hashPass("admin")
    t = (passwordData["hash"], passwordData["salt"],1)
    conn.execute('''INSERT INTO users (username, password, salt, isAdmin) VALUES ('admin',?,?,?)''', t)

    # Setup settings
    t = ("Hub", "0", 'bool', 1)
    conn.execute('''INSERT INTO settings (key, value, type, canModify) VALUES (?,?,?,?)''', t)
    t = ("Port", "8888", 'string', 1)
    conn.execute('''INSERT INTO settings (key, value, type, canModify) VALUES (?,?,?,?)''',t)
    t = ("firstStart", "1", 'bool', 0)
    conn.execute('''INSERT INTO settings (key, value, type, canModify) VALUES (?,?,?,?)''', t)

    defaultCamid = str(uuid.uuid4())
    t = ("localCamera", defaultCamid, 'string', 0)
    conn.execute('''INSERT INTO settings (key, value, type, canModify) VALUES (?,?,?,?)''', t)

    conn.commit()
    conn.close()

    # Default camera built into pi
    createCamera("Main Camera", "/feed/", 0, defaultCamid, 0)

def changeSetting(key, value):
    conn = sqlite3.connect(databaseFilename)
    t = (key,str(value),key,)
    conn.execute('''UPDATE settings SET key = ?, value = ? WHERE key = ?''', t)
    conn.commit()
    conn.close()

def getSetting(key):
    conn = sqlite3.connect(databaseFilename)
    t = (key,)
    for row in conn.execute('''SELECT value FROM settings WHERE key = ?''', t):
        return row[0]
    return None

# returns all settings in their KeyValuePair form
def getSettings():
    conn = sqlite3.connect(databaseFilename)
    keyvals = []
    for row in conn.execute('''SELECT * FROM settings'''):
        keyvals.append(raspcam.models.KeyValuePair(row[0], row[1], row[2], row[3]))
    return keyvals

# Might not need
def createCamera(name, location, privacy, uniqueid, rotation=0):
    conn = sqlite3.connect(databaseFilename)
    t = (name,location,privacy,uniqueid,rotation,)
    conn.execute('''INSERT INTO cameras (name, lastKnownLocation, privacy, uniqueid, rotation) VALUES (?,?,?,?,?)''', t)
    conn.commit()
    conn.close()

def getCamera(uniqueId):
    conn = sqlite3.connect(databaseFilename)
    t = (uniqueId,)
    for row in conn.execute('''SELECT * FROM cameras WHERE uniqueId = ?'''):
        return raspcam.models.Camera(row[0], row[1], row[2], row[3])

def getUser(username):
    conn = sqlite3.connect(databaseFilename)
    t = (username,)
    for row in conn.execute('''SELECT * FROM users WHERE username =?''', t):
        return raspcam.models.User(row[0], row[1], row[4]) # exclude password and salt. use userCheck for that
    print("No user found")
    return None

def getCameras(local=False):
    conn = sqlite3.connect(databaseFilename)
    cams = []
    for row in conn.execute('''SELECT * FROM cameras''') if not local else \
            conn.execute('''SELECT * FROM cameras WHERE uniqueid = ?''', (getSetting("localCamera"),)):
        cams.append(raspcam.models.Camera(row[0], row[1], row[2], row[3], row[4]))
    return cams

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