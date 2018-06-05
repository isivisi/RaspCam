# Database functions
# Author: John Iannandrea

import sqlite3
import hashlib
import uuid
import os
import raspcam.models
import uuid
import json

databaseFilename = "raspcam.json"

# Sets up the default database state
def default():

    # default json settings
    settings = {
        "isHub": True,
        "setup": True,
        "port":8080,
        "users":[
            {
                "userName":"admin",
                "password":"admin"
            }
        ],
        "cameras": [
            {
                "name":"Camera Name",
                "ip": "127.0.0.1",
                "port": 8080
            }
         ]
    }

    # write json file in pwd
    with open(databaseFilename, 'w') as fp:
        json.dump(settings, fp)

    defaultCamid = str(uuid.uuid4())

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