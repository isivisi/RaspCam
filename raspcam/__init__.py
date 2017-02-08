# RaspCam
# A simple web controller for raspberry pi cameras.
# Written by John Iannandrea

import raspcam.camera
import threading
import time
import tornado
import tornado.ioloop
import tornado.web
import raspcam.database
import os
import uuid
import signal

port = 8888
cam = raspcam.camera.PICam()
performLoop = True

# Create app
def main():
    # cam.streamCamera()
    #threading._start_new_thread(record, (cam, fileLocation,))

    app = make_app()
    app.listen(port)
    print("Starting web application on port %s" % port)
    signal.signal(signal.SIGINT, signalHandler)
    tornado.ioloop.IOLoop.current().start()


# stop ioloop on shutdown
def signalHandler(signum, frame):
    global performLoop, cam
    tornado.ioloop.IOLoop.instance().stop()
    del(cam)
    performLoop = False
    print("RaspCam application shut down")
    exit()

# Grabs current image from the camera and saves it on the filesystem.
def record(cam, file):
    global performLoop
    #while performLoop == True:
        #time.sleep(0.1)
        #file = open(file, 'wb')
    cam.getImage(file);
        #file.flush()
        #file.close()
    print("file capture begin")

# Describes the tornado webapp.
def make_app():
    settings= {
        "static_path": os.path.dirname(__file__),
        "cookie_secret": uuid.uuid4().hex
    }

    return tornado.web.Application([
        (r"/", MainHandler),
        (r'/login', LoginHandler),
        (r"/camera/.*", CameraHandler),
        #(r'/feed/(.*)', tornado.web.StaticFileHandler, {'path': os.path.dirname(__file__) + '/feed'}),
        (r'/feed/.*', FeedHandler)
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

class FeedHandler(tornado.web.RequestHandler):
    def get(self):
        imageStream = cam.getImage()
        bytes = imageStream.getvalue()
        self.set_header('Content-type', 'image/jpg')
        self.set_header('Content-length', len(bytes))
        self.write(bytes)

main()