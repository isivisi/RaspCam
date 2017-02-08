# RaspCam
# A simple web controller for raspberry pi cameras.
# Written by John Iannandrea

import raspcam.camera
import raspcam.models
import threading
import time
import tornado
import tornado.ioloop
import tornado.web
import raspcam.database
import os
import uuid
import signal

cam = raspcam.camera.PICam()
performLoop = True

# Create app
def main():
    port = int(database.getSetting("port"))
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

# Describes the tornado webapp.
def make_app():
    settings= {
        "static_path": os.path.dirname(__file__),
        "cookie_secret": uuid.uuid4().hex
    }

    return tornado.web.Application([
        (r"/", MainHandler),
        (r'/login', LoginHandler),
        (r"/camera/(.*)", CameraHandler),
        #(r'/feed/(.*)', tornado.web.StaticFileHandler, {'path': os.path.dirname(__file__) + '/feed'}),
        (r'/feed/.*', FeedHandler)
    ], **settings)

# Handles the main webpage
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # Make sure the user is logged in
        #if not self.get_secure_cookie("user"):
        #    self.redirect("/login")
        #    return

        # grab camera details and split them into arrays of two for visual purposes
        cameras = database.getCameras()
        cameras = [cameras[i:i + 2] for i in range(0, len(cameras), 2)]
        self.render("web/index.html", cameras=cameras)

# Specific camera view
class CameraHandler(tornado.web.RequestHandler):
    def get(self, page):
        if page == "new":
            self.render('web/newcamera.html')
        else:
            self.render("web/camera.html")

    def post(self, page):
        camName = self.get_argument("cameraName")
        ip = self.get_argument("ip")
        port = self.get_argument("port")

        if camName and ip and port:
            location = '%s:%s/feed/' % (ip, port,)
            database.createCamera(camName, location, 0, str(uuid.uuid4()))
            print("New camera location added")
            self.redirect('/')
            return
        self.redirect("/camera/new")

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

# Grab image from camera upon request
class FeedHandler(tornado.web.RequestHandler):
    def get(self):
        # returns the image in bytes
        imageStream = cam.getImage()
        bytes = imageStream.getvalue()
        # setup headers so the webbrowser know how to deal with our dats
        self.set_header('Content-type', 'image/jpg')
        self.set_header('Content-length', len(bytes))
        self.write(bytes)

main()