class Camera:
    def __init__(self, name, location, privacy, uniqueid, rotation):
        self.name = name
        self.location = location
        self.privacy = privacy
        self.uniqueid = uniqueid
        self.rotation = rotation

    def __str__(self):
        return "%s,%s,%s,%s" % (self.name, self.location, self.privacy, self.uniqueid)

# User info that isnt password data
class User:
    def __init__(self, id, username, isAdmin):
        self.id = id
        self.username = username
        self.isAdmin = isAdmin

class KeyValuePair:
    def __init__(self, key, value, type, isVisible):
        self.key = key
        self.value = value
        self.type = type
        self.isVisible = isVisible