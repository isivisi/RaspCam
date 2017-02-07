# RaspCam
# A simple web controller for raspberry pi cameras.
# Written by John Iannandrea

#import raspcam.camera
import threading
import time
import tornado
import tornado.ioloop
import tornado.web
import raspcam.database
import os
import uuid

fileLocation = "liveFeed.png"
port = 8888

# Create app
def main():
    #cam = raspcam.camera.PICam()
    #file =open(fileLocation, 'wb')
    #threading._start_new_thread(record, (cam, file,))

    app = make_app()
    app.listen(port)
    print("Starting web application on port %s" % port)
    tornado.ioloop.IOLoop.current().start()

# Grabs current image from the camera and saves it on the filesystem.
def record(cam, file):
    while 1:
        cam.getImage(file);
        time.sleep(0.15) # 60 times a second

# Describes the tornado webapp.
def make_app():
    settings= {
        "static_path": os.path.dirname(__file__),
        "cookie_secret": uuid.uuid4().hex
    }

    return tornado.web.Application([
        (r"/", MainHandler),
        (r'/login', LoginHandler),
        (r"/camera/.*", CameraHandler)
    ], **settings)

# Handles the main webpage
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # Make sure the user is logged in
        if not self.get_secure_cookie("user"):
            self.redirect("/login")
            return
        self.render("web/index.html")

# Specific camera view
class CameraHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("web/camera.html")

# Handles login page and sets up session
class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("web/login.html")

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        if username != "" and password != "":
            #If user information was correct give them a secure cookie so we can identify what user they are later.
            if raspcam.database.userCheck(username, password):
                self.set_secure_cookie("user", username)
                print("Login successful for user %s" % username)
                self.redirect("/")
                return
        print("Failed login attempt for user %s" % username)
        self.redirect("/login")

main()