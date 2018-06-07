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
                "userName": "admin",
                "isAdmin": True,
                "password": hashPass("admin")
            }
        ],
        "cameras": [
            {
                "uniqueid":str(uuid.uuid4()),
                "name":"Camera Name",
                "location": "/feed/",
                "localCamera": True
            }
         ]
    }

    # write json file in pwd
    saveSettings(settings)

    defaultCamid = str(uuid.uuid4())

    # Default camera built into pi
    # createCamera("Main Camera", "/feed/", 0, defaultCamid, 0)

def getSettings():
    with open(databaseFilename, 'r') as fp:
        settings = json.load(fp)

    return settings

def saveSettings(settings):
    with open(databaseFilename, 'w') as fp:
        json.dump(settings, fp)

# Might not need
def createCamera(name, location, privacy, uniqueid, rotation=0):
    settings = getSettings()

    settings['cameras'].append({
        'uniqueid': uniqueid,
        'name':name,
        'location':location,
        'privacy':privacy,
        'rotation':rotation,
        'localCamera':False
    })

    saveSettings(settings)


def getCamera(uniqueId):
    settings = getSettings()

    # list comprehension ftw
    return next(x for x in settings['cameras'] if x['uniqueid'] == uniqueId)

def getUser(username):
    settings = getSettings()

    return next(x for x in settings['users'] if x['userName'] == username)

def getCameras(local=False):
    settings = getSettings()

    return settings['cameras']

# Checks if username and password are in the database. This function takes in the unhashed password.
def userCheck(username, password):
    settings = getSettings()
    passwordHashed = hashPass(password)

    foundUser = next(x for x in settings['users'] if x['password'] == passwordHashed)
    if foundUser:
        return True
    return False

# Hashes a given password with a unique salt or specified salt. Returns both the final hash and generated salt.
def hashPass(password):
    t_sha = hashlib.sha512(password.encode('utf-8'))
    return t_sha.hexdigest()

# make sure database exists
if not os.path.isfile(databaseFilename):
    default()